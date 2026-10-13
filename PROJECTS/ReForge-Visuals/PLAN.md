# ReForge Visuals — plan

Status: pending validation only. Static archive review is complete and recorded in [CACHE.md](CACHE.md); completed work is not duplicated here.

## P1 — In-world smoke test and Content Log

- **Outcome:** verify the 3.24.1 artifact in a real Bedrock world.
- **Prerequisite:** test world and intended Bedrock runtime are available.
- **Checks:** enable Content Log, load the add-on, exercise settings and relevant visual/audio states, and capture errors and reproducible observations.
- **Complete when:** runtime/version and steps are recorded, Content Log results are preserved, and each remaining issue is either fixed and re-tested or explicitly left open.
- **Current state:** not run.

## P2 — Performance and multiplayer measurement

- **Outcome:** establish a baseline before considering new optimization code.
- **Prerequisite:** a runnable test setup and repeatable scene/player count.
- **Checks:** record device/runtime, player count, duration, relevant tick/frame observations, and baseline-versus-candidate results.
- **Complete when:** results are reproducible and identify either a measured bottleneck worth addressing or no demonstrated need for additional optimization.
- **Current state:** not run.

## P3 — Target-environment compatibility

- **Outcome:** verify behavior on the intended target device/runtime.
- **Checks:** repeat the smoke test and note device-specific API, visual, audio or load issues.
- **Complete when:** target environment, steps, results and limitations are recorded.
- **Current state:** not run.

Do not add raycast, dummy-entity, N-way direction-mask or other low-benefit approaches without new evidence that expected improvement justifies runtime and maintenance cost.
