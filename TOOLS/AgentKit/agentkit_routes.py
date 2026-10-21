#!/usr/bin/env python3
"""Automatic AgentKit route selector for supported bounded tasks."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
HERE = Path(__file__).resolve().parent
TASKS: dict[str, dict[str, Any]] = {
    "python-lint": {"preferred": "ruff", "fallback": "agentkit_ruff.py", "kind": "python"},
    "mcp-inventory": {"preferred": None, "fallback": "agentkit_mcp.py", "kind": "python"},
    "json-check": {"preferred": ["jq"], "fallback": "agentkit_resolve.py", "kind": "resolver"},
    "search": {"preferred": ["rg", "grep"], "fallback": "agentkit_resolve.py", "kind": "resolver"},
    "find-files": {"preferred": ["fd", "find"], "fallback": "agentkit_resolve.py", "kind": "resolver"},
    "archive-list": {"preferred": ["7z", "unzip", "tar"], "fallback": "agentkit_resolve.py", "kind": "resolver"},
    "sha256": {"preferred": ["sha256sum", "shasum"], "fallback": "agentkit_resolve.py", "kind": "resolver"},
}


def plan(task: str, force_fallback: bool = False) -> dict[str, Any]:
    spec = TASKS[task]
    commands = spec["preferred"]
    if isinstance(commands, str):
        commands = [commands]
    found = [(name, shutil.which(name)) for name in commands if name and shutil.which(name)]
    if found and not force_fallback:
        selected_name, selected_path = found[0]
        route = "direct"
        selected = selected_path
        compatibility = "native command selected by ordered availability; behavior depends on the command and arguments"
    else:
        selected_name = None
        route = "agentkit_fallback"
        selected = str(HERE / spec["fallback"])
        compatibility = "task-specific reduced alternative; not a drop-in replacement"
    return {
        "schema_version": 1, "agentkit_routes_version": VERSION, "task": task,
        "route": route, "selected": selected, "selected_command": selected_name,
        "preferred_commands": commands, "available_commands": [{"command": n, "path": p} for n, p in found],
        "fallback": str(HERE / spec["fallback"]), "compatibility": compatibility,
        "automatic_install": False,
        "limitations": ["PATH presence is not proof of successful execution.", "MCP inventory reports local config only, not GPT-hosted connections."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=sorted(TASKS))
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--pattern")
    parser.add_argument("--plan", action="store_true", help="Report the selected route without executing it.")
    parser.add_argument("--json-report", action="store_true", help="Print route plan as JSON and exit.")
    parser.add_argument("--force-fallback", action="store_true")
    parser.add_argument("--prefer-fallback", action="store_true")
    parser.add_argument("--format", choices=("json", "text", "markdown"), default="text")
    parser.add_argument("--config", action="append", default=[])
    args = parser.parse_args(argv)
    force = args.force_fallback or args.prefer_fallback
    report = plan(args.task, force)
    if args.plan or args.json_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.task == "python-lint":
        command = [sys.executable, str(HERE / "agentkit_ruff.py"), "check", args.target]
        if args.format == "json":
            command += ["--format", "json"]
        if force:
            command.append("--force-fallback")
    elif args.task == "mcp-inventory":
        command = [sys.executable, str(HERE / "agentkit_mcp.py"), "--root", args.target, "--format", "json" if args.format == "json" else "markdown"]
        for config in args.config:
            command += ["--config", config]
    else:
        command = [sys.executable, str(HERE / "agentkit_resolve.py"), args.task, args.target]
        if args.pattern:
            command += ["--pattern", args.pattern]
        if force:
            command.append("--prefer-fallback")

    print(f"ROUTE: {report['route']} | task={args.task} | selected={report['selected']}", file=sys.stderr)
    if report["route"] == "agentkit_fallback":
        print("注意、代替コマンドな為既存とは動作が異なります。", file=sys.stderr)
    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"ERROR: failed to start selected route: {type(exc).__name__}", file=sys.stderr)
        return 127
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
