# Instructions for AI agents

For every new task and every resumption after context loss, follow the reread route in [AI_WORKFLOW.md](AI_WORKFLOW.md) rather than relying on conversation memory. The purpose is to reread the short canonical route, not every file in the repository.

- Read [AI workflow](AI_WORKFLOW.md), [workspace state](STATE/workspace_state.md), [current tasks](TASKS/tasks.md), and [repository map](DOCS/REPOSITORY_MAP.md).
- If a specific project is in scope, read its `WORK_MODELS.md` and `IN_PROGRESS.md`; read `PLAN.md` and `CACHE.md` only when relevant. The canonical format and lifecycle are in [Project workflow](DOCS/PROJECT_WORKFLOW.md).
- Use the [prompt/use-case index](PROMPTS/README.md) and the [rule index](RULES/README.md) to select the one relevant procedure instead of copying or loading unrelated instructions.
- Inspect before editing; keep changes scoped and avoid overwriting another contributor's active work.
- Do not invent facts, links, test results or completion claims. Do not expose secrets, private conversations, personal data or private workspace links.
- Prefer existing tools; check availability and behavior before implementing substitutes.
- Validate links and relevant tests before reporting. Summarize changed files, evidence, limits and next steps in the PR.
