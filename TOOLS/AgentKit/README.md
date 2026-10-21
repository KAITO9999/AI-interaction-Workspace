# AgentKit — environment discovery and workflow helpers

Core CLI: version 0.1.0. Extension CLI: version 0.2.0. Python standard library only. Python 3.9+ is recommended.

## Core CLI

    python3 TOOLS/AgentKit/agentkit.py --help
    python3 TOOLS/AgentKit/agentkit.py probe --root . --json /tmp/agentkit-report.json
    python3 TOOLS/AgentKit/agentkit.py probe --root . --list-files
    python3 TOOLS/AgentKit/agentkit.py locate path/to/file.py --start 20 --end 50
    python3 TOOLS/AgentKit/agentkit.py versions --root . --output /tmp/agentkit-capabilities.md
    python3 TOOLS/AgentKit/agentkit.py fetch-probe https://github.com/OWNER/REPOSITORY.git --timeout 5

The core probe reports a curated set of known commands and format hints. This is heuristic: finding a command does not prove a target project builds or runs.

## Extension CLI

Run:

    python3 TOOLS/AgentKit/agentkit_ext.py --help

### 1. Enumerate actual PATH executables

    python3 TOOLS/AgentKit/agentkit_ext.py commands
    python3 TOOLS/AgentKit/agentkit_ext.py commands --filter rust
    python3 TOOLS/AgentKit/agentkit_ext.py commands --all-path-entries --format tsv
    python3 TOOLS/AgentKit/agentkit_ext.py commands --format json --output /tmp/path-command-inventory.json

The inventory scans executable files in PATH without running them. By default, it keeps the first command name in PATH order. The all-path-entries option also lists shadowed duplicates. Shell built-ins, aliases and functions are not included. Output paths may reveal local usernames or installation layouts; do not commit raw environment inventories without review and sanitization.

### 2. TypeScript to JavaScript compilation

    python3 TOOLS/AgentKit/agentkit_ext.py compile-ts --root path/to/project
    python3 TOOLS/AgentKit/agentkit_ext.py compile-ts --root path/to/project --check
    python3 TOOLS/AgentKit/agentkit_ext.py compile-ts --root path/to/project --file src/main.ts --out-dir dist

This helper uses an existing tsc executable and never installs packages automatically. If tsconfig.json exists, it compiles the project configuration; do not combine project mode with explicit file arguments. Without a config, .ts files use ES2022/ESNext defaults. .tsx requires tsconfig.json so JSX settings are not guessed. Default output directory is dist; confirm runtime/module expectations before running the generated JavaScript. The check option uses no-emit type checking.

### 3. Record who changed what, and which work mode was used

    python3 TOOLS/AgentKit/agentkit_ext.py record-change --root . --actor ai --mode mixed --summary "Add and test environment tooling" --path TOOLS/AgentKit/agentkit_ext.py --path TOOLS/AgentKit/tests/test_agentkit_ext.py

Required values:
- actor: ai or human, depending on who authored/materially edited the files. If both made distinct changes, add separate records.
- mode: online if remote services/network were used, offline if only local resources were used, mixed if both.
- summary and one or more changed paths, each passed as a repeated path argument.

By default, records append to LOGS/change-ledger.jsonl. Review before committing. The PR CI verifies append-only behavior and path coverage. This is a workflow label, not proof of identity and not a replacement for Git history.

Never record raw prompts, conversations, access tokens, private URLs or personal data.

### 4. Static Minecraft add-on audit

    python3 TOOLS/AgentKit/agentkit_ext.py audit-addon /path/to/ReForge_Visuals-3.24.1.mcaddon
    python3 TOOLS/AgentKit/agentkit_ext.py audit-addon /path/to/addon.mcaddon --json /tmp/addon-audit.json

The audit checks ZIP CRC and member paths, parses JSON, compares BP/RP manifest versions and dependencies, and uses Node --check on JavaScript when Node is present. It does not extract the archive, validate every Minecraft schema or prove runtime behavior. In-world and Content Log checks remain separate.

### 6. Automatic execution route selection

    python3 TOOLS/AgentKit/agentkit_routes.py python-lint path/to/code
    python3 TOOLS/AgentKit/agentkit_routes.py python-lint path/to/code --format json
    python3 TOOLS/AgentKit/agentkit_routes.py python-lint path/to/code --force-fallback
    python3 TOOLS/AgentKit/agentkit_routes.py json-check path/to/data.json --plan
    python3 TOOLS/AgentKit/agentkit_routes.py search path/to/project --pattern TODO
    python3 TOOLS/AgentKit/agentkit_routes.py mcp-inventory --root path/to/project --format json

The route selector prefers the first available allowlisted command and otherwise uses an AgentKit fallback. `--plan` reports the selected route without executing the task. It does not install packages automatically. When a fallback is used, the CLI prints:

    注意、代替コマンドな為既存とは動作が異なります。

### 7. Ruff route and reduced Python fallback

    python3 TOOLS/AgentKit/agentkit_ruff.py check path/to/code
    python3 TOOLS/AgentKit/agentkit_ruff.py check path/to/file.py --format json
    python3 TOOLS/AgentKit/agentkit_ruff.py check path/to/file.py --force-fallback
    python3 TOOLS/AgentKit/agentkit_ruff.py format path/to/file.py --check

If official `ruff` is on PATH, the wrapper delegates to it. Otherwise, the standard-library fallback reports syntax/parse errors (E999) and a conservative subset of unused imports (F401). It is **not Ruff-compatible**, does not implement Ruff configuration, auto-fixes, all lint rules, or formatting. It never rewrites source. The fallback's formatter command exits with status 3 and explains that real Ruff is required for formatting. Do not report a clean fallback run as equivalent to a full Ruff run.

