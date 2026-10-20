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
