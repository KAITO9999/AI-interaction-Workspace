# AI Agent Usage Contract

Before implementing a substitute tool:

1. Run: python3 TOOLS/AgentKit/agentkit.py probe --root <explicit-root> --json <report.json>
2. Inspect commands_found and format_capabilities before writing/downloading anything.
3. If a tool exists, inspect its help/version and run a bounded smoke test.
4. Distinguish execution of a format from static inspection.
5. Only if no adequate tool exists, inspect public source projects and verify license/provenance before copying.
6. Run fetch-probe once before repository retrieval. On first error/timeout, record it and continue with independent tasks; do not retry automatically.
7. Use locate for specific line ranges instead of dumping whole files.
8. Use note for concise handoff facts. ingest reads only explicitly supplied files/stdin; it cannot access chat history by itself.
9. Use timer for wall-clock waits; record local and UTC planned end times.
10. Report FACT / INTERPRETATION / UNKNOWN separately. Never claim installation/testing without evidence.

## Syscall tracing fallback

If strace is absent, check perf trace, ltrace, gdb, and environment restrictions first. Only then consider a limited prototype such as strace-lite with compatibility warnings and disposable-process tests. /proc polling is not equivalent to strace.

## Error policy

A failure in one check should be recorded and independent checks should continue. Repository retrieval is an exception: the first error or timeout ends that retrieval attempt.

## Transcript access boundary

A script running in Linux cannot assume it can read ChatGPT message history, connector memory, or private app internals. Use ingest only with a transcript/log explicitly supplied by the user or an authorized integration.


## Existing tools reviewed before adding substitutes

- has: https://github.com/kdabir/has — lightweight PATH command/version presence checks. Use it if already installed; AgentKit adds format hints, file pagination, local notes, line-range viewing, timer, and explicit transcript ingestion.
- isetup: https://github.com/host452b/isetup — broader environment/package-manager detection and installation. Prefer its detection features where available; do not run installation commands unless explicitly intended.
- ctx-forge: https://github.com/sylvester-francis/ctx-forge — AI context assembly and code-range workflows. Evaluate it for context selection instead of duplicating its capabilities.

These are reference candidates, not vendored dependencies. Check the current repository license, release/version, and target-environment compatibility before adoption or copying.
