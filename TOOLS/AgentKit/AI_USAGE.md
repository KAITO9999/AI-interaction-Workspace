# AI Agent Usage Contract

For every new task and every resumption after context loss, reread [the canonical AI workflow](../../AI_WORKFLOW.md), current workspace state and task list. Use the [prompt routing index](../../PROMPTS/README.md) and [project workflow](../../DOCS/PROJECT_WORKFLOW.md) to choose the smallest relevant instruction set. Do not load unrelated project caches or duplicate procedures.

## Repository retrieval priority

- Prefer downloading the relevant source files through the GitHub connector first, after confirming the repository and ref. Fetch only the files needed for the task.
- If connector retrieval cannot place files into the execution environment, copy and paste the exact required files from the connector output, preserving paths and UTF-8 content.
- For bulk source retrieval or when copy/paste is impractical, try Git retrieval (for example, a bounded `git clone`/`git fetch`) after the connector route. Run `fetch-probe` once before the Git retrieval attempt; stop that route on its first error or timeout and do not automatically retry it. Record which route actually worked.

Before implementing a substitute tool:

1. Run `python3 TOOLS/AgentKit/agentkit.py probe --root <explicit-root> --json <report.json>`.
2. Run `python3 TOOLS/AgentKit/agentkit_ext.py commands --output /tmp/path-command-inventory.md` to enumerate executables found in PATH.
3. Inspect the inventory and format-capability hints before writing or downloading anything.
4. If a suitable tool exists, inspect its help/version and run a bounded smoke test.
5. Distinguish execution of a format from static inspection.
6. Only if no adequate tool exists, inspect public source projects and verify license/provenance before copying.
7. Prefer the GitHub connector for repository source download. If it cannot materialize files, use exact manual copy/paste for a small set of files; for bulk retrieval, run `fetch-probe` once and then try Git. On the first Git error/timeout, record it and stop that route without automatic retry.
8. Use `locate` for specific line ranges instead of dumping whole files.
9. Use `note` for concise handoff facts. `ingest` reads only explicitly supplied files/stdin and cannot access chat history by itself.
10. Use `timer` for wall-clock waits; record local and UTC planned end times.
11. Use `compile-ts` when the project contains TypeScript and a suitable `tsc` is available. Never auto-install packages through this helper.
12. For a Minecraft `.mcaddon`/`.mcpack`, run `audit-addon` before claiming static validation. Use an in-world test when runtime behavior matters.
13. Before finishing a work set, append a change-ledger record with explicit actor and mode. PR CI rejects missing/invalid provenance.
14. For smartphone checks, use `mobile_test.py` to create a profile matrix; treat it as static preflight, not emulator/device runtime testing. Read [MOBILE_TESTING.md](MOBILE_TESTING.md).
15. Report FACT / INTERPRETATION / DECISION / UNKNOWN separately. Never claim installation or testing without evidence.

## Online / offline mode

Use online if network access, a remote service/API or a connector was used; offline only if the work stayed local; mixed if both were used. Do not infer mode from tool name alone. For work that changes repository files, keep the actor and mode in the append-only change ledger.

## Handoff and active work

For project work, record implementation, bug fixes and regression investigations in the project's `IN_PROGRESS.md` before editing. Transfer command results with the exact command, working directory, exit/status, relevant output, evidence path, classification and next action. Follow [the project handoff format](../../DOCS/PROJECT_WORKFLOW.md).

## Syscall tracing fallback

If `strace` is absent, check `perf trace`, `ltrace`, `gdb` and environment restrictions first. Only then consider a limited prototype such as strace-lite with compatibility warnings and disposable-process tests. `/proc` polling is not equivalent to `strace`.

## Error policy

A failure in one independent check should be recorded and independent checks should continue. Repository retrieval is an exception: the first error or timeout ends that retrieval attempt.

## Transcript access boundary

A script running in Linux cannot assume it can read ChatGPT history, connector memory or private app internals. Use `ingest` only with a transcript/log explicitly supplied by the user or an authorized integration.

## Existing tools reviewed before adding substitutes

- has: https://github.com/kdabir/has — lightweight PATH command/version presence checks. Use it if installed; AgentKit adds format hints, local pagination, provenance and archive checks.
- isetup: https://github.com/host452b/isetup — broader environment/package-manager detection and installation. Prefer its detection features where available; do not run installation commands unless explicitly intended.
- ctx-forge: https://github.com/sylvester-francis/ctx-forge — AI context assembly and code-range workflows. Evaluate it for context selection instead of duplicating its capabilities.

