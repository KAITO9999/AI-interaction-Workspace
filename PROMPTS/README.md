# Prompt and instruction routing

Index only. Canonical text lives in one place; this file routes by purpose.

## By purpose

| Purpose | Canonical entry | Use |
|---|---|---|
| Every task / resume after context loss | [AI workflow](../AI_WORKFLOW.md) | Re-read the common procedure and current state |
| Agent startup | [AGENTS.md](../AGENTS.md) | Short cross-agent entry |
| Claude Code startup | [CLAUDE.md](../CLAUDE.md) | Surface-specific entry; reuses AGENTS + workflow |
| Non-trivial work procedure (investigate/design/implement/verify) | [work-assist workflow](work-assist/workflow.md) | On-demand steps; not for one-line edits |
| Environment / missing commands / AgentKit | [environment](work-assist/environment.md) | Probe before inventing tools |
| Bugs / reuse / upstream merge | [debug-and-reuse](work-assist/debug-and-reuse.md) | Reproduce, minimize, integrate without bulk overwrite |
| Structure / versioning / language migration | [quality-and-migration](work-assist/quality-and-migration.md) | Residues, SemVer, JS/TS/Rust choices |
| External research / writing instructions | [research-and-instructions](work-assist/research-and-instructions.md) | Search, evidence, prompt design |
| Project structure and lifecycle | [Project workflow](../DOCS/PROJECT_WORKFLOW.md) | Four-file model and handoff |
| Constraint selection | [Rules index](../RULES/README.md) | Open only task-relevant rules |
| Tool discovery | [AgentKit AI usage](../TOOLS/AgentKit/AI_USAGE.md) | Probe installed tools first |
| Publishing | [GitHub workflow](../DOCS/GITHUB_WORKFLOW.md) | Branch, validation, PR |
| Data boundary | [Public/private](../DOCS/SPACE_CLASSIFICATION.md) | Filter before public publish |

## Duplication policy

- Do not paste the full canonical workflow into agent-specific entry files.
- Do not create a separate prompt for an operation already described in a rule or tool guide; link instead.
- Add a use-case entry only when it has a distinct trigger, input, output, and verification method.
- After context loss, re-read the short mandatory route. Do not trust remembered instructions or state.
- Project-specific procedures stay in that project's `WORK_MODELS.md`; live activity stays in `IN_PROGRESS.md`.

## Role and perspective (anti-meta drift)

- Stay one agent role. Do not invent committees, multi-persona debates, or virtual reviewers unless the user explicitly asks.
- Do not replace concrete checks with "from X's perspective" narration.
- Prefer: action → target → verification. Avoid abstract meta-commentary that does not change the next command or edit.
