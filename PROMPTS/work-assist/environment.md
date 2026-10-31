# environment — 環境探査と AgentKit
他: [workflow](workflow.md) / [debug-and-reuse](debug-and-reuse.md)

## 環境探査
コマンド存在≠機能可用 / ホスト≠ゲスト / 共有領域≠権限。対象名・版が既存ファイル・履歴から分かるなら質問より先に確認。

目的に必要な項目だけ: OS/実行層/版/CPU・ABI/パス/権限/実行入口。README/設定/ソース/テスト/CI/ログ/履歴/`--help`を調べ、例にない確認も目的に応じて足す。

### 共通コマンド例
    pwd
    uname -a
    command -v python3 && python3 --version
    command -v node && node --version
    find . -maxdepth 2 -type f | grep -E '(^|/)(README[^/]*|AGENTS[.]md|package[.]json|Cargo[.]toml|pyproject[.]toml|CMakeLists[.]txt|Makefile)$' || true

### 特殊環境(該当のみ)
- .mcaddon: ZIP検査後 BP/RP・manifest・UUID・依存・root階層。`file` / `unzip -t` / `unzip -l` または `python3 -m zipfile`
- Wine: 版・WINEPREFIX・EXE形式・アーキテクチャ・prefix内外パス
- Samsung/Android: manufacturer/release/abi、Termux、ストレージ権限、BG制限、DeX
- Proot: ホストTermuxとゲストを分離。実行場所/PATH/ABI/共有ストレージ。root権限や完全隔離ではない

### コマンドがないとき
PATH → 別実行層(ゲスト/ホスト) → 既存ツール → AgentKit

## AgentKit
出所: https://github.com/KAITO9999/AI-interaction-Workspace/tree/main/TOOLS/AgentKit  
Python標準ライブラリ中心。実行前に該当CLIの `--help` を確認。探査・静的検査の出力は動作の証明ではない。

| 用途 | 入口 |
|---|---|
| 環境/既知コマンド | `agentkit.py probe` |
| PATH一覧(実行しない) | `agentkit_ext.py commands` |
| TS compile/check(既存tscのみ) | `agentkit_ext.py compile-ts` |
| addon静的監査 / スマホ静的計画 | `audit-addon` / `mobile_test.py` |
| 変更記録(actor/mode) | `record-change`。生プロンプト・トークン・個人情報は書かない |
| 不足コマンド代替 | `agentkit_resolve.py` (json-check/search/find-files/archive-list/sha256) |
| lint/repo/sqlite/artifact/context | `agentkit_work.py` (ruff/shellcheck優先、無いとき限定fallback) |
| 変更監視+検証再実行 | `agentkit_watch.py` |

自作前: probe・commands → 既存ツール → resolve。権限昇格/制限回避/認証探索はしない。`fetch-probe` は `git ls-remote` を1回だけ、初回エラー/タイムアウトで止める。重い端末ビルドは[workflow](workflow.md)に従う。
スクリプト実行不能なAIでは、ユーザー実行手順として提示する。
