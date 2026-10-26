# Rule index

For every new task and every resumption after context loss, start with [AI_WORKFLOW.md](../AI_WORKFLOW.md), then read only the rule relevant to the current task. Use the [prompt/use-case index](../PROMPTS/README.md) for routing; do not duplicate full instructions into agent-specific files.

- [Conversation and evidence](CONVERSATION_RULES.md): preserve original meaning; label interpretations.
- [Work claims](WORK_CLAIM_RULES.md): declare scope, track active work and avoid overlapping edits.
- [File changes](FILE_CHANGE_RULES.md): inspect first, preserve unrelated changes.
- [Public data](PUBLIC_DATA_RULES.md): prevent secret/private-data exposure.
- [Truth and errors](TRUTH_AND_ERROR_RULES.md): evidence, uncertainty and corrections.
- [Android APK builds](ANDROID_BUILD_RULES.md): prohibit on-device compilation and route builds through GitHub Actions.
- [Reports](SCOPE_AND_REPORT_RULES.md): summarize changes and validation.
- [Commits](COMMIT_RULES.md): meaningful, traceable change units.
- [Project documentation format](../DOCS/PROJECT_WORKFLOW.md): required work models / plan / cache / editing structure, transitions and handoff fields.

When a specific project is in scope, read its `WORK_MODELS.md` and `IN_PROGRESS.md`; use `PLAN.md` and `CACHE.md` only as needed. Do not read every rule or cache by default.
