# Scope and report rules

Every completion report must distinguish:

- Scope and files changed
- Work performed
- Checks actually run and their results
- Items not checked or not supported by the environment
- Known limitations and next steps

“Changed” does not mean “tested”; a configured CI job does not mean CI passed.

For project-specific work, use the [four-file project format](../DOCS/PROJECT_WORKFLOW.md): `WORK_MODELS.md` holds distinct procedures, `PLAN.md` holds pending work, `IN_PROGRESS.md` holds active implementation/bug fixes and handoff results, and `CACHE.md` holds verified durable results and completed items moved from the plan. Avoid duplicate task histories across those files.