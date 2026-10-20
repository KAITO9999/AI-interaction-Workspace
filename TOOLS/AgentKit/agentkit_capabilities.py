#!/usr/bin/env python3
"""Safe inventory and bounded version probes for high-impact agent tools.

Discovery never executes commands. Optional version probes use fixed arguments
for an allowlisted set of directly discovered executables; package runners such
as npx are deliberately never invoked because they may install code.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
SOURCES = {
    "playwright-cli": "https://playwright.dev/docs/getting-started-cli",
    "playwright": "https://playwright.dev/mcp/introduction",
    "pytest": "https://docs.pytest.org/",
    "node": "https://nodejs.org/en",
    "npm": "https://docs.npmjs.com/",
    "git": "https://git-scm.com/docs",
    "docker": "https://docs.docker.com/",
    "podman": "https://podman.io/docs",
    "python3": "https://docs.python.org/3/",
    "uv": "https://docs.astral.sh/uv/",
    "codex": "https://developers.openai.com/codex/",
    "claude": "https://docs.anthropic.com/",
}
# Fixed argv only; never construct commands from model/user-provided strings.
VERSION_ARGS = {
    "playwright-cli": ["--version"],
    "playwright": ["--version"],
    "pytest": ["--version"],
    "node": ["--version"],
    "npm": ["--version"],
    "git": ["--version"],
    "docker": ["--version"],
    "podman": ["--version"],
    "python3": ["--version"],
    "uv": ["--version"],
    "codex": ["--version"],
    "claude": ["--version"],
}
GROUPS = {
    "browser_automation": ["playwright-cli", "playwright"],
    "test_and_evaluation": ["pytest"],
    "runtime_and_package_tools": ["node", "npm", "python3", "uv"],
    "workspace_and_container_tools": ["git", "docker", "podman"],
    "agent_cli": ["codex", "claude"],
}


def discover(path_value: str | None = None) -> dict[str, Any]:
    """Discover direct executable paths without running any executable."""
    env_path = os.environ.get("PATH", "") if path_value is None else path_value
    tools: list[dict[str, Any]] = []
    for group, names in GROUPS.items():
        for name in names:
            found = shutil.which(name, path=env_path)
            tools.append({
                "name": name,
                "group": group,
                "installed": bool(found),
                "path": str(Path(found).resolve()) if found else None,
                "version": None,
                "probe_status": "not_run" if found else "not_found",
                "source_url": SOURCES[name],
                "evidence": "path_discovery_only" if found else "not_found_on_path",
            })
    return {
        "schema_version": 1,
        "agentkit_capability_probe_version": VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "discovery_executes_commands": False,
        "version_probes_requested": False,
        "tools": tools,
        "limitations": [
            "PATH discovery does not prove that a tool works or that browser binaries are installed.",
            "MCP servers may be configured outside PATH and are not inferred.",
            "No package installation is performed.",
            "Only the optional fixed-argument version probes execute known allowlisted commands.",
            "Availability is environment-specific and must be rechecked in the target environment.",
        ],
    }


def probe_versions(report: dict[str, Any], timeout: float = 2.0, output_limit: int = 500) -> dict[str, Any]:
    """Run fixed version arguments only for discovered allowlisted executables."""
    for item in report["tools"]:
        if not item["installed"]:
            continue
        name = item["name"]
        args = VERSION_ARGS.get(name)
        if not args:
            continue
        try:
            result = subprocess.run(
                [item["path"], *args],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
                shell=False,
                env={"PATH": os.environ.get("PATH", ""), "LANG": "C", "LC_ALL": "C"},
            )
            output = (result.stdout or "").strip()
            item["version"] = output[:output_limit] if output else None
            item["probe_status"] = "version_ok" if result.returncode == 0 else "version_nonzero"
            item["exit_code"] = result.returncode
            item["evidence"] = "fixed_version_command"
        except subprocess.TimeoutExpired:
            item["probe_status"] = "timeout"
            item["evidence"] = "version_probe_timeout"
        except OSError as exc:
            item["probe_status"] = "execution_error"
            item["error_type"] = type(exc).__name__
            item["evidence"] = "version_probe_error"
    report["version_probes_requested"] = True
    report["version_probe_timeout_seconds"] = timeout
    report["version_probe_output_limit_chars"] = output_limit
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AgentKit capability report", "",
        f"- Generated (UTC): {report['generated_at']}",
        f"- AgentKit probe version: {report['agentkit_capability_probe_version']}",
        f"- Discovery executes commands: {report['discovery_executes_commands']}",
        f"- Version probes requested: {report['version_probes_requested']}", "",
        "| Group | Tool | Found on PATH | Version probe | Version/output | Source |",
        "|---|---|---:|---|---|---|",
    ]
    for item in report["tools"]:
        version = (item.get("version") or "—").replace("|", "\\|").replace("\n", " ")
        path_status = "yes" if item["installed"] else "no"
        source = f"[docs]({item['source_url']})"
        lines.append(f"| {item['group']} | {item['name']} | {path_status} | {item['probe_status']} | {version} | {source} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limit}" for limit in report["limitations"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", help="Optional output file; stdout if omitted.")
    parser.add_argument("--probe-versions", action="store_true", help="Run fixed --version commands for discovered allowlisted tools.")
    parser.add_argument("--timeout", type=float, default=2.0, help="Per-command version probe timeout (0.1-10 seconds).")
    args = parser.parse_args(argv)
    if not 0.1 <= args.timeout <= 10:
        parser.error("--timeout must be between 0.1 and 10 seconds")
    report = discover()
    if args.probe_versions:
        report = probe_versions(report, timeout=args.timeout)
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(report)
    if args.output:
        target = Path(args.output).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Saved capability report: {target.resolve()}")
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
