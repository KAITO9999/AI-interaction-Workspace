# AI Interaction Workspace

公開AIが共通の作業資料を読み、変更を提案・検証できるためのワークスペースです。GitHubを公開コラボレーションの入口にします。

## Start here

1. AI workflow — shared procedure and mandatory reread route ([AI_WORKFLOW.md](AI_WORKFLOW.md))
2. Prompt routing — purpose-based entrypoints without duplicated instructions ([PROMPTS/README.md](PROMPTS/README.md))
3. Repository map — where documents and tools belong ([DOCS/REPOSITORY_MAP.md](DOCS/REPOSITORY_MAP.md))
4. Project format — work models, plan, cache, editing and handoff lifecycle ([DOCS/PROJECT_WORKFLOW.md](DOCS/PROJECT_WORKFLOW.md))
5. Workspace rules — read only the rules relevant to the task ([RULES/README.md](RULES/README.md))
6. Current state — verified status and known limits ([STATE/workspace_state.md](STATE/workspace_state.md))
7. Tasks — actionable backlog ([TASKS/tasks.md](TASKS/tasks.md))
8. AgentKit — environment discovery and engineering helpers ([TOOLS/AgentKit/README.md](TOOLS/AgentKit/README.md))
9. GitLab parity audit — migration mapping and intentional omissions ([DOCS/GITLAB_PARITY_AUDIT.md](DOCS/GITLAB_PARITY_AUDIT.md))

## For AI coding agents

- [AGENTS.md](AGENTS.md) is the short cross-agent entry point; [CLAUDE.md](CLAUDE.md) routes Claude Code to the same canonical workflow.
- At every new task and every resume after context loss, reread the short route. Do not read all rules or project caches unless relevant.
- For a specific project, use the four-file format defined in [Project documentation workflow](DOCS/PROJECT_WORKFLOW.md): `WORK_MODELS.md`, `PLAN.md`, `CACHE.md`, and `IN_PROGRESS.md`.
- Keep facts, interpretations, decisions, unknowns, test results and limitations distinct.
- Before opening a PR, record changed paths with AgentKit and review the public-safe ledger entry.

## Repository layout

| Path | Purpose |
|---|---|
| PROMPTS/ | Purpose-based prompt and instruction routing |
| RULES/ | Canonical collaboration and safety rules |
| DOCS/ | Navigation, project format, source boundaries, parity audit and GitHub workflow |
| STATE/ | Shared verified state and known limitations |
| TASKS/ | Actionable backlog |
| TOOLS/ | Reusable tools and tests |
| PROJECTS/ | Project-specific four-file records; read only the current project |
| LOGS/change-ledger.jsonl | Append-only actor/mode/path provenance |

## Public/private boundary

This repository is public. Do not add raw conversations, personal data, credentials, private source material or private workspace URLs. Ledger records must contain only concise, public-safe summaries and changed paths. Never put prompts or sensitive data in them. See [public-data rules](RULES/PUBLIC_DATA_RULES.md).

## Source and migration

This repository was prepared from the public [GitLab AI Integration Workspace](https://gitlab.com/ai-work-space2/ai-integration-workspace), with links and layout adapted for GitHub. The [parity audit](DOCS/GITLAB_PARITY_AUDIT.md) explains which items were preserved, transformed or intentionally omitted.
