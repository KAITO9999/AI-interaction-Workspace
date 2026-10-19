"""Discover local AI-agent CLIs and report integration routes for AgentKit.

Detection is deliberately conservative: a CLI found on PATH proves only that
an executable exists, not that it is authenticated, configured, or connected.
Hosted products are never inferred from local package state.
"""
from __future__ import annotations

import argparse
import json
import shutil
from typing import Any

VERSION = "0.1.0"

AGENTS: dict[str, dict[str, Any]] = {
    "codex": {
        "name": "OpenAI Codex CLI",
        "kind": "local_cli",
        "commands": ["codex"],
        "transports": ["mcp-stdio", "mcp-http"],
        "config_hint": "codex mcp add <name> -- <server-command> [args...]",
        "verification_hint": "codex mcp list",
        "notes": "PATH detection does not prove login, MCP configuration, or tool availability.",
    },
    "claude-code": {
        "name": "Claude Code",
        "kind": "local_cli",
        "commands": ["claude"],
        "transports": ["mcp-stdio", "mcp-http"],
        "config_hint": "claude mcp add <name> -- <server-command> [args...]",
        "verification_hint": "claude mcp list (then /mcp in an interactive session)",
        "notes": "PATH detection does not prove login, MCP configuration, or tool availability.",
    },
    "opencode": {
        "name": "OpenCode",
        "kind": "local_cli",
        "commands": ["opencode"],
        "transports": ["mcp-stdio", "mcp-http"],
        "config_hint": "Configure an MCP server in opencode.json / opencode.jsonc, or use opencode mcp add",
        "verification_hint": "opencode mcp list",
        "notes": "MCP config syntax can vary by OpenCode version; check the installed CLI help/docs.",
    },
    "cursor": {
        "name": "Cursor Agent",
        "kind": "desktop_or_editor",
        "commands": ["cursor"],
        "transports": ["mcp-config"],
        "config_hint": "Configure MCP in the Cursor MCP configuration file/UI",
        "verification_hint": "Check Cursor's MCP settings and tool picker",
        "notes": "A cursor executable alone does not prove the editor, Agent mode, or MCP is enabled.",
    },
    "vscode-copilot": {
        "name": "VS Code with GitHub Copilot Agent mode",
        "kind": "desktop_or_editor",
        "commands": ["code"],
        "transports": ["mcp-config"],
        "config_hint": "Configure an MCP server in .vscode/mcp.json and enable it in Agent mode",
        "verification_hint": "Check the MCP server status and Agent-mode tool picker",
        "notes": "The code executable only detects VS Code CLI, not Copilot installation, entitlement, or Agent mode.",
    },
    "chatgpt": {
        "name": "ChatGPT (hosted product)",
        "kind": "hosted_product",
        "commands": [],
        "transports": ["plugin", "remote-mcp", "secure-tunnel-or-bridge"],
        "config_hint": "Use a supported ChatGPT plugin/MCP integration or a secured bridge reachable by the hosted service",
        "verification_hint": "Verify the integration in ChatGPT's available tools; local PATH cannot detect it",
        "notes": "A Termux localhost server is not automatically reachable from hosted ChatGPT.",
    },
    "generic-mcp-client": {
        "name": "Generic MCP-compatible client",
        "kind": "protocol_profile",
        "commands": [],
        "transports": ["mcp-stdio", "mcp-http"],
        "config_hint": "Use the client's documented MCP transport and authentication configuration",
        "verification_hint": "Run the client's MCP connection/tool-list check",
        "notes": "Protocol support must be confirmed for the specific client and version.",
    },
}

CAPABILITY_ROUTES: dict[str, dict[str, Any]] = {
    "termux-command-execution": {
        "requires": ["termux-mcp"],
        "preferred_transports": ["mcp-stdio", "mcp-http"],
        "fallback": "Use a narrowly scoped local CLI wrapper or AgentKit subprocess API",
        "safety": "Do not expose unrestricted shell execution to remote clients; allowlist tools and arguments.",
    },
    "file-search": {
        "requires_any": ["rg", "grep", "find", "fd"],
        "preferred_transports": ["mcp-stdio", "mcp-http", "cli-wrapper"],
        "fallback": "Python pathlib traversal with depth/result limits",
        "safety": "Restrict roots and skip secrets/dependency directories by default.",
    },
    "process-tracing": {
        "requires_any": ["strace"],
        "preferred_transports": ["mcp-stdio", "mcp-http", "cli-wrapper"],
        "fallback": "Python subprocess metadata/logging; not syscall-equivalent",
        "safety": "Tracing may be restricted by Android/kernel permissions; label incomplete traces clearly.",
    },
    "json-processing": {
        "requires_any": ["jq", "python"],
        "preferred_transports": ["mcp-stdio", "mcp-http", "cli-wrapper"],
        "fallback": "Python standard-library json module",
        "safety": "Bound input and output sizes; do not evaluate expressions from untrusted input.",
    },
}


def discover(command_lookup=shutil.which) -> dict[str, Any]:
    """Return profiles with conservative local presence signals."""
    profiles = []
    for key, spec in AGENTS.items():
        found = [{"command": cmd, "path": command_lookup(cmd)} for cmd in spec["commands"]]
        found = [item for item in found if item["path"]]
        if spec["kind"] == "hosted_product":
            status = "not_locally_detectable"
        elif spec["kind"] == "protocol_profile":
            status = "requires_client_confirmation"
        else:
            status = "cli_detected" if found else "not_detected"
        profiles.append({"id": key, **spec, "detected_commands": found, "status": status})
    return {
        "schema_version": 1,
        "version": VERSION,
        "detection_scope": "local executable presence only; configuration/authentication/connectivity are not proven",
        "agents": profiles,
        "capability_routes": CAPABILITY_ROUTES,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument("--agent", choices=sorted(AGENTS), help="show one agent profile")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args(argv)
    report = discover()
    if args.agent:
        report["agents"] = [item for item in report["agents"] if item["id"] == args.agent]
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("AgentKit agent compatibility report")
        print("Detection: local executable presence only; no auth/connectivity claim.\n")
        for item in report["agents"]:
            commands = ", ".join(f"{entry['command']}={entry['path']}" for entry in item["detected_commands"]) or "—"
            print(f"{item['name']} [{item['status']}] — {commands}")
            print(f"  transports: {', '.join(item['transports'])}")
            print(f"  verify: {item['verification_hint']}")
        print("\nCapability routes:")
        for key, route in report["capability_routes"].items():
            required = route.get("requires", route.get("requires_any", []))
            print(f"  {key}: requires {', '.join(required)}; fallback: {route['fallback']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
