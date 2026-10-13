# Project documentation workflow

This document defines the single project-record format. Each active project uses exactly four canonical files:

| File | Japanese label | Purpose | What belongs here |
|---|---|---|---|
| `WORK_MODELS.md` | work models | How work on this project is carried out | Distinct work models, trigger, inputs, steps, outputs, acceptance checks and limits |
| `PLAN.md` | 予定 | Future work that has not started | Pending outcomes, priority, prerequisites and completion criteria |
| `CACHE.md` | cache | Durable knowledge | Verified facts, decisions, constraints, completed items moved from the plan, evidence and unresolved unknowns |
| `IN_PROGRESS.md` | 編集中 | Active investigation, implementation and handoff | Current scope, including bug fixes, hypotheses, modified files, checks, command results and next action |

## Required lifecycle

1. **Starting a specific project:** create or update its `WORK_MODELS.md` before implementation. Describe only work models that add a distinct procedure; merge overlapping routes and link to one canonical route rather than copying it.
2. **Planning:** put not-yet-started work in `PLAN.md`. A plan item needs a clear outcome and a verifiable completion criterion. Do not label planned work as active.
3. **Starting implementation or a bug fix:** move the item being started out of the pending list and record it in `IN_PROGRESS.md` before making code changes. Bug investigation, reproduction, regression fixes and refactors all count; do not wait until a feature is complete.
4. **Working:** update `IN_PROGRESS.md` with the current hypothesis, scope, paths touched, executed checks, exact outcomes and next step. Mark a check as passed only when its result was observed.
5. **Completing:** remove the completed item from the pending portion of `PLAN.md`, then append it to `CACHE.md` under **Completed items moved from PLAN**, including date, result and evidence. Keep runtime validation separate from static checks.
6. **Handoff or pause:** leave a structured handoff entry in `IN_PROGRESS.md`. A new AI/person must be able to continue from the written record without relying on chat memory.
7. **Resuming after context loss:** follow the reread route below. Do not trust remembered state over the repository.

Do not maintain duplicate files, duplicate task lists, or alternate instructions for the same operation. One fact or procedure has one canonical home; other files link to it. A historical alias is allowed only when required for compatibility and must point to the canonical file without duplicating its content.

## Handoff format for command results

Use one entry per handoff or tightly related command set in the project's `IN_PROGRESS.md`. Keep output concise and transferable:

- **Record:** timestamp and short ID
- **Actor:** AI or human
- **Work mode:** online, offline or mixed, based on the route actually used
- **Purpose / scope:** what was checked and which paths were involved
- **Command:** exact command and working directory
- **Result:** exit code/status and the relevant stdout/stderr excerpt; never paraphrase a failure as success
- **Evidence:** artifact/log path or source link, if one exists
- **Classification:** FACT, INTERPRETATION, DECISION or UNKNOWN
- **Next action / receiver:** what the next worker should do

Do not paste huge logs, secrets, raw private prompts, personal data or machine-local paths into the public repository. Store large safe logs as artifacts when available and cite their path. If no durable artifact exists, include only the minimum relevant output and state that the full output was not saved.

## Prompt reading and rereading route

Every new task and every resumption after a context switch must start with this short route:

1. Read [AGENTS.md](../AGENTS.md) and [AI_WORKFLOW.md](../AI_WORKFLOW.md).
2. Read [workspace state](../STATE/workspace_state.md), [task list](../TASKS/tasks.md), and [repository map](REPOSITORY_MAP.md).
3. If a specific project is in scope, read that project's `WORK_MODELS.md` and `IN_PROGRESS.md`; open `PLAN.md` or `CACHE.md` only as needed for that task.
4. Follow the relevant entries in the [rules index](../RULES/README.md) and the [prompt/use-case index](../PROMPTS/README.md). Do not load unrelated project caches or every rule file by default.
5. Re-read the same route after context loss or when resuming work. This deliberate reread is required; it is not replaced by chat history or memory.

## Required checks before closing a work set

- Check that every project-specific path referenced from navigation or prompts exists.
- Check links in all Markdown files, not only the files just edited.
- Confirm every active project has the four-file format and every plan item has completion criteria.
- Confirm active bugs/implementation are in `IN_PROGRESS.md`, and completed items have been moved from `PLAN.md` into `CACHE.md` with evidence.
- Confirm a reader can reach the format rule from [AGENTS.md](../AGENTS.md), [AI_WORKFLOW.md](../AI_WORKFLOW.md), [repository map](REPOSITORY_MAP.md), and [project index](../PROJECTS/README.md).
- Record actual test results and unresolved validation; do not claim that an unrun check passed.
