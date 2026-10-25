#!/usr/bin/env python3
"""Dependency-free, deliberately limited static checks for AgentKit.

This module is a fallback, not a reimplementation of Ruff or ShellCheck.
Rules are conservative heuristics and report rule IDs so findings can be reviewed.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


def lint_python_source(source: str, filename: str = "<string>") -> list[dict[str, Any]]:
    """Run syntax validation and a small set of AST-based correctness checks."""
    findings: list[dict[str, Any]] = []
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [{"rule": "PY-SYNTAX", "severity": "error", "line": exc.lineno or 1,
                 "column": exc.offset or 1, "message": exc.msg}]
    # A package __init__ commonly imports names to expose a public API.
    is_init = Path(filename).name == "__init__.py"
    used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
                  and isinstance(node.ctx, ast.Load)}

    if not is_init:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    bound = alias.asname or alias.name.split(".", 1)[0]
                    if bound not in used_names and not bound.startswith("_"):
                        findings.append({"rule": "F401", "severity": "warning",
                                         "line": node.lineno, "column": node.col_offset + 1,
                                         "message": f"unused import {alias.name!r}"})
            elif isinstance(node, ast.ImportFrom):
                if node.module == "__future__":
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    bound = alias.asname or alias.name
                    if bound not in used_names and not bound.startswith("_"):
                        findings.append({"rule": "F401", "severity": "warning",
                                         "line": node.lineno, "column": node.col_offset + 1,
                                         "message": f"unused import {alias.name!r} from {node.module or '.'}"})

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append({"rule": "E722", "severity": "warning", "line": node.lineno,
                             "column": node.col_offset + 1,
                             "message": "bare except catches BaseException; name the expected exception"})
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append({"rule": "PY-MUTABLE-DEFAULT", "severity": "warning",
                                     "line": default.lineno, "column": default.col_offset + 1,
                                     "message": "mutable literal default is shared between calls"})
    findings.sort(key=lambda item: (item["line"], item["column"], item["rule"]))
    return findings


def _unquoted_expansions(line: str) -> list[tuple[int, str]]:
    """Return unquoted shell parameter/command expansions; not a full shell lexer."""
    found: list[tuple[int, str]] = []
    quote: str | None = None
    escaped = False
    i = 0
    while i < len(line):
        char = line[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if quote == "'":
            if char == "'":
                quote = None
            i += 1
            continue
        if char == "\\" and quote != "'":
            escaped = True
            i += 1
            continue
        if quote is None and char == "#":
            break
        if char in ("'", '"'):
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            i += 1
            continue
        if char == "$" and quote is None and i + 1 < len(line):
            nxt = line[i + 1]
            if nxt == "(" and (i + 2 >= len(line) or line[i + 2] != "("):
                found.append((i + 1, "command"))
            elif nxt == "{":
                found.append((i + 1, "parameter"))
            elif nxt.isalpha() or nxt == "_" or nxt in "@*?#$!0123456789":
                found.append((i + 1, "parameter"))
        i += 1
    return found


def lint_shell_source(source: str, dialect: str = "sh") -> list[dict[str, Any]]:
    """Run conservative line-based checks for common shell pitfalls."""
    if dialect not in {"sh", "bash"}:
        raise ValueError("dialect must be sh or bash")
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.splitlines(), 1):
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        # In assignment-only context, an unquoted RHS expansion is not subject
        # to the same word-splitting/globbing behavior as command arguments.
        assignment_only = bool(re.match(r"^(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*=", stripped))
        if not assignment_only:
            for column, kind in _unquoted_expansions(line):
                if kind == "command":
                    rule, message = "SC2046", "quote command substitution to prevent word splitting"
                else:
                    rule, message = "SC2086", "quote this variable expansion unless splitting/globbing is intentional"
                findings.append({"rule": rule, "severity": "warning", "line": line_number,
                                 "column": column, "message": message})
        if re.search(r"\bexport\s+[A-Za-z_][A-Za-z0-9_]*=\$\(", line):
            findings.append({"rule": "SC2155", "severity": "warning", "line": line_number,
                             "column": line.find("export") + 1,
                             "message": "separate declaration/export from command substitution to preserve its exit status"})
        if "`" in line and not stripped.startswith("#"):
            findings.append({"rule": "SC2006", "severity": "info", "line": line_number,
                             "column": line.find("`") + 1,
                             "message": "prefer $(...) command substitution over legacy backticks"})
        if re.search(r"\$\?\s*(-eq|-ne|==|!=)\s*0", line):
            findings.append({"rule": "SC2181", "severity": "info", "line": line_number,
                             "column": line.find("$?") + 1,
                             "message": "test the command directly instead of inspecting its exit status later"})
    findings.sort(key=lambda item: (item["line"], item["column"], item["rule"]))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dependency-free limited static analysis (not Ruff/ShellCheck equivalent).")
    sub = parser.add_subparsers(dest="kind", required=True)
    py = sub.add_parser("python", help="AST-based Python checks")
    py.add_argument("files", nargs="+")
    sh = sub.add_parser("shell", help="heuristic shell checks")
    sh.add_argument("--dialect", choices=("sh", "bash"), default="sh")
    sh.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    results = []
    for raw in args.files:
        path = Path(raw)
        try:
            source = path.read_text(encoding="utf-8")
            findings = lint_python_source(source, str(path)) if args.kind == "python" else lint_shell_source(source, args.dialect)
            results.append({"file": str(path), "findings": findings})
        except (OSError, UnicodeError) as exc:
            results.append({"file": str(path), "error": f"{type(exc).__name__}: {exc}"})
    print(json.dumps({"tool": "agentkit-lint", "equivalence": "limited-native-rules; not upstream-equivalent",
                      "results": results}, ensure_ascii=False, indent=2))
    return 1 if any(r.get("error") or any(f["severity"] == "error" for f in r.get("findings", []))
                    for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