These are reference candidates, not vendored dependencies. Check the current repository license, release/version and target-environment compatibility before adoption or copying.
## Tool resolver and installation safety

- The resolver's built-in substitutes are task-specific and are not drop-in CLI compatibility layers.
- Installation is disabled unless `--install` is explicitly supplied; only fixed package mappings and supported package managers are allowed.
- Never add automatic retries, shell interpolation, privilege escalation, or unreviewed arbitrary package names.
- After an install attempt, verify the executable and rerun a bounded task-specific test. Report install success separately from task success.


## Workflow checks and context budget

- Use `python3 TOOLS/AgentKit/agentkit_work.py context --root <root> --target <path> --start <n> --end <n> --json` to retrieve only a line range, or `--pattern <text>` to return matching lines. Keep `--max-lines` and `--max-bytes` bounded; do not dump whole repositories/files when a focused range suffices.
- Use `repo-check` for read-only Git status and staged/unstaged diff checks. If Git is missing or the target is not a worktree, treat that check as unavailable; never approximate Git semantics.
- Use `lint-python` and `audit-shell` before claiming static validation. Record whether Ruff/ShellCheck ran or whether the dependency-free `agentkit_lint.py` fallback ran. The fallback checks a small set of AST/line-based rules and is not equivalent to either upstream linter; never describe it as full lint coverage. Review its findings for false positives and false negatives.
- Use `sqlite-inspect` only with an explicit database path; it opens the DB read-only and does not accept arbitrary SQL.
- Use `artifact-inspect` for bounded magic-byte and SHA-256 reports. A magic-byte guess is not proof of safety or runtime compatibility.
- Treat JSON reports as evidence with explicit limits, not proof beyond the checks named. Keep separate checks running when one unrelated check fails; do not convert unavailable checks into PASS.

- For concurrent editing and verification, run `python3 TOOLS/AgentKit/agentkit_watch.py --root <root> --watch <source-dir> --watch <test-dir> -- python3 -m unittest discover -s <test-dir> -v` in a separate terminal. The watcher uses content hashes, a debounce interval and bounded runs/timeouts; it does not execute a shell command string. Choose explicit watch roots and an explicit test command.


## Native static-analysis fallback and logic tests

- When Ruff is absent, `agentkit_work.py lint-python` uses `agentkit_lint.py` for syntax, unused-import, bare-except and mutable-literal-default checks. When ShellCheck is absent, `audit-shell` combines the selected shell's `-n` syntax check with limited heuristics for common quoting/expansion pitfalls.
- Prefer upstream tools when available. The native fallback is a bounded subset, not a compatibility clone; its report must preserve that distinction.
- For changes to fallback logic, add tests for both detection and non-detection cases (e.g. quoted variables, assignment contexts, `__init__.py` re-exports), then run `python3 -m unittest discover -s TOOLS/AgentKit/tests -v`.
- For resource/path logic, test root escape rejection, symlink boundaries, output/byte budgets, timeout behavior, and read-only guarantees. Hosted CI is not a substitute for Termux or target virtual-Linux smoke tests.


## Shared process supervision and status semantics

AgentKit's workflow tools use one subprocess supervisor instead of maintaining separate timeout and output-capture implementations. It passes argument vectors without shell interpolation, drains each output stream while the child runs, retains only bounded output tails, closes pipes, and separates normal failure from timeout and launch unavailability. POSIX timeouts terminate the command's process group; intentionally detached descendants are not guaranteed to be terminated.

- PASS: the check completed without detected issues.
- FAIL: a check or command reported a problem.
- TIMEOUT: the configured total deadline elapsed.
- UNAVAILABLE: the required executable or a valid automatic target set was not available.
- LIMIT: the scan/input/diagnostic budget prevented a complete report.

Symlinks and dependency/build directories are pruned during automatic discovery. Static analysis is limited to 10,000 files, 5 MB per file and 50 MB aggregate source bytes; fallback findings are capped at 500. Ruff and ShellCheck are executed in batches of at most 100 paths under one total deadline. The watcher snapshot has its own 10,000-file / 100 MB budget. Treat LIMIT as incomplete, never as a clean result.

Hosted evidence: workflow run 40154904648 passed 88 unit tests along with Python compilation, POSIX shell syntax, provenance, and local Markdown-link checks at commit 9e6814ef66678ba90b355beeebd103c437bf7f35. Subsequent output-reporting edits are being revalidated by CI. Termux/device tests are still separate and unverified.
