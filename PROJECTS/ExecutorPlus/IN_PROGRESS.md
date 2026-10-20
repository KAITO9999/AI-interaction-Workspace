# Executor++ — editing / handoff

Current status: requirements and project structure drafted on branch `work/executor-plus-long-work-mode`. Application code has not been implemented; no app build, MCP runtime test, or Android device test has been run.

## Active work

### EX-LONG-001 — Long-running project mode requirements

- **Status:** specification drafted; cross-check and implementation pending
- **Actor:** AI
- **Work mode:** online (GitHub connector used to inspect repository workflow and write project records)
- **Scope:** define a standalone long-work connector feature with durable per-conversation state, checklist checkpoints, staged termination guard, handoff planning, research-backed help, app-visible progress, logs exposed by the integration, notifications and battery-setting guidance.
- **Paths:** `PROJECTS/ExecutorPlus/WORK_MODELS.md`, `PROJECTS/ExecutorPlus/PLAN.md`, `PROJECTS/ExecutorPlus/CACHE.md`, `PROJECTS/ExecutorPlus/IN_PROGRESS.md`.
- **Checks run:** repository README and canonical project workflow inspected; existing project-record examples inspected; feature requirement records drafted. No code tests or runtime tests were run.
- **Evidence:** branch `work/executor-plus-long-work-mode`; project workflow `DOCS/PROJECT_WORKFLOW.md`; repository entrypoint `README.md`.
- **Classification:** FACT — project record structure and workflow were retrieved from the repository. DECISION — long-work requirements and platform boundaries captured in this project. UNKNOWN — host API capability and runtime behavior.
- **Next action:** cross-check the user requirements against the project record; then inspect available AgentKit and host integration surfaces, research long-horizon agent reliability/checklist practices, and refine the implementation architecture before coding.
