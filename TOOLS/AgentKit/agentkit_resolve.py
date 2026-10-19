#!/usr/bin/env python3
"""Safe, opt-in command resolver with Python standard-library fallbacks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
    "archive-list": {"commands": ["unzip", "tar"], "fallback": "archive-list"},
    "sha256": {"commands": ["sha256sum", "shasum"], "fallback": "sha256"},
}
# Package identifiers are intentionally allowlisted; never use sudo or a shell.
PACKAGES = {
    "jq": {"brew": "jq", "apt-get": "jq", "dnf": "jq", "pacman": "jq", "winget": "jqlang.jq"},
    "rg": {"brew": "ripgrep", "apt-get": "ripgrep", "dnf": "ripgrep", "pacman": "ripgrep", "winget": "BurntSushi.ripgrep.MSVC"},
    "fd": {"brew": "fd", "apt-get": "fd-find", "dnf": "fd-find", "pacman": "fd", "winget": "sharkdp.fd"},
    "unzip": {"brew": "unzip", "apt-get": "unzip", "dnf": "unzip", "pacman": "unzip", "winget": "GnuWin32.UnZip"},
    "sha256sum": {"brew": "coreutils", "apt-get": "coreutils", "dnf": "coreutils", "pacman": "coreutils"},
}
INSTALLERS = {
    "brew": lambda package: ["brew", "install", package],
    "apt-get": lambda package: ["apt-get", "install", "-y", package],
    "dnf": lambda package: ["dnf", "install", "-y", package],
    "pacman": lambda package: ["pacman", "-S", "--noconfirm", package],
    "winget": lambda package: ["winget", "install", "--exact", "--id", package, "--accept-source-agreements", "--accept-package-agreements"],
}


def run(argv: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run an explicit argv list without shell expansion and with a timeout."""
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)


def available_installers() -> list[str]:
    return [name for name in INSTALLERS if shutil.which(name)]


def resolve(task: str) -> dict[str, object]:
    spec = TASKS[task]
    found = [(name, shutil.which(name)) for name in spec["commands"] if shutil.which(name)]
    return {
        "task": task,
        "available_commands": [{"command": name, "path": path} for name, path in found],
        "selected_command": found[0][0] if found else None,
        "python_fallback": spec["fallback"],
        "fallback_available": True,
        "installers": available_installers(),
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


def try_install(command: str, timeout: int) -> int:
    is_root = getattr(os, "geteuid", lambda: -1)() == 0
    package_map = PACKAGES.get(command, {})
    for manager in available_installers():
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("task", choices=sorted(TASKS))
    parser.add_argument("target", nargs="?", default=".", help="File, archive, or directory depending on task.")
    parser.add_argument("--pattern", help="Search text or filename substring.")
    parser.add_argument("--install", action="store_true", help="Explicitly permit one allowlisted package-install attempt.")
    parser.add_argument("--timeout", type=int, default=120, choices=range(1, 601))
    parser.add_argument("--prefer-fallback", action="store_true", help="Use the Python implementation even when a command exists.")
    parser.add_argument("--json-report", action="store_true", help="Print resolution report and exit without running a task.")
    args = parser.parse_args()
    report = resolve(args.task)
    if args.json_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    selected = report["selected_command"]
    if selected and not args.prefer_fallback:
        command_args: list[str] | None = None
        if args.task == "json-check" and selected == "jq":
            command_args = [selected, "empty", args.target]
        elif args.task == "search" and args.pattern:
            command_args = [selected, "-F", "-i", args.pattern, args.target] if selected == "rg" else [selected, "-R", "-n", "-i", "-F", args.pattern, args.target]
        elif args.task == "find-files" and args.pattern:
            command_args = [selected, args.pattern, args.target] if selected == "fd" else [selected, args.target, "-iname", f"*{args.pattern}*"]
        elif args.task == "archive-list":
            command_args = [selected, "-l", args.target] if selected == "unzip" else [selected, "-tf", args.target]
        elif args.task == "sha256":
            command_args = [selected, args.target] if selected == "sha256sum" else [selected, "-a", "256", args.target]
        if command_args is None:
            print(f"AVAILABLE: {selected} ({shutil.which(selected)})")
            print("This task needs additional arguments; provide --pattern where applicable or use --prefer-fallback.")
            return 2
        print("RUN:", " ".join(command_args), flush=True)
        try:
            result = run(command_args, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"ERROR: command timed out after {args.timeout}s; no automatic retry.", file=sys.stderr)
            return 124
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\\n") else "\\n")
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\\n") else "\\n", file=sys.stderr)
        return result.returncode
    if args.install and not selected:
        command = TASKS[args.task]["commands"][0]
        status = try_install(command, args.timeout)
        if status == 0:
            print("Install succeeded; rerun the intended task explicitly to validate its behavior.")
            return 0
        print("Continuing with Python fallback where possible.", file=sys.stderr)
    else:
        print("Using Python standard-library fallback.")
    return fallback(args.task, args)


if __name__ == "__main__":
    raise SystemExit(main())
