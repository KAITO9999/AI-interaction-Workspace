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
### AK-WORK-001 — Python-first checks and context-bounded inspection

- **Status:** implementation and hosted CI passed; review and target-environment smoke tests remain pending.
- **Actor:** AI
- **Work mode:** online (GitHub connector used for repository inspection and branch edits).
- **Scope:** add separate `agentkit_work.py` commands for Git-native read-only checks, Python lint with explicit syntax-only fallback, shell audit with explicit syntax-only fallback, read-only SQLite inspection, bounded artifact hashing/type hints, and context-limited line/search retrieval. Add `agentkit_watch.py` for bounded verification reruns while source files are being edited.
- **Compatibility rule:** invoke official tools when present; do not claim fallback parity where the fallback implements less. Git behavior is not simulated. Existing AgentKit command variants remain separate.
- **Safety boundaries:** no shell interpolation; explicit subprocess timeouts; read-only SQLite; bounded artifact reads; context output byte/line limits; reject root escapes and skip symlinks in recursive context scans.
- **Paths:** `TOOLS/AgentKit/agentkit_work.py`, `TOOLS/AgentKit/tests/test_agentkit_work.py`, `TOOLS/AgentKit/README.md`, `TOOLS/AgentKit/AI_USAGE.md`, `.github/workflows/agentkit-tests.yml`, `PROJECTS/AgentKit/WORK_MODELS.md`, `PROJECTS/AgentKit/PLAN.md`, `PROJECTS/AgentKit/IN_PROGRESS.md`, `LOGS/change-ledger.jsonl`.
- **Checks run:** first hosted CI run compiled the module and shell scripts, then failed during tests because `main()` was missing from the new CLI; 12 new tests exposed this entrypoint defect (workflow run [40137316256](https://github.com/KAITO9999/AI-interaction-Workspace/actions/runs/40137316256)). Added the missing CLI dispatcher in commit `e50c4957ac8d39b78193ae06493f4e44f1ef88e7`. The rerun result is pending; no local execution is claimed.
- **Classification:** FACT — files were committed to the feature branch. UNKNOWN — full CI outcome and behavior under target Termux/other virtual Linux environments.
- **Next action:** review the consolidated diff, open a PR, and smoke-test on Termux and another virtual Linux environment when available; keep environment-specific results separate from CI evidence.
