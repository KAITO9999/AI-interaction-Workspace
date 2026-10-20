# Executor++ — editing / handoff

Current status: requirements, initial research leads, and the project plan are drafted on branch `work/executor-plus-long-work-mode`. Application code has not been implemented; no app build, MCP runtime test, or Android device test has been run.

## Active work

### EX-LONG-001 — Long-running project mode requirements

- **Status:** requirements captured and manually cross-checked against the current request; architecture validation and implementation pending
- **Actor:** AI
- **Work mode:** online (GitHub connector used to inspect repository workflow, record project requirements, and consult public research sources)
- **Scope:** define a standalone long-work connector feature with durable per-conversation state, checklist checkpoints, staged termination guard, handoff planning, research-backed help, app-visible progress, logs exposed by the integration, notifications and battery-setting guidance. The plan also preserves earlier requirements for asset caching, provider selection, whitelist-based text input, context handoff, concurrent goals, queue handling, connector lifecycle, GPT suggestions, Auth0 evaluation, and the icon.
- **Paths:** `PROJECTS/ExecutorPlus/WORK_MODELS.md`, `PROJECTS/ExecutorPlus/PLAN.md`, `PROJECTS/ExecutorPlus/CACHE.md`, `PROJECTS/ExecutorPlus/IN_PROGRESS.md`, `PROJECTS/README.md`, `DOCS/REPOSITORY_MAP.md`, `TASKS/tasks.md`.
- **Checks run:** repository README, canonical project workflow, and existing project-record examples inspected. Initial research leads recorded in CACHE. Requirements compared against the currently visible user request and prior Executor++ scope. No code tests, link checker, AgentKit runtime, or application runtime tests were run.
- **Evidence:** branch `work/executor-plus-long-work-mode`; project workflow `DOCS/PROJECT_WORKFLOW.md`; repository entrypoint `README.md`; research links in `PROJECTS/ExecutorPlus/CACHE.md`.
- **Classification:** FACT — project record structure and workflow were retrieved from the repository; the cited research pages were located. DECISION — long-work requirements and platform boundaries captured in this project. UNKNOWN — host API capability, provider support details, and runtime behavior.
- **Next action:** inspect host integration/API capabilities and the current AgentKit environment; validate links and the full requirements matrix; then refine architecture and begin test-first implementation.
