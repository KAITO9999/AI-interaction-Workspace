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

### 5. Review source-code risks

    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project
    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project --file src/main.py --json /tmp/code-audit.json
    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project --fail-on medium

The read-only audit reports risk category, priority, location, rationale, and a review suggestion. It checks common patterns such as dynamic eval/exec, shell-enabled subprocess calls, bare exception handlers, unusually long Python functions, suspicious local Python call arity, comment-heavy files, and generic deferred-work markers. A comment ratio is a review signal, not a recommendation to delete comments: preserve meaningful design rationale and public API documentation.

The tool recognizes source/config extensions across many ecosystems, but this does **not** mean full semantic support for every language. Python gets AST-based checks; other languages currently receive generic text heuristics. For stronger language-specific results, use installed tools such as Ruff/Pylint/Mypy, ESLint/tsc, ShellCheck, or language-specific compilers. AgentKit does not silently install or replace them. Findings are heuristic, can be false positives, and are not proof of a defect.

### 6. Sequential ZIP extraction, tagging, and cleanup

    python3 TOOLS/AgentKit/agentkit_zipset.py extract path/to/archive.zip --output /tmp/agentkit-expanded --tag task-123
    python3 TOOLS/AgentKit/agentkit_zipset.py extract path/to/archive-folder --output /tmp/agentkit-expanded --tag review
    python3 TOOLS/AgentKit/agentkit_zipset.py extract path/to/archive-folder --output /tmp/agentkit-expanded --recursive
    python3 TOOLS/AgentKit/agentkit_zipset.py list --output /tmp/agentkit-expanded --tag task-123
    python3 TOOLS/AgentKit/agentkit_zipset.py delete --output /tmp/agentkit-expanded --older-than-days 14
    python3 TOOLS/AgentKit/agentkit_zipset.py delete --output /tmp/agentkit-expanded --id RECORD_ID --yes
    python3 TOOLS/AgentKit/agentkit_zipset.py delete --output /tmp/agentkit-expanded --all --yes

Directory mode extracts ZIP files in sorted order, one at a time. Each archive gets its own directory named like `archive-name（zip）`, and the ZIP's internal folder structure is preserved. A manifest stores record ID, source archive, output directory, timestamp, and tags. Listing can filter by tag; deletion can target a single ID, old records, or all managed records. Deletion is a dry run unless `--yes` is explicitly supplied. Only directories recorded in the manifest and contained within the selected output root can be deleted.

The extractor rejects path traversal and symbolic-link entries, limits member count and total uncompressed size, and avoids overwriting existing extraction directories. Use a separate output directory to make generated content easy to move or review. ZIP only; this is not a general extractor for every archive format.

### 7. Suggest commands and fallback routes

    python3 TOOLS/AgentKit/agentkit_toolplan.py search
    python3 TOOLS/AgentKit/agentkit_toolplan.py code-audit --json
    python3 TOOLS/AgentKit/agentkit_toolplan.py zip-batch --paths-only

This planner lists candidate commands and their actual PATH locations without executing them. It suggests fallbacks and explains scope limitations. It does not install packages, run candidate binaries, or replace existing commands.

## Security and limitations

- No privilege escalation, restriction bypass or credential discovery. Package installation is opt-in only through the resolver's explicit `--install` flag.
- Discovered PATH executables are never invoked by the command inventory or tool planner.
- fetch-probe performs one read-only git ls-remote attempt and stops on the first error/timeout; it does not clone.
- Standard commands are preferred when available. Python fallbacks are used only when no preferred command is found, unless `--prefer-fallback` is explicitly supplied for deliberate comparison/testing.
- Core shell fallback is deliberately reduced and is not feature-equivalent to Python.
- File and command scans skip common dependency/build directories.
- Local outputs may contain environment paths; inspect them before publication.

## Tests

    python -m unittest discover -s TOOLS/AgentKit/tests -v
    python -m py_compile TOOLS/AgentKit/agentkit.py TOOLS/AgentKit/agentkit_ext.py TOOLS/AgentKit/agentkit_resolve.py TOOLS/AgentKit/agentkit_code_audit.py TOOLS/AgentKit/agentkit_zipset.py TOOLS/AgentKit/agentkit_toolplan.py

### 8. Resolve a missing command or use a Python fallback

    python3 TOOLS/AgentKit/agentkit_resolve.py json-check path/to/data.json
    python3 TOOLS/AgentKit/agentkit_resolve.py search path/to/project --pattern TODO
    python3 TOOLS/AgentKit/agentkit_resolve.py find-files path/to/project --pattern config
    python3 TOOLS/AgentKit/agentkit_resolve.py archive-list path/to/archive.zip
    python3 TOOLS/AgentKit/agentkit_resolve.py sha256 path/to/file
    python3 TOOLS/AgentKit/agentkit_resolve.py json-check --json-report

The resolver's JSON inventory mode only detects commands; normal task mode executes a fixed, task-specific argument list for the selected command. Use `--prefer-fallback` to run the Python standard-library equivalent even if an external command exists. Current fallbacks support JSON validation, text search, file-name search, ZIP listing, and SHA-256 hashing. They are not claimed to be fully compatible with jq, ripgrep, fd, unzip, or platform-specific options.

