# research-and-instructions — 調査・検索発想・指示書
他: [workflow](workflow.md) / [debug-and-reuse](debug-and-reuse.md)

## いつこのファイルを開くか
初回に全mdを読まない。次に該当するとき開く。
- UI設計・画面構成・アクセシビリティ
- ビジュアル/見た目の改変・視認性
- 性能・実装の「既存の良い案」を先に探す
- 検索語自体が思い浮かばない／再発明しそう
- 指示書・スキルの書き方を直す

## 調査の原則
外部情報が実装・設計・性能・互換・信頼性の判断を変え得る場合に調べる。検索量自体を成果としない。
仕様/版は公式・ソース・テスト、実動作は再現とログ、研究上の効果は方法・比較条件・限界が明示された研究を重視。

## 手順
1. 問い/対象/版/環境/制約/成功条件を決める
2. 既知実装・公式仕様・ソース/テストを確認し不確定点を質問に分解
3. **検索発想を先に広げる**（下記）。必要なら「この分野の検索語の作り方」自体を短くWeb検索してから本検索する（AI単独の語彙に閉じない）
4. 日本語と英語で検索。別名/規格名/実装名/エラー文へ広げる。地域差が効くときだけ多言語
5. 現行案だけでなく別方式・失敗例・反証・限界を探す
6. 使う情報だけ作業MDへ記録し結論/実装/検証へ接続。リンク集だけで終えない
7. 独立根拠が増えず判断が変わらない見込みなら止める。未解決は`未確認`

## 目的別の検索（主な意図）

### UI設計
専門のUI/UX資料・パターン・ガイドラインを先に当たる。フレームワーク名＋pattern / accessibility / information architecture。
例: `[framework] navigation pattern` / `mobile form usability guidelines` / `WCAG [component]` / `design system [topic]`

### ビジュアル改変
人間の視覚・コントラスト・階層・既存の良い作例を探す。感覚だけで決めない。
例: `visual hierarchy contrast spacing` / `color accessibility APCA OR WCAG` / `[genre] UI reference` / `motion accessibility vestibular`

### コード最適化・規定案
先に「既に良い実装・定石・ライブラリ」があるか探す。再発明より引用・組み合わせ・差分改善。
例: `[problem] best practice [language]` / `[algorithm] reference implementation` / `[library] vs [library] [workload]` / `site:github.com [topic] awesome OR cookbook`

### 検索発想の広域化
思いついた語だけで打ち止めにしない。同義語・失敗語・規格名、必要なら検索戦略の記事を1回当てる。
例: `how to search [domain] literature` / `[domain] taxonomy OR glossary` / 多言語は概念単位で変換（逐語訳しない）

| 範囲 | 使い方 |
|---|---|
| 日本語 | 国内事例・用語・利用者報告 |
| 英語 | 公式・論文・上流実装 |
| 中国語など | 地域実装が判断を変えるときのみ |
| 同一論文の翻訳転載 | 独立根拠に数えない |

## 根拠の評価
- API/版/構文: 対象版の公式・ソース・テスト
- 実動作: 再現、終了状態、ログ。Issueは版と条件を追う
- 性能: 測定法・比較条件・母数・制約。一事例を一般則にしない
- 衝突: 条件差を説明。出典の強さで機械的順位を付けない

## 検索型（短例）
- 仕様: `[tool] [version] official docs` / `changelog breaking`
- 不具合: `"[exact error]" [version]` / `limitations` / `minimal reproducible`
- 性能: `[A] vs [B] benchmark [same workload]` / `failure modes trade-offs`
- 依存: `[package] CVE OR GHSA` / `Android minSdk [level]` / `Termux aarch64`

## 指示書の設計（間違えにくさ・性能）
- 一文は「対象/条件→行動→確認できる結果」。再確認強制より、先に確認する書き方へ
- 一般知識の羅列より、制約・選択基準・検証・失敗時切替
- コメント指示: Why（制約・例外・非自明な選択）のみ。Whatの重複禁止
- 常時指示は短く。長い手順・検索式は本ファイル等の必要時資料へ
- 規則数を増やしすぎない。追加前に重複と文字数増の悪化を確認
