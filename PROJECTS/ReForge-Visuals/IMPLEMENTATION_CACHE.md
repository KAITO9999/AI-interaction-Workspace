# ReForge Visuals — implementation cache

Status: STATIC REVIEW COMPLETE / RUNTIME TEST PENDING  
Current artifact: ReForge_Visuals-3.24.1.mcaddon  
Updated: 2026-10-13

## Verified facts

- BP and RP manifest versions both equal 3.24.1.
- Minimum engine version is 1.26.0.
- BP dependencies include @minecraft/server 2.9.0 and @minecraft/server-ui 2.1.0.
- Package inventory: 1,192 files, including 1,149 JSON files and 12 BP JavaScript files.
- performance_engine.js supplies the shared scheduler/queue. Preserve it as the primary work-budget gate instead of inventing a second scheduler.
- The BP scripts do not contain Dimension.getBlockFromRay, Dimension.getTopmostBlock, or spawnEntity calls. The former ray / dummy-entity / N-way proposal is not active implementation in this artifact.

## Static validation

- ZIP integrity and unsafe-path scan: PASS.
- BP/RP version and dependency matching: PASS.
- JSON parsing: 1,149 / 1,149 PASS.
- JavaScript syntax with Node: 12 / 12 PASS.
- These checks do not prove Bedrock runtime behavior.

## Unknown / not yet tested

- In-world appearance and settings behavior.
- Sound and fog behavior across biome, weather and water-depth changes.
- Content Log warnings/errors.
- Performance under multiple players and target-device constraints.
- Actual tick/frame cost or visual improvement from any future optimization.

## Current decision

Do not continue the older 3.17.8 / 3.18.0 history as if it described the current artifact. Remove the low-benefit approaches from the plan and remove their duplicate references from incomplete-task lists. Future optimization must be justified by a measured bottleneck and validated in-game; preserve current task budget and cache behavior unless profiling shows a regression.
