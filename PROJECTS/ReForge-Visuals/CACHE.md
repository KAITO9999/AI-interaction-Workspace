# ReForge Visuals — cache

Status: static source review complete; runtime validation pending.  
Current artifact: `ReForge_Visuals-3.24.1.mcaddon`  
Last reviewed: 2026-10-13

## Verified facts

- BP and RP manifest versions are 3.24.1.
- Both packs declare minimum engine version 1.26.0.
- BP dependencies include `@minecraft/server` 2.9.0 and `@minecraft/server-ui` 2.1.0; the BP-to-RP dependency matches the RP header UUID/version.
- Archive inventory: 1,192 files, including 1,149 JSON files and 12 BP JavaScript files.
- `BP/scripts/performance_engine.js` supplies the shared scheduler/queue and is the primary work-budget gate.
- Static inspection of the 12 BP scripts found no `Dimension.getBlockFromRay`, `Dimension.getTopmostBlock`, `spawnEntity` calls or named light-shaft subsystem. These were old proposals, not active implementation in this 3.24.1 artifact.

## Completed items moved from PLAN

| Date | Item moved from plan | Result / evidence |
|---|---|---|
| 2026-10-13 | Inspect the supplied artifact and verify BP/RP versions and dependencies | PASS; manifests inspected for 3.24.1 |
| 2026-10-13 | Check archive integrity and paths | PASS; ZIP CRC and unsafe-path scan |
| 2026-10-13 | Parse JSON files | PASS; 1,149 / 1,149 |
| 2026-10-13 | Syntax-check JavaScript files | PASS; 12 / 12 with Node |
| 2026-10-13 | Remove stale low-benefit raycast / dummy-entity / N-way approaches from planning | Planning change complete; no active gameplay code was removed |

These are static/documentation results, not proof of in-world behavior. Pending runtime tasks remain in [PLAN.md](PLAN.md).

## Decisions

- Do not treat older 3.17.8 / 3.18.0 notes as descriptions of the 3.24.1 artifact.
- Do not add a second scheduler, queue or equivalent archive-audit path when a canonical implementation already exists.
- Future optimization needs a reproducible bottleneck, measurable expected benefit and rollback path.
- Separate static checks from real-world / Content Log checks.

## UNKNOWN — not yet verified

- In-world appearance, settings behavior, sound and fog across biomes/weather/water depth.
- Content Log warnings/errors.
- Multiplayer load and target-device compatibility.
- Actual tick/frame cost or visual improvement of a future optimization.
