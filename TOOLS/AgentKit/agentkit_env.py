"""Diagnose the agent execution environment and recommend capability fallbacks.

AgentKit combines existing tools and standard-library fallbacks so bounded
verification can continue in restricted agent environments when a preferred
tool is missing. It records failures instead of silently discarding them, and
never claims a fallback is equivalent to the original tool. It does not bypass
OS/agent policy or elevate privileges.

This module is the read-only environment diagnostic, not the practical task
runner. It describes the runtime where it is executed (not a remote user's
machine or a hosted AI product). Active probes are local, temporary, bounded,
and opt-in. It never installs packages or contacts the network. For observing a
specific child command and writing timestamped process/output logs, use
agentkit_observe.py; that runner is intentionally separate.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
COMMANDS = (
    "python", "python3", "sh", "bash", "git", "rg", "grep", "find", "fd",
    "jq", "strace", "ltrace", "gdb", "lldb", "perf", "valgrind", "timeout",
    "flock", "inotifywait", "entr", "tree", "tar", "unzip", "7z", "sha256sum",
    "curl", "wget", "pkg", "apt", "apt-get", "brew", "dnf", "pacman", "npm",
    "node", "cargo", "rustc", "gcc", "clang", "cmake", "make", "ninja",
)
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "target", "dist"}

FEATURES: dict[str, dict[str, Any]] = {
    "python_execution": {
        "requires_any": ["python", "python3"],
        "fallback": "No external-command fallback; use the configured agent runtime or report blocked.",
        "why": "Run bounded Python helpers and standard-library implementations.",
    },
    "subprocess_execution": {
        "requires_any": ["python", "python3"],
        "probe": "subprocess",
        "fallback": "Use in-process Python implementations; do not assume shell access.",
        "why": "Launch child processes without shell interpolation.",
    },
    "shell_execution": {
        "requires_any": ["sh", "bash"],
        "fallback": "Use argv-based subprocess calls or Python standard-library operations.",
        "why": "Run scripts through a detected shell; presence does not prove policy permits execution.",
    },
    "filesystem_search": {
        "requires_any": ["rg", "grep", "find", "fd"],
        "fallback": "Python pathlib/os.walk with root, depth, and result-count limits.",
        "why": "Search files or text in a bounded workspace.",
    },
    "json_processing": {
        "requires_any": ["jq", "python", "python3"],
        "fallback": "Python json module.",
        "why": "Validate and transform JSON.",
    },
    "archive_inspection": {
        "requires_any": ["tar", "unzip", "7z", "python", "python3"],
        "fallback": "Python zipfile/tarfile where format support exists; do not extract by default.",
        "why": "List archive contents without extracting untrusted paths.",
    },
    "system_call_tracing": {
        "requires_any": ["strace"],
        "probe": "strace",
        "fallback": "Record argv, timestamps, exit code, duration, stdout/stderr and timeout; this is not syscall tracing.",
        "why": "Observe system calls only if the executable and runtime permissions allow it.",
    },
    "debugging": {
        "requires_any": ["gdb", "lldb"],
        "fallback": "Use application logs, Python tracebacks, core metadata if available, and minimal reproductions.",
        "why": "Native debugger presence does not prove ptrace or target-process access.",
    },
    "process_inspection": {
        "requires_any": ["python", "python3"],
        "fallback": "Use only visible process metadata or application-owned process records.",
        "why": "Inspect the current process and limited /proc metadata; other processes may be hidden.",
    },
    "file_change_watch": {
        "requires_any": ["inotifywait"],
        "fallback": "Bounded polling using file metadata; slower and not event-equivalent.",
        "why": "Watch for file changes if the watcher exists and the filesystem supports it.",
    },
    "package_installation": {
        "requires_any": ["pkg", "apt", "apt-get", "brew", "dnf", "pacman"],
        "fallback": "Do not install automatically; use available commands or document the missing dependency.",
        "why": "A package-manager executable does not prove repositories, permissions, or network access.",
    },
    "network_access": {
        "requires_any": ["curl", "wget"],
        "fallback": "Use local-only workflows or a separately approved network bridge.",
        "why": "Client binaries are not evidence that network egress is allowed. Network is not probed by this tool.",
    },
    "build_native": {
        "requires_any": ["clang", "gcc", "cmake", "make", "ninja", "cargo", "rustc"],
        "fallback": "Use an existing interpreter/runtime or report the required compiler/toolchain.",
        "why": "Compiler presence does not prove headers, linker, SDK, or target architecture support.",
    },
    "persistent_write": {
        "requires_any": ["python", "python3"],
        "probe": "write",
        "fallback": "Use a caller-provided writable workspace or stdout; do not assume home directories are writable.",
        "why": "Probe temporary write access without leaving a file behind.",
    },
}


def _run_probe(argv: list[str], timeout: float = 2.0) -> dict[str, Any]:
    try:
        result = subprocess.run(
            argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-1000:],
            "stderr": result.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout"}
    except (OSError, ValueError) as exc:
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:300]}


def _active_probe(name: str, commands: dict[str, str | None]) -> dict[str, Any]:
    if name == "subprocess":
        return _run_probe([sys.executable, "-c", "print('agentkit-child-ok')"])
    if name == "write":
        candidates = [os.environ.get("TMPDIR"), tempfile.gettempdir(), str(Path.cwd())]
        seen: set[str] = set()
        for raw in candidates:
            if not raw:
                continue
            candidate = str(Path(raw).expanduser())
            if candidate in seen:
                continue
            seen.add(candidate)
            try:
                with tempfile.TemporaryDirectory(prefix="agentkit-probe-", dir=candidate):
                    return {"ok": True, "writable_temp_directory": candidate}
            except (OSError, PermissionError):
                continue
        return {"ok": False, "error": "no writable temporary directory found"}
    if name == "strace":
        executable = commands.get("strace")
        if not executable:
            return {"ok": False, "error": "strace not found"}
        try:
            with tempfile.TemporaryDirectory(prefix="agentkit-strace-") as directory:
                logfile = str(Path(directory) / "trace.log")
                result = subprocess.run(
                    [executable, "-f", "-o", logfile, sys.executable, "-c", "pass"],
                    stdin=subprocess.DEVNULL, capture_output=True, text=True,
                    timeout=3, check=False,
                )
                log_exists = Path(logfile).is_file()
                log_size = Path(logfile).stat().st_size if log_exists else 0
                return {
                    "ok": result.returncode == 0 and log_exists and log_size > 0,
                    "returncode": result.returncode,
                    "trace_log_created": log_exists,
                    "trace_log_bytes": log_size,
                    "stderr": result.stderr[-1000:],
                    "note": "Tests a child process only; it does not prove tracing arbitrary processes.",
                }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout"}
        except OSError as exc:
            return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:300]}
    return {"ok": False, "error": "unknown probe"}


def inspect_environment(active_tests: bool = False) -> dict[str, Any]:
    """Inspect this process's runtime, command presence, and optional local probes."""
    commands = {name: shutil.which(name) for name in COMMANDS}
    termux_prefix = os.environ.get("PREFIX", "")
    is_termux = bool(os.environ.get("TERMUX_VERSION")) or "/com.termux/" in termux_prefix
    is_proot = bool(os.environ.get("PROOT_TMP_DIR")) or bool(os.environ.get("PROOT_LOADER"))
    try:
        euid: int | None = os.geteuid()
    except AttributeError:
        euid = None
    try:
        cwd = str(Path.cwd().resolve())
    except OSError:
        cwd = str(Path.cwd())
    runtime = {
        "os_name": os.name,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "cwd": cwd,
        "home": str(Path.home()),
        "uid": getattr(os, "getuid", lambda: None)(),
        "euid": euid,
        "is_root": euid == 0 if euid is not None else None,
        "is_termux": is_termux,
        "termux_prefix_present": bool(termux_prefix),
        "is_proot_hint": is_proot,
        "container_hints": {
            key: bool(os.environ.get(key))
            for key in ("CI", "CONTAINER", "REMOTE_CONTAINERS", "CODESPACES", "GITHUB_ACTIONS")
        },
    }
    probes: dict[str, Any] = {}
    if active_tests:
        probes["subprocess"] = _active_probe("subprocess", commands)
        probes["write"] = _active_probe("write", commands)
        if commands.get("strace"):
            probes["strace"] = _active_probe("strace", commands)

    features: dict[str, Any] = {}
    for name, spec in FEATURES.items():
        required_all = spec.get("requires", [])
        required_any = spec.get("requires_any", [])
        available_all = all(commands.get(command) for command in required_all)
        available_any = not required_any or any(commands.get(command) for command in required_any)
        if not available_all or not available_any:
            status = "blocked"
            reason = "required executable not found on PATH"
        elif spec.get("probe") and active_tests:
            probe_result = probes.get(spec["probe"], {"ok": False, "error": "probe unavailable"})
            status = "available" if probe_result.get("ok") else "degraded"
            reason = "active probe succeeded" if probe_result.get("ok") else "executable found but active probe failed"
        elif spec.get("probe"):
            status = "detected_unverified"
            reason = "executable found; active test not requested"
        else:
            status = "detected_unverified"
            reason = "prerequisite executable found; permissions and full feature support are not proven"
        if name == "network_access":
            status = "detected_unverified" if available_any else "blocked"
            reason = "network deliberately not tested; executable presence is not proof of egress"
        features[name] = {
            "status": status,
            "reason": reason,
            "detected_prerequisites": [
                {"command": command, "path": commands[command]}
                for command in dict.fromkeys(required_all + required_any)
                if commands.get(command)
            ],
            "fallback": spec["fallback"],
            "why": spec["why"],
        }

    limitations = [
        "This report describes only the process environment where AgentKit is running.",
        "Command presence does not prove authentication, permission, network egress, or successful operation.",
        "Network access is never probed and packages are never installed.",
        "Active probes are local, bounded, and temporary; strace is tested only against a child process.",
        "A detected root UID or container hint is not a security boundary assessment.",
    ]
    return {
        "schema_version": 1,
        "tool": "AgentKit environment capability probe",
        "version": VERSION,
        "active_tests": active_tests,
        "runtime": runtime,
        "commands": {
            "found": [{"command": name, "path": path} for name, path in commands.items() if path],
            "missing": [name for name, path in commands.items() if not path],
        },
        "probes": probes,
        "features": features,
        "limitations": limitations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    parser.add_argument("--output", help="write the report to a file (creates or overwrites it)")
    parser.add_argument("--active-tests", action="store_true", help="run bounded local subprocess/write/strace probes")
    parser.add_argument("--feature", choices=sorted(FEATURES), help="show one feature route")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args(argv)
    report = inspect_environment(active_tests=args.active_tests)
    if args.feature:
        report["features"] = {args.feature: report["features"][args.feature]}
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = Path(args.output).expanduser()
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"ERROR writing report: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        print(f"Saved environment report: {target.resolve()}")
    elif args.json:
        print(rendered, end="")
    else:
        runtime = report["runtime"]
        print(f"{report['tool']} {VERSION}")
        print(f"Runtime: {runtime['system']} {runtime['machine']} | Python {runtime['python_version']}")
        print(f"Termux: {runtime['is_termux']} | PRoot hint: {runtime['is_proot_hint']} | EUID: {runtime['euid']}")
        print(f"Commands: {len(report['commands']['found'])} found / {len(COMMANDS)} checked")
        print("\nFeature routes:")
        for name, item in report["features"].items():
            print(f"  {name}: {item['status']} — {item['reason']}")
            print(f"    fallback: {item['fallback']}")
        if report["probes"]:
            print("\nActive probes:")
            for name, item in report["probes"].items():
                print(f"  {name}: {'PASS' if item.get('ok') else 'FAIL'}")
        print("\nNo packages were installed and no network access was attempted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
