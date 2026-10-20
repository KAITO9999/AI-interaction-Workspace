"""Safe, opt-in command resolver with Python standard-library fallbacks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

VERSION = "0.1.0"
# Task -> preferred external commands, then a Python-native fallback.
TASKS = {
    "json-check": {"commands": ["jq"], "fallback": "json-check"},
    "search": {"commands": ["rg", "grep"], "fallback": "search"},
    "find-files": {"commands": ["fd", "find"], "fallback": "find-files"},
    "archive-list": {"commands": ["7z", "unzip", "tar"], "fallback": "archive-list"},
    "sha256": {"commands": ["sha256sum", "shasum"], "fallback": "sha256"},
}
# Package identifiers are intentionally allowlisted; never use sudo or a shell.
PACKAGES = {
    "jq": {"brew": "jq", "apt-get": "jq", "dnf": "jq", "pacman": "jq", "winget": "jqlang.jq", "pkg": "jq"},
    "rg": {"brew": "ripgrep", "apt-get": "ripgrep", "dnf": "ripgrep", "pacman": "ripgrep", "winget": "BurntSushi.ripgrep.MSVC", "pkg": "ripgrep"},
    "fd": {"brew": "fd", "apt-get": "fd-find", "dnf": "fd-find", "pacman": "fd", "winget": "sharkdp.fd", "pkg": "fd"},
    "unzip": {"brew": "unzip", "apt-get": "unzip", "dnf": "unzip", "pacman": "unzip", "winget": "GnuWin32.UnZip", "pkg": "unzip"},
    "sha256sum": {"brew": "coreutils", "apt-get": "coreutils", "dnf": "coreutils", "pacman": "coreutils", "pkg": "coreutils"},
    "7z": {"brew": "p7zip", "apt-get": "p7zip-full", "dnf": "p7zip", "pacman": "p7zip", "pkg": "p7zip"},
}
INSTALLERS = {
    "pkg": lambda package: ["pkg", "install", "-y", package],
    "brew": lambda package: ["brew", "install", package],
    "apt-get": lambda package: ["apt-get", "install", "-y", package],
    "dnf": lambda package: ["dnf", "install", "-y", package],
    "pacman": lambda package: ["pacman", "-S", "--noconfirm", package],
    "winget": lambda package: ["winget", "install", "--exact", "--id", package, "--accept-source-agreements", "--accept-package-agreements"],
}


def run(argv: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run an explicit argv list without shell expansion and with a timeout."""
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)


ENVIRONMENTS = ("auto", "termux", "linux", "wsl", "macos", "windows")


def detect_environment() -> str:
    """Detect the current execution environment, not a remote target."""
    if os.environ.get("TERMUX_VERSION") and "/com.termux/" in os.environ.get("PREFIX", ""):
        return "termux"
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "macos"
    if system == "linux":
        try:
            version = Path("/proc/version").read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            version = ""
        return "wsl" if "microsoft" in version or "wsl" in version else "linux"
    return "linux"


def effective_environment(requested: str) -> tuple[str, str]:
    return (detect_environment(), "auto-detected") if requested == "auto" else (requested, "explicit")


def available_installers(environment: str = "auto") -> list[str]:
    current, _source = effective_environment(environment)
    allowed = {
        "termux": ("pkg",),
        "linux": ("apt-get", "dnf", "pacman", "brew"),
        "wsl": ("apt-get", "dnf", "pacman", "brew"),
        "macos": ("brew",),
        "windows": ("winget",),
    }[current]
    return [name for name in allowed if shutil.which(name)]


def resolve(task: str, environment: str = "auto") -> dict[str, object]:
    spec = TASKS[task]
    found = [(name, shutil.which(name)) for name in spec["commands"] if shutil.which(name)]
    current_environment, environment_source = effective_environment(environment)
    return {
        "task": task,
        "environment": current_environment,
        "environment_source": environment_source,
        "available_commands": [{"command": name, "path": path} for name, path in found],
        "selected_command": found[0][0] if found else None,
        "python_fallback": spec["fallback"],
        "fallback_available": True,
        "installers": available_installers(current_environment),
    }


