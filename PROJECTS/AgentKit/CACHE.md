# AgentKit — cache

Status: smartphone profile preflight implementation and CI validation passed; Android runtime validation pending.
Last reviewed: 2026-10-25

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

| 2026-10-21 | Add smartphone profile preflight and automated compatibility gate | PASS; 39 AgentKit unit tests passed in GitHub Actions on Ubuntu; Python compilation and shell syntax checks passed; provenance validation passed; 115 repository-local Markdown links checked. Pull request: [#13](https://github.com/KAITO9999/AI-interaction-Workspace/pull/13). Physical-device/emulator tests remain pending.

## Completed items

| 2026-10-25 | Add Python-first workflow checks, context-bounded inspection and concurrent verification watcher | PASS; GitHub Actions run [40137923343](https://github.com/KAITO9999/AI-interaction-Workspace/actions/runs/40137923343) passed Python compilation, POSIX shell syntax, all 57 unit tests, change-ledger provenance and Markdown-link validation. The tools were exercised on GitHub-hosted Ubuntu; Termux and other target virtual-Linux environments remain unverified. |


| 2026-10-25 | Centralize subprocess supervision and audit AgentKit tool consistency | PASS; GitHub Actions run [40156135136](https://github.com/KAITO9999/AI-interaction-Workspace/actions/runs/40156135136) passed 98 unit tests, Python compilation, POSIX shell syntax, change-ledger provenance and local Markdown-link checks. Runtime process launches now share the bounded supervisor; target-environment/Termux tests remain unverified. Draft PR: [#17](https://github.com/KAITO9999/AI-interaction-Workspace/pull/17). |
