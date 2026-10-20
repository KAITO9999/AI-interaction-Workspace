# AgentKit — implementation plan

Status: roadmap created after comparing the global task list, AgentKit documentation, known project requirements and open pull requests. This plan is dependency-ordered; dates are intentionally not guessed. Move an item to [IN_PROGRESS.md](IN_PROGRESS.md) before starting implementation.

## P0 — Establish the actual baseline and resolve pending changes

### P0.1 — Reconcile open AgentKit pull requests

- **Outcome:** one known baseline for subsequent work; no roadmap item assumes an unmerged branch is already in `main`.
- **Scope:** review [PR #10](https://github.com/KAITO9999/AI-interaction-Workspace/pull/10) (code audit, ZIP workflow, tool planner) and [PR #11](https://github.com/KAITO9999/AI-interaction-Workspace/pull/11) (AI-side Linux execution scope). Inspect current status, diffs, CI and overlapping paths before deciding merge order.
- **Complete when:** each PR is merged, closed, or has a recorded blocker and next action; the roadmap and tests are checked against the actual base branch.
- **Constraint:** do not merge automatically or mark PRs complete based on their existence.

### P0.2 — Close the audit's comment-related false positives

- **Outcome:** commented-out code and examples are not incorrectly reported as active executable risk patterns.
- **Checks:** add regression cases for full-line comments, inline comments, docstrings/documentation examples, strings containing risky tokens, and actual active risky code.
- **Complete when:** tests demonstrate the prior false positive, then pass after the fix; genuine active-code findings remain detectable.
- **Dependency:** reconcile PR #10 before editing overlapping audit code.

## P1 — Finish explicitly requested behavior and test selection

### P1.1 — Select tests by file or exact invocation target

- **Outcome:** users can skip/select tests by test-file path and/or explicit test entry point/invocation, rather than substring matching.
- **Checks:** exact file selection; exact test node/entry point where supported; paths with spaces; unknown targets; duplicate selections; deterministic selection logs; compatibility with existing quick mode.
- **Complete when:** skip decisions are based on structured test identity, not broad substring matches; skipped and selected tests are logged with reasons; existing test suite passes.
- **Note:** do not treat a test function name as a universal invocation ID when the framework cannot identify it. Document framework-specific support and fail clearly on ambiguous targets.

### P1.2 — Validate profile-run reports and workload-estimate boundaries

- **Outcome:** all configured profiles run in one invocation and write distinct reports/logs, while unsupported precision is not implied.
- **Checks:** all-profile mode; independent report paths; missing workload data; malformed templates; repeated run behavior; no shared output collision.
- **Complete when:** automated tests verify report isolation and deterministic schema; estimates without calibration/input are explicitly unknown or low-confidence, not fabricated precise runtimes.

### P1.3 — Improve test/skip transparency

- **Outcome:** users can tell which tests ran, which were skipped, why, and whether a failure is a real failure or an unavailable capability.
- **Checks:** skip-by-file/entry-point, quick mode, no matching tests, invalid selectors, runner interruption, and log-write failure.
- **Complete when:** every selection decision is explainable in logs and invalid requests do not silently turn into a successful empty run.

## P2 — Validate real environments and compiler integrations

### P2.1 — Run a real-environment smoke matrix

- **Targets:** AI-side Linux environment and Termux/Android where access is available; include a second distinct target if possible.
- **Checks:** core probe, PATH inventory, resolver/fallbacks, archive utilities, bounded observer/diagnostics where present, file-write denial handling and exit statuses.
- **Complete when:** each target has dated command evidence and an explicit pass/fail/not-run result. A host inventory is not evidence of Android or Termux behavior.

### P2.2 — Test TypeScript compilation on real project configurations

- **Outcome:** validate `compile-ts` against representative real `tsconfig.json` projects in addition to stub-compiler tests.
- **Checks:** project mode, no-emit mode, project references if in scope, TSX config handling, missing compiler, and compiler errors.
- **Complete when:** at least two representative configurations or one project plus a documented edge-case fixture are tested; unsupported cases are explicit.

### P2.3 — Add exact file/invocation selection to the test runner

- **Outcome:** selection logic is stable across supported test layouts and does not accidentally omit unrelated tests.
- **Complete when:** selection tests cover path normalization and framework limitations; documentation includes examples and a safe default.

## P2 — Expand language and platform audit coverage

### P2.4 — C/C++/Rust analysis adapters

- **Outcome:** add language-aware checks beyond generic text heuristics for C, C++, and Rust.
- **Scope:** prefer compiler/linter output or parser-backed checks when available; otherwise clearly label heuristic-only findings.
- **Complete when:** representative positive and negative fixtures exist, confidence is calibrated, and no compiler-grade semantic-analysis claim is made without such an implementation.

### P2.5 — Kotlin/API/UI interaction analysis

- **Outcome:** reduce false positives and detect common UI-thread/coroutine/lifecycle hazards.
- **Checks:** UI dispatcher usage, blocking calls, lifecycle-aware coroutine scope, repeated UI invalidation, JNI/native boundaries and Compose effects.
- **Complete when:** fixtures cover supported patterns and known limitations; recommendations distinguish candidate signals from proven defects.

### P2.6 — Android, graphics API and architecture requirements

- **Outcome:** make platform policy explicit and validate manifests/build metadata without claiming runtime GPU support.
- **Current policy candidates:** Android API 30 baseline, OpenGL ES 3.0 baseline, Vulkan 1.1 baseline with Vulkan 1.3 as optional higher capability; ARM64, x86-64 and 32-bit x86 identification.
- **Checks:** Android manifest/build metadata, ABI declarations, OpenGL ES declarations, Vulkan version declarations and missing/contradictory metadata.
- **Complete when:** official-source references are recorded, checks have fixtures, and the report says runtime support still depends on device/driver/runtime verification.

### P2.7 — Cross-language risk-audit confidence calibration

- **Outcome:** findings expose severity, confidence and review recommendation consistently across language adapters.
- **Complete when:** regression fixtures cover comments, strings, generated/vendor files, duplicate code and actual risk patterns; lower-than-HIGH confidence explicitly recommends human review.

## P2 — Complete data-transfer and editing workflows

### P2.8 — MCP connector integration (separate from local payload bridge)

- **Outcome:** validate MCP-to-GPT, GPT-to-MCP and MCP-to-GPT-to-MCP flows using an actual authorized connector/server.
- **Current boundary:** local JSON/text extraction, file copy and hashing do not themselves connect to arbitrary MCP servers or guarantee ChatGPT connector access.
- **Checks:** supported connector actions, authorization failures, bounded payloads, binary/image preservation, partial extraction, direction metadata and error handling.
- **Complete when:** each supported direction is exercised end-to-end against a named supported integration; unsupported generic-server cases are stated plainly.

### P2.9 — Ten virtual edit slots and conflict handling

- **Outcome:** inspection/staging remains isolated until explicit apply; conflicting writes are detected.
- **Checks:** ten slot metadata records, same-file conflicts, stale source hash, partial/incomplete edits, explicit apply, rollback/failed write reporting and non-concurrent operations.
- **Complete when:** tests prove source files are unchanged before apply and stale/conflicting edits are rejected with actionable messages.

### P2.10 — Multi-route download and bundle verification

- **Outcome:** users can identify viable download routes and receive a verifiable tool bundle without manual file-by-file copying.
- **Checks:** HTTPS/redirect handling, public-target restrictions, GitHub archive/API route planning, unavailable route reporting, bundle manifest hashes, ZIP integrity and extraction path safety.
- **Complete when:** each route is described according to what it actually tests; a successful URL probe is not presented as proof of authentication, full download or connector permission.

## P3 — Measure before optimizing

### P3.1 — Calibrate workload estimates with repeatable measurements

- **Outcome:** estimate quality is measured against known workload fixtures and observed target results.
- **Complete when:** inputs, hardware/runtime profile, warm-up/repetition policy, error metric and confidence bands are documented; uncalibrated workloads remain explicitly approximate.

### P3.2 — Performance and maintenance review

- **Outcome:** avoid optimizing tools without evidence and keep the tool surface understandable.
- **Checks:** run-time overhead, memory/log growth, dependency count, repeated logic and fallback compatibility.
- **Complete when:** any optimization has before/after evidence and does not weaken safety or error visibility.

## Gap review — items added after comparison

The comparison identified these gaps not sufficiently explicit in the existing global task list and open-PR summaries:

- Regression coverage specifically preventing commented-out code from triggering audit findings.
- Test selection by file/entry-point identity rather than substring-based skipping.
- A dependency gate for open PRs #10 and #11 so roadmap work does not assume their changes are already in `main`.
- Real connector-backed end-to-end tests for the three MCP/GPT directions; local payload extraction is not enough.
- Explicit conflict/stale-hash and pre-apply source-preservation tests for the ten virtual slots.
- Evidence-based report-isolation and calibration criteria for multi-profile workload analysis.
- Explicit distinction between Android/API/graphics manifest checks and actual device/driver runtime support.
- Download-route checks that distinguish public URL reachability from authenticated or full transfer success.

These are tracked here as the canonical AgentKit plan. The global [task list](../../TASKS/tasks.md) should link here rather than duplicating every detail.
