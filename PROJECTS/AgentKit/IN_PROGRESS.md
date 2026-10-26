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
- **Checks run:** final hosted CI run [40137923343](https://github.com/KAITO9999/AI-interaction-Workspace/actions/runs/40137923343) passed Python compilation, POSIX shell syntax, 57 unit tests, change-ledger provenance, and Markdown-link checks on Ubuntu. Earlier failed runs exposed a missing CLI dispatcher and test expectation mismatch; both were fixed and regression-tested. No direct local GPT-container or Termux execution is claimed.
- **Classification:** FACT — files were committed to the feature branch. UNKNOWN — full CI outcome and behavior under target Termux/other virtual Linux environments.
- **Next action:** review draft PR [#15](https://github.com/KAITO9999/AI-interaction-Workspace/pull/15), then smoke-test on Termux and another virtual Linux environment when available; keep environment-specific results separate from hosted CI evidence.


### AK-LINT-001 — Native static-analysis fallback

- Status: core implementation exercised in hosted CI; current output-reporting refinements are under revalidation. PR remains draft.
- Actor: AI; work mode: online.
- Scope: add dependency-free AST checks for Python and limited shell heuristics when Ruff/ShellCheck are absent, integrate them into existing commands, and add tests for rules, false-positive boundaries, path containment, resource limits and timeout behavior.
- Compatibility: official tools remain preferred; fallback is a limited subset and is not equivalent.
- Paths: TOOLS/AgentKit/agentkit_lint.py, TOOLS/AgentKit/tests/test_agentkit_lint.py, TOOLS/AgentKit/tests/test_agentkit_logic.py, TOOLS/AgentKit/agentkit_work.py, .github/workflows/agentkit-tests.yml, TOOLS/AgentKit/README.md, TOOLS/AgentKit/AI_USAGE.md, PROJECTS/AgentKit/IN_PROGRESS.md, LOGS/change-ledger.jsonl.
- Evidence: official Ruff rule documentation and ShellCheck project documentation informed the small rule set. No external source code copied.
- Unknown: Termux and other target virtual-Linux runtime behavior remain unverified.
- Next: keep the PR draft until the latest CI run is green and target-environment smoke tests are possible.


### AK-PROC-001 — Shared process supervision and consistency hardening

- **Scope:** route AgentKit runtime subprocess launches through one bounded runner; distinguish PASS, FAIL, TIMEOUT, UNAVAILABLE and LIMIT; stream user-facing output without unbounded capture; expose progress callbacks; terminate process groups on POSIX timeout; close pipes; cap output and source scans; avoid symlink traversal; and test incomplete-report semantics.
- **Regression coverage:** argv is passed without shell interpolation; timeout versus exit failure; missing executable; bounded capture with live output; progress callbacks; POSIX child-process group cleanup; symlinked explicit and discovered paths; empty target semantics; byte/file/finding/report-output limits; version-probe timeout; resolver, compiler, fetch-probe and watcher timeout propagation.
- **Latest hosted validation:** [GitHub Actions run 40156135136](https://github.com/KAITO9999/AI-interaction-Workspace/actions/runs/40156135136) passed 98 tests plus Python compilation, POSIX shell syntax, change-ledger provenance and Markdown-link checks on Ubuntu. The latest logic pass also covered overall status precedence and output-capture failure handling.
- **Unverified:** Termux and other target virtual-Linux process behavior. POSIX process-group termination is not a sandbox and cannot guarantee cleanup of descendants that deliberately detach into a new session. Keep PR #17 draft until target-environment verification is possible.