Package installation is **off by default**. `--install` explicitly permits one bounded attempt to install the preferred command even if a less-preferred alternative exists. Only fixed package mappings are accepted. On Termux, the resolver uses `pkg`; elsewhere it supports detected package managers with known mappings. It does not invoke a shell or sudo, does not retry a failed install, and verifies the command appears on PATH afterward. Package-manager behavior and permissions vary by operating system; review the printed command before using this option. A successful installation is not proof that the original task worked; rerun and validate the intended operation.

### 9. Termux-derived tool candidates

See [TERMUX_TOOL_CANDIDATES.md](TERMUX_TOOL_CANDIDATES.md) for the observed Termux command inventory summary and non-duplicating feature proposals. The resolver also supports 7-Zip for archive listing and Termux's `pkg` package manager when running in a detected Termux environment.


### Source-code audit

    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project --json /tmp/code-audit.json
    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project --fail-on medium

The read-only audit emits category, priority, file/line, rationale, and a suggested review. It checks common patterns including eval/exec, shell-enabled subprocess calls, bare exception handlers, long Python functions, simple local-call arity mismatches, and comment-heavy files. Comment ratio is only a review signal: preserve useful design rationale and API documentation.

It recognizes extensions from many language ecosystems, but Python gets AST-based checks while other languages currently get generic text heuristics. This is not full semantic support for every language. Prefer installed language-specific analyzers (for example Ruff/Pylint/Mypy, ESLint/tsc, or ShellCheck) for deeper analysis. AgentKit does not install or replace them automatically; heuristic findings can be false positives.

### Sequential ZIP extraction and tagged cleanup

    python3 TOOLS/AgentKit/agentkit_zipset.py extract path/to/zip-folder --output /tmp/agentkit-expanded --tag task-123
    python3 TOOLS/AgentKit/agentkit_zipset.py list --output /tmp/agentkit-expanded --tag task-123
    python3 TOOLS/AgentKit/agentkit_zipset.py delete --output /tmp/agentkit-expanded --older-than-days 14
    python3 TOOLS/AgentKit/agentkit_zipset.py delete --output /tmp/agentkit-expanded --all --yes

Directory mode processes ZIPs sequentially in sorted order, one archive at a time. Each archive gets its own `name（zip）` directory, preserving the ZIP's internal folders. A manifest stores IDs, source, output, timestamp, and tags. Delete operations are dry-run unless `--yes` is given, and only manifest-tracked directories contained in the output root may be removed. The extractor rejects traversal/symlink entries, limits archive size, and does not overwrite existing extraction directories.

### Command and fallback planner

    python3 TOOLS/AgentKit/agentkit_toolplan.py search
    python3 TOOLS/AgentKit/agentkit_toolplan.py code-audit --json
    python3 TOOLS/AgentKit/agentkit_toolplan.py zip-batch --paths-only

The planner lists candidate commands and their PATH locations without executing them, plus a fallback and its limitations. It never installs or replaces commands.

Standard commands remain preferred when present. Fallbacks are used only when no preferred command is detected, unless `--prefer-fallback` is explicitly supplied.


### 10. Confidence-ranked code, duplication, and performance audit

    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project --json /tmp/code-audit.json
    python3 TOOLS/AgentKit/agentkit_code_audit.py path/to/project --log-dir .agentkit-logs

Findings now carry `detection_confidence` and `review_recommended`. HIGH confidence means the observed fact is directly established (for example exact file hashes or a parser result); it does not mean that the finding is necessarily a bug. MEDIUM/LOW findings are marked for confirmation. Duplicate files, repeated substantial source lines, and identical normalized Python function bodies are reported as duplication candidates. Repetition is not automatically wrong; common boilerplate, generated code, and intentional compatibility wrappers can be legitimate.

Execution-time and processing-volume observations are integrated into the same audit tool. Two separate append-only logs are produced: `.agentkit-logs/code-audit-findings.jsonl` and `.agentkit-logs/code-audit-performance.jsonl`. The performance log records the actual audit elapsed time, files/bytes/lines scanned, and throughput. It does not claim to predict the runtime of the audited program; static loop/sleep signals are only leads for review.

### 11. Quick test runs and runtime calibration

    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project --list
    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project --quick
    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project --skip integration
    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project

The runner probes host metadata before estimating: OS, architecture, Python version, CPU count, available memory metadata, and Minecraft add-on/package/manifest signals. Runtime estimates are produced only from prior successful/recorded runs with matching environment and identical test selection; without calibration data it explicitly says the estimate is unavailable. Estimates use the median of matching history, with confidence based on sample count. Minecraft-like projects always downgrade estimates and print a warning because game engine/version, script APIs, target device, and in-game state may not match the host environment. Inspect the actual target environment before trusting timing estimates.

Quick mode selects tests whose IDs contain `smoke`, `fast`, `sanity`, or `critical`; explicit `--skip` filters test IDs by substring. Every skipped test is written to `.agentkit-logs/test-skips.jsonl`; run durations and environment fingerprints are written to `.agentkit-logs/test-runtime.jsonl`. A zero-test selection is an error, not success. Quick/skip runs are partial verification and must not replace a full test run before release or merge.

The first run on a new environment has no calibrated estimate by design. Matching OS/Python/CPU metadata still cannot fully account for virtualization, load, power limits, external services, Minecraft runtime behavior, or other environment-specific variables.
