# AI workflow

Use this as the single canonical workflow. Agent-specific entry files should link here rather than duplicate these instructions.

## Before changing files

1. Read this file and [the repository map](DOCS/REPOSITORY_MAP.md).
2. Read [workspace state](STATE/workspace_state.md) and the relevant task.
3. Inspect the current branch, file content, history, and existing implementation before proposing replacements.
4. Declare the intended scope in the PR description or task note. Do not overwrite another contributor's work.
5. Classify findings as `FACT`, `INTERPRETATION`, `DECISION`, or `UNKNOWN`.

## During work

- Prefer existing, maintained tools over new substitutes. Check availability and license before reusing external code.
- Make the smallest coherent change; avoid unrelated formatting and prompt duplication.
- Keep links relative for files in this repository. Use absolute links only for external sources.
- Never copy credentials, personal information, raw private conversations, or private materials into this public repository.
- Errors in one independent check should not suppress unrelated checks. Stop a specific operation when its own safety/timeout policy says to stop.
- Do not assume the current AI can access another app's private memory, conversation history, local filesystem, or credentials unless an explicit supported integration provides it.

## Before reporting completion

1. Run the checks relevant to the change.
2. Inspect the final diff and verify local links/paths.
3. Report: scope changed, checks actually run and results, unverified items, and follow-up work.
4. Keep the task open if a required validation did not run or failed.

## Evidence labels

- `FACT`: directly verified by source, tool output, or executed test.
- `INTERPRETATION`: reasoned explanation, not direct evidence.
- `DECISION`: selected course of action and why.
- `UNKNOWN`: not yet verified.

See [the rules index](RULES/README.md) for focused details.
