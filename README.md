# AI Interaction Workspace

公開AIが共通の作業資料を読み、変更を提案・検証できるためのワークスペースです。GitHubを公開コラボレーションの入口にします。

## Start here

1. AI workflow — shared procedure, evidence labels and work-mode recording ([AI_WORKFLOW.md](AI_WORKFLOW.md))
2. Repository map — where documents and tools belong ([DOCS/REPOSITORY_MAP.md](DOCS/REPOSITORY_MAP.md))
3. Workspace rules — read only the rules relevant to the task ([RULES/README.md](RULES/README.md))
4. Current state — verified status and known limits ([STATE/workspace_state.md](STATE/workspace_state.md))
5. Tasks — actionable backlog ([TASKS/tasks.md](TASKS/tasks.md))
6. AgentKit — environment discovery and engineering helpers ([TOOLS/AgentKit/README.md](TOOLS/AgentKit/README.md))
7. GitLab parity audit — migration mapping and intentional omissions ([DOCS/GITLAB_PARITY_AUDIT.md](DOCS/GITLAB_PARITY_AUDIT.md))

## For AI coding agents

- AGENTS.md is the short cross-agent entry point.
- CLAUDE.md points Claude Code to the same canonical workflow.
- Do not load every rule file by default. Read only the rules relevant to the task.
- Keep facts, interpretations, decisions, unknowns, test results and limitations distinct.
- Before opening a PR, record the changed paths with AgentKit and review the public-safe ledger entry.

## Repository layout

| Path | Purpose |
|---|---|
| RULES/ | Canonical collaboration and safety rules |
| DOCS/ | Navigation, source boundaries, parity audit and GitHub workflow |
| STATE/ | Shared verified state and known limitations |
| TASKS/ | Actionable backlog |
| TOOLS/ | Reusable tools and tests |
| PROJECTS/ | Project-specific plans, separate from global instructions |
| LOGS/change-ledger.jsonl | Append-only actor/mode/path provenance |

## Public/private boundary

This repository is public. Do not add raw conversations, personal data, credentials, private source material or private workspace URLs. Ledger records must contain only concise, public-safe summaries and changed paths. Never put prompts or sensitive data in them. See [public-data rules](RULES/PUBLIC_DATA_RULES.md).

## Source and migration

This repository was prepared from the public [GitLab AI Integration Workspace](https://gitlab.com/ai-work-space2/ai-integration-workspace), with links and layout adapted for GitHub. The [parity audit](DOCS/GITLAB_PARITY_AUDIT.md) explains which items were preserved, transformed or intentionally omitted.
