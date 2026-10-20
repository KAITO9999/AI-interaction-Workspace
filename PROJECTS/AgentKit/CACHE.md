# AgentKit — cache

Status: smartphone profile preflight implementation and CI validation passed in merged PR #13; explicit environment/help follow-up is in PR #14 with CI pending; Android runtime validation pending.
Last reviewed: 2026-10-21

## Verified source facts

- AgentKit previously had core environment probing, executable inventory, TypeScript compilation, provenance recording, add-on auditing, and command resolution.
- The prior source did not contain a smartphone hardware profile matrix with CPU-core, clock, GPU, or thermal parameters.
- Smartphone memory budgets requested for this feature are 4 GB, 8 GB, 12 GB and 16 GB.
- Android 11 maps to API 30 and Android 15 maps to API 35 for the configured compatibility gates.

- The command resolver accepts an explicit environment policy (`auto`, `termux`, `linux`, `wsl`, `macos`, `windows`) for installer filtering. This is not OS emulation; package installation is blocked if an explicit environment conflicts with the current runtime.
- Compatibility warnings are emitted only when a non-preferred external command or Python substitute actually executes, not in ordinary help output.

## Decisions

- Low-end defaults to 4 GB and Android 11/API 30; mid-end defaults to 8 GB and Android 15/API 35; mid-high and high-end default to 12 GB and 16 GB without a default Android-version gate.
- When a literal minSdkVersion exceeds a selected target API, that profile is rejected. An unresolved minimum SDK blocks version-gated profiles for review rather than assuming compatibility.
- The tool is a static preflight and profile planner. It does not claim emulator, physical-device, or performance testing.

## Completed items moved from PLAN

| 2026-10-21 | Add smartphone profile preflight and automated compatibility gate | PASS; 39 AgentKit unit tests passed in GitHub Actions on Ubuntu; Python compilation and shell syntax checks passed; provenance validation passed; 115 repository-local Markdown links checked. Pull request: [#13](https://github.com/KAITO9999/AI-interaction-Workspace/pull/13). Physical-device/emulator tests remain pending.
