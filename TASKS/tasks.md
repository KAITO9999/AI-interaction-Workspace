# Tasks

## Executor++

- [ ] Validate host capabilities for asynchronous connector execution, connector lifecycle control, and accessible input/output logs; document supported and fallback paths.
- [ ] Implement app-side durable request queue: show “キューに追加しました”, let the current task finish to a safe checkpoint, then ask the user to review/confirm before execution; support edit/reorder/cancel/dependencies.
- [ ] Implement both supported native/in-host GPT integration and official API access as separate adapters, including distinct permissions, context handling, cost limits and audit logs.
- [ ] Research long-horizon agent reliability, checklist/checkpoint design, project planning, and effective coding/review workflows; add sourced help.
- [ ] Implement the long-work checklist lifecycle with mandatory initial, intermediate, and final checks.
- [ ] Implement conversation-isolated durable MCP workspaces, artifacts, event logs, dependencies, and resume checkpoints.
- [ ] Implement an AI handoff bundle (goal/acceptance criteria, status/next action, decisions, paths and versions, command/test evidence, blockers/risks, dependency graph and recovery steps) plus redacted context export/import.
- [ ] Add change provenance, bounded retry/idempotency, destructive-action checkpoints, and an acceptance-evidence packet.
- [ ] Add reproducible failure bundles and per-tool permission/side-effect policies enforced by the execution layer.
- [ ] Add re-observation/reconciliation after interruptions; do not blindly replay uncertain tool actions.
- [ ] Add action receipts/effect ledger, evidence-linked claims, and recoverable context-compaction checkpoints.
- [ ] Run prompt-injection tests against untrusted web pages/files/tool outputs and validate allowlists, least privilege, and confirmation gates.
- [ ] Add fault-injection tests for crashes, network loss, timeouts after side effects, duplicate events, revoked auth, and corrupted checkpoints.
- [ ] Implement staged termination guard: first refusal with remaining items; second request prompts a handoff plan; subsequent request recommends dependency/omission review, without trapping the user indefinitely.
- [ ] Implement app-visible progress states, workspace inspection, notifications, and user-confirmation queue.
- [ ] Evaluate Android battery-optimization exemption flow and document OS/background execution limitations.
- [ ] Evaluate storage adapters, app authentication (Auth0 candidate), and MCP authentication separately.
- [ ] Design and validate the Executor++ icon; run static, integration, security-isolation, and Android runtime checks.

- [ ] Record the exact model/provider identity for each substantive contribution whenever available; mark unknown rather than infer it.
- [ ] Create a separate, extensible model-characteristics catalog for GPT-6, Sonnet 5, Grok 4.5 and future additions; mark unverified entries until authoritative evidence is found.
- [ ] Require source URLs and source dates for every factual model claim, including capabilities, limits, benchmarks, context windows, modalities, availability, and pricing; preserve uncertainty and conflicting evidence.
- [ ] Add a named second-model review path and structured AI self-audit for omissions, dependencies, inconsistencies, security risks, and acceptance evidence; findings require evidence and must not be treated as ground truth.


## Workspace project format and prompt routing

- [x] Define `WORK_MODELS.md`, `PLAN.md`, `CACHE.md` and `IN_PROGRESS.md` as the canonical project record files.
- [x] Define transitions: plan → active implementation/bug fix → cache with dated evidence.
- [x] Add structured AI/person handoff fields for command outputs, status, evidence and next action.
- [x] Group prompt entrypoints by purpose and retain a mandatory reread route for new tasks/context recovery.
- [x] Link the project format from agent entrypoints, prompt index, repository map and rule index.
- [x] Run PR CI and review all repository-local Markdown links for the project format change.

## Workspace and source parity

