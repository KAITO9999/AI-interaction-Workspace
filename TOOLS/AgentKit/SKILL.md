---
name: agentkit
description: 環境探査・不足コマンド代替・補助CLI。PATH一覧、jq/rg/fd/unzip代替、TS/addon/mobile静的確認、lint/repo/sqlite/artifact/context、変更監視と標準MCP読み取りconnector。Termux/Proot混在や自作前の環境確認に使う。
---

# AgentKit

環境にないコマンドを補い、環境を調べるCLI群。Python標準ライブラリ中心(3.9+推奨)。スクリプトは `scripts/`。

    SK=<このSKILL.mdのフォルダ>
    python3 $SK/scripts/agentkit.py --help

実行前に `--help` を確認。出力は事実であり、プロジェクトが動く証明ではない。版: `VERSION.json` または upstream 0.1.0 系。

## 用途別

| やりたいこと | コマンド |
|---|---|
| 環境と既知コマンド | `python3 $SK/scripts/agentkit.py probe --root <dir> --json <out.json>` |
| PATH実行可能一覧 | `python3 $SK/scripts/agentkit_ext.py commands [--filter 語] [--format json\|tsv]` |
| 版一覧 | `python3 $SK/scripts/agentkit.py versions --root <dir> --output <out.md>` |
| 行範囲読取 | `python3 $SK/scripts/agentkit.py locate <file> --start N --end M` |
| 不足コマンド代替 | `python3 $SK/scripts/agentkit_resolve.py <json-check\|search\|find-files\|archive-list\|sha256> <target>` |
| 代替状況のみ | `python3 $SK/scripts/agentkit_resolve.py json-check --json-report` |
| TS compile/check | `python3 $SK/scripts/agentkit_ext.py compile-ts --root <dir> [--check]` (既存tscのみ) |
| addon静的監査 | `python3 $SK/scripts/agentkit_ext.py audit-addon <file>` |
| スマホ静的計画 | `python3 $SK/scripts/mobile_test.py --root <dir> [--profile low-end]` |
| 変更記録 | `python3 $SK/scripts/agentkit_ext.py record-change --root . --actor ai\|human --mode online\|offline\|mixed --summary "…" --path <file>` |
| lint/repo/sqlite/artifact/context | `python3 $SK/scripts/agentkit_work.py {lint-python\|audit-shell\|repo-check\|sqlite-inspect\|artifact-inspect\|context}` |
| 変更監視+検証再実行 | `python3 $SK/scripts/agentkit_watch.py --root . --watch <path> -- <cmd…>` |
| 取得経路確認 | `python3 $SK/scripts/agentkit.py fetch-probe <repo-url> --timeout 5` |

Python無し時は `sh $SK/scripts/agentkit.sh probe`(probeのみ)。`scripts/agentkit` は実装を自動選択。

## 進め方
1. probe と commands で既存ツールと形式ヒントを見る
2. 適したツールがあれば `--help` と版を見て範囲を絞って確認
3. 無いときだけ resolve の代替。JSON検証・テキスト検索・ファイル名検索・ZIP一覧・SHA-256のみ。jq/rg/fd/unzipと完全互換ではない
4. それでも足りないとき公開ソースを調べ、ライセンスと出所確認後に取込

静的検査(`audit-addon` / `mobile_test` / work系fallback)は動作確認の代わりにならない。

## 守ること
- 権限昇格・制限回避・認証探索はしない。commands はPATH上ファイルを実行しない
- record-change に生プロンプト・会話・トークン・非公開URL・個人情報を書かない。actor/modeは実際の編集側とネットワーク使用有無で決める
- 出力にユーザー名・パスが含まれることがある。公開前に確認
- fetch-probe は読み取り専用 git ls-remote を1回だけ。初回エラー/タイムアウトでその経路を止め自動再試行しない
- APK/AAB端末ビルドは高負荷のため非推奨。CI/Remoteを使う

## 報告
FACT / INTERPRETATION / DECISION / UNKNOWN を分ける。証拠なしにインストールやテスト完了を言わない。

## 詳細(必要時)
- `references/mobile-testing.md`
- `references/termux-tool-candidates.md`
- `references/AI_USAGE.md`(上流契約)
- 標準MCP接続を使う場合は `CONNECTOR.md`。HTTP/Secure MCP Tunnel向けの読み取り専用connectorとHyAI内の別経路を説明

出所: KAITO9999/AI-interaction-Workspace TOOLS/AgentKit (MIT)
