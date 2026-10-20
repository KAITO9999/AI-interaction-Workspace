"""Heuristic, read-only source audit for common maintainability and correctness risks."""
from __future__ import annotations
import argparse
import ast
import json
import re
import sys
from pathlib import Path

VERSION = "0.1.0"
EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".kt", ".kts",
    ".go", ".rs", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".fs", ".fsx", ".vb",
    ".php", ".rb", ".rake", ".swift", ".m", ".mm", ".scala", ".sc", ".clj", ".cljs",
    ".ex", ".exs", ".erl", ".hrl", ".hs", ".lhs", ".lua", ".pl", ".pm", ".r", ".R",
    ".jl", ".dart", ".vue", ".svelte", ".sh", ".bash", ".zsh", ".ps1", ".psm1",
    ".sql", ".yaml", ".yml", ".toml", ".json", ".xml", ".html", ".css", ".scss",
}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__", ".next"}
COMMENT_RE = re.compile(r"^\s*(#|//|/\*|\*|<!--|--|;)")
RISKY_RE = [
    (re.compile(r"\beval\s*\("), "SECURITY", "HIGH", "Dynamic eval call", "Review whether untrusted text can reach eval; prefer explicit parsing."),
    (re.compile(r"\bexec\s*\("), "SECURITY", "HIGH", "Dynamic exec call", "Review code/data boundaries and remove dynamic execution where possible."),
    (re.compile(r"shell\s*=\s*True"), "SECURITY", "HIGH", "Shell-enabled subprocess call", "Prefer an argv list with shell disabled; validate any unavoidable shell input."),
    (re.compile(r"\bexcept\s*:"), "CORRECTNESS", "MEDIUM", "Bare exception handler", "Catch the expected exception types and preserve diagnostic context."),
    (re.compile(r"\b(TODO|FIXME|HACK)\b", re.I), "MAINTAINABILITY", "LOW", "Deferred-work marker", "Confirm whether this is still relevant and track real work outside source comments."),
    (re.compile(r"\b(time\.sleep|sleep)\s*\("), "PERFORMANCE", "LOW", "Sleep call in source", "Check whether polling/event-driven waiting is more appropriate; context determines severity."),
    (re.compile(r"\bwhile\s+True\s*:"), "PERFORMANCE", "LOW", "Unbounded loop pattern", "Verify the loop has a reachable stop condition, cancellation, and bounded waiting."),
]

def finding(path: Path, line: int, category: str, priority: str, title: str, detail: str) -> dict:
    return {"path": str(path), "line": line, "category": category, "priority": priority, "title": title, "detail": detail}

def python_ast_findings(path: Path, source: str) -> list[dict]:
    out = []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [finding(path, exc.lineno or 1, "CORRECTNESS", "HIGH", "Python syntax error", exc.msg)]
    definitions = {}
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions[node.name] = node
            end = getattr(node, "end_lineno", node.lineno)
            if end - node.lineno + 1 > 80:
                out.append(finding(path, node.lineno, "MAINTAINABILITY", "MEDIUM", "Very long function", f"{node.name} spans {end-node.lineno+1} lines; split by responsibility if useful."))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append(node)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "call", "check_call", "check_output"}:
            if any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords):
                out.append(finding(path, node.lineno, "SECURITY", "HIGH", "Shell-enabled subprocess call", "Prefer argv lists with shell disabled; validate any unavoidable shell input."))
    for node in calls:
        target = definitions.get(node.func.id)
        if target is None:
            continue
        positional = len(target.args.posonlyargs) + len(target.args.args)
        required = positional - len(target.args.defaults)
        supplied = len(node.args)
        has_varargs = target.args.vararg is not None
        if not has_varargs and (supplied < required or supplied > positional):
            out.append(finding(path, node.lineno, "CORRECTNESS", "HIGH", f"Possible local call arity mismatch: {node.func.id}", f"Call supplies {supplied} positional argument(s); local definition accepts {required}..{positional}. Keyword arguments, decorators, and dynamic dispatch can affect this heuristic."))
    return out

def audit_file(path: Path, root: Path, max_bytes: int) -> tuple[list[dict], dict]:
    try:
        if path.stat().st_size > max_bytes:
            return [], {"path": str(path.relative_to(root)), "skipped": "file exceeds size limit"}
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [finding(path, 1, "ENVIRONMENT", "LOW", "Could not read file", str(exc))], {}
    lines = source.splitlines()
    rel = path.relative_to(root)
    out = []
    if path.suffix.lower() == ".py":
        out.extend(python_ast_findings(rel, source))
    for number, line in enumerate(lines, 1):
        for pattern, category, priority, title, detail in RISKY_RE:
            if pattern.search(line):
                out.append(finding(rel, number, category, priority, title, detail))
    comment_lines = sum(1 for line in lines if COMMENT_RE.match(line))
    code_lines = sum(1 for line in lines if line.strip() and not COMMENT_RE.match(line))
    if len(lines) >= 30 and comment_lines / max(1, comment_lines + code_lines) > 0.40:
        out.append(finding(rel, 1, "MAINTAINABILITY", "LOW", "High comment-to-code ratio", f"{comment_lines} comment-like lines vs {code_lines} code-like lines. Comments are not inherently bad; review stale, redundant, or line-by-line narration rather than deleting useful rationale."))
    max_run = run = 0
    for line in lines:
        if COMMENT_RE.match(line) and line.strip():
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    if max_run >= 12:
        out.append(finding(rel, 1, "MAINTAINABILITY", "LOW", "Long consecutive comment block", f"Found {max_run} consecutive comment-like lines; check whether documentation belongs in a docstring or separate document."))
    return out, {"path": str(rel), "language_hint": path.suffix.lower().lstrip("."), "lines": len(lines), "comment_like_lines": comment_lines, "bytes": path.stat().st_size}

def collect_files(root: Path, explicit: list[str]) -> list[Path]:
    if explicit:
        files = []
        for value in explicit:
            path = (root / value).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError(f"path escapes audit root: {value}")
            if path.is_file():
                files.append(path)
            else:
                raise ValueError(f"not a file: {value}")
        return files
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS and not any(part in SKIP_DIRS for part in p.relative_to(root).parts))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--file", action="append", default=[], help="Relative file to audit; repeatable.")
    parser.add_argument("--json", dest="json_path", help="Write a machine-readable report.")
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--fail-on", choices=["never", "low", "medium", "high"], default="never")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        files = collect_files(root, args.file)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    findings, metrics = [], []
    for path in files:
        found, metric = audit_file(path, root, args.max_bytes)
        findings.extend(found)
        if metric:
            metrics.append(metric)
    rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda item: (rank[item["priority"]], item["path"], item["line"], item["title"]))
    report = {"tool": "agentkit_code_audit", "version": VERSION, "root": str(root), "files_scanned": len(metrics), "metrics": metrics, "findings": findings, "limitations": ["Heuristic static audit, not proof of a defect.", "Non-Python languages use generic text rules unless an external language-specific analyzer is run separately.", "A language extension being recognized does not imply full semantic or type analysis."]}
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not findings:
        print(f"No heuristic findings. Scanned {len(metrics)} file(s).")
    for item in findings:
        print(f"[{item['priority']}] {item['category']} {item['path']}:{item['line']} — {item['title']}: {item['detail']}")
    print(f"Scanned {len(metrics)} file(s); findings: {len(findings)}.")
    if args.fail_on != "never":
        threshold = {"low": 2, "medium": 1, "high": 0}[args.fail_on]
        if any(rank[item["priority"]] <= threshold for item in findings):
            return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
