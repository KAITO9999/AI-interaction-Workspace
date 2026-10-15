# ReForge Visuals — plan

Status: static work complete for candidate 3.24.2; target-world and runtime validation pending. Completed static tasks are recorded in [CACHE.md](CACHE.md) and are not duplicated here.

## P1 — Verify 3.24.2 water tint in-world and inspect Content Log

- **Outcome:** confirm that normal biome water gains the intended blue tint without making rivers/oceans/swamps visually wrong.
- **Prerequisite:** a real Bedrock world on the intended game version and the exact 3.24.2 candidate.
- **Checks:**
  - Test with Vibrant Visuals enabled and disabled.
  - Check default-water biomes (such as plains/forest), river/frozen river, ocean/warm ocean and swamp/mangrove/lush-cave exceptions.
  - Repeat with the expected subpack/quality tiers where applicable.
  - Inspect Content Log after pack activation and during water/biome/weather transitions.
  - Record screenshots or reproducible observations, game/device version and selected subpack.
- **Complete when:** observations show whether the blue tint is improved and exceptions remain appropriate; Content Log output is recorded; any new failures are triaged and re-tested or left explicitly open.
- **Current state:** not run; requires in-game runtime.

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
