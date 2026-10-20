"""Suggest installed command candidates and safe fallbacks without running discovered commands."""
from __future__ import annotations
import argparse
import json
import shutil
import sys

VERSION = "0.1.0"
PLANS = {
    "search": {"preferred": ["rg", "grep"], "fallback": "Python pathlib/text scan", "reason": "Search text in files."},
    "find": {"preferred": ["fd", "find"], "fallback": "Python pathlib.rglob", "reason": "Discover files by name/path."},
    "json": {"preferred": ["jq", "python3"], "fallback": "Python json.JSONDecoder stream validation", "reason": "Inspect or validate JSON; Python fallback does not implement jq filters."},
    "archive": {"preferred": ["7z", "unzip", "tar"], "fallback": "Python zipfile (ZIP only)", "reason": "List or process archives; standard-library fallback is ZIP-specific."},
    "hash": {"preferred": ["sha256sum", "shasum", "openssl"], "fallback": "Python hashlib.sha256", "reason": "Calculate SHA-256."},
    "code-audit": {"preferred": ["ruff", "pylint", "mypy", "eslint", "tsc", "shellcheck", "hadolint", "semgrep"], "fallback": "agentkit_code_audit.py heuristics", "reason": "Use installed language-specific analyzers first; generic checks are not semantic analysis."},
    "zip-batch": {"preferred": ["7z", "unzip"], "fallback": "agentkit_zipset.py using Python zipfile", "reason": "Sequential safe ZIP extraction with tags and manifest-backed cleanup."},
}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=sorted(PLANS))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths-only", action="store_true", help="Only report discovered executable paths.")
    args = parser.parse_args()
    plan = PLANS[args.task]
    candidates = []
    for name in plan["preferred"]:
        path = shutil.which(name)
        candidates.append({"command": name, "available": bool(path), "path": path})
    report = {"tool": "agentkit_toolplan", "version": VERSION, "task": args.task, "reason": plan["reason"], "candidates": candidates, "fallback": plan["fallback"], "policy": "Discovery only: does not execute commands, install packages, or replace installed commands."}
    if args.paths_only:
        report["candidates"] = [item for item in candidates if item["available"]]
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Task: {args.task} — {plan['reason']}")
        for item in report["candidates"]:
            status = item["path"] if item["available"] else "not found"
            print(f"  {item['command']}: {status}")
        print(f"Fallback candidate: {plan['fallback']}")
        print(report["policy"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
