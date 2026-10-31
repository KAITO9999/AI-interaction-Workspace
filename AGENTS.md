# Instructions for AI agents

## Every new task / resume after context loss

Reread this short route. Do **not** rely on chat memory. Do **not** open every file in the repo.

1. This file
2. [AI_WORKFLOW.md](AI_WORKFLOW.md)
3. [STATE/workspace_state.md](STATE/workspace_state.md)
4. [TASKS/tasks.md](TASKS/tasks.md) (skim)

Then open **at most one** extra file from [DOCS/REPOSITORY_MAP.md](DOCS/REPOSITORY_MAP.md) or [PROMPTS/README.md](PROMPTS/README.md) by task match.

## Project scope

If a named project is in scope: read its `IN_PROGRESS.md` and `WORK_MODELS.md` only. `PLAN.md` / `CACHE.md` only when needed. Format: [DOCS/PROJECT_WORKFLOW.md](DOCS/PROJECT_WORKFLOW.md).

## Hard limits

- Do not invent facts, links, test results, or completion claims
- Do not load unrelated `PROJECTS/`, full `RULES/`, or all of `PROMPTS/work-assist/`
- Prefer existing tools; probe before inventing substitutes ([TOOLS/AgentKit](TOOLS/AgentKit/AI_USAGE.md))
- One agent role; no unprompted multi-persona debate ([RULES/ROLE_AND_PERSPECTIVE.md](RULES/ROLE_AND_PERSPECTIVE.md))
- No secrets, private conversations, private workspace dumps in public commits
- Android APK/AAB: never build on-device ([RULES/ANDROID_BUILD_RULES.md](RULES/ANDROID_BUILD_RULES.md))

## Before reporting

Validate what you claim. Summarize changed files, evidence, limits, next steps. Keep the task open if required validation did not run.
