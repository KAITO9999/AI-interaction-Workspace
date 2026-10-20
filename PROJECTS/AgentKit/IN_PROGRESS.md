# AgentKit — editing / handoff

Current status: smartphone-profile PR #13 is merged. Follow-up changes are on branch `work/agentkit-mobile-profiles` in PR #14; CI validation for the follow-up is not yet confirmed. Real Android runtime testing remains pending.

## Active work

### AK-CLI-002 — Explicit environment selection and tool help

- **Status:** implementation drafted; CI pending; PR #14 open
- **Actor:** AI
- **Work mode:** online (GitHub connector used to inspect and update the branch)
- **Scope:** add an explicit execution-environment override to the resolver; document that it does not emulate another OS; prevent installs when an explicit environment conflicts with the current runtime; emit a compatibility warning only when a non-preferred external command or Python substitute actually runs; improve per-tool help and regression tests.
- **Paths:** `TOOLS/AgentKit/agentkit.py`, `TOOLS/AgentKit/agentkit_resolve.py`, `TOOLS/AgentKit/mobile_test.py`, `TOOLS/AgentKit/README.md`, `TOOLS/AgentKit/AI_USAGE.md`, and relevant tests.
- **Checks run:** pending GitHub Actions after the latest branch updates.
- **Classification:** FACT — implementation changes are on the feature branch. UNKNOWN — final CI status until the latest run completes.
- **Next action:** inspect the latest workflow run, fix any failures, then update the task and cache records.

### AK-MOBILE-001 — Smartphone profile and Android compatibility preflight

- **Status:** implementation drafted; CI passed; PR open
- **Actor:** AI
- **Work mode:** online (GitHub connector used to retrieve repository source and write the feature branch)
- **Scope:** add smartphone memory profiles and Android minSdk compatibility gating; document repository retrieval fallback guidance.
- **Profile matrix:** low-end 4 GB / Android 11 API 30; mid-end 8 GB / Android 15 API 35; mid-high 12 GB / no default Android target; high-end 16 GB / no default Android target.
- **Safety behavior:** known incompatible minSdk is rejected; unknown minSdk blocks version-gated profile checks; explicit `--android-version` and `--min-sdk` overrides are available.
- **Paths:** `TOOLS/AgentKit/mobile_test.py`, `TOOLS/AgentKit/tests/test_mobile_test.py`, `TOOLS/AgentKit/MOBILE_TESTING.md`, AgentKit instructions/README, task/state/project records and change ledger.
- **Checks run:** source files and relevant tests/docs were fetched through the GitHub connector before testing. GitHub Actions Ubuntu runner: Python compilation PASS; POSIX shell syntax PASS; 39 unit tests PASS; change-ledger provenance PASS; 115 repository-local Markdown links PASS. Run: https://github.com/KAITO9999/AI-interaction-Workspace/actions/runs/39477402139. The GPT sandbox's local filesystem did not contain a checkout, so this evidence is from the hosted Linux runner, not a direct run inside the GPT container.
- **Evidence:** branch `work/agentkit-mobile-profiles`; base commit `3b0438ecfc5bbd05ef3c081b8fe7980bf524f0d8`.
- **Classification:** FACT — branch implementation is CI-green. UNKNOWN — actual Android device/emulator behavior and measured resource/performance values.
- **Next action:** review PR #13. After merge, run a representative Android app on an emulator/physical device and record actual OS/API, memory budget, logs, and observed behavior.
