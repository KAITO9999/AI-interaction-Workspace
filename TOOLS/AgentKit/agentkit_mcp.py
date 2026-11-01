#!/usr/bin/env python3
"""Read-only MCP connector for AgentKit's bounded inspection commands."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server import MCPServer
    from mcp.types import ToolAnnotations
except ImportError as exc:  # pragma: no cover - depends on optional connector package
    raise SystemExit(
        "AgentKit MCP connector requires the optional 'mcp' package. "
        "Install requirements-mcp.txt in the connector environment."
    ) from exc

from agentkit_process import run_process

SCRIPTS_DIR = Path(__file__).resolve().parent
ANNOTATIONS = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)
OUTPUT_LIMIT = 16_000
DEFAULT_TIMEOUT = 15
MAX_TIMEOUT = 60
MAX_PROBE_FILES = 3_000
ROOT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")

mcp = MCPServer(
    "AgentKit",
    instructions=(
        "Use AgentKit tools for bounded, read-only inspection of configured roots. "
        "Only root IDs from agentkit_roots are available. Paths must be relative to a configured root. "
        "These tools do not install packages, write reports, change files, or run user-provided commands."
    ),
)


def configured_roots() -> dict[str, dict[str, str]]:
    """Load an explicit allowlist; never default to HOME or the current directory."""
    raw = os.environ.get("AGENTKIT_ROOTS_JSON", "")
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("AGENTKIT_ROOTS_JSON must be a JSON object") from exc
    if not isinstance(value, dict):
        raise ValueError("AGENTKIT_ROOTS_JSON must be a JSON object")
    roots: dict[str, dict[str, str]] = {}
    for root_id, item in value.items():
        if not isinstance(root_id, str) or not ROOT_ID.fullmatch(root_id):
            raise ValueError("root IDs must use 1-64 letters, digits, '_' or '-' and start alphanumeric")
        if isinstance(item, str):
            path_value, description = item, root_id
        elif isinstance(item, dict) and isinstance(item.get("path"), str):
            path_value = item["path"]
            description = str(item.get("description") or root_id)
        else:
            raise ValueError(f"root {root_id!r} must be a path string or an object with a path")
        path = Path(path_value).expanduser().resolve(strict=True)
        if not path.is_dir():
            raise ValueError(f"configured root {root_id!r} is not a directory")
        roots[root_id] = {"path": str(path), "description": description[:200]}
    return roots


def get_root(root_id: str) -> Path:
    roots = configured_roots()
    if root_id not in roots:
        raise ValueError("Unknown root_id; call agentkit_roots and use a configured ID")
    return Path(roots[root_id]["path"])


def resolve_path(root: Path, relative_path: str, *, must_exist: bool = True) -> Path:
    """Resolve a model-supplied relative path and reject traversal/symlink escapes."""
    candidate_text = Path(relative_path)
    if candidate_text.is_absolute():
        raise ValueError("path must be relative to the configured root")
    candidate = (root / candidate_text).resolve(strict=must_exist)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("path resolves outside the configured root") from exc
    if must_exist and not candidate.is_file() and not candidate.is_dir():
        raise ValueError("path must identify a file or directory")
    return candidate


def invoke(script: str, args: list[str], *, cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """Run one fixed AgentKit script with argv, timeout, and bounded output."""
    if timeout < 1 or timeout > MAX_TIMEOUT:
        raise ValueError(f"timeout must be between 1 and {MAX_TIMEOUT} seconds")
    script_path = SCRIPTS_DIR / script
    result = run_process(
        [sys.executable, str(script_path), *args],
        timeout=timeout,
        cwd=cwd,
        output_limit=OUTPUT_LIMIT,
    )
    return {
        "status": result["status"],
        "exit_code": result.get("returncode"),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "stdout_truncated": bool(result.get("stdout_truncated")),
        "stderr_truncated": bool(result.get("stderr_truncated")),
        "duration_seconds": result.get("duration_seconds"),
    }


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_roots() -> list[dict[str, str]]:
    """List the configured project roots available for read-only inspection."""
    return [
        {"root_id": root_id, "description": item["description"]}
        for root_id, item in configured_roots().items()
    ]


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_version() -> dict[str, Any]:
    """Report the installed AgentKit version."""
    return invoke("agentkit.py", ["--version"], cwd=SCRIPTS_DIR)


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_probe(root_id: str) -> dict[str, Any]:
    """Inventory known tools, format hints, and a bounded file sample in a configured root."""
    root = get_root(root_id)
    return invoke("agentkit.py", ["probe", "--root", str(root), "--max-scan", str(MAX_PROBE_FILES)], cwd=root)


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_locate(root_id: str, path: str, start: int, end: int | None = None) -> dict[str, Any]:
    """Read a bounded line range from a UTF-8 file under a configured root."""
    if start < 1 or (end is not None and (end < start or end - start > 199)):
        raise ValueError("provide a 1-based range of at most 200 lines")
    root = get_root(root_id)
    target = resolve_path(root, path)
    if task in {"json-check", "sha256"} and not target.is_file():
        raise ValueError(f"{task} requires a file")
    if task == "json-check" and target.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("JSON validation is limited to files at or below 16 MiB")
    if task == "sha256" and target.stat().st_size > 256 * 1024 * 1024:
        raise ValueError("SHA-256 inspection is limited to files at or below 256 MiB")
    if not target.is_file():
        raise ValueError("path must identify a file")
    args = [str(target), "--start", str(start)]
    if end is not None:
        args.extend(["--end", str(end)])
    return invoke("agentkit.py", ["locate", *args], cwd=root)


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_resolve(root_id: str, task: str, path: str = ".", pattern: str = "") -> dict[str, Any]:
    """Use AgentKit's Python fallback for JSON checks, text search, file names, archive lists, or SHA-256."""
    if task not in {"json-check", "search", "find-files", "archive-list", "sha256"}:
        raise ValueError("task must be json-check, search, find-files, archive-list, or sha256")
    if task in {"search", "find-files"} and not pattern:
        raise ValueError("pattern is required for search and find-files")
    root = get_root(root_id)
    target = resolve_path(root, path)
    args = [task, str(target), "--prefer-fallback"]
    if pattern:
        args.extend(["--pattern", pattern[:500]])
    return invoke("agentkit_resolve.py", args, cwd=root)


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_context(
    root_id: str,
    target: str = ".",
    pattern: str = "",
    start: int | None = None,
    end: int | None = None,
    max_lines: int = 100,
    max_bytes: int = 32_000,
) -> dict[str, Any]:
    """Read a bounded context range or search matching lines under a configured root."""
    if max_lines < 1 or max_lines > 200 or max_bytes < 1 or max_bytes > 64_000:
        raise ValueError("max_lines must be 1..200 and max_bytes must be 1..64000")
    if (start is None) != (end is None) or (start is not None and (start < 1 or end < start)):
        raise ValueError("start and end must be supplied together as a valid 1-based range")
    root = get_root(root_id)
    target_path = resolve_path(root, target)
    args = ["context", "--root", str(root), "--target", str(target_path), "--max-lines", str(max_lines), "--max-bytes", str(max_bytes), "--json"]
    if pattern:
        args.extend(["--pattern", pattern[:500]])
    if start is not None and end is not None:
        args.extend(["--start", str(start), "--end", str(end)])
    return invoke("agentkit_work.py", args, cwd=root)


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_lint_python(root_id: str, paths: list[str] | None = None) -> dict[str, Any]:
    """Run AgentKit's bounded Python inspection in a configured root; reports fallback limits."""
    root = get_root(root_id)
    args = ["lint-python", "--root", str(root), "--json"]
    for relative in (paths or [])[:20]:
        target = resolve_path(root, relative)
        if not target.is_file() or target.suffix != ".py":
            raise ValueError("each path must identify a Python file")
        args.extend(["--file", str(target.relative_to(root))])
    return invoke("agentkit_work.py", args, cwd=root, timeout=MAX_TIMEOUT)


@mcp.tool(annotations=ANNOTATIONS)
def agentkit_mobile_plan(root_id: str, profile: str = "low-end") -> dict[str, Any]:
    """Create a read-only static mobile compatibility preflight; it does not build or test an app."""
    if profile not in {"low-end", "mid-end", "mid-high", "high-end", "all"}:
        raise ValueError("profile must be low-end, mid-end, mid-high, high-end, or all")
    root = get_root(root_id)
    args = ["--root", str(root)]
    if profile != "all":
        args.extend(["--profile", profile])
    return invoke("mobile_test.py", args, cwd=root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind address; defaults to loopback.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--stateless", action="store_true", help="Use stateless HTTP sessions.")
    args = parser.parse_args()
    # Validate config before opening a transport.
    configured_roots()
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            stateless_http=args.stateless,
            streamable_http_path="/mcp",
        )


if __name__ == "__main__":
    main()
