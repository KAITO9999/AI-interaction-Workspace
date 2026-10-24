#!/usr/bin/env python3
"""Bounded file-change watcher that reruns an explicit verification command.

This lets an agent keep tests running in a second terminal while editing. Commands
are argv arrays (never shell strings); watched paths and resource limits are explicit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "target", "dist", "build", ".next", ".cache"}
MAX_FILES = 10000
MAX_TOTAL_BYTES = 100 * 1024 * 1024
OUTPUT_LIMIT = 12000


def snapshot(root: Path, watched: list[str]) -> tuple[str, dict[str, str], dict[str, str]]:
    """Return a deterministic digest, per-file digests, and scan warnings."""
    root = root.resolve()
    files: list[Path] = []
    warnings: dict[str, str] = {}
    for raw in watched:
        path = (root / raw).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            warnings[raw] = "path escapes root"
            continue
        if path.is_symlink():
            warnings[raw] = "symlink roots are skipped"
            continue
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for candidate in path.rglob("*"):
                try:
                    rel = candidate.relative_to(root)
                    if any(part in SKIP_DIRS for part in rel.parts) or candidate.is_symlink():
                        continue
                    if candidate.is_file():
                        resolved = candidate.resolve()
                        resolved.relative_to(root)
                        files.append(candidate)
                except (OSError, ValueError):
                    continue
        else:
            warnings[raw] = "path does not exist"
    files = sorted(set(files))
    if len(files) > MAX_FILES:
        warnings["scan"] = f"file limit exceeded ({len(files)} > {MAX_FILES}); snapshot rejected"
        return "", {}, warnings
    per_file: dict[str, str] = {}
    total = 0
    for path in files:
        try:
            size = path.stat().st_size
            total += size
            if total > MAX_TOTAL_BYTES:
                warnings["scan"] = f"byte limit exceeded ({total} > {MAX_TOTAL_BYTES}); snapshot rejected"
                return "", {}, warnings
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            per_file[path.relative_to(root).as_posix()] = digest.hexdigest()
        except OSError as exc:
            warnings[path.relative_to(root).as_posix()] = f"{type(exc).__name__}: {exc}"
    combined = hashlib.sha256(json.dumps(per_file, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return combined, per_file, warnings


def run_check(command: list[str], root: Path, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                                errors="replace", timeout=timeout, check=False)
        return {"status": "PASS" if result.returncode == 0 else "FAIL",
                "returncode": result.returncode, "stdout": result.stdout[-OUTPUT_LIMIT:],
                "stderr": result.stderr[-OUTPUT_LIMIT:],
                "duration_seconds": round(time.monotonic() - started, 3), "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        def decode(value: str | bytes | None) -> str:
            if value is None:
                return ""
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else value
        return {"status": "TIMEOUT", "returncode": 124, "stdout": decode(exc.stdout)[-OUTPUT_LIMIT:],
                "stderr": (decode(exc.stderr) + f"\nTIMEOUT after {timeout}s")[-OUTPUT_LIMIT:],
                "duration_seconds": round(time.monotonic() - started, 3), "timed_out": True}
    except OSError as exc:
        return {"status": "UNAVAILABLE", "returncode": 127, "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}", "duration_seconds": round(time.monotonic() - started, 3),
                "timed_out": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rerun an explicit test/check command when watched files change.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--watch", action="append", required=True, help="File or directory relative to root; repeatable.")
    parser.add_argument("--interval", type=float, default=0.5, help="Polling interval, 0.2..30 seconds.")
    parser.add_argument("--debounce", type=float, default=0.4, help="Quiet period after a change, 0..10 seconds.")
    parser.add_argument("--timeout", type=int, default=300, help="Verification command timeout, 1..1800 seconds.")
    parser.add_argument("--max-runs", type=int, default=25, help="Maximum executions, 1..1000.")
    parser.add_argument("--no-initial-run", action="store_true", help="Wait for a change before the first verification.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command argv after --; never evaluated by a shell.")
    args = parser.parse_args(argv)
    if not 0.2 <= args.interval <= 30:
        parser.error("--interval must be 0.2..30")
    if not 0 <= args.debounce <= 10:
        parser.error("--debounce must be 0..10")
    if not 1 <= args.timeout <= 1800:
        parser.error("--timeout must be 1..1800")
    if not 1 <= args.max_runs <= 1000:
        parser.error("--max-runs must be 1..1000")
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        parser.error("provide a verification command after -- (for example: -- python -m unittest discover -s tests)")
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")
    baseline, _, warnings = snapshot(root, args.watch)
    if not baseline:
        parser.error("initial snapshot failed: " + "; ".join(warnings.values()))
    events: list[dict[str, object]] = []
    runs = 0
    if not args.no_initial_run:
        runs += 1
        report = run_check(command, root, args.timeout)
        events.append({"event": "initial", "run": runs, **report})
        print(json.dumps(events[-1], ensure_ascii=False) if args.json else
              f"[{report['status']}] initial verification ({report['duration_seconds']}s)")
    try:
        while runs < args.max_runs:
            time.sleep(args.interval)
            current, _, current_warnings = snapshot(root, args.watch)
            if current_warnings:
                warnings.update(current_warnings)
            if not current:
                continue
            if current == baseline:
                continue
            time.sleep(args.debounce)
            settled, files, settled_warnings = snapshot(root, args.watch)
            warnings.update(settled_warnings)
            if not settled:
                continue
            baseline = settled
            runs += 1
            report = run_check(command, root, args.timeout)
            event = {"event": "change", "run": runs, "changed_files": sorted(files), **report}
            events.append(event)
            print(json.dumps(event, ensure_ascii=False) if args.json else
                  f"[{report['status']}] change-triggered verification #{runs} ({report['duration_seconds']}s)")
            if not args.json and report.get("stderr"):
                print(str(report["stderr"]))
    except KeyboardInterrupt:
        pass
    summary = {"summary": "watch stopped", "runs": runs, "warnings": warnings, "events": events}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"Stopped after {runs} verification run(s).")
    return 0 if all(e.get("status") == "PASS" for e in events) and not warnings else 1


if __name__ == "__main__":
    raise SystemExit(main())
