# ReForge Visuals — plan

Status: candidate 3.24.6 static checks pass; in-world appearance and Content Log validation remain pending. Completed static evidence is recorded in [CACHE.md](CACHE.md).

## P1 — Validate water/fog candidate 3.24.6 in-world

- **Outcome:** confirm water color, underwater visibility and distance behavior with VV on/off; keep water stylized and substantial rather than over-clear or muddy.
- **Prerequisite:** import the exact ReForge_Visuals-3.24.6.mcaddon artifact and confirm the target Bedrock version/device.
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


## P4 — Validate the local ReForge Visuals 4.1.0 sidecar in-world

- **Outcome:** verify the candidate derived from the supplied 4.0.6 artifact in Bedrock; compare the 8×8, 12×12 and 16×16 logical-pixel sun variants and check the four candle-color helper lights.
- **Prerequisite:** import the exact local `ReForge_Visuals-4.1.0.mcaddon` handoff artifact. For the size comparison, activate only one of `ReForge_Sky_Discs-8x8-Test-4.1.0.mcpack`, `ReForge_Sky_Discs-4.1.0.mcpack` (12×12), or `ReForge_Sky_Discs-16x16-Test-4.1.0.mcpack` above other sky-changing packs.
- **Checks:** test Simple/non-VV and Vibrant Visuals; inspect sun shape/apparent size, all moon phases, clouds and sky colors; verify the four helper blocks' point-light colors/intensity and selection/removal; repeat at least one representative scene across the PBR subpack tiers; inspect Content Log after import and world load.
- **Complete when:** screenshots and the game/device/version are recorded for both graphics modes, the preferred sun-size variant is selected, and any loading/light issues are either fixed and re-tested or left explicitly open.
- **Current state:** the 4.1.0 sidecar is statically built and checked. No Bedrock launch, in-world visual test or Content Log capture has been performed in this session. This candidate is a separate local 4.0.6-derived line; it is not asserted to match the public 3.24.6 candidate.
