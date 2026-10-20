# AgentKit — plan

## P1 — Verify smartphone profiles on an Android test environment

- **Outcome:** validate profile gating against an actual Android emulator or physical device, separately from static preflight.
- **Prerequisite:** a representative Android project/APK, emulator or authorized device, and a repeatable test procedure.
- **Checks:** run low-end (4 GB / Android 11) and mid-end (8 GB / Android 15) cases where available; confirm rejection/skip behavior and record device OS, memory limits, logs and results.
- **Complete when:** runtime results are reproducible and static preflight results remain clearly separated from runtime evidence.
- **Current state:** not run; the current feature is a static test-plan/preflight only.

## P2 — Validate memory-budget realism with representative devices

- **Outcome:** decide whether additional CPU/GPU/core/thermal constraints are justified.
- **Prerequisite:** measured data from named device classes or a user-approved hardware matrix.
- **Complete when:** every added parameter has a source or measurement and an explicit rationale; do not invent values to fill gaps.
- **Current state:** RAM budgets are set to 4/8/12/16 GB; no other hardware parameters were found in the current AgentKit source to tune.


## P3 — Agent capability toolchain (research-backed)

- **Outcome:** AgentKit can discover, safely enable, and verify tools that materially improve practical task completion.
- **Priority:** (1) Playwright CLI/MCP/Test for browser interaction and UI regression; (2) workspace-scoped shell/filesystem/patch adapters; (3) deterministic evaluation and regression-test evidence; (4) separately named reviewer-agent integration; (5) MCP tool-surface/security audit.
- **Research record:** see [AGENT_CAPABILITY_TOOLS.md](../../TOOLS/AgentKit/AGENT_CAPABILITY_TOOLS.md) for source URLs, integration rules and acceptance criteria.
- **Implementation sequence:** discover installed tools without executing unknown binaries; record exact observed versions and confidence; run bounded help/version/smoke checks; implement only adapters supported by evidence; emit structured evidence packets; add recovery and adversarial tests.
- **Safety:** no automatic package installs, unrestricted shell, hidden credential collection, or broad browser permissions. Require explicit workspace roots, timeouts, output caps, least privilege and approval for consequential external actions.
- **Complete when:** availability probes, safe adapters, result schema, unit tests, integration tests and security/fault-injection tests pass in a named environment. A plan or static check is not runtime proof.
- **Current state:** sourced research/design recorded. A standard-library capability inventory and bounded version-probe CLI have been implemented; CI passed on commit `0f80d46d921dbf1023eb11dbe9a705e56c94708e`. Browser execution adapters and target-device/runtime integration are not yet implemented or verified.
