# HyAI と AgentKit の連携

## 役割

AgentKit は Termux 上の環境確認・限定的な代替CLI・ソースの静的確認を補います。HyAI Bridge、Lane状態、承認、外部AIへの推論依頼を置き換えません。AgentKit の結果や端末情報を外部モデルへ自動で渡す機能もありません。

## GitHubから取得・更新

上流ソースは `KAITO9999/AI-interaction-Workspace` の `TOOLS/AgentKit/` です。初回は Git で取得し、更新は対象リポジトリで差分を確認してから fast-forward します。

```sh
git clone --branch feat/agentkit-readonly-mcp https://github.com/KAITO9999/AI-interaction-Workspace.git
sh AI-interaction-Workspace/TOOLS/AgentKit/install-skill.sh
git -C AI-interaction-Workspace pull --ff-only
sh AI-interaction-Workspace/TOOLS/AgentKit/install-skill.sh
```

2回目の installer 実行前に `git diff` で取得差分を確認します。installer は上流ファイルを `~/.codex/skills/agentkit` へコピーしますが、既存の未収録ファイルを削除しません。`pull` だけでインストール済み skill が自動更新されるわけではありません。

## Termux / HyAI 内の CLI 経路

Codex skill は `~/.codex/skills/agentkit/SKILL.md` を入口にし、CLI は同じフォルダの `scripts/` にあります。まず `--help` を確認し、対象プロジェクトのパスを明示します。

```sh
SK="$HOME/.codex/skills/agentkit"
python3 "$SK/scripts/agentkit.py" --help
python3 "$SK/scripts/agentkit.py" probe --root <project-dir>
python3 "$SK/scripts/agentkit_work.py" context --root <project-dir> --target <relative-path> --start 1 --end 80 --json
```

HyAI から呼ぶ場合も Termux の既存コマンド実行・承認経路を使います。任意コマンドが HyAI に登録されていない場合は、AI に実行を求めず `HyAI commands` で現行の入口を確認します。AgentKit の静的レポートを実行・ビルド・端末実測の証拠として扱いません。

## GPT標準 MCP connector

`agentkit_mcp.py` は GPT系クライアントで使う標準 MCP サーバーです。HyAI の Bridge API とは別プロセス・別認可境界です。HTTP/Secure MCP Tunnel から利用し、設定した root の読み取り専用ツールだけを公開します。

- 既定は root 未設定で、HOME全体を自動公開しません。
- `AGENTKIT_ROOTS_JSON` に対象プロジェクトだけを登録します。
- 任意shell、パッケージ導入、書き込み、Android操作は公開しません。
- 外部MCP接続を使っても、HyAI の Lane・履歴・承認・端末stateは自動で渡りません。
- 公開 HTTPS に置く場合は認証を別途設けます。Termux上では loopback と Secure MCP Tunnel を使い、未認証HTTPを外部ネットワークへ公開しません。

## 境界

AgentKit は不足CLIをタスク別に補う補助ツールです。jq、rg、fd、unzip等の完全互換ではありません。HyAI Bridge のファイル読み書き・承認・Lane作業を実行せず、ユーザーが明示していないファイルを変更しません。