def fallback(task: str, args: argparse.Namespace) -> int:
    if task == "json-check":
        path = Path(args.target)
        try:
            with path.open("r", encoding="utf-8-sig") as handle:
                json.load(handle)
        except OSError as exc:
            print(f"ERROR reading file: {exc}", file=sys.stderr)
            return 2
        except (UnicodeError, json.JSONDecodeError) as exc:
            print(f"INVALID JSON: {exc}", file=sys.stderr)
            return 1
        print(f"VALID JSON: {path}")
        return 0
    if task == "search":
        if not args.pattern:
            print("ERROR: --pattern is required for search fallback.", file=sys.stderr)
            return 2
        root = Path(args.target).expanduser()
        paths = [root] if root.is_file() else sorted(root.rglob("*")) if root.is_dir() else []
        if not paths:
            print(f"ERROR: target does not exist: {root}", file=sys.stderr)
            return 2
        count = 0
        for path in paths:
            if not path.is_file() or any(part in {".git", "node_modules", ".venv", "venv"} for part in path.parts):
                continue
            try:
                for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if args.pattern.casefold() in line.casefold():
                        print(f"{path}:{number}:{line}")
                        count += 1
            except OSError:
                continue
        return 0 if count else 1
    if task == "find-files":
        root = Path(args.target).expanduser()
        if not root.is_dir():
            print(f"ERROR: directory not found: {root}", file=sys.stderr)
            return 2
        matches = 0
        for path in sorted(root.rglob("*")):
            if any(part in {".git", "node_modules", ".venv", "venv", "__pycache__"} for part in path.parts):
                continue
            if args.pattern and args.pattern.casefold() not in path.name.casefold():
                continue
            print(path)
            matches += 1
        return 0 if matches else 1
    if task == "archive-list":
        path = Path(args.target).expanduser()
        if not path.is_file():
            print(f"ERROR: archive not found: {path}", file=sys.stderr)
            return 2
        try:
            with zipfile.ZipFile(path) as archive:
                for item in archive.infolist():
                    print(f"{item.file_size}\t{item.filename}")
        except (OSError, zipfile.BadZipFile) as exc:
            print(f"ERROR: ZIP listing failed: {exc}", file=sys.stderr)
            return 1
        return 0
    if task == "sha256":
        path = Path(args.target).expanduser()
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        print(f"{digest.hexdigest()}  {path}")
        return 0
    return 2


