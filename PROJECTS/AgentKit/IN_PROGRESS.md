# AgentKit — editing / handoff

Current status: implementation is on branch `work/agentkit-mobile-profiles`; GitHub Actions passed; PR #13 is open. Real Android runtime testing remains pending.

## Active work

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


## AK-CAP-RESEARCH-001 — Research-backed agent capability candidates

- **Status:** literature and open-source candidate survey recorded; implementation and target-environment validation pending.
- **Actor:** AI.
- **Work mode:** online (public web research and GitHub connector reads/writes).
- **Scope:** identify research-backed methods associated with practical performance gains, then map them to open-source/self-hosted candidates with near-unlimited local-use options.
- **Canonical artifact:** TOOLS/AgentKit/AGENT_CAPABILITY_TOOLS.md.
- **Main conclusion:** prioritize tool interaction with environment feedback, deterministic verification and task-specific retrieval; use bounded search/repair selectively; do not default to costly multi-agent debate or reflection without external evidence.
- **No-install constraint:** no external packages, model weights or browser runtime were installed by this research pass.
- **Evidence classification:** FACT — linked papers and project pages report the summarized findings/features. INTERPRETATION — integration priorities are synthesized across task categories. UNKNOWN — target machine suitability, local-model capability, runtime availability, security posture and task-level gains.
- **Next action:** extend the inventory to detect local model runtimes and browser/MCP setup without reading secrets; then choose an approved hardware profile and run a fixed baseline/candidate task set.
