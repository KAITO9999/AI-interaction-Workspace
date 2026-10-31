# AI Interaction Workspace

公開AIが共通の作業資料を読み、変更を提案・検証するためのワークスペース。GitHub を公開コラボレーションの入口にする。

## Start here (AI)

**毎回この短い順だけ読む。全部は読まない。**

1. [AGENTS.md](AGENTS.md)
2. [AI_WORKFLOW.md](AI_WORKFLOW.md)
3. [STATE/workspace_state.md](STATE/workspace_state.md)
4. [TASKS/tasks.md](TASKS/tasks.md)（流し読みで可）

追加はタスクに合わせて **1ファイルだけ**:

| 用途 | ファイル |
|---|---|
| 指示の振り分け | [PROMPTS/README.md](PROMPTS/README.md) |
| 地図・読み忘れ防止 | [DOCS/REPOSITORY_MAP.md](DOCS/REPOSITORY_MAP.md) |
| プロジェクト4ファイル | [DOCS/PROJECT_WORKFLOW.md](DOCS/PROJECT_WORKFLOW.md) |
| ルール索引 | [RULES/README.md](RULES/README.md) |
| ツール | [TOOLS/AgentKit/README.md](TOOLS/AgentKit/README.md) |

非自明作業の詳細手順は `PROMPTS/work-assist/` 内の **名前が内容を示す** 単一ファイルを必要時のみ開く（workflow / environment / debug-and-reuse / quality-and-migration / research-and-instructions）。

## For agents

- 新タスク・文脈喪失のたびに上記ショートルートを再読。記憶や会話履歴で代替しない
- 無関係な `PROJECTS/*` や RULES 全件、work-assist 全件を読まない
- 事実 / 解釈 / 決定 / 未確認 / 検証結果を分けて書く
- PR 前に AgentKit で変更パスを記録し、公開してよい要約だけ ledger へ

## Public / private

このリポジトリは **公開**。会話生データ・個人情報・認証情報・非公開URLを入れない。  
端末固有の長い診断ログは **[AI-interaction-Private-Workspace](https://github.com/KAITO9999/AI-interaction-Private-Workspace)**（非公開）へ。境界は [SPACE_CLASSIFICATION](DOCS/SPACE_CLASSIFICATION.md) と [PUBLIC_DATA_RULES](RULES/PUBLIC_DATA_RULES.md)。

## Layout

| Path | Purpose |
|---|---|
| PROMPTS/ | 用途別ルーティング + work-assist |
| RULES/ | 制約 |
| DOCS/ | 地図・形式・GitHub手順 |
| STATE/ | 検証済み状態 |
| TASKS/ | バックログ |
| TOOLS/ | AgentKit |
| PROJECTS/ | プロジェクト別4ファイル |
| LOGS/ | 変更 provenance |
