# AgentKit standard MCP connector

This optional MCP server exposes a read-only subset of AgentKit to standard MCP clients, including ChatGPT custom MCP apps and Codex. It uses the official Python MCP SDK and supports stdio plus Streamable HTTP; it is not a desktop-only plugin. ChatGPT custom MCP setup is currently on the web, and availability depends on the account/workspace plan and policy.

## Install from GitHub

```sh
git clone https://github.com/KAITO9999/AI-interaction-Workspace.git
cd AI-interaction-Workspace
python3 -m pip install -r TOOLS/AgentKit/requirements-mcp.txt
```

On Termux, Python 3.11+ is required for the optional MCP SDK. The AgentKit CLI and skill remain usable without this dependency.

## Restrict accessible folders

The connector starts with **no accessible roots**. Configure only project folders that the model may inspect. Do not add your whole home directory or folders containing credentials.

```sh
export AGENTKIT_ROOTS_JSON='{"project":{"path":"/path/to/project","description":"Selected project source"}}'
```

Root IDs are names supplied by the operator. Tool calls use those IDs and relative paths; absolute paths and symlink escapes are rejected.

## Run locally

For a private Termux connector, use the default stdio transport with OpenAI's `tunnel-client`. Keep the runtime key in an environment variable and configure only selected project folders:

```sh
export AGENTKIT_ROOTS_JSON='{"project":{"path":"/path/to/project","description":"Selected project source"}}'
export CONTROL_PLANE_API_KEY='<enter locally; do not paste into chat or commit>'
tunnel-client init \
  --sample sample_mcp_stdio_local \
  --profile agentkit \
  --tunnel-id '<tunnel-id>' \
  --mcp-command 'python3 /path/to/AI-interaction-Workspace/TOOLS/AgentKit/agentkit_mcp.py'
tunnel-client doctor --profile agentkit --explain
tunnel-client run --profile agentkit
```

Keep `tunnel-client` running while ChatGPT discovers or calls the tools. The tunnel client starts the server as a local stdio process and carries MCP requests over an outbound connection; no inbound listener is required. For another MCP host that launches local subprocesses, use `python3 .../agentkit_mcp.py` directly.

In ChatGPT on the web, add a custom MCP server from the Plugins page, select the matching Secure MCP Tunnel, then review the discovered actions and account permissions. Read-only access is the broadest supported permission class, but availability still depends on plan and workspace policy.

For an HTTP MCP host, use `--transport streamable-http --host 127.0.0.1 --port 8765 --stateless`; configure `tunnel-client` with `--mcp-server-url http://127.0.0.1:8765/mcp`. A public HTTPS deployment needs an authenticated front end and HTTPS. Do not expose this filesystem reader directly to the Internet without authentication.

## Available tools

- `agentkit_roots`: list configured root IDs and descriptions.
- `agentkit_version`: report the AgentKit version.
- `agentkit_probe`: inspect environment capabilities and a bounded file sample.
- `agentkit_locate`: read up to 200 lines from a selected file.
- `agentkit_resolve`: JSON check, search, filename search, archive listing, or SHA-256 using the Python fallback.
- `agentkit_context`: bounded file context or text search.
- `agentkit_lint_python`: AgentKit's bounded Python checks; reports fallback limits.
- `agentkit_mobile_plan`: static mobile compatibility preflight only.

The connector does not expose arbitrary shell execution, package installation, TypeScript emission, provenance recording, file writes, or Android actions. MCP read-only annotations improve host UX; path restrictions and fixed argument vectors enforce the boundary.

## HyAI local integration

HyAI can use the Termux skill/CLI directly as a local AgentKit path. This is separate from the HyAI Bridge API, Lane routing, approval system, and any external model API call. Do not send local state or project contents to an external provider unless the user explicitly requests it.

```sh
SK="$HOME/.codex/skills/agentkit"
python3 "$SK/scripts/agentkit.py" --help
```

The skill is installed as `~/.codex/skills/agentkit`; consult `SKILL.md` for its command reference.
