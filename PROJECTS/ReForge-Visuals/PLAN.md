# ReForge Visuals — plan

Status: candidate 3.24.5 static checks pass; in-world appearance and Content Log validation remain pending. Completed static evidence is recorded in [CACHE.md](CACHE.md).

## P1 — Validate water/fog candidate 3.24.5 in-world

- **Outcome:** confirm water color, underwater visibility and distance behavior with VV on/off; keep water stylized and substantial rather than over-clear or muddy.
- **Prerequisite:** import the exact ReForge_Visuals-3.24.5.mcaddon artifact and confirm the target Bedrock version/device.
- **Checks:**
  - Test both Vibrant Visuals/Deferred and Simple/non-VV modes.
  - Inspect standard water, swamp/mangrove, desert/mesa, jungle, river, ocean/deep ocean and a deep-water location.
  - Check surface tint, entry transition, mid-depth blue progression, visibility near the bottom, and darkening at several world heights.
  - Test non-VV swamp at 14 blocks; keep desert/mesa at 28; check VV ocean distance and biome changes while still underwater.
  - Change biome and graphics mode at the same in-game time to verify time-progressive fog does not retain an old range.
  - Inspect Content Log after pack activation and transitions; capture evidence with game version, device, mode, biome and subpack tier.
- **Complete when:** visual evidence and Content Log results exist for both modes; regressions are fixed/re-tested or clearly left open. Static JSON checks alone cannot close this item.
- **Current state:** static verification passed; Bedrock runtime not run in this session.

## P2 — Performance and multiplayer measurement

- **Outcome:** establish a baseline before considering new optimization code.
- **Prerequisite:** a runnable test setup and repeatable scene/player count.
- **Checks:** record device/runtime, player count, duration, relevant tick/frame observations, and baseline-versus-candidate results.
- **Complete when:** results are reproducible and identify either a measured bottleneck worth addressing or no demonstrated need for additional optimization.
- **Current state:** not run.

## P3 — Target-environment compatibility

- **Outcome:** verify behavior on the intended target device/runtime.
- **Checks:** repeat P1 and note device-specific API, visual, audio or load issues.
- **Complete when:** target environment, steps, results and limitations are recorded.
- **Current state:** not run.

Do not add raycast, dummy-entity, N-way direction-mask or other low-benefit approaches without new evidence that expected improvement justifies runtime and maintenance cost.
