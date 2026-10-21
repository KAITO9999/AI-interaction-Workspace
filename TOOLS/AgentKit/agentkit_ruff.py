#!/usr/bin/env python3
"""Ruff-aware Python lint route with an intentionally limited stdlib fallback.

The fallback is NOT Ruff-compatible. It currently reports Python syntax errors
(E999) and a conservative subset of unused imports (F401). It never rewrites
source files. Formatting requires real Ruff.
"""
from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist", ".tox", ".nox"}


def python_files(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths or ["."]:
        path = Path(raw).expanduser()
        if path.is_file():
            if path.suffix == ".py":
                found.append(path.resolve())
            continue
        if path.is_dir():
            for current, dirs, names in __import__("os").walk(path):
                dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
                found.extend((Path(current) / name).resolve() for name in sorted(names) if name.endswith(".py"))
    return sorted(set(found))


def lint_file(path: Path) -> list[dict[str, Any]]:
    try:
        with tokenize.open(path) as stream:
            source = stream.read()
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
        return [{
            "code": "E999",
            "message": f"Syntax/parse error: {getattr(exc, 'msg', str(exc))}",
            "filename": str(path),
            "row": getattr(exc, "lineno", 1) or 1,
            "column": max(0, (getattr(exc, "offset", 1) or 1) - 1),
        }]

    if path.name == "__init__.py":
        return []
    used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    diagnostics: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                if bound not in used:
                    diagnostics.append({
                        "code": "F401",
                        "message": f"'{alias.name}' imported but unused",
                        "filename": str(path),
                        "row": node.lineno,
                        "column": node.col_offset,
                    })
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound = alias.asname or alias.name
                if bound not in used:
                    diagnostics.append({
                        "code": "F401",
                        "message": f"'{alias.name}' imported but unused",
                        "filename": str(path),
                        "row": node.lineno,
                        "column": node.col_offset,
                    })
    return sorted(diagnostics, key=lambda item: (item["filename"], item["row"], item["column"], item["code"]))


def fallback_check(paths: list[str]) -> tuple[int, dict[str, Any]]:
    files = python_files(paths)
    diagnostics = [item for path in files for item in lint_file(path)]
    report = {
        "schema_version": 1,
        "engine": "agentkit-ruff-lite",
        "compatibility": "partial",
        "supported_rules": ["E999", "F401 (conservative subset)"],
        "unsupported_rules": ["all other Ruff lint rules", "Ruff configuration semantics", "Ruff formatter"],
        "files_checked": len(files),
        "diagnostics": diagnostics,
        "limitations": [
            "This is a reduced Python standard-library fallback, not a drop-in Ruff replacement.",
            "Unused-import analysis is conservative and does not implement Ruff's scope/configuration semantics.",
            "No source file is modified.",
            "Formatting is not emulated because a safe standard-library formatter cannot preserve all comments and formatting semantics.",
        ],
    }
    return (1 if diagnostics else 0), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "format"))
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--format", dest="output_format", choices=("text", "json"), default="text")
    parser.add_argument("--force-fallback", action="store_true", help="Use AgentKit's reduced Python fallback even if Ruff exists.")
    parser.add_argument("--check", action="store_true", help="Check formatting without modifying files (real Ruff only).")
    parser.add_argument("--diff", action="store_true", help="Show formatting diff (real Ruff only).")
    args = parser.parse_args(argv)

    ruff = None if args.force_fallback else shutil.which("ruff")
    if ruff:
        forwarded = [ruff, args.command]
        if args.command == "check" and args.output_format == "json":
            forwarded += ["--output-format", "json"]
        if args.command == "format" and (args.check or args.diff):
            forwarded += ["--check"] if args.check else ["--diff"]
        forwarded += args.paths
        result = subprocess.run(forwarded, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        return result.returncode

    if args.command == "format":
        print("ERROR: no Ruff executable found. AgentKit's fallback does not format source; it is not Ruff-compatible.", file=sys.stderr)
        print("Install or connect official Ruff, or skip formatting. Source was not modified.", file=sys.stderr)
        return 3

    status, report = fallback_check(args.paths)
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("ENGINE: AgentKit Ruff fallback (partial; not Ruff-compatible)")
        print(f"FILES CHECKED: {report['files_checked']}")
        for item in report["diagnostics"]:
            print(f"{item['filename']}:{item['row']}:{item['column']}: {item['code']} {item['message']}")
        print("SUPPORTED: E999, conservative F401 only; no formatting or auto-fix.")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
