"""Read-only source audit with confidence-ranked findings and separate performance logs."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.2.0"
EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".kt", ".kts",
    ".go", ".rs", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".fs", ".fsx", ".vb",
    ".php", ".rb", ".rake", ".swift", ".m", ".mm", ".scala", ".sc", ".clj", ".cljs",
    ".ex", ".exs", ".erl", ".hrl", ".hs", ".lhs", ".lua", ".pl", ".pm", ".r", ".R",
    ".jl", ".dart", ".vue", ".svelte", ".sh", ".bash", ".zsh", ".ps1", ".psm1",
    ".sql", ".yaml", ".yml", ".toml", ".json", ".xml", ".html", ".css", ".scss",
}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__", ".next", ".agentkit-logs"}
COMMENT_RE = re.compile(r"^\s*(#|//|/\*|<!--|--)")

def mask_comments_and_strings(source: str, suffix: str) -> tuple[str, set[int]]:
    """Mask comments and string literals without changing line numbers or code positions."""
    suffix = suffix.lower()
    line_comments = {"//"}
    if suffix in {".py", ".pyi", ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".yaml", ".yml", ".toml", ".r", ".rb", ".pl", ".pm"}:
        line_comments = {"#"}
    elif suffix in {".sql"}:
        line_comments = {"--"}
    elif suffix in {".html", ".xml", ".vue", ".svelte", ".css", ".scss"}:
        line_comments = set()
    elif suffix == ".php":
        line_comments = {"#", "//"}
    block_pairs = [("/*", "*/")] if suffix not in {".py", ".pyi", ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".yaml", ".yml", ".toml", ".sql", ".rb", ".r", ".R", ".pl", ".pm"} else []
    if suffix in {".html", ".xml", ".vue", ".svelte"}:
        block_pairs.append(("<!--", "-->"))
    chars = list(source)
    comment_chars = set()
    i = 0
    quote = None
    triple = False
    escaped = False
    block_end = None
    line_has_code = False
    line_comment_only = set()
    current_line = 1
    line_prefix_code = False
    while i < len(chars):
        ch = chars[i]
        if ch == "\n":
            if current_line in comment_chars and not line_prefix_code:
                line_comment_only.add(current_line)
            current_line += 1
            line_prefix_code = False
            escaped = False
            if quote and not triple and suffix not in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".php", ".swift", ".m", ".mm", ".scala", ".dart", ".lua"}:
                quote = None
            i += 1
            continue
        if block_end:
            if source.startswith(block_end, i):
                for j in range(i, i + len(block_end)):
                    if chars[j] != "\n": chars[j] = " "
                i += len(block_end)
                block_end = None
                continue
            if ch != "\n":
                comment_chars.add(current_line)
                chars[i] = " "
            i += 1
            continue
        if quote:
            if ch != "\n": chars[i] = " "
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif triple and source.startswith(quote * 3, i):
                for j in range(i, min(i + 3, len(chars))):
                    if chars[j] != "\n": chars[j] = " "
                i += 3
                quote = None
                triple = False
                continue
            elif not triple and ch == quote:
                quote = None
            i += 1
            continue
        started = False
        for opener, closer in block_pairs:
            if source.startswith(opener, i):
                block_end = closer
                for j in range(i, i + len(opener)):
                    if chars[j] != "\n": chars[j] = " "
                comment_chars.add(current_line)
                i += len(opener)
                started = True
                break
        if started:
            continue
        if any(source.startswith(marker, i) for marker in line_comments):
            while i < len(chars) and chars[i] != "\n":
                comment_chars.add(current_line)
                chars[i] = " "
                i += 1
            if not line_prefix_code:
                line_comment_only.add(current_line)
            continue
        if suffix in {".py", ".pyi"} and ch in {"'", '"'} and source.startswith(ch * 3, i):
            quote, triple = ch, True
            for j in range(i, min(i + 3, len(chars))):
                if chars[j] != "\n": chars[j] = " "
            i += 3
            continue
        if ch in {"'", '"', "`"}:
            quote, triple = ch, False
            chars[i] = " "
            i += 1
            continue
        if not ch.isspace():
            line_prefix_code = True
        i += 1
    return "".join(chars), line_comment_only
RISKY_RE = [
    (re.compile(r"\beval\s*\("), "SECURITY", "HIGH", "Dynamic eval call", "Review whether untrusted text can reach eval; prefer explicit parsing.", "MEDIUM"),
    (re.compile(r"\bexec\s*\("), "SECURITY", "HIGH", "Dynamic exec call", "Review code/data boundaries and remove dynamic execution where possible.", "MEDIUM"),
    (re.compile(r"shell\s*=\s*True"), "SECURITY", "HIGH", "Shell-enabled subprocess call", "Prefer an argv list with shell disabled; validate any unavoidable shell input.", "HIGH"),
    (re.compile(r"\bexcept\s*:"), "CORRECTNESS", "MEDIUM", "Bare exception handler", "Catch expected exception types and preserve diagnostic context.", "HIGH"),
    (re.compile(r"\b(TODO|FIXME|HACK)\b", re.I), "MAINTAINABILITY", "LOW", "Deferred-work marker", "Confirm whether this is still relevant and track real work outside source comments.", "HIGH"),
    (re.compile(r"\b(time\.sleep|sleep)\s*\("), "PERFORMANCE", "LOW", "Sleep call in source", "Check whether polling/event-driven waiting is appropriate; context determines severity.", "HIGH"),
    (re.compile(r"\bwhile\s+True\s*:"), "PERFORMANCE", "LOW", "Unbounded loop pattern", "Verify reachable stop condition, cancellation, and bounded waiting.", "MEDIUM"),
    (re.compile(r"\b(for|while)\b.*\b(for|while)\b"), "PERFORMANCE", "LOW", "Possible nested-loop line", "Inspect algorithmic complexity; this text match alone does not prove nested control flow.", "LOW"),
]

def finding(path, line, category, priority, title, detail, confidence="MEDIUM"):
    return {"path": str(path), "line": line, "category": category, "priority": priority, "title": title,
            "detail": detail, "detection_confidence": confidence,
            "review_recommended": confidence != "HIGH"}

def python_ast_findings(path: Path, source: str) -> list[dict]:
    out = []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [finding(path, exc.lineno or 1, "CORRECTNESS", "HIGH", "Python syntax error", exc.msg, "HIGH")]
    definitions = {}
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions[node.name] = node
            end = getattr(node, "end_lineno", node.lineno)
            if end - node.lineno + 1 > 80:
                out.append(finding(path, node.lineno, "MAINTAINABILITY", "MEDIUM", "Very long function",
                    f"{node.name} spans {end-node.lineno+1} lines; split by responsibility if useful.", "HIGH"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append(node)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "call", "check_call", "check_output"}:
            if any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords):
                out.append(finding(path, node.lineno, "SECURITY", "HIGH", "Shell-enabled subprocess call",
                    "Prefer argv lists with shell disabled; validate any unavoidable shell input.", "HIGH"))
    for node in calls:
        target = definitions.get(node.func.id)
        if target is None:
            continue
        positional = len(target.args.posonlyargs) + len(target.args.args)
        required = positional - len(target.args.defaults)
        supplied = len(node.args)
        if target.args.vararg is None and (supplied < required or supplied > positional):
            out.append(finding(path, node.lineno, "CORRECTNESS", "HIGH",
                f"Possible local call arity mismatch: {node.func.id}",
                f"Call supplies {supplied} positional argument(s); local definition accepts {required}..{positional}. Keyword arguments, decorators, and dynamic dispatch can affect this heuristic.",
                "MEDIUM"))
    # Exact normalized AST matches detect duplicate function bodies, but duplicate code is not automatically a defect.
    seen = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            normalized = ast.dump(ast.Module(body=node.body, type_ignores=[]), annotate_fields=True, include_attributes=False)
            digest = hashlib.sha256(normalized.encode()).hexdigest()
            if digest in seen:
                first_name, first_line = seen[digest]
                out.append(finding(path, node.lineno, "DUPLICATION", "LOW", "Exact duplicate Python function",
                    f"{node.name} has the same normalized AST as {first_name} at line {first_line}; duplication may be intentional.", "HIGH"))
            else:
                seen[digest] = (node.name, node.lineno)
    return out

def audit_file(path: Path, root: Path, max_bytes: int):
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return [], {"path": str(path.relative_to(root)), "skipped": "file exceeds size limit", "bytes": size}
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [finding(path, 1, "ENVIRONMENT", "LOW", "Could not read file", str(exc), "HIGH")], {}
    lines = source.splitlines()
    rel = path.relative_to(root)
    masked, comment_only_lines = mask_comments_and_strings(source, path.suffix.lower())
    masked_lines = masked.splitlines()
    out = python_ast_findings(rel, source) if path.suffix.lower() in {".py", ".pyi"} else []
    for number, line in enumerate(masked_lines, 1):
        for pattern, category, priority, title, detail, confidence in RISKY_RE:
            if pattern.search(line):
                out.append(finding(rel, number, category, priority, title, detail, confidence))
    comment_lines = len(comment_only_lines)
    code_lines = sum(1 for line in masked_lines if line.strip())
    if len(lines) >= 30 and comment_lines / max(1, comment_lines + code_lines) > 0.40:
        out.append(finding(rel, 1, "MAINTAINABILITY", "LOW", "High comment-to-code ratio",
            f"{comment_lines} comment-only lines vs {code_lines} code-like lines. Review stale/redundant narration; preserve useful rationale.", "HIGH"))
    max_run = run = 0
    for number, line in enumerate(lines, 1):
        run = run + 1 if number in comment_only_lines and line.strip() else 0
        max_run = max(max_run, run)
    if max_run >= 12:
        out.append(finding(rel, 1, "MAINTAINABILITY", "LOW", "Long consecutive comment block",
            f"Found {max_run} consecutive comment-only lines; check whether material belongs in API docs/docstrings.", "HIGH"))
    return out, {"path": str(rel), "language_hint": path.suffix.lower().lstrip("."), "lines": len(lines),
                 "comment_like_lines": comment_lines, "bytes": size, "sha256": hashlib.sha256(source.encode()).hexdigest()}

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
        return sorted(set(files))
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS
                  and not any(part in SKIP_DIRS for part in p.relative_to(root).parts))

def append_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--file", action="append", default=[], help="Relative file to audit; repeatable.")
    parser.add_argument("--json", dest="json_path", help="Write full machine-readable report.")
    parser.add_argument("--log-dir", default=".agentkit-logs", help="Separate append-only audit/performance logs.")
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--fail-on", choices=["never", "low", "medium", "high"], default="never")
    args = parser.parse_args()
    started = time.perf_counter()
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
    content_seen = defaultdict(list)
    line_seen = defaultdict(list)
    for path in files:
        found, metric = audit_file(path, root, args.max_bytes)
        findings.extend(found)
        if metric:
            metrics.append(metric)
            if "sha256" in metric:
                content_seen[metric["sha256"]].append(metric["path"])
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                    masked_text, _ = mask_comments_and_strings(text, path.suffix.lower())
                    for number, line in enumerate(masked_text.splitlines(), 1):
                        stripped = line.strip()
                        if len(stripped) >= 40:
                            line_seen[stripped].append((metric["path"], number))
                except OSError:
                    pass
    for digest, paths in content_seen.items():
        if len(paths) > 1:
            for duplicate in paths[1:]:
                findings.append(finding(duplicate, 1, "DUPLICATION", "LOW", "Byte-identical source file",
                    f"Exact SHA-256 duplicate of {paths[0]}; verify whether both copies are required.", "HIGH"))
    for line, locations in line_seen.items():
        distinct = sorted(set(locations))
        if len({path for path, _ in distinct}) > 1:
            first = distinct[0]
            for duplicate in distinct[1:]:
                findings.append(finding(duplicate[0], duplicate[1], "DUPLICATION", "LOW", "Repeated source line",
                    f"Exact repeated non-comment line also appears at {first[0]}:{first[1]}; repetition may be intentional.", "HIGH"))
    rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda item: (rank[item["priority"]], item["path"], item["line"], item["title"]))
    elapsed = time.perf_counter() - started
    total_bytes = sum(m.get("bytes", 0) for m in metrics)
    total_lines = sum(m.get("lines", 0) for m in metrics)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report = {"tool": "agentkit_code_audit", "version": VERSION, "run_id": run_id, "root": str(root),
        "files_scanned": sum(1 for m in metrics if "sha256" in m), "metrics": metrics, "findings": findings,
        "confidence_policy": {"HIGH": "Detection is directly established (for example exact hash or syntax parser result); no routine confirmation required, though the finding may be informational.",
            "MEDIUM": "Heuristic or context-dependent; confirmation recommended.", "LOW": "Weak contextual signal; confirmation recommended."},
        "limitations": ["Heuristic static audit, not proof of a defect.",
            "Python receives AST checks; other languages currently receive generic text checks.",
            "Recognizing a language extension does not imply full semantic or type analysis."]}
    log_dir = Path(args.log_dir)
    if not log_dir.is_absolute():
        log_dir = root / log_dir
    stamp = datetime.now(timezone.utc).isoformat()
    audit_log = log_dir / "code-audit-findings.jsonl"
    performance_log = log_dir / "code-audit-performance.jsonl"
    for item in findings:
        append_jsonl(audit_log, {"timestamp_utc": stamp, "run_id": run_id, **item})
    perf = {"timestamp_utc": stamp, "run_id": run_id, "tool": "agentkit_code_audit", "root": str(root),
        "files_discovered": len(files), "files_scanned": report["files_scanned"], "bytes_read": total_bytes,
        "lines_scanned": total_lines, "findings_count": len(findings), "elapsed_seconds": round(elapsed, 6),
        "bytes_per_second": round(total_bytes / elapsed, 2) if elapsed else None,
        "notes": ["Measured runtime applies to this audit run and environment only.",
            "Static performance findings are leads, not reliable runtime predictions.",
            "Environment-specific execution (including Minecraft add-ons) needs a separate environment/runtime probe."]}
    append_jsonl(performance_log, perf)
    report["performance"] = perf
    report["logs"] = {"findings": str(audit_log), "performance": str(performance_log)}
    if args.json_path:
        output = Path(args.json_path)
        if not output.is_absolute():
            output = root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in findings:
        flag = "CONFIRM" if item["review_recommended"] else "HIGH-CONFIDENCE"
        print(f"[{item['priority']}/{item['detection_confidence']}] [{flag}] {item['category']} {item['path']}:{item['line']} — {item['title']}: {item['detail']}")
    print(f"Scanned {report['files_scanned']} file(s), {total_bytes} bytes, {total_lines} lines; findings: {len(findings)}; audit runtime: {elapsed:.3f}s.")
    print(f"Finding log: {audit_log}\nPerformance log: {performance_log}")
    if args.fail_on != "never":
        threshold = {"low": 2, "medium": 1, "high": 0}[args.fail_on]
        if any(rank[item["priority"]] <= threshold for item in findings):
            return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
