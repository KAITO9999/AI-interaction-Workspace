# AI Interaction Workspace

公開AIが共通の作業資料を読み、変更を提案・検証できるためのワークスペースです。GitHubを公開コラボレーションの入口にします。

## Start here

1. **[AI workflow](AI_WORKFLOW.md)** — 最小限の作業手順
2. **[Repository map](DOCS/REPOSITORY_MAP.md)** — 何をどこに置くか
3. **[Workspace rules](RULES/README.md)** — 必要なルールだけ読む
4. **[Current state](STATE/workspace_state.md)** — 確認済みの状態と未完了項目
5. **[Tasks](TASKS/tasks.md)** — 次に行う作業
6. **[AgentKit](TOOLS/AgentKit/README.md)** — 環境探査・作業補助ツール

## For AI coding agents

- [AGENTS.md](AGENTS.md) is the short cross-agent entry point.
- [CLAUDE.md](CLAUDE.md) points Claude Code to the same canonical workflow.
- Do not load every rule file by default. Read only the rule relevant to the current task.
- Keep claims, test results, and uncertainty explicit. Never say a test passed unless it was actually run.

## Repository layout

| Path | Purpose |
|---|---|
| `RULES/` | Canonical collaboration and safety rules |
| `DOCS/` | Navigation, source boundaries, GitHub workflow |
| `STATE/` | Shared verified state and known limitations |
| `TASKS/` | Actionable backlog |
| `TOOLS/` | Reusable tools and their tests |
| `PROJECTS/` | Project-specific plans, separated from global instructions |

## Public/private boundary

This repository is public. Do not add raw conversations, personal data, credentials, private source material, or private workspace URLs. See [public-data rules](RULES/PUBLIC_DATA_RULES.md).

## Source and migration

This repository was prepared from the public [GitLab AI Integration Workspace](https://gitlab.com/ai-work-space2/ai-integration-workspace), with links and layout adapted for GitHub. GitLab remains an historical source until each migrated item is verified.
