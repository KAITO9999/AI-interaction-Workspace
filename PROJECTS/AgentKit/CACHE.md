# AgentKit — cache

Status: smartphone profile preflight implementation added; CI validation pending.
Last reviewed: 2026-10-21

## Verified source facts

- AgentKit previously had core environment probing, executable inventory, TypeScript compilation, provenance recording, add-on auditing, and command resolution.
- The prior source did not contain a smartphone hardware profile matrix with CPU-core, clock, GPU, or thermal parameters.
- Smartphone memory budgets requested for this feature are 4 GB, 8 GB, 12 GB and 16 GB.
- Android 11 maps to API 30 and Android 15 maps to API 35 for the configured compatibility gates.

## Decisions

- Low-end defaults to 4 GB and Android 11/API 30; mid-end defaults to 8 GB and Android 15/API 35; mid-high and high-end default to 12 GB and 16 GB without a default Android-version gate.
- When a literal minSdkVersion exceeds a selected target API, that profile is rejected. An unresolved minimum SDK blocks version-gated profiles for review rather than assuming compatibility.
- The tool is a static preflight and profile planner. It does not claim emulator, physical-device, or performance testing.

## Completed items moved from PLAN

No plan items completed yet. CI and implementation review are pending.
