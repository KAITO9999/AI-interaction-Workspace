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
import sys
import time
from pathlib import Path

from agentkit_process import process_status, run_process

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "target", "dist", "build", ".next", ".cache"}
MAX_FILES = 10000
MAX_TOTAL_BYTES = 100 * 1024 * 1024
OUTPUT_LIMIT = 12000


def _iter_watch_files(start: Path, root: Path):
    for current, directories, filenames in os.walk(start, topdown=True, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name for name in directories
            if name not in SKIP_DIRS and not (current_path / name).is_symlink()
        )
        for name in sorted(filenames):
            candidate = current_path / name
            if candidate.is_symlink():
                continue
            try:
                if candidate.is_file():
                    candidate.resolve().relative_to(root)
                    yield candidate
            except (OSError, ValueError):
                continue


def snapshot(root: Path, watched: list[str]) -> tuple[str, dict[str, str], dict[str, str]]:
    """Return a deterministic bounded digest, per-file hashes and scan warnings."""
    root = root.resolve()
    files: set[Path] = set()
    warnings: dict[str, str] = {}
    for raw in watched:
        lexical_path = Path(raw).expanduser()
        if not lexical_path.is_absolute():
            lexical_path = root / lexical_path
        if lexical_path.is_symlink():
            warnings[raw] = "symlink roots are skipped"
            continue
        path = lexical_path.resolve()
        try:
            path.relative_to(root)
        except ValueError:
            warnings[raw] = "path escapes root"
            continue
        if path.is_file():
            files.add(path)
        elif path.is_dir():
            for candidate in _iter_watch_files(path, root):
                files.add(candidate)
                if len(files) > MAX_FILES:
                    warnings["scan"] = f"file limit exceeded (> {MAX_FILES}); snapshot rejected"
                    return "", {}, warnings
        else:
            warnings[raw] = "path does not exist"
    ordered_files = sorted(files)
    if len(ordered_files) > MAX_FILES:
        warnings["scan"] = f"file limit exceeded ({len(ordered_files)} > {MAX_FILES}); snapshot rejected"
        return "", {}, warnings
    per_file: dict[str, str] = {}
    total = 0
    for path in ordered_files:
        try:
            size = path.stat().st_size
            remaining = MAX_TOTAL_BYTES - total
            if size > remaining:
                warnings["scan"] = (
                    f"byte limit exceeded by {path.relative_to(root).as_posix()} "
                    f"({size} > remaining {remaining}); snapshot rejected"
                )
                return "", {}, warnings
            digest = hashlib.sha256()
            read_size = 0
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(min(1024 * 1024, remaining - read_size + 1))
                    if not chunk:
                        break
                    read_size += len(chunk)
                    if read_size > remaining:
                        warnings["scan"] = "file grew beyond the byte budget while being scanned; snapshot rejected"
                        return "", {}, warnings
                    digest.update(chunk)
            total += read_size
            per_file[path.relative_to(root).as_posix()] = digest.hexdigest()
        except (OSError, ValueError) as exc:
            warnings[path.relative_to(root).as_posix()] = f"{type(exc).__name__}: {exc}"
    combined = hashlib.sha256(
        json.dumps(per_file, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return combined, per_file, warnings


def run_check(command: list[str], root: Path, timeout: int) -> dict[str, object]:
    result = run_process(command, cwd=root, timeout=timeout, output_limit=OUTPUT_LIMIT)
    return {
        "status": process_status(result),
        "returncode": result["returncode"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "duration_seconds": result["duration_seconds"],
        "timed_out": result["timed_out"],
        "launch_error": result.get("launch_error"),
        "capture_error": result.get("capture_error"),
        "stdout_truncated": result.get("stdout_truncated", False),
        "stderr_truncated": result.get("stderr_truncated", False),
    }


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
    baseline, baseline_files, warnings = snapshot(root, args.watch)
    if not baseline or warnings:
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
            current, current_files, current_warnings = snapshot(root, args.watch)
            if current_warnings:
                warnings.update(current_warnings)
                break
            if not current:
                break
            if current == baseline:
                continue
            time.sleep(args.debounce)
            settled, settled_files, settled_warnings = snapshot(root, args.watch)
            warnings.update(settled_warnings)
            if settled_warnings or not settled:
                break
            changed_files = sorted(
                name for name in set(baseline_files) | set(settled_files)
                if baseline_files.get(name) != settled_files.get(name)
            )
            baseline, baseline_files = settled, settled_files
            runs += 1
            report = run_check(command, root, args.timeout)
            event = {"event": "change", "run": runs, "changed_files": changed_files, **report}
            events.append(event)
            print(json.dumps(event, ensure_ascii=False) if args.json else
                  f"[{report['status']}] change-triggered verification #{runs} ({report['duration_seconds']}s)")
            if not args.json and report.get("stderr"):
                print(str(report["stderr"]))
    except KeyboardInterrupt:
        pass
    summary_events = [
        {key: event[key] for key in ("event", "run", "status", "returncode", "duration_seconds", "timed_out", "changed_files") if key in event}
        for event in events
    ]
    summary = {"summary": "watch stopped", "runs": runs, "warnings": warnings, "events": summary_events}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"Stopped after {runs} verification run(s).")
    return 0 if runs > 0 and all(e.get("status") == "PASS" for e in events) and not warnings else 1


if __name__ == "__main__":
    raise SystemExit(main())
