# AI Agent Usage Contract

Before implementing a substitute tool:

1. Run python3 TOOLS/AgentKit/agentkit.py probe --root <explicit-root> --json <report.json>.
2. Run python3 TOOLS/AgentKit/agentkit_ext.py commands --output /tmp/path-command-inventory.md to enumerate executables actually found in PATH.
3. Inspect command inventory and format capability hints before writing or downloading anything.
4. If a suitable tool exists, inspect its help/version and run a bounded smoke test.
5. Distinguish execution of a format from static inspection.
6. Only if no adequate tool exists, inspect public source projects and verify license/provenance before copying.
7. Run fetch-probe once before repository retrieval. On the first error/timeout, record it and continue with independent tasks; do not retry automatically.
8. Use locate for specific line ranges instead of dumping whole files.
9. Use note for concise handoff facts. ingest reads only explicitly supplied files/stdin and cannot access chat history by itself.
10. Use timer for wall-clock waits; record local and UTC planned end times.
11. Use compile-ts when the project contains TypeScript and a suitable tsc is available. Never auto-install packages through this helper.
12. For a Minecraft .mcaddon/.mcpack, run audit-addon before claiming static validation. Use an in-world test when runtime behavior matters.
13. Before finishing a work set, append a change-ledger record with explicit actor and mode. PR CI rejects missing/invalid provenance.
14. Report FACT / INTERPRETATION / DECISION / UNKNOWN separately. Never claim installation or testing without evidence.

## Online / offline mode

Use online if network access, a remote service/API or a connector was used; offline only if the work stayed local; mixed if both were used. Do not infer mode from tool name alone.

## Syscall tracing fallback

If strace is absent, check perf trace, ltrace, gdb and environment restrictions first. Only then consider a limited prototype such as strace-lite with compatibility warnings and disposable-process tests. /proc polling is not equivalent to strace.

## Error policy

A failure in one independent check should be recorded and independent checks should continue. Repository retrieval is an exception: the first error or timeout ends that retrieval attempt.

## Transcript access boundary

A script running in Linux cannot assume it can read ChatGPT history, connector memory or private app internals. Use ingest only with a transcript/log explicitly supplied by the user or an authorized integration.

## Existing tools reviewed before adding substitutes

- has: https://github.com/kdabir/has — lightweight PATH command/version presence checks. Use it if installed; AgentKit adds format hints, local pagination, provenance and archive checks.
- isetup: https://github.com/host452b/isetup — broader environment/package-manager detection and installation. Prefer its detection features where available; do not run installation commands unless explicitly intended.
- ctx-forge: https://github.com/sylvester-francis/ctx-forge — AI context assembly and code-range workflows. Evaluate it for context selection instead of duplicating its capabilities.

These are reference candidates, not vendored dependencies. Check the current repository license, release/version and target-environment compatibility before adoption or copying.