- [x] Migrate substantive public source items to GitHub and compare the current GitLab tree.
- [x] Keep GitHub workflow/CI distinct from GitLab source configuration.
- [x] Record the source-to-destination mapping and intentional omissions.
- [ ] Decide whether GitLab becomes archival or continues to receive deliberate backports.
- [ ] Re-run semantic parity review if GitLab changes again.

## AgentKit

- [x] Build an initial safe capability inventory for known high-impact tool CLIs without executing commands or installing packages.
- [x] Add fixed-argument, bounded version probes for discovered allowlisted tools and JSON/Markdown reports with source URLs.
- [x] Add unit tests for no-execution discovery, fixed argv, timeout handling, bounded output and report provenance.
- [x] Review primary research on tool use, program execution, test-time search, retrieval, reflection and multi-agent coordination; record experimental findings and limitations.
- [x] Catalog open-source/local candidates and distinguish local/self-hosted use from API-backed fees and quotas.
- [ ] Expand discovery to verify browser binaries, MCP configuration, local model runtimes/endpoints and more language-specific test runners without exposing secrets.
- [ ] Collect an approved hardware/runtime profile and compare local inference paths (Ollama vs llama.cpp; vLLM only where appropriate) without automatic installation.
- [ ] Add a Playwright adapter for approved browser exploration, screenshots/traces and repeatable UI regression tests; keep consequential actions approval-gated.
- [ ] Add a workspace-scoped execution/patch adapter with path containment, command policy, timeout/output limits, postcondition checks and provenance records.
- [ ] Add a deterministic evaluation/result schema mapping acceptance criteria to test IDs, expected/actual results, artifacts and limitations.
- [ ] Add a bounded adaptive repair/search loop that escalates only after objective failure and selects candidates using tests/validators.
- [ ] Add versioned local checkpoint/memory records and resume/re-observation behavior for interrupted tasks.
- [ ] Evaluate local exact search/repository maps first; add a local vector/RAG index only if retrieval recall tests show a material gap.
- [ ] Add optional separately named reviewer routing for independent work or a genuinely distinct second model; findings remain advisory and evidence-checked.
- [ ] Add security/fault-injection tests for prompt injection, path traversal, unknown tools, output flooding, timeouts, interrupted operations and uncertain external side effects.
- [ ] Compare baseline and candidate toolchains on fixed tasks using the same model/context/compute budget where practical; report pass rate, latency, call count, failure class and environment evidence.

## ReForge Visuals

- [x] Inspect supplied 3.24.1 archive and confirm BP/RP manifest versions.
- [x] Parse-check all 1,149 JSON files in the 3.24.1 source.
- [x] Syntax-check all 12 JavaScript files in the 3.24.1 source.
- [x] Remove low-benefit ray / dummy-entity / N-way planning and duplicate unresolved-item references.
- [x] Standardize project records and move completed static checks out of the pending plan into cache.
- [x] Increase default-water biome-color contribution 0.04→0.20 and river contribution 0.05→0.12 across all six subpacks.
- [x] Synchronize 71 legacy biome water colors with the current per-biome color definitions.
- [x] Fix the `minecraft:swampland` water classifier omission.
- [x] Correct four out-of-schema `sampleWidth=1.25` values and update the medium-shadow label.
- [x] Fix generation of unresolved per-altitude weather-fog keys at Y≤30 and clear the transition latch.
- [x] Generate candidate 3.24.2 and pass full static package audit (0 findings) plus 8/8 regression tests.
- [ ] Test candidate 3.24.2 in a real Bedrock world with Vibrant Visuals both on and off; inspect default water, river, ocean and tinted biomes.
- [ ] Review in-world Content Log and target-device/subpack compatibility.
- [ ] Measure tick/frame cost under expected target-device and multiplayer conditions.
- [ ] Add future optimization code only after a reproducible bottleneck and visual benefit have been recorded.

## Runtime feature claims

- [ ] Keep static checks and in-world testing as separate completion criteria.
- [ ] Never mark a runtime issue fixed solely because syntax/manifest checks pass.
