# AI workflow

This is the single canonical cross-agent workflow. Agent-specific entry files should link here rather than duplicate the instructions. Use the [prompt/use-case index](PROMPTS/README.md) to find a focused procedure.

## Required reread route

At task start, read this workflow and inspect the current branch, active task and relevant files. Read the repository map, workspace state and task list when they help locate work or establish cross-project scope; they are not a mandatory bundle for a self-contained change.

For a project-specific change, read that project's `WORK_MODELS.md` and `IN_PROGRESS.md`; consult `PLAN.md` or `CACHE.md` only when needed. Open only the rules and prompt procedures relevant to the task. After context loss, reload the active task/project state and the relevant canonical instructions rather than replaying unrelated reading steps.

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
2. Inspect the final diff. Run the repository-wide Markdown-link check once for the final PR commit through CI; run it locally only when CI is unavailable or the final commit is not covered by CI.
3. Ensure the project has the four canonical records; active work is in `IN_PROGRESS.md`, and completed items are moved from `PLAN.md` into `CACHE.md` with evidence.
4. Report scope, changed files, checks actually run/results, unverified items and next steps.
5. Keep the task open if a required validation did not run or failed.

## Evidence labels

- FACT: directly verified by source, tool output or executed test.
- INTERPRETATION: reasoned explanation, not direct evidence.
- DECISION: selected design and why.
- UNKNOWN: not yet verified.

See the [rules index](RULES/README.md) for focused details.
