# AI workflow

Use this as the single canonical workflow. Agent-specific entry files should link here rather than duplicate these instructions.

## Before changing files

1. Read this file and [the repository map](DOCS/REPOSITORY_MAP.md).
2. Read [workspace state](STATE/workspace_state.md) and the relevant task.
3. Inspect the current branch, file content, history and existing implementation before proposing replacements.
4. Declare the intended scope in the task note or PR. Do not overwrite another contributor's work.
5. Classify findings as FACT, INTERPRETATION, DECISION or UNKNOWN.

## During work

- Prefer existing, maintained tools over substitutes. Check availability, current behavior and license before reuse.
- Make the smallest coherent change; avoid unrelated formatting and duplicate prompts.
- Keep links relative for repository files and absolute only for external sources.
- Never copy credentials, personal information, raw private conversations or private materials into this public repository.
- A failure in one independent check should not suppress unrelated checks. Stop an operation when its own safety/timeout policy says to stop.
- Do not assume that an AI can access another app's private memory, conversation history, local filesystem or credentials unless a supported integration provides it.

## Explicit work mode

Every work set must state one mode in the change-ledger record:

- ONLINE — network, hosted repository, remote API or connector used.
- OFFLINE — work stayed local and used no network or remote service.
- MIXED — both local execution and remote/network access were used.

Do not infer the mode from the application name; record the route actually used. When a work set transitions between online and offline, record separate entries rather than retroactively changing an earlier one.

## Change actor and provenance

Use python3 TOOLS/AgentKit/agentkit_ext.py record-change for every PR changeset. Each record requires:

- actor: ai or human
- mode: online, offline or mixed
- a short public-safe summary
- every modified file as a repeated path argument

ai marks files created or materially edited by an AI agent; human marks changes authored directly by a person. If a PR includes distinct AI and human edits, add separate records with the respective path sets. This is a workflow label, not cryptographic proof of identity.

Records append to LOGS/change-ledger.jsonl. Do not rewrite prior records or include private text. Pull-request CI verifies append-only behavior, changed-path coverage and valid actor/mode values. This makes missing attribution actionable rather than an informal convention.

## Before reporting completion

1. Run checks relevant to the change.
2. Inspect the final diff and verify local links/paths.
3. Report scope, changed files, checks actually run/results, unverified items and next steps.
4. Keep the task open if a required validation did not run or failed.

## Evidence labels

- FACT: directly verified by source, tool output or executed test.
- INTERPRETATION: reasoned explanation, not direct evidence.
- DECISION: selected design and why.
- UNKNOWN: not yet verified.

See the [rules index](RULES/README.md) for focused details.
