#!/usr/bin/env python3
"""Discover local MCP configuration files without exposing secret values.

This reports local configuration evidence only. It cannot observe connections
owned by a hosted ChatGPT process or prove that a configured server is reachable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

VERSION = "0.1.0"


def candidates(home: Path, root: Path) -> list[Path]:
    xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))).expanduser()
    values = [
        home / ".claude.json",
        home / ".claude" / "settings.json",
        home / ".cursor" / "mcp.json",
        home / ".codeium" / "windsurf" / "mcp_config.json",
        home / ".cline" / "mcp_settings.json",
        home / ".roo" / "mcp.json",
        home / ".config" / "Claude" / "claude_desktop_config.json",
        home / ".config" / "claude" / "claude_desktop_config.json",
        xdg_config / "Claude" / "claude_desktop_config.json",
        home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        home / ".codex" / "config.toml",
        home / ".config" / "Code" / "User" / "mcp.json",
        root / ".mcp.json",
        root / ".cursor" / "mcp.json",
        root / ".vscode" / "mcp.json",
        root / ".windsurf" / "mcp_config.json",
        root / ".cline" / "mcp_settings.json",
        root / ".roo" / "mcp.json",
        root / ".claude" / "settings.json",
        root / ".codex" / "config.toml",
    ]
    continue_dir = home / ".continue" / "mcpServers"
    if continue_dir.is_dir():
        values.extend(sorted(continue_dir.glob("*.json")))
    return list(dict.fromkeys(path.resolve() for path in values))


def safe_command(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return Path(value).name


def server_records(data: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    containers: list[tuple[str, Any]] = []
    for key in ("mcpServers", "servers", "mcp_servers"):
        value = data.get(key)
        if isinstance(value, dict):
            containers.extend((str(name), config) for name, config in value.items())
    for name, config in containers:
        if not isinstance(config, dict):
            continue
        url = config.get("url") or config.get("serverUrl")
        command = config.get("command")
        env = config.get("env")
        if isinstance(url, str):
            parsed = urlsplit(url)
            configured_type = str(config.get("type", "")).casefold()
            if configured_type in {"sse", "http", "streamable-http", "streamable_http"}:
                transport = "sse" if configured_type == "sse" else "http"
            else:
                transport = "http" if parsed.scheme in {"http", "https"} else "url"
            host = parsed.hostname
            records.append({
                "name": name, "config_path": str(source), "transport": transport,
                "host": host, "command": None, "env_keys": [],
                "evidence": "configured_not_connection_tested",
            })
        elif isinstance(command, str):
            records.append({
                "name": name, "config_path": str(source), "transport": "stdio",
                "host": None, "command": safe_command(command),
                "env_keys": sorted(str(key) for key in env) if isinstance(env, dict) else [],
                "evidence": "configured_not_connection_tested",
            })
    return records


def strip_json_comments(raw: str) -> str:
    """Remove JSONC // and /* */ comments without changing quoted strings."""
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(raw):
        char = raw[index]
        nxt = raw[index + 1] if index + 1 < len(raw) else ""
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            index += 1
        elif char == "/" and nxt == "/":
            while index < len(raw) and raw[index] not in "\r\n":
                output.append(" ")
                index += 1
        elif char == "/" and nxt == "*":
            output.extend([" ", " "])
            index += 2
            while index < len(raw) and raw[index:index + 2] != "*/":
                output.append("\n" if raw[index] == "\n" else " ")
                index += 1
            if index < len(raw):
                output.extend([" ", " "])
                index += 2
        else:
            output.append(char)
            index += 1
    comment_free = "".join(output)
    output = []
    index = 0
    in_string = False
    escaped = False
    while index < len(comment_free):
        char = comment_free[index]
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            index += 1
        elif char == ",":
            lookahead = index + 1
            while lookahead < len(comment_free) and comment_free[lookahead].isspace():
                lookahead += 1
            if lookahead < len(comment_free) and comment_free[lookahead] in "}]":
                index += 1
            else:
                output.append(char)
                index += 1
        else:
            output.append(char)
            index += 1
    return "".join(output)


def inspect_config(path: Path) -> tuple[list[dict[str, Any]], dict[str, str] | None]:
    try:
        raw = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".toml":
            data = tomllib.loads(raw)
        else:
            data = json.loads(strip_json_comments(raw))
        if not isinstance(data, dict):
            return [], {"path": str(path), "error": "top_level_value_is_not_an_object"}
        return server_records(data, path), None
    except FileNotFoundError:
        return [], None
    except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        return [], {"path": str(path), "error": type(exc).__name__}


def build_report(home: Path, root: Path, explicit: list[str]) -> dict[str, Any]:
    paths = candidates(home.expanduser(), root.expanduser())
    paths.extend(Path(item).expanduser().resolve() for item in explicit)
    paths = list(dict.fromkeys(paths))
    servers: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    inspected: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        inspected.append(str(path))
        found, error = inspect_config(path)
        servers.extend(found)
        if error:
            errors.append(error)
    unique: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for item in servers:
        unique[(item["name"], item["config_path"], item["host"])] = item
    return {
        "schema_version": 1,
        "tool": "AgentKit local MCP configuration discovery",
        "version": VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "status": "local_configs_found" if inspected else "no_local_mcp_config_found",
        "config_files_inspected": inspected,
        "servers": list(unique.values()),
        "config_errors": errors,
        "runtime_mcp_related_environment_variable_names": sorted(
            key for key in os.environ if "MCP" in key.upper() and any(word in key.upper() for word in ("CONFIG", "SERVER", "ENDPOINT"))
        ),
        "limitations": [
            "Only known local config paths and explicitly supplied --config files are inspected.",
            "Secret values, server argument values and URL paths/query strings are never emitted; only environment variable names are listed.",
            "Configured entries are not proof that a server is installed, reachable, authenticated or usable.",
            "GPT-hosted MCP connections are not observable from this local Linux process.",
            "This command does not read conversation history, credential stores, shell history, or arbitrary files under the home directory.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=str(Path.home()), help="Home directory to inspect (default: current user's home).")
    parser.add_argument("--root", default=".", help="Project root for project-local MCP configs.")
    parser.add_argument("--config", action="append", default=[], help="Explicit config path to inspect; repeatable.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", help="Optional report output path.")
    args = parser.parse_args(argv)
    report = build_report(Path(args.home), Path(args.root), args.config)
    if args.format == "json":
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    else:
        lines = [
            "# AgentKit local MCP configuration report", "",
            f"- Generated (UTC): {report['generated_at']}",
            f"- Status: {report['status']}",
            f"- Config files inspected: {len(report['config_files_inspected'])}",
            f"- Configured server entries: {len(report['servers'])}", "",
            "| Server | Transport | Command basename | Host | Config file | Environment keys |",
            "|---|---|---|---|---|---|",
        ]
        for item in report["servers"]:
            lines.append(f"| {item['name']} | {item['transport']} | {item['command'] or '—'} | {item['host'] or '—'} | {item['config_path']} | {', '.join(item['env_keys']) or '—'} |")
        if report["config_errors"]:
            lines += ["", "## Config errors", ""]
            lines.extend(f"- {item['path']}: {item['error']}" for item in report["config_errors"])
        lines += ["", "## Limitations", ""]
        lines.extend(f"- {item}" for item in report["limitations"])
        content = "\n".join(lines) + "\n"
    if args.output:
        target = Path(args.output).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Saved MCP report: {target.resolve()}")
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
