#!/usr/bin/env python3
"""Python-first, bounded workflow checks for AgentKit.

External linters are invoked with fixed argv lists and timeouts. Native fallbacks
are explicitly weaker and never claim compatibility they cannot provide.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

VERSION = "0.1.0"
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "target", "dist", "build", ".next", ".cache"}
DEFAULT_MAX_BYTES = 1_000_000
DEFAULT_MAX_LINES = 250


def emit(data: dict[str, Any], json_mode: bool = False) -> None:
    if json_mode:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print(data.get("summary", "AgentKit work report"))
    for item in data.get("checks", []):
        print(f"{item.get('status', 'INFO')} {item.get('name', 'check')}: {item.get('detail', '')}")
    for warning in data.get("warnings", []):
        print(f"WARN {warning}")
    for error in data.get("errors", []):
        print(f"FAIL {error}", file=sys.stderr)


def run_argv(argv: list[str], timeout: int = 30, cwd: Path | None = None) -> dict[str, Any]:
    """Run an explicit argument vector; never invoke a shell."""
    started = time.monotonic()
    try:
        result = subprocess.run(argv, cwd=str(cwd) if cwd else None, capture_output=True,
                                text=True, errors="replace", timeout=timeout, check=False)
        return {"argv": argv, "returncode": result.returncode, "stdout": result.stdout,
                "stderr": result.stderr, "duration_seconds": round(time.monotonic() - started, 3),
                "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {"argv": argv, "returncode": 124, "stdout": _decode(exc.stdout),
                "stderr": _decode(exc.stderr) + f"\nTIMEOUT after {timeout}s",
                "duration_seconds": round(time.monotonic() - started, 3), "timed_out": True}
    except OSError as exc:
        return {"argv": argv, "returncode": 127, "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
                "duration_seconds": round(time.monotonic() - started, 3), "timed_out": False}


def _decode(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else value


def repo_check(root: Path, timeout: int) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return {"summary": "Repository check failed", "checks": [], "errors": [f"root is not a directory: {root}"]}
    git = shutil.which("git")
    if not git:
        return {"summary": "Repository check unavailable", "checks": [], "errors": ["git not found; Git semantics are not emulated"]}
    inside = run_argv([git, "-C", str(root), "rev-parse", "--is-inside-work-tree"], timeout)
    if inside["returncode"] != 0 or inside["stdout"].strip() != "true":
        return {"summary": "Repository check unavailable", "checks": [], "errors": [f"not a Git work tree: {root}"]}
    checks = []
    for name, args in (
        ("status", ["status", "--short", "--branch", "--untracked-files=normal"]),
        ("diff-check", ["diff", "--check"]),
        ("diff-staged-check", ["diff", "--cached", "--check"]),
        ("diff-stat", ["diff", "--stat"]),
        ("diff-staged-stat", ["diff", "--cached", "--stat"]),
    ):
        result = run_argv([git, "-C", str(root), *args], timeout)
        checks.append({"name": name, "status": "PASS" if result["returncode"] == 0 else "FAIL",
                       "returncode": result["returncode"], "stdout": result["stdout"][:20000],
                       "stderr": result["stderr"][:4000], "timed_out": result["timed_out"]})
    return {"summary": "Git repository inspection complete; no files changed",
            "root": str(root), "checks": checks, "errors": [], "read_only": True}


def lint_python(root: Path, files: list[str], timeout: int) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return {"summary": "Python lint unavailable", "checks": [], "errors": [f"root is not a directory: {root}"]}
    candidates: list[Path] = []
    if files:
        for raw in files:
            path = (root / raw).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                return {"summary": "Python lint rejected path", "checks": [], "errors": [f"path escapes root: {raw}"]}
            if not path.is_file() or path.suffix != ".py":
                return {"summary": "Python lint rejected input", "checks": [], "errors": [f"not an existing .py file: {raw}"]}
            candidates.append(path)
    else:
        for path in root.rglob("*.py"):
            if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
                continue
            candidates.append(path)
    candidates.sort()
    if not candidates:
        return {"summary": "No Python files found", "checks": [], "errors": []}
    ruff = shutil.which("ruff")
    if ruff:
        result = run_argv([ruff, "check", "--output-format", "concise", *[str(p) for p in candidates]], timeout, root)
        return {"summary": "Ruff lint completed", "tool": "ruff", "equivalence": "native-linter",
                "checks": [{"name": "ruff-check", "status": "PASS" if result["returncode"] == 0 else "FAIL",
                            "returncode": result["returncode"], "stdout": result["stdout"][:30000],
                            "stderr": result["stderr"][:6000], "timed_out": result["timed_out"]}],
                "errors": [], "file_count": len(candidates)}
    py = shutil.which("python3") or sys.executable
    result = run_argv([py, "-m", "py_compile", *[str(p) for p in candidates]], timeout, root)
    return {"summary": "Python syntax-only fallback completed", "tool": "py_compile",
            "equivalence": "syntax-only; NOT Ruff-equivalent",
            "checks": [{"name": "python-syntax", "status": "PASS" if result["returncode"] == 0 else "FAIL",
                        "returncode": result["returncode"], "stdout": result["stdout"][:10000],
                        "stderr": result["stderr"][:6000], "timed_out": result["timed_out"]}],
            "warnings": ["ruff not found; lint rules were not checked"], "errors": [], "file_count": len(candidates)}


def audit_shell(root: Path, files: list[str], dialect: str, timeout: int) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if dialect not in {"sh", "bash"}:
        return {"summary": "Shell audit rejected dialect", "checks": [], "errors": ["dialect must be sh or bash"]}
    candidates: list[Path] = []
    if files:
        for raw in files:
            path = (root / raw).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                return {"summary": "Shell audit rejected path", "checks": [], "errors": [f"path escapes root: {raw}"]}
            if not path.is_file():
                return {"summary": "Shell audit rejected input", "checks": [], "errors": [f"not a file: {raw}"]}
            candidates.append(path)
    else:
        for path in root.rglob("*.sh"):
            if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
                continue
            candidates.append(path)
    candidates.sort()
    if not candidates:
        return {"summary": "No shell scripts found", "checks": [], "errors": []}
    shellcheck = shutil.which("shellcheck")
    if shellcheck:
        result = run_argv([shellcheck, "--shell=" + dialect, "--", *[str(p) for p in candidates]], timeout, root)
        tool, equivalence = "shellcheck", "native-linter"
    else:
        shell = shutil.which(dialect)
        if not shell:
            return {"summary": "Shell audit unavailable", "checks": [], "errors": [f"neither shellcheck nor {dialect} is available"]}
        failures = []
        for path in candidates:
            result_one = run_argv([shell, "-n", str(path)], timeout, root)
            if result_one["returncode"] != 0:
                failures.append({"file": str(path.relative_to(root)), "returncode": result_one["returncode"],
                                 "stderr": result_one["stderr"][:2000], "timed_out": result_one["timed_out"]})
        result = {"returncode": 1 if failures else 0, "stdout": "", "stderr": json.dumps(failures, ensure_ascii=False)}
        tool, equivalence = dialect + " -n", "syntax-only; NOT ShellCheck-equivalent"
    return {"summary": "Shell audit completed", "tool": tool, "equivalence": equivalence,
            "checks": [{"name": "shell-audit", "status": "PASS" if result["returncode"] == 0 else "FAIL",
                        "returncode": result["returncode"], "stdout": result.get("stdout", "")[:20000],
                        "stderr": result.get("stderr", "")[:8000], "timed_out": result.get("timed_out", False)}],
            "warnings": [] if tool == "shellcheck" else ["shellcheck not found; only shell syntax was checked"],
            "errors": [], "file_count": len(candidates), "dialect": dialect}


def sqlite_inspect(database: Path, row_counts: bool, integrity: bool) -> dict[str, Any]:
    database = database.expanduser().resolve()
    if not database.is_file():
        return {"summary": "SQLite inspection failed", "checks": [], "errors": [f"database file not found: {database}"]}
    uri = database.as_uri() + "?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=5)
        connection.execute("PRAGMA query_only = ON")
        connection.set_authorizer(_sqlite_read_authorizer)
        tables = connection.execute("SELECT name, type, sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name").fetchall()
        result_tables = []
        for name, kind, sql in tables:
            item: dict[str, Any] = {"name": name, "type": kind, "schema": sql}
            if row_counts and kind == "table" and not name.startswith("sqlite_"):
                # Quote identifiers by doubling embedded double quotes; values are never interpolated.
                quoted = '"' + name.replace('"', '""') + '"'
                item["row_count"] = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
            result_tables.append(item)
        report: dict[str, Any] = {"summary": "SQLite database inspected read-only", "database": str(database),
                                  "tables": result_tables, "checks": [], "errors": [], "read_only": True}
        if integrity:
            # integrity_check is a PRAGMA and blocked by the restrictive authorizer; run it on a separate RO connection.
            connection.close()
            check_connection = sqlite3.connect(uri, uri=True, timeout=5)
            check_connection.execute("PRAGMA query_only = ON")
            integrity_rows = [row[0] for row in check_connection.execute("PRAGMA integrity_check").fetchmany(20)]
            check_connection.close()
            report["checks"].append({"name": "integrity-check",
                                     "status": "PASS" if integrity_rows == ["ok"] else "FAIL",
                                     "detail": integrity_rows})
        else:
            connection.close()
        return report
    except (sqlite3.Error, OSError) as exc:
        return {"summary": "SQLite inspection failed", "checks": [], "errors": [f"{type(exc).__name__}: {exc}"]}


def _sqlite_read_authorizer(action: int, arg1: str | None, arg2: str | None,
                            db_name: str | None, trigger: str | None) -> int:
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


MAGIC = (
    (b"PK\x03\x04", "ZIP archive"),
    (b"\x1f\x8b", "gzip data"),
    (b"\x7fELF", "ELF executable/object"),
    (b"MZ", "DOS/Windows PE candidate"),
    (b"\x89PNG\r\n\x1a\n", "PNG image"),
    (b"\xff\xd8\xff", "JPEG image"),
    (b"SQLite format 3\x00", "SQLite database"),
    (b"\x7fELF", "ELF executable/object"),
)


def artifact_inspect(paths: list[str], max_bytes: int) -> dict[str, Any]:
    if max_bytes < 1:
        return {"summary": "Artifact inspection rejected limit", "checks": [], "errors": ["max-bytes must be positive"]}
    reports = []
    errors = []
    for raw in paths:
        path = Path(raw).expanduser()
        try:
            stat = path.stat()
            if not path.is_file():
                errors.append(f"not a regular file: {path}")
                continue
            digest = hashlib.sha256()
            first = b""
            total = 0
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(min(1024 * 1024, max_bytes - total + 1))
                    if not chunk:
                        break
                    if not first:
                        first = chunk[:32]
                    total += len(chunk)
                    digest.update(chunk)
                    if total > max_bytes:
                        break
            if total > max_bytes:
                reports.append({"path": str(path.resolve()), "size_bytes": stat.st_size,
                                "status": "LIMIT", "max_bytes": max_bytes,
                                "detail": "hash is partial and intentionally omitted"})
                continue
            kind = next((label for signature, label in MAGIC if first.startswith(signature)), "unknown / not in magic allowlist")
            file_cmd = shutil.which("file")
            file_description = None
            type_source = "python-magic-allowlist"
            if file_cmd:
                file_result = run_argv([file_cmd, "--brief", "--", str(path)], timeout=10)
                if file_result["returncode"] == 0:
                    file_description = file_result["stdout"].strip()[:1000]
                    type_source = "file"
            reports.append({"path": str(path.resolve()), "size_bytes": stat.st_size,
                            "sha256": digest.hexdigest(), "magic_type": kind,
                            "file_description": file_description, "type_source": type_source,
                            "extension": path.suffix.lower(), "extension_matches_magic": _extension_hint(path.suffix.lower(), kind)})
        except OSError as exc:
            errors.append(f"{path}: {type(exc).__name__}: {exc}")
    return {"summary": "Artifact inspection complete; no files executed or modified",
            "artifacts": reports, "checks": [], "errors": errors, "read_only": True}


def _extension_hint(extension: str, kind: str) -> bool | None:
    mapping = {".zip": "ZIP archive", ".jar": "ZIP archive", ".apk": "ZIP archive",
               ".png": "PNG image", ".jpg": "JPEG image", ".jpeg": "JPEG image",
               ".gz": "gzip data", ".db": "SQLite database", ".sqlite": "SQLite database",
               ".sqlite3": "SQLite database", ".exe": "DOS/Windows PE candidate"}
    return None if kind.startswith("unknown") or extension not in mapping else mapping[extension] == kind


def context_inspect(root: Path, target: str, start: int | None, end: int | None,
                    pattern: str | None, regex: bool, max_lines: int, max_bytes: int,
                    ignore_case: bool) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return {"summary": "Context inspection failed", "matches": [], "errors": [f"root is not a directory: {root}"]}
    if max_lines < 1 or max_bytes < 1:
        return {"summary": "Context inspection rejected limits", "matches": [], "errors": ["limits must be positive"]}
    if (start is not None and start < 1) or (end is not None and end < 1):
        return {"summary": "Context inspection rejected line range", "matches": [], "errors": ["line numbers must be >= 1"]}
    if start is not None and end is not None and start > end:
        return {"summary": "Context inspection rejected line range", "matches": [], "errors": ["start must be <= end"]}
    target_path = (root / target).resolve()
    try:
        target_path.relative_to(root)
    except ValueError:
        return {"summary": "Context inspection rejected path", "matches": [], "errors": [f"path escapes root: {target}"]}
    candidates = [target_path] if target_path.is_file() else sorted(target_path.rglob("*")) if target_path.is_dir() else []
    if not candidates:
        return {"summary": "No matching target files", "matches": [], "errors": [f"target does not exist: {target_path}"]}
    compiled = None
    if pattern is not None and regex:
        try:
            compiled = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
        except re.error as exc:
            return {"summary": "Invalid regular expression", "matches": [], "errors": [str(exc)]}
    matches: list[dict[str, Any]] = []
    bytes_seen = 0
    truncated = False
    for path in candidates:
        try:
            rel = path.relative_to(root)
            # Do not follow symlinks during recursive context gathering: a link
            # inside the selected root may disclose files outside that boundary.
            if path.is_symlink():
                continue
            resolved = path.resolve()
            resolved.relative_to(root)
        except (ValueError, OSError):
            continue
        if any(part in SKIP_DIRS for part in rel.parts) or not path.is_file():
            continue
        try:
            size = path.stat().st_size
            if size > max_bytes - bytes_seen:
                truncated = True
                break
            remaining = max_bytes - bytes_seen
            with path.open("rb") as handle:
                raw = handle.read(remaining + 1)
            if len(raw) > remaining:
                truncated = True
                break
            content = raw.decode("utf-8", errors="replace")
            bytes_seen += len(raw)
        except OSError:
            continue
        lines = content.splitlines()
        selected: Iterable[tuple[int, str]]
        if pattern is None:
            lo = max(1, start or 1)
            hi = min(len(lines), end if end is not None else lo + max_lines - 1)
            selected = ((n, lines[n - 1]) for n in range(lo, hi + 1))
        else:
            selected = ((n, line) for n, line in enumerate(lines, 1)
                        if (compiled.search(line) if compiled else
                            (pattern.casefold() in line.casefold() if ignore_case else pattern in line)))
        for number, line in selected:
            matches.append({"path": rel.as_posix(), "line": number, "text": line[:2000]})
            if len(matches) >= max_lines:
                truncated = True
                break
        if truncated:
            break
    return {"summary": "Context inspection complete", "root": str(root), "matches": matches,
            "files_scanned_bytes": bytes_seen, "truncated": truncated,
            "limits": {"max_lines": max_lines, "max_bytes": max_bytes},
            "errors": [], "read_only": True}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentkit-work", description="Python-first bounded checks and context-efficient source inspection.")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    item = sub.add_parser("repo-check", help="Run read-only Git status and diff checks using Git itself.")
    item.add_argument("--root", default=".")
    item.add_argument("--timeout", type=int, default=30)
    item.add_argument("--json", action="store_true")
    item.set_defaults(handler=lambda a: repo_check(Path(a.root), a.timeout), json_arg="json")

    item = sub.add_parser("lint-python", help="Use Ruff; fall back to syntax-only py_compile.")
    item.add_argument("--root", default=".")
    item.add_argument("--file", action="append", default=[])
    item.add_argument("--timeout", type=int, default=120)
    item.add_argument("--json", action="store_true")
    item.set_defaults(handler=lambda a: lint_python(Path(a.root), a.file, a.timeout), json_arg="json")

    item = sub.add_parser("audit-shell", help="Use ShellCheck; fall back to dialect-specific -n syntax check.")
    item.add_argument("--root", default=".")
    item.add_argument("--file", action="append", default=[])
    item.add_argument("--dialect", choices=("sh", "bash"), default="sh")
    item.add_argument("--timeout", type=int, default=30)
    item.add_argument("--json", action="store_true")
    item.set_defaults(handler=lambda a: audit_shell(Path(a.root), a.file, a.dialect, a.timeout), json_arg="json")

    item = sub.add_parser("sqlite-inspect", help="Inspect SQLite schema and optional row counts read-only.")
    item.add_argument("database")
    item.add_argument("--row-counts", action="store_true")
    item.add_argument("--integrity-check", action="store_true")
    item.add_argument("--json", action="store_true")
    item.set_defaults(handler=lambda a: sqlite_inspect(Path(a.database), a.row_counts, a.integrity_check), json_arg="json")

    item = sub.add_parser("artifact-inspect", help="Bounded file magic and SHA-256 inspection; never executes files.")
    item.add_argument("paths", nargs="+")
    item.add_argument("--max-bytes", type=int, default=64 * 1024 * 1024)
    item.add_argument("--json", action="store_true")
    item.set_defaults(handler=lambda a: artifact_inspect(a.paths, a.max_bytes), json_arg="json")

    item = sub.add_parser("context", help="Read exact line ranges or search matching lines with output budgets.")
    item.add_argument("--root", default=".")
    item.add_argument("--target", default=".")
    item.add_argument("--start", type=int)
    item.add_argument("--end", type=int)
    item.add_argument("--pattern")
    item.add_argument("--regex", action="store_true")
    item.add_argument("--ignore-case", action="store_true")
    item.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    item.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    item.add_argument("--json", action="store_true")
    item.set_defaults(handler=lambda a: context_inspect(Path(a.root), a.target, a.start, a.end, a.pattern, a.regex, a.max_lines, a.max_bytes, a.ignore_case), json_arg="json")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not 1 <= getattr(args, "timeout", 30) <= 600:
        parser.error("--timeout must be in range 1..600")
    try:
        report = args.handler(args)
    except KeyboardInterrupt:
        report = {"summary": "Interrupted; no automatic retry", "checks": [], "errors": ["interrupted"]}
    emit(report, args.json)
    return 1 if report.get("errors") or any(c.get("status") == "FAIL" for c in report.get("checks", [])) else 0


if __name__ == "__main__":
    raise SystemExit(main())