def try_install(command: str, timeout: int, environment: str = "auto") -> int:
    is_root = getattr(os, "geteuid", lambda: -1)() == 0
    package_map = PACKAGES.get(command, {})
    for manager in available_installers(environment):
        package = package_map.get(manager)
        if not package:
            continue
        if manager == "apt-get" and not is_root:
            print("SKIP apt-get: run is not elevated; AgentKit never invokes sudo.", file=sys.stderr)
            continue
        if manager == "pacman" and not is_root:
            print("SKIP pacman: run is not elevated; AgentKit never invokes sudo.", file=sys.stderr)
            continue
        argv = INSTALLERS[manager](package)
        if any(ch.isspace() for ch in package.strip()) or not package.strip():
            print(f"SKIP invalid allowlisted package for {command}.", file=sys.stderr)
            continue
        print("INSTALL ATTEMPT:", " ".join(argv), flush=True)
        try:
            result = run(argv, timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"INSTALL TIMEOUT after {timeout}s; no automatic retry.", file=sys.stderr)
            return 124
        if result.stdout.strip():
            print(result.stdout.strip()[-2000:])
        if result.stderr.strip():
            print(result.stderr.strip()[-2000:], file=sys.stderr)
        if result.returncode == 0 and shutil.which(command):
            print(f"INSTALL VERIFIED: {command} is now on PATH.")
            return 0
        print(f"INSTALL NOT VERIFIED: exit={result.returncode}; no automatic retry.", file=sys.stderr)
        return result.returncode or 1
    print(f"No safe allowlisted installer/package mapping available for {command}.", file=sys.stderr)
    return 127


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve a task to an installed command or a task-specific Python fallback.",
        epilog="Examples: agentkit_resolve.py json-check data.json; agentkit_resolve.py search src --pattern TODO --prefer-fallback",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("task", choices=sorted(TASKS), help="Task to run.")
    parser.add_argument("target", nargs="?", default=".", help="File, archive, or directory depending on task (default: current directory).")
    parser.add_argument("--pattern", help="Search text or filename substring for search/find-files.")
    parser.add_argument("--environment", choices=ENVIRONMENTS, default="auto", help="Execution environment for installer selection: auto-detect (default), termux, linux, wsl, macos, or windows. This does not emulate another OS.")
    parser.add_argument("--install", action="store_true", help="Explicitly permit one allowlisted package-install attempt; no sudo and no automatic retry.")
    parser.add_argument("--timeout", type=int, default=120, choices=range(1, 601), help="Per-command timeout in seconds (1..600).")
    parser.add_argument("--prefer-fallback", action="store_true", help="Use the Python implementation even when an external command exists; output may differ.")
    parser.add_argument("--json-report", action="store_true", help="Print the resolution report and exit without running a task.")
    args = parser.parse_args()
    report = resolve(args.task, args.environment)
    if args.json_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    selected = report["selected_command"]
    # --install explicitly tries to install the preferred tool even when a less-preferred
    # alternative (for example `find`) is already available. JSON-report remains read-only.
    preferred = TASKS[args.task]["commands"][0]
    if args.install and not args.prefer_fallback and not shutil.which(preferred):
        install_status = try_install(preferred, args.timeout, args.environment)
        if install_status == 0:
            report = resolve(args.task)
            selected = report["selected_command"]
        else:
            print("Preferred command installation failed; continuing with an available alternative or Python fallback.", file=sys.stderr)
    if selected and not args.prefer_fallback:
        command_args: list[str] | None = None
        if args.task == "json-check" and selected == "jq":
            command_args = [selected, "empty", args.target]
        elif args.task == "search" and args.pattern:
            command_args = [selected, "-F", "-i", args.pattern, args.target] if selected == "rg" else [selected, "-R", "-n", "-i", "-F", args.pattern, args.target]
        elif args.task == "find-files" and args.pattern:
            command_args = [selected, args.pattern, args.target] if selected == "fd" else [selected, args.target, "-iname", f"*{args.pattern}*"]
        elif args.task == "archive-list":
            command_args = [selected, "l", args.target] if selected == "7z" else [selected, "-l", args.target] if selected == "unzip" else [selected, "-tf", args.target]
        elif args.task == "sha256":
            command_args = [selected, args.target] if selected == "sha256sum" else [selected, "-a", "256", args.target]
        if command_args is None:
            print(f"AVAILABLE: {selected} ({shutil.which(selected)})")
            print("This task needs additional arguments; provide --pattern where applicable or use --prefer-fallback.")
            return 2
        preferred_for_task = TASKS[args.task]["commands"][0]
        if selected != preferred_for_task:
            print(f"注意、代替コマンドな為既存とは動作が異なります: {selected} (preferred: {preferred_for_task})", file=sys.stderr)
        print("RUN:", " ".join(command_args), flush=True)
        try:
            result = run(command_args, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"ERROR: command timed out after {args.timeout}s; no automatic retry.", file=sys.stderr)
            return 124
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
        return result.returncode
    print("注意、代替コマンドな為既存とは動作が異なります: Python standard-library fallback", file=sys.stderr)
    return fallback(args.task, args)


if __name__ == "__main__":
    raise SystemExit(main())
