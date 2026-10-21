# AgentKit — editing / handoff

Current status: new MCP discovery, Ruff fallback and route-selector implementation is being validated on branch `work/executor-plus-long-work-mode`. Prior mobile-profile work remains on branch `work/agentkit-mobile-profiles`; PR #13 and its device-runtime validation are separate.

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


## AK-ROUTE-MCP-001 — Ruff fallback, automatic route selection and MCP detection

- **Status:** source and initial tests added; CI/runtime verification pending.
- **Actor:** AI.
- **Work mode:** online (official Ruff docs and GitHub source reviewed; GitHub connector used for repository reads/writes).
- **Scope:** implement an honest, reduced Python lint fallback; select direct commands or AgentKit fallback routes; inspect known local MCP config paths without exposing secrets.
- **Files:** `TOOLS/AgentKit/agentkit_ruff.py`, `TOOLS/AgentKit/agentkit_mcp.py`, `TOOLS/AgentKit/agentkit_routes.py`, corresponding tests, README/AI_USAGE, plan/task/cache and workflow.
- **Ruff source reference:** https://github.com/astral-sh/ruff and https://github.com/astral-sh/ruff/blob/main/docs/configuration.md. Fallback currently covers syntax/parse errors (E999) and conservative unused-import checks (F401) only; formatting is explicitly unsupported without official Ruff.
- **MCP boundary:** detector inspects known local config paths and explicit config files only. It redacts server argument values, environment values and URL paths/query strings. It cannot observe GPT-hosted MCP connections.
- **Out of scope:** Playwright/browser automation and local LLM setup/serving are not AgentKit deliverables.
- **Next action:** run focused tests and full CI; fix failures before marking tasks complete. Then inspect the CI result and distinguish local config discovery from actual server connectivity.
