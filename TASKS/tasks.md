# Tasks

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

Detailed sequencing, dependencies, acceptance criteria and the completed gap review live in the canonical [AgentKit plan](../PROJECTS/AgentKit/PLAN.md). Keep this global list as a short index rather than duplicating the project plan.

- [x] Core environment probe and reduced POSIX shell fallback.
- [x] Inventory actual external executables in PATH without executing discovered tools.
- [x] Wrap installed tsc for TypeScript build and no-emit check.
- [x] Add static mcaddon/mcpack validation.
- [x] Add path-level change records with actor (AI/human) and mode (online/offline/mixed).
- [x] Add tests for extension CLI and provenance validation.
- [x] Add CI gate for append-only ledger and changed-path coverage.
- [ ] Reconcile open AgentKit PRs #10 and #11 against the current default branch and CI before relying on their changes.
- [ ] Fix audit false positives for commented-out code, with regression tests.
- [ ] Add file-path and exact test-entry-point selection instead of substring-only skipping.
- [ ] Smoke-test on Termux and another target environment.
- [ ] Test compile-ts against representative real tsconfig.json projects.
- [ ] Test actual connector-backed MCP/GPT directions; the local payload bridge alone is not end-to-end integration.
- [ ] Test virtual edit conflict/stale-hash rejection and source preservation before explicit apply.
- [ ] Decide whether the core probe should call the extension CLI directly or remain intentionally small.

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
