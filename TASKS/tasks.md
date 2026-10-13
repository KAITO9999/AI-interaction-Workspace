# Tasks

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
- [ ] Test in a real Bedrock world and review Content Log.
- [ ] Measure tick/frame cost under expected target-device and multiplayer conditions.
- [ ] Add future optimization code only after a reproducible bottleneck and visual benefit have been recorded.

## Runtime feature claims

- [ ] Keep static checks and in-world testing as separate completion criteria.
- [ ] Never mark a runtime issue fixed solely because syntax/manifest checks pass.
