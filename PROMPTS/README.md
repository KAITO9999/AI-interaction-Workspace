# Prompt and instruction routing

This is an index, not a second copy of the rules. Keep complete instructions in one canonical location.

## By purpose

| Purpose | Canonical entry | Use |
|---|---|---|
| Every task / resume after context loss | [AI workflow](../AI_WORKFLOW.md) | Re-read the common procedure and current state on each new task or resumption |
| Agent startup | [AGENTS.md](../AGENTS.md) | Short cross-agent entry; routes to the canonical workflow |
| Claude Code startup | [CLAUDE.md](../CLAUDE.md) | Surface-specific entry that reuses AGENTS.md and the canonical workflow |
| Project structure and work lifecycle | [Project workflow](../DOCS/PROJECT_WORKFLOW.md) | Four-file project model, task transitions and handoff fields |
| Constraint selection | [Rules index](../RULES/README.md) | Open only the rules relevant to the task |
| Tool discovery and use | [AgentKit AI usage contract](../TOOLS/AgentKit/AI_USAGE.md) | Probe installed tools before building substitutes |
| Publishing / review | [GitHub workflow](../DOCS/GITHUB_WORKFLOW.md) | Branch, validation, provenance, PR and merge |
| Data boundary | [Public/private boundary](../DOCS/SPACE_CLASSIFICATION.md) | Filter content before public publication |

## Duplication policy

- Do not paste the complete canonical workflow into agent-specific entry files.
- Do not create a separate prompt for an operation already described in a canonical rule or tool guide; add a link instead.
- Add a new use-case entry only when it has a distinct trigger, input, output and verification method.
- When context may have been compressed or lost, re-read the short mandatory route. Do not attempt to save reading time by trusting remembered instructions or state.
- Project-specific procedures belong in that project's `WORK_MODELS.md`; current activity and transferable command results belong in `IN_PROGRESS.md`.
