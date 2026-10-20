# Project records

Each project uses the same four canonical files, with no duplicate plan/cache/editing routes:

- [Executor++ work models](./ExecutorPlus/WORK_MODELS.md), [plan](./ExecutorPlus/PLAN.md), [model characteristics catalog](./ExecutorPlus/MODEL_CATALOG.md), [cache](./ExecutorPlus/CACHE.md), and [active handoff](./ExecutorPlus/IN_PROGRESS.md).
- [ReForge Visuals work models](./ReForge-Visuals/WORK_MODELS.md), [plan](./ReForge-Visuals/PLAN.md), [cache](./ReForge-Visuals/CACHE.md), and [active handoff](./ReForge-Visuals/IN_PROGRESS.md).
- [AgentKit work models](./AgentKit/WORK_MODELS.md), [plan](./AgentKit/PLAN.md), [cache](./AgentKit/CACHE.md), and [active handoff](./AgentKit/IN_PROGRESS.md).

## Adding or resuming a project

When work begins on a specific project, create or update all four files using the format in [Project documentation workflow](../DOCS/PROJECT_WORKFLOW.md). Record an active bug fix in `IN_PROGRESS.md` before changing code. Do not copy the project model into global prompts; link to it.

Do not open every project's records at startup. Read the four-file set only for the project currently in scope; at minimum re-read `WORK_MODELS.md` and `IN_PROGRESS.md` when starting or resuming that project.
