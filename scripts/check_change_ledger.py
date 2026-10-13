#!/usr/bin/env python3
"""Enforce append-only AI/human and online/offline provenance on pull requests."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

LEDGER = "LOGS/change-ledger.jsonl"
ALLOWED_ACTORS = {"ai", "human"}
ALLOWED_MODES = {"online", "offline", "mixed"}


def validate_snapshot(base_text: str, head_text: str, changed_paths: set[str]) -> list[str]:
    errors: list[str] = []
    base_lines = [line for line in base_text.splitlines() if line.strip()]
    head_lines = [line for line in head_text.splitlines() if line.strip()]
    if head_lines[:len(base_lines)] != base_lines:
        return ["change ledger must be append-only; prior records were changed or removed"]
    new_lines = head_lines[len(base_lines):]
    if changed_paths and not new_lines:
        errors.append("changed pull request has no new provenance record")
    added_records: list[dict[str, Any]] = []
    for index, line in enumerate(new_lines, start=len(base_lines) + 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"ledger line {index} is invalid JSON: {exc}")
            continue
        if record.get("schema_version") != 1:
            errors.append(f"ledger line {index} has unsupported schema_version")
        if record.get("actor_type") not in ALLOWED_ACTORS:
            errors.append(f"ledger line {index} actor_type must be ai or human")
        if record.get("work_mode") not in ALLOWED_MODES:
            errors.append(f"ledger line {index} work_mode must be online, offline, or mixed")
        if not isinstance(record.get("summary"), str) or not record["summary"].strip():
            errors.append(f"ledger line {index} is missing a summary")
        paths = record.get("paths")
        if not isinstance(paths, list) or any(not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or ".." in Path(path).parts for path in paths):
            errors.append(f"ledger line {index} has invalid paths")
        else:
            added_records.append(record)
    declared = {path for record in added_records for path in record.get("paths", [])}
    required_paths = set(changed_paths) - {LEDGER}
    missing = sorted(required_paths - declared)
    if missing:
        errors.append("changed files missing from provenance paths: " + ", ".join(missing))
    return errors


def git_text(arguments: list[str], allow_missing: bool = False) -> str | None:
    result = subprocess.run(["git", *arguments], capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return result.stdout
    if allow_missing:
        return None
    raise RuntimeError((result.stderr or result.stdout).strip() or f"git {' '.join(arguments)} failed")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    base_branch = os.environ.get("GITHUB_BASE_REF", "").strip()
    if not base_branch:
        print("SKIP: GITHUB_BASE_REF is unset; pull-request ledger enforcement is CI-only.")
        return 0
    try:
        git_text(["check-ref-format", "--branch", base_branch])
        base = f"origin/{base_branch}"
        git_text(["rev-parse", "--verify", f"{base}^{{commit}}"])
        diff = git_text(["diff", "--name-only", "--no-renames", f"{base}...HEAD"])
        changed_paths = {line.strip() for line in (diff or "").splitlines() if line.strip()}
        if LEDGER not in changed_paths:
            print(f"FAIL: this pull request must append a reviewed record to {LEDGER}.", file=sys.stderr)
            return 1
        base_ledger = git_text(["show", f"{base}:{LEDGER}"], allow_missing=True) or ""
        head_path = root / LEDGER
        if not head_path.is_file():
            print(f"FAIL: {LEDGER} is missing from the branch.", file=sys.stderr)
            return 1
        errors = validate_snapshot(base_ledger, head_path.read_text(encoding="utf-8"), changed_paths)
    except (OSError, RuntimeError) as exc:
        print(f"FAIL: cannot validate provenance: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(f"FAIL: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"OK: provenance covers {len(changed_paths) - 1} changed file(s); actor and work mode are explicit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
