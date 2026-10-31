# Repository map

## Mandatory short route (every task / resume)

Read **only** these, in order. Do not bulk-load the rest.

1. [AGENTS.md](../AGENTS.md) — entry
2. [AI_WORKFLOW.md](../AI_WORKFLOW.md) — procedure
3. [STATE/workspace_state.md](../STATE/workspace_state.md) — verified / blockers
4. [TASKS/tasks.md](../TASKS/tasks.md) — backlog (skim)

Then open **one** more file only if the task matches the "Read when" column below.

## Do not read by default

- Other projects under `PROJECTS/` (only the named project)
- Full `RULES/` set (use [RULES/README.md](../RULES/README.md) to pick one)
- Full `PROMPTS/work-assist/` (open one file by name when needed)
- `LOGS/change-ledger.jsonl` (only when provenance/PR)
- `DOCS/GITLAB_PARITY_AUDIT.md` (migration only)
- Private workspace content or URLs (never into public commits)

## Situation → file

| Situation | Open |
|---|---|
| New task / context loss | Mandatory route above |
| Pick instruction by purpose | [PROMPTS/README.md](../PROMPTS/README.md) |
| Non-trivial work steps | [PROMPTS/work-assist/workflow.md](../PROMPTS/work-assist/workflow.md) |
| Env / missing commands | [PROMPTS/work-assist/environment.md](../PROMPTS/work-assist/environment.md) or [TOOLS/AgentKit](../TOOLS/AgentKit/README.md) |
| Bugs / reuse / upstream | [PROMPTS/work-assist/debug-and-reuse.md](../PROMPTS/work-assist/debug-and-reuse.md) |
| Structure / language choice | [PROMPTS/work-assist/quality-and-migration.md](../PROMPTS/work-assist/quality-and-migration.md) |
| UI / visual / search ideation | [PROMPTS/work-assist/research-and-instructions.md](../PROMPTS/work-assist/research-and-instructions.md) |
| Project lifecycle four files | [DOCS/PROJECT_WORKFLOW.md](PROJECT_WORKFLOW.md) |
| Named project active work | `PROJECTS/<name>/IN_PROGRESS.md` (+ WORK_MODELS if needed) |
| Android / APK build | [RULES/ANDROID_BUILD_RULES.md](../RULES/ANDROID_BUILD_RULES.md) |
| Public vs private data | [DOCS/SPACE_CLASSIFICATION.md](SPACE_CLASSIFICATION.md) |
| PR / branch / CI | [DOCS/GITHUB_WORKFLOW.md](GITHUB_WORKFLOW.md) |
| Private diagnostics only | Use **AI-interaction-Private-Workspace** (not this repo) |

## Layout (what lives where)

| Path | Purpose |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | Agent entry (short) |
| `AI_WORKFLOW.md` | Canonical workflow |
| `PROMPTS/` | Routing index + on-demand work-assist |
| `RULES/` | Constraints by topic |
| `DOCS/` | Maps, project format, GitHub process |
| `STATE/` | Shared verified state |
| `TASKS/` | Backlog |
| `TOOLS/` | AgentKit |
| `PROJECTS/` | Per-project four-file records |
| `LOGS/` | Append-only ledger |
| `scripts/` | CI helpers |

Names under `PROMPTS/work-assist/` are content labels: open by need, not by batch.
