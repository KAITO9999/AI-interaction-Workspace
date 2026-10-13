# Work scope / claim rules

Before changing files, state the paths or feature area intended for modification in the task or PR.

- Avoid overlapping another contributor's active work. If overlap exists, coordinate or limit scope rather than overwrite.
- When starting work on a specific project, follow the four-file lifecycle in [Project documentation workflow](../DOCS/PROJECT_WORKFLOW.md) and create or update `WORK_MODELS.md` before implementation.
- Before changing code for an implementation, bug fix, reproduction, regression investigation or refactor, record the active item in that project's `IN_PROGRESS.md`.
- Keep not-yet-started work in `PLAN.md`. When complete, remove it from the pending plan and append dated evidence to `CACHE.md`.
- For AI/person handoff, record commands, working directory, status/exit code, relevant output, evidence, classification and next action in `IN_PROGRESS.md`.
- Update shared state/task when project status changes. Do not claim that coordination is automated unless it is implemented and verified.
- Every PR changeset must identify who authored/materially edited the files (AI or human) and the route used (online/offline/mixed).
- Use `TOOLS/AgentKit/agentkit_ext.py record-change` for path-level records. If AI and human edits differ, add separate records with their own path sets.
- The PR gate rejects changed files without corresponding records; it does not verify real-world identity.