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


## Python-first workflow tools (`agentkit_work.py`)

These tools are additive; they do not replace the core probe, command resolver, TypeScript compiler, provenance recorder, add-on audit, or mobile preflight.

```sh
python3 TOOLS/AgentKit/agentkit_work.py --help
python3 TOOLS/AgentKit/agentkit_work.py repo-check --root . --json
python3 TOOLS/AgentKit/agentkit_work.py lint-python --root . --json
python3 TOOLS/AgentKit/agentkit_work.py audit-shell --root . --dialect sh --json
python3 TOOLS/AgentKit/agentkit_work.py sqlite-inspect path/to/data.db --row-counts --integrity-check --json
python3 TOOLS/AgentKit/agentkit_work.py artifact-inspect path/to/file --json
python3 TOOLS/AgentKit/agentkit_work.py context --root . --target TOOLS/AgentKit/agentkit_work.py --start 1 --end 80 --json
python3 TOOLS/AgentKit/agentkit_work.py context --root . --target TOOLS/AgentKit --pattern "def context_inspect" --max-lines 20 --json
```

- `repo-check` invokes Git itself for status, staged/unstaged whitespace checks and summaries. If Git or a Git worktree is absent, it fails explicitly; it does not simulate Git.
- `lint-python` uses `ruff check` when available; otherwise it uses Python's built-in `compile()` without writing bytecode and labels the result **syntax-only**, not lint-equivalent.
- `audit-shell` uses ShellCheck when available; otherwise it uses the explicitly selected `sh -n` or `bash -n` syntax checker. It never claims parity with ShellCheck.
- `sqlite-inspect` uses Python's standard-library SQLite binding in read-only mode; arbitrary SQL is not accepted. Row counts and integrity checks are opt-in.
- `artifact-inspect` computes SHA-256 and checks a small magic-byte allowlist within a byte budget; when the official `file` utility is available, it also records that utility's description. The Python magic list is only a fallback hint, not a full replacement for `file`. It never executes files; unknown file types remain unknown.
- `context` reads bounded line ranges or matching lines and emits machine-readable JSON when requested. It excludes dependency/build directories, rejects root escapes and skips symlinks during recursive scans. Default limits are 250 output lines and 1 MB of scanned file content.

All external commands use argument arrays (no shell expansion), bounded timeouts, and bounded report excerpts. A fallback only provides the explicitly named subset; it is not a general reimplementation of the upstream command. Run the test suite with `python3 -m unittest discover -s TOOLS/AgentKit/tests -v`.

## Keep verification running during edits

`agentkit_watch.py` reruns an explicit verification command when watched files change. Run it in a separate terminal while editing:

```sh
python3 TOOLS/AgentKit/agentkit_watch.py --root . --watch TOOLS/AgentKit --max-runs 25 -- python3 -m unittest discover -s TOOLS/AgentKit/tests -v
```

The watcher performs one initial run unless `--no-initial-run` is supplied, then polls file content hashes and reruns after a quiet/debounce period. It uses an argument vector without shell evaluation, bounds polling interval, command timeout, number of runs, watched file count, total scanned bytes, and captured output. Default limit is 25 runs. Stop it with Ctrl-C. Its exit status reflects the verification runs and scan warnings; a clean watcher exit does not prove runtime behavior beyond the supplied command.

## Upstream behavior references

The wrappers intentionally invoke the upstream command rather than reimplementing its full behavior. Recheck these references when changing arguments or fallback claims:

- [Git `status`](https://git-scm.com/docs/git-status) and [Git `diff`](https://git-scm.com/docs/git-diff): repository state, staged/unstaged differences, whitespace checks and stable porcelain output.
- [Ruff `check`](https://docs.astral.sh/ruff/configuration/): actual linting behavior and supported output formats. The Python `compile()` fallback only checks syntax.
- [ShellCheck](https://github.com/koalaman/shellcheck): shell static analysis. `sh -n`/`bash -n` only check syntax.
- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html) and [SQLite URI filenames](https://www.sqlite.org/uri.html): read-only `mode=ro` behavior.
- [`file(1)` manual](https://man7.org/linux/man-pages/man1/file.1.html): upstream file-type description. The Python magic-byte allowlist is deliberately incomplete.
