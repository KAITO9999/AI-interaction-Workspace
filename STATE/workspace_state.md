# Workspace state

Status: GitHub public collaboration entry; private diagnostics live in AI-interaction-Private-Workspace.  
Last updated: 2026-11-01

## Verified

- Public repo: AI-interaction-Workspace. Private: AI-interaction-Private-Workspace (diagnostics only; no full workflow duplicate).
- Mandatory AI read route is short: AGENTS → AI_WORKFLOW → STATE → TASKS (skim). Map: [DOCS/REPOSITORY_MAP.md](../DOCS/REPOSITORY_MAP.md).
- Prompt routing: [PROMPTS/README.md](../PROMPTS/README.md). On-demand work-assist under `PROMPTS/work-assist/` (open by filename, not batch).
- Project format: four files per [DOCS/PROJECT_WORKFLOW.md](../DOCS/PROJECT_WORKFLOW.md).
- AgentKit: PATH inventory, resolve fallbacks, lint/work/watch, mobile static preflight, change ledger. See TOOLS/AgentKit.
- PR CI rejects missing/rewritten ledger coverage for changed paths.

## Not implemented / not verified

- ReForge Visuals runtime in real Bedrock world (water appearance, Content Log, multiplayer) still pending where noted in PROJECTS/ReForge-Visuals.
- Termux / physical-device AgentKit smoke tests pending.
- Full core Python CLI vs shell fallback parity unverified.
- Automatic GitLab→GitHub sync not configured.
- Provenance is metadata coverage, not cryptographic identity.

## Operating notes

- After context loss, reread the short route; do not trust memory.
- Do not bulk-read PROJECTS, RULES, or work-assist.
- PATH discovery ≠ tool works. Static package check ≠ runtime.
- Keep public/private boundary; no secrets or private URLs in public commits.
