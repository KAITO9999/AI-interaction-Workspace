# Tasks

## Workspace project format and prompt routing

- [x] Define `WORK_MODELS.md`, `PLAN.md`, `CACHE.md` and `IN_PROGRESS.md` as the canonical project record files.
- [x] Define transitions: plan → active implementation/bug fix → cache with dated evidence.
- [x] Add structured AI/person handoff fields for command outputs, status, evidence and next action.
- [x] Group prompt entrypoints by purpose and retain a mandatory reread route for new tasks/context recovery.
- [x] Link the project format from agent entrypoints, prompt index, repository map and rule index.
- [ ] Run PR CI and review all repository-local Markdown links before merge.

## Workspace and source parity

- [x] Migrate substantive public source items to GitHub and compare the current GitLab tree.
- [x] Keep GitHub workflow/CI distinct from GitLab source configuration.
- [x] Record the source-to-destination mapping and intentional omissions.
- [ ] Decide whether GitLab becomes archival or continues to receive deliberate backports.
- [ ] Re-run semantic parity review if GitLab changes again.

## AgentKit

- [x] Core environment probe and reduced POSIX shell fallback.
- [x] Inventory actual external executables in PATH without executing discovered tools.
- [x] Wrap installed tsc for TypeScript build and no-emit check.
- [x] Add static mcaddon/mcpack validation.
- [x] Add path-level change records with actor (AI/human) and mode (online/offline/mixed).
- [x] Add tests for extension CLI and provenance validation.
- [x] Add CI gate for append-only ledger and changed-path coverage.
- [ ] Smoke-test on Termux and another target environment.
- [ ] Test compile-ts against representative real tsconfig.json projects.
- [ ] Decide whether the core probe should call the extension CLI directly or remain intentionally small.

## ReForge Visuals

- [x] Inspect supplied 3.24.1 archive and confirm BP/RP manifest versions.
- [x] Parse-check all 1,149 JSON files.
- [x] Syntax-check all 12 JavaScript files.
- [x] Remove low-benefit ray / dummy-entity / N-way planning and duplicate unresolved-item references.
- [x] Standardize project records and move completed static checks out of the pending plan into cache.
- [ ] Test in a real Bedrock world and review Content Log.
- [ ] Measure tick/frame cost under expected target-device and multiplayer conditions.
- [ ] Add future optimization code only after a reproducible bottleneck and visual benefit have been recorded.

## Runtime feature claims

- [ ] Keep static checks and in-world testing as separate completion criteria.
- [ ] Never mark a runtime issue fixed solely because syntax/manifest checks pass.