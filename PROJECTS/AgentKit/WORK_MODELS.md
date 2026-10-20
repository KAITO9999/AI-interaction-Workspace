# AgentKit — work models

Canonical plan: [PLAN.md](PLAN.md). Verified decisions and completed work: [CACHE.md](CACHE.md). Current handoff: [IN_PROGRESS.md](IN_PROGRESS.md).

## Model A — Repository-backed implementation

Use for CLI behavior, audits, fallbacks, packaging, tests and CI.

1. Re-read the canonical workflow, workspace state and global tasks.
2. Inspect current main, relevant open PRs, target files, existing tests and change-ledger rules.
3. Move the selected plan item into [IN_PROGRESS.md](IN_PROGRESS.md) before implementation.
4. Write a regression test first; confirm it fails for the reported gap.
5. Implement the smallest change, run focused tests, then the full AgentKit suite and applicable compile/shell/link/provenance checks.
6. Update README/AI_USAGE only where behavior or limits changed; do not overstate compatibility.
7. Record changed paths in the append-only change ledger, open a focused PR, and verify the actual CI result.
8. On completion, move the item from PLAN to CACHE with date, evidence and limits.

**Completion boundary:** static checks, CI and runtime validation are separate. A passing test suite does not prove behavior on Termux, Android, Minecraft or another target runtime unless it was tested there.

## Model B — Target-environment validation

Use for Termux/Linux execution, compiler integration, Android API/GPU assumptions and Minecraft add-ons.

1. Identify the exact target OS/runtime/version/device and what access is actually available.
2. Prefer a real target environment; otherwise label a stub/simulation as such.
3. Record exact commands, exit status, relevant output and limitations without credentials or private machine details.
4. Separate command discovery from command execution, and static inspection from runtime evidence.
5. Do not install, elevate privileges, bypass agent/OS policy or repeat a command with side effects after an ambiguous failure.
6. Record a test as passed only after observing the result.

## Model C — Capability boundary and fallback review

Use when a preferred utility is missing or restricted.

1. Inventory existing tools without executing unknown candidates.
2. Describe the intended operation and required semantics.
3. Compare candidate and fallback behavior, exit codes, data handling, limits and failure modes.
4. Keep fallbacks explicit and bounded; do not silently replace an existing command or claim full compatibility.
5. Record blocked/unavailable routes as structured failures, not as success.

## Model D — MCP/data bridge and staged edits

Use for MCP payload preparation, large-data extraction, file/media transfer, and multi-slot virtual edits.

1. Separate local extraction/relay from actual connector/server integration.
2. Preserve original files and binary media; record MIME type, size and hash where applicable.
3. Extract only requested ranges/fields to avoid flooding model context.
4. Stage proposed edits in isolated slots; do not alter source until explicit apply.
5. Detect conflicting paths, stale source hashes and operations that cannot safely run concurrently.
6. Test each direction independently before claiming bidirectional support.

## Shared priority rules

- **P0:** correctness, safety boundaries, CI/merge blockers.
- **P1:** explicit requested functionality and false-positive/false-negative defects.
- **P2:** language/platform breadth, integrations and target-environment verification.
- **P3:** performance tuning or convenience work without demonstrated impact.

Priorities are ordering, not calendar promises. Re-evaluate after each stage using test evidence and dependency status.
