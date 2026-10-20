# Project records

Each project uses the same four canonical files, with no duplicate plan/cache/editing routes:

- [`WORK_MODELS.md`](./ReForge-Visuals/WORK_MODELS.md) — working methods and validation model.
- [`PLAN.md`](./ReForge-Visuals/PLAN.md) — work not yet started.
- [`CACHE.md`](./ReForge-Visuals/CACHE.md) — verified facts, decisions, and completed items moved from the plan.
- [`IN_PROGRESS.md`](./ReForge-Visuals/IN_PROGRESS.md) — active implementation, bug fixes, evidence and handoff.

## Adding or resuming a project

When work begins on a specific project, create or update all four files using the format in [Project documentation workflow](../DOCS/PROJECT_WORKFLOW.md). Record an active bug fix in `IN_PROGRESS.md` before changing code. Do not copy the project model into global prompts; link to it.

Do not open every project's records at startup. Read the four-file set only for the project currently in scope; at minimum re-read `WORK_MODELS.md` and `IN_PROGRESS.md` when starting or resuming that project.

## AgentKit

The canonical project records for AgentKit tooling and smartphone profile work are in [WORK_MODELS.md](AgentKit/WORK_MODELS.md), [PLAN.md](AgentKit/PLAN.md), [CACHE.md](AgentKit/CACHE.md), and [IN_PROGRESS.md](AgentKit/IN_PROGRESS.md). Implementation details live in [TOOLS/AgentKit](../TOOLS/AgentKit/README.md).
