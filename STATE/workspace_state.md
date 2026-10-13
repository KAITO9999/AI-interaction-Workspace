# Workspace state

Status: GitHub is the public collaboration entry point; the GitLab source remains unchanged.  
Last updated: 2026-10-13

## Verified

- Public GitHub repository exists: AI-interaction-Workspace.
- GitLab public workspace tree was re-read and mapped to the GitHub layout; see DOCS/GITLAB_PARITY_AUDIT.md.
- The supplied ReForge Visuals package is version 3.24.1 in both BP/RP manifests.
- Static audit passed ZIP integrity/path checks, BP/RP version and dependency matching, parsing for all 1,149 JSON files, and Node syntax checking for all 12 JavaScript files.
- AgentKit extensions are implemented for PATH executable inventory, tsc-based TypeScript compilation, append-only actor/mode provenance, and static mcaddon/mcpack audit.
- Pull-request CI is configured to reject missing provenance entries, rewritten ledger history and changed paths not covered by records.

## Not implemented / not verified

- ReForge Visuals in-world smoke test and Content Log review.
- Runtime frame/tick performance or multiplayer-load measurements.
- TypeScript compilation against representative real projects with their own tsconfig.json; automated tests use a stub compiler for invocation.
- Termux and other target-device smoke tests.
- Full feature parity between the core Python CLI and reduced shell fallback.
- Automatic GitLab to GitHub synchronization. GitLab has not been modified.
- Provenance records validate declared metadata and changed-path coverage, not cryptographic identity.

## Operating notes

- Keep public/private boundaries strict; ledger summaries and environment inventories must not include secrets, private URLs, raw conversations or local identifiers.
- PATH discovery does not execute each command and does not prove a tool works.
- Static package validation is not runtime validation.
- State CI as passed only after an actual successful run is observed.
