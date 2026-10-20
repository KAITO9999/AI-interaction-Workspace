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

The resolver's JSON inventory mode only detects commands; normal task mode executes a fixed, task-specific argument list for the selected command. Use `--prefer-fallback` to run the Python standard-library equivalent even if an external command exists. Current fallbacks support JSON validation, text search, file-name search, ZIP listing, and SHA-256 hashing. They are not claimed to be fully compatible with jq, ripgrep, fd, unzip, or platform-specific options. The `json-check` fallback specifically matches `jq empty` stream semantics for exit codes: valid or empty/whitespace-only input returns 0, malformed JSON returns 5, and file read errors return 2. It accepts multiple whitespace-separated JSON texts like jq; it does not implement jq filters or guarantee identical error wording.

Package installation is **off by default**. `--install` explicitly permits one bounded attempt to install the preferred command even if a less-preferred alternative exists. Only fixed package mappings are accepted. On Termux, the resolver uses `pkg`; elsewhere it supports detected package managers with known mappings. It does not invoke a shell or sudo, does not retry a failed install, and verifies the command appears on PATH afterward. Package-manager behavior and permissions vary by operating system; review the printed command before using this option. A successful installation is not proof that the original task worked; rerun and validate the intended operation.

### 6. Termux-derived tool candidates

See [TERMUX_TOOL_CANDIDATES.md](TERMUX_TOOL_CANDIDATES.md) for the observed Termux command inventory summary and non-duplicating feature proposals. The resolver also supports 7-Zip for archive listing and Termux's `pkg` package manager when running in a detected Termux environment.
