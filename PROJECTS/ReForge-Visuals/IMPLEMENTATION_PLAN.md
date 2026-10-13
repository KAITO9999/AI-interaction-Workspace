# ReForge Visuals — current source review and plan

Status: STATIC SOURCE REVIEW COMPLETE; runtime validation pending  
Reviewed: 2026-10-13  
Reference artifact: user-provided ReForge_Visuals-3.24.1.mcaddon

## Verified package facts

- BP and RP header/module versions are 3.24.1.
- Both packs declare minimum engine version 1.26.0.
- BP dependencies include @minecraft/server 2.9.0 and @minecraft/server-ui 2.1.0; its RP dependency matches the RP header UUID/version.
- The archive contains 1,192 files: 1,149 JSON, 12 JavaScript, and other pack assets.
- This artifact supersedes older 3.17.8 / 3.18.0 notes. Those notes are historical only.

## Current script structure observed

| Script | Observed role |
|---|---|
| BP/scripts/main.js | Entry point, settings UI, periodic dispatch and debug display |
| BP/scripts/performance_engine.js | Shared queues, cadence and execution budget |
| BP/scripts/lighting_engine.js | Hand light and mixed light-profile handling |
| BP/scripts/biome_cache_engine.js | Biome classification, cache and factors |
| BP/scripts/coordinate_engine.js | Coordinate and water-state sampling |
| BP/scripts/environment_state.js | Per-player environment snapshot |
| BP/scripts/weather_engine.js | Weather selection and dynamic rain |
| BP/scripts/fog_controller.js | Weather, altitude and water fog |
| BP/scripts/weather_audio.js / water_audio.js | Weather and underwater sound state |
| BP/scripts/runtime_config.js | Persistent runtime settings |
| BP/scripts/admin_bootstrap.js | Permission-gated admin bootstrap |

Names and static call paths do not substitute for in-game profiling.

## Removed planning approaches

The former sections 4.3–4.5 are removed because their expected visual benefit does not justify their extra work and load at this stage:

- Raycast-based boundary and direction probing.
- Dummy-entity probing.
- N-way direction masks and related candidate/rendering work.

Static inspection found no Dimension.getBlockFromRay, Dimension.getTopmostBlock, spawnEntity, or named light-shaft subsystem in the 12 BP scripts. These were proposed approaches in old planning text, not active runtime features in this 3.24.1 artifact. Related entries in later phase lists, unresolved-question lists, completion criteria and priority rankings have also been trimmed. No active gameplay code was removed on the basis of that old plan.

## Remaining engineering priorities

1. Keep Performance Engine as the single scheduler; do not create a second queue without measurements.
2. Profile expensive paths before adding environment scans. Record call frequency, budget impact and observed gameplay difference.
3. Preserve existing cache reuse, task deduplication and cancellation behavior unless a reproducible regression justifies a change.
4. Verify Script API/runtime behavior in the target Bedrock version using Content Log and a real world before changing API assumptions.
5. Treat JSON and JavaScript syntax checks as static checks only. Keep runtime errors and visual results as separate test criteria.
6. Make future optimizations independently measurable and reversible.

## Validation boundary

The AgentKit static archive audit reported:

- ZIP CRC and archive path checks: PASS.
- BP/RP manifest version and dependency consistency: PASS.
- JSON parsing: 1,149 / 1,149 PASS.
- Node syntax check: 12 / 12 JavaScript files PASS.

Not verified: in-world appearance, sound behavior, Content Log output, multiplayer load, target-device compatibility, or any measured runtime performance delta. Do not call the add-on runtime-tested based on static results alone.
