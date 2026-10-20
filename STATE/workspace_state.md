# Workspace state

Status: GitHub is the public collaboration entry point; the GitLab source remains unchanged.  
Last updated: 2026-10-21

## Verified

- Public GitHub repository exists: AI-interaction-Workspace.
- GitLab public workspace tree was re-read and mapped to the GitHub layout; see [DOCS/GITLAB_PARITY_AUDIT.md](../DOCS/GITLAB_PARITY_AUDIT.md).
- The canonical project format is defined in [DOCS/PROJECT_WORKFLOW.md](../DOCS/PROJECT_WORKFLOW.md): `WORK_MODELS.md`, `PLAN.md`, `CACHE.md`, `IN_PROGRESS.md`.
- Prompt entrypoints are grouped by purpose in [PROMPTS/README.md](../PROMPTS/README.md); `AGENTS.md` and `AI_WORKFLOW.md` define the reread route for new tasks and resumptions.
- A local ReForge Visuals 3.24.2 candidate was generated from the supplied 3.24.1 artifact. Full static audit on a clean extraction reported 0 findings, and 8 regression tests passed. The audit report and candidate are handoff files, not committed binary assets.
- Candidate static audit: 1,149 JSON files parsed with duplicate-key detection; 12 JavaScript files syntax/import checked; 513 fog IDs and 338 fog references checked; water definitions/schema checked across all six subpacks; 12 OGG and 9 PNG assets checked; ZIP CRC/path checks passed.
- The candidate includes a water-tint adjustment and statically identified corrections; see [ReForge cache](../PROJECTS/ReForge-Visuals/CACHE.md) and [active validation handoff](../PROJECTS/ReForge-Visuals/IN_PROGRESS.md).
- AgentKit extensions are implemented for PATH executable inventory, tsc-based TypeScript compilation, append-only actor/mode provenance, static mcaddon/mcpack audit, safe command resolution, and smartphone profile compatibility preflight. Follow-up PR [#14](https://github.com/KAITO9999/AI-interaction-Workspace/pull/14) adds resolver environment overrides, richer CLI help, and warnings when alternate/fallback paths actually execute; latest CI status is not yet confirmed.
- Smartphone profile budgets are 4/8/12/16 GB; low-end defaults to Android 11/API 30, mid-end to Android 15/API 35, and higher tiers have no default Android-version target. See [AgentKit smartphone profile docs](../TOOLS/AgentKit/MOBILE_TESTING.md).
- Pull-request CI is configured to reject missing provenance entries, rewritten ledger history and changed paths not covered by records.

## Not implemented / not verified

- ReForge Visuals 3.24.2 has not been loaded in a real Bedrock world; its exact water appearance is not verified.
- Bedrock Content Log output, target-device behavior, and multiplayer performance remain pending.
- Runtime frame/tick performance or multiplayer-load measurements have not been performed.
- TypeScript compilation against representative real projects with their own tsconfig.json remains untested; automated tests use a stub compiler for invocation.
- Termux and other target-device smoke tests remain pending.
- AgentKit smartphone profiles have only static preflight logic; emulator/physical-device tests and actual CPU/GPU/frame-time/memory/thermal measurements remain pending.
- Full feature parity between the core Python CLI and reduced shell fallback remains unverified.
- Automatic GitLab to GitHub synchronization is not configured. GitLab has not been modified.
- Provenance records validate declared metadata and changed-path coverage, not cryptographic identity.

## Operating notes

- Keep public/private boundaries strict; ledger summaries, handoff entries and environment inventories must not include secrets, private URLs, raw conversations or local identifiers.
- PATH discovery does not execute each command and does not prove a tool works.
- Static package validation is not runtime validation.
- State CI as passed only after an actual successful run is observed.
- Read only the project records in the current task's scope; reread the canonical route after context loss instead of relying on memory.
