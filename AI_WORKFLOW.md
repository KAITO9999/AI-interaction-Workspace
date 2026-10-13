# AI workflow

This is the single canonical cross-agent workflow. Agent-specific entry files should link here rather than duplicate the instructions. Use the [prompt/use-case index](PROMPTS/README.md) to find a focused procedure.

## Required reread route

Run this route at the start of every new task and whenever work resumes after a context switch or possible context loss. Do not rely on chat history or remembered state in place of these files.

1. Read this file and the [repository map](DOCS/REPOSITORY_MAP.md).
2. Read [workspace state](STATE/workspace_state.md) and [the task list](TASKS/tasks.md).
3. If one specific project is in scope, reread its [work models](PROJECTS/README.md) entry and `IN_PROGRESS.md`; read its `PLAN.md` or `CACHE.md` only as needed. The canonical record format is in [Project documentation workflow](DOCS/PROJECT_WORKFLOW.md).
4. Use [the rules index](RULES/README.md) to open only the rules relevant to the task.
5. Inspect the current branch, target files, relevant history and active work before editing. State scope before changes.

This route is intentionally short: reread the canonical workflow and current state every time, but do not bulk-load unrelated projects, caches or every rule.

## During work

- Prefer existing, maintained tools over substitutes. Check availability, current behavior and license before reuse.
- Make the smallest coherent change; avoid unrelated formatting and duplicate prompts/procedures. Maintain one canonical home per fact and operation.
- Keep links relative for repository files and absolute only for external sources.
- Never copy credentials, personal information, raw private conversations or private materials into this public repository.
- A failure in one independent check should not suppress unrelated checks. Stop an operation when its own safety/timeout policy says to stop.
- Do not assume an AI can access another app's private memory, conversation history, local filesystem or credentials unless a supported integration provides it.

## Project work model and lifecycle

When starting work on a specific project, create or update its `WORK_MODELS.md` before implementation. All active projects use exactly four canonical files: `WORK_MODELS.md`, `PLAN.md`, `CACHE.md` and `IN_PROGRESS.md`. Follow [their format, transition and handoff rules](DOCS/PROJECT_WORKFLOW.md).

- Put not-yet-started work in `PLAN.md`, with acceptance criteria.
- Before editing code for an implementation, bug fix, reproduction, regression investigation or refactor, move the active item from the pending plan to `IN_PROGRESS.md`.
- On completion, remove the item from the pending plan and add a dated result and evidence to `CACHE.md` under the completed-items section.
- For AI/person handoff, record commands, working directory, exit/status, relevant output, evidence, classification and next action in `IN_PROGRESS.md`. Avoid raw huge logs and private data.
- Eliminate overlapping work models and duplicated routes; link to canonical instructions instead of copying them.

## Explicit work mode

Every work set must state one mode in the change-ledger record:

- ONLINE — network, hosted repository, remote API or connector used.
- OFFLINE — work stayed local and used no network or remote service.
- MIXED — both local execution and remote/network access were used.

Do not infer the mode from the application name; record the route actually used. When a work set transitions between online and offline, record separate entries rather than retroactively changing an earlier one.

## Change actor and provenance

Use `python3 TOOLS/AgentKit/agentkit_ext.py record-change` for every PR changeset. Each record requires actor (`ai` or `human`), mode (`online`, `offline` or `mixed`), a short public-safe summary and every modified file as a repeated path argument. If a PR includes distinct AI and human edits, add separate records with their respective paths.

Records append to `LOGS/change-ledger.jsonl`. Do not rewrite prior records or include private text. Pull-request CI verifies append-only behavior, changed-path coverage and valid actor/mode values. This is a workflow label, not cryptographic proof of identity.

## Before reporting completion

1. Run relevant checks and distinguish static inspection from runtime tests.
2. Inspect the final diff and check Markdown links across the repository, not only the edited files.
3. Ensure the project has the four canonical records; active work is in `IN_PROGRESS.md`, and completed items are moved from `PLAN.md` into `CACHE.md` with evidence.
4. Report scope, changed files, checks actually run/results, unverified items and next steps.
5. Keep the task open if a required validation did not run or failed.

## Evidence labels

- FACT: directly verified by source, tool output or executed test.
- INTERPRETATION: reasoned explanation, not direct evidence.
- DECISION: selected design and why.
- UNKNOWN: not yet verified.

See the [rules index](RULES/README.md) for focused details.
