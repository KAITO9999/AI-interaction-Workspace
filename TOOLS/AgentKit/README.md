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
    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project --skip-file tests/test_integration.py
    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project --skip-test-id package.tests.test_core.CoreTests.test_edge_case
    python3 TOOLS/AgentKit/agentkit_testfast.py --root path/to/project

The runner probes host metadata before estimating: OS, architecture, Python version, CPU count, available memory metadata, and Minecraft add-on/package/manifest signals. Runtime estimates are produced only from prior successful/recorded runs with matching environment and identical test selection; without calibration data it explicitly says the estimate is unavailable. Estimates use the median of matching history, with confidence based on sample count. Minecraft-like projects always downgrade estimates and print a warning because game engine/version, script APIs, target device, and in-game state may not match the host environment. Inspect the actual target environment before trusting timing estimates.

Quick mode selects tests whose IDs contain `smoke`, `fast`, `sanity`, or `critical`. Explicit exclusions use exact file paths (`--skip-file tests/test_integration.py`) or exact unittest IDs (`--skip-test-id package.tests.test_core.CoreTests.test_edge_case`), not substring matching. File exclusions apply to tests defined in that file; a typo or unknown test ID is an error. Every skipped test is written to `.agentkit-logs/test-skips.jsonl`; measured run durations are written to `.agentkit-logs/test-runtime.jsonl`. A zero-test selection is an error, not success. Quick/skip runs are partial verification and must not replace a full test run before release or merge.

The test runner's environment metadata and measured history are operational diagnostics only; they are not the new source-code workload prediction model. The JS workload analyzer below deliberately does not inspect the host.


### 12. JavaScript workload and API-load analysis (explicit target profile)

    python3 TOOLS/AgentKit/agentkit_js_load.py --root path/to/project --profile low --workload-template workload-template.json
    python3 TOOLS/AgentKit/agentkit_js_load.py --root path/to/project --profile mid --clock-ghz 3.2 --cores 8 --memory-gb 8
    python3 TOOLS/AgentKit/agentkit_js_load.py --root path/to/project --file src/main.js --profile high-end --json js-load.json
    python3 TOOLS/AgentKit/agentkit_js_load.py --root path/to/project --profile mid --workload-json workload.json --calibration-json calibration.json

The profile is supplied by the user: low, mid, mid-high, or high-end. Optional clock/core/memory figures are assumptions supplied on the command line. This tool never reads the host's CPU, RAM, OS, or clock to infer a target device. The source-linked workload template lists detected API call sites and loop sites, but leaves call counts and concurrency null on purpose. Fill those values from a defined scenario or measured execution; the tool will not assume that one source call equals one runtime call.

The initial analyzer flags likely API-heavy call sites, timer/frame callbacks, collection operations, allocations, calls inside approximate loop bodies, possible nested loops, and functions with no direct textual references. Findings include confidence and review guidance. A missing direct reference is **not** proof of dead code: exports, cross-file imports, callbacks, reflection, framework registration, and dynamic calls can all make code reachable.

**Absolute time is calculated only from an explicit workload scenario and measured calibration.** Static syntax alone cannot establish runtime input sizes, iteration counts, engine/JIT behavior, API latency, cache/network state, or concurrent overlap. Without both files below, the estimate remains unavailable; clock GHz alone is not converted into JavaScript throughput.

Workload file (the counts must come from a documented scenario or measured execution, not guesses hidden in the tool):

```json
{
  "schema_version": 1,
  "scenario": "one complete update tick for 1000 entities",
  "assumptions": ["CPU and memory counts describe one tick", "API count is the number of calls in one tick"],
  "operations": [
    {"kind": "cpu_ops", "count": 1000000},
    {"kind": "memory_bytes", "count": 1048576},
    {"kind": "api", "name": "fetch", "count": 4, "concurrency": 1}
  ]
}
```

Calibration file example (rates and latency ranges must be measured on the selected target runtime/profile; the values here are illustrative only and must not be copied as authoritative benchmarks. Include measurement method and source URLs; the tool checks that evidence is recorded but does not verify its contents):

```json
{
  "schema_version": 1,
  "target_runtime": "name and version of the measured JS runtime",
  "evidence": {
    "measurement_method": "benchmark harness, input shape, and warm/cold-run policy",
    "source_urls": ["https://v8.dev/blog/real-world-performance"]
  },
  "profiles": {
    "mid": {
      "samples": 10,
      "cpu_ops_per_second": [1000000, 2000000],
      "memory_bytes_per_second": [10000000, 20000000],
      "api_latency_ms": {"fetch": [20, 250]},
      "reference_clock_ghz": 3.0,
      "allow_linear_clock_scaling": false,
      "reference_memory_bandwidth_gbps": 10,
      "allow_linear_memory_bandwidth_scaling": false
    }
  }
}
```

The estimator sums the calibrated CPU, memory-transfer, and API components. API count is divided into batches using the explicit concurrency value. The total is a serial-component estimate; it does not model arbitrary overlap between CPU work and network waits. Optional clock and memory-bandwidth scaling is applied only when the calibration explicitly sets the corresponding allow_linear_* flag and provides reference specifications. Core count is recorded but is not multiplied into main-thread JavaScript throughput. A working_set_bytes operation is checked against --memory-gb when supplied; exceeding the specified total memory makes the estimate unavailable. The confidence label reflects the number of calibration samples supplied, not independent verification of their quality. Static source findings and workload JSON are separate evidence: the analyzer does not silently infer loop counts, input sizes, or function invocation counts from source text. Each finding and the run summary are appended to .agentkit-logs/js-load-analysis.jsonl; the JSON report stores hashes of the workload and calibration input files for traceability.

For design rationale, see the V8 team's [real-world performance methodology](https://v8.dev/blog/real-world-performance), [JavaScript execution costs](https://v8.dev/blog/cost-of-javascript-2019), and [benchmark limitations](https://v8.dev/blog/retiring-octane). Those sources emphasize representative workload measurement and show why a single synthetic benchmark or clock rate is not a universal runtime predictor. For browser targets, Chrome documents 50 ms as the Long Tasks threshold and recommends breaking up work that blocks the main thread ([Long Animation Frames / Long Tasks](https://developer.chrome.com/docs/web-platform/long-animation-frames)). AgentKit only uses that threshold as a conditional warning when the selected calibration identifies a browser-like runtime. The follow-on estimator should accumulate bounded operation counts and API-specific cost ranges, with each coefficient traceable to a target-runtime benchmark or published evidence.