### 8. Local MCP configuration discovery

    python3 TOOLS/AgentKit/agentkit_mcp.py --root .
    python3 TOOLS/AgentKit/agentkit_mcp.py --root . --format json
    python3 TOOLS/AgentKit/agentkit_mcp.py --home /path/to/home --root /path/to/project
    python3 TOOLS/AgentKit/agentkit_mcp.py --config /explicit/path/to/mcp.json --format json

The detector checks known local config locations for Claude Desktop/Code, Cursor, VS Code and Codex, plus explicitly supplied files. It reports server names, transport, command basename, host and environment-variable names only; it does not emit argument values, environment values, URL paths or query strings. It does not read conversation history, credential stores, shell history or arbitrary home-directory files. A config entry does not prove that a server is running, reachable, authenticated or usable. GPT-hosted MCP connections cannot be observed from this Linux process; those must be inspected through the host's available tool/connection metadata.

## Security and limitations

- No privilege escalation, restriction bypass or credential discovery. Package installation is opt-in only through the resolver's explicit `--install` flag.
- Discovered PATH executables are never invoked by the command inventory.
- fetch-probe performs one read-only git ls-remote attempt and stops on the first error/timeout; it does not clone.
- Core shell fallback is deliberately reduced and is not feature-equivalent to Python.
- File and command scans skip common dependency/build directories.
- Local outputs may contain environment paths; inspect them before publication.

## Tests

    python -m unittest discover -s TOOLS/AgentKit/tests -v
    python -m py_compile TOOLS/AgentKit/agentkit.py TOOLS/AgentKit/agentkit_ext.py TOOLS/AgentKit/agentkit_resolve.py

### 5. Resolve a missing command or use a Python fallback

    python3 TOOLS/AgentKit/agentkit_resolve.py json-check path/to/data.json
    python3 TOOLS/AgentKit/agentkit_resolve.py search path/to/project --pattern TODO
    python3 TOOLS/AgentKit/agentkit_resolve.py find-files path/to/project --pattern config
    python3 TOOLS/AgentKit/agentkit_resolve.py archive-list path/to/archive.zip
    python3 TOOLS/AgentKit/agentkit_resolve.py sha256 path/to/file
    python3 TOOLS/AgentKit/agentkit_resolve.py json-check --json-report

The resolver's JSON inventory mode only detects commands; normal task mode executes a fixed, task-specific argument list for the selected command. Use `--prefer-fallback` to run the Python standard-library equivalent even if an external command exists. Current fallbacks support JSON validation, text search, file-name search, ZIP listing, and SHA-256 hashing. They are not claimed to be fully compatible with jq, ripgrep, fd, unzip, or platform-specific options.

Package installation is **off by default**. `--install` explicitly permits one bounded attempt to install the preferred command even if a less-preferred alternative exists. Only fixed package mappings are accepted. On Termux, the resolver uses `pkg`; elsewhere it supports detected package managers with known mappings. It does not invoke a shell or sudo, does not retry a failed install, and verifies the command appears on PATH afterward. Package-manager behavior and permissions vary by operating system; review the printed command before using this option. A successful installation is not proof that the original task worked; rerun and validate the intended operation.

### 6. Termux-derived tool candidates

See [TERMUX_TOOL_CANDIDATES.md](TERMUX_TOOL_CANDIDATES.md) for the observed Termux command inventory summary and non-duplicating feature proposals. The resolver also supports 7-Zip for archive listing and Termux's `pkg` package manager when running in a detected Termux environment.

### 7. Smartphone test profiles

Build a default smartphone profile matrix and check Android minimum-SDK compatibility:

```sh
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project --profile low-end
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project --android-version 11 --json /tmp/mobile-test-plan.json
```

When `--profile` is omitted, all profiles are assigned automatically: low-end 4 GB / Android 11 (API 30), mid-end 8 GB / Android 15 (API 35), mid-high 12 GB / no default Android target, and high-end 16 GB / no default Android target. A known minSdk higher than the selected target API rejects that profile; an unknown minSdk blocks version-gated checks for review. See [MOBILE_TESTING.md](MOBILE_TESTING.md) for details.

This is a static compatibility preflight and test-plan generator only. It does not launch an emulator, install an APK, or measure real-device performance.


## Capability tool inventory

Run a discovery-only report (does not execute discovered tools):

```sh
python3 TOOLS/AgentKit/agentkit_capabilities.py
python3 TOOLS/AgentKit/agentkit_capabilities.py --format json --output /tmp/agent-capabilities.json
```

Optional bounded version probes use fixed `--version` arguments only for allowlisted tools already found on PATH. They never invoke `npx` or install packages:

```sh
python3 TOOLS/AgentKit/agentkit_capabilities.py --probe-versions
python3 TOOLS/AgentKit/agentkit_capabilities.py --probe-versions --timeout 1.5 --format json
```

Discovery does not prove a tool works or that browser binaries/MCP configuration exist. Review the report and run a task-specific smoke test before relying on any tool.

## Researched agent capability tools

See [AGENT_CAPABILITY_TOOLS.md](AGENT_CAPABILITY_TOOLS.md) for the sourced priority list and planned integration of Playwright, sandboxed execution, deterministic evaluations, independent review, and MCP security checks. Research/design is recorded; runtime integrations are not yet claimed installed or tested.
