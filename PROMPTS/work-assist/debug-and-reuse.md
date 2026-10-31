# debug-and-reuse — 不具合調査・再利用・上流統合
他: [workflow](workflow.md) / [environment](environment.md) / [research-and-instructions](research-and-instructions.md)

## 不具合調査
再現→最小化→切り分け→仮説を1つずつ検証→最小修正→再現・回帰。同一修正2回失敗で止め、仮説か経路を変える。原因未確定のまま修正を重ねない。

1. 現象確定: 期待/実出力/操作/版/環境。ログは関連範囲と前後。再現しない場合は[environment](environment.md)
2. 最小化: 入力/設定/コードを削って再現を保つ
3. 切り分け: 動いていた版との差分 / bisect / 入力・設定・依存の二分
4. 基準照合: 仕様/型/単位/戻り値/不変条件/テスト期待と実装。実行できても意図に反するケースを含める
5. 既知事例: 正確なエラー文/適用版の上流Issue・PR/変更履歴/修正済みテスト
6. 原因不明・複数仮説・再失敗時: 作業ファイルに「仮説 | 根拠 | 反証テスト | 結果」
7. 原因に対する最小修正 → 再現テスト → 回帰

失敗継続時: 失敗済みパターンを避け、前提(版・設定・環境変数・権限・パス)/データ流/呼び出し順/依存更新を調べる。上流履歴・別実行経路・実環境へ広げ、仕様・入力・ログも一次情報で再確認。

観点(関連のみ): 境界/空・重複/日時TZ/文字コード・改行/条件優先/初期化/非同期・競合/キャッシュ失効/副作用・例外/設定優先度/パス権限/単位丸め/版差。検索式は[research-and-instructions](research-and-instructions.md)。

## 再利用と改善
新規前に標準機能/既存ツール/定石/保守中ライブラリを探し、要件に合う候補だけ比較。

1. 要件を3〜5行: 入出力/対象版/環境/制約
2. 候補: 言語・FW標準 / 既存CLI・API / 保守中ライブラリ / 実績サンプル / 手元既存コード
3. 比較: 版互換/依存の重さ/ライセンス/保守(最終リリース・Issue)/安全性/副作用/導入コスト/テスト容易性
4. 順: 再利用 > 薄いラッパー > 新規。新規理由は1行
5. 採用前に最小例で対象版・環境の動作確認

レビュー観点(必要分): 方式一致/責務・依存向き/型・データ流/入力検証・権限/複雑性・重複・死コード/テスト容易性/失敗時挙動。依頼範囲内の必要改善のみ。範囲外は提案。構造基準は[quality-and-migration](quality-and-migration.md)。

## 上流統合
共通祖先を特定しローカル独自と上流を分ける。一括上書きせず小さく取り込み、統合ごとに検証。

探査例(`upstream/main`等は実環境に置換):
    git fetch upstream   # 必要な場合のみ
    git merge-base HEAD upstream/main
    git log --oneline --left-right HEAD...upstream/main
    git diff --stat $(git merge-base HEAD upstream/main) HEAD
    git diff --stat $(git merge-base HEAD upstream/main) upstream/main

取り込みは目的に応じて merge / cherry-pick を選ぶ。例を一括実行しない。

1. 独自変更を一覧保全。上流を「取込/除外/競合」に分類。削除・rename・依存・設定・API互換・ライセンスを確認
2. 競合は両側意図を読んで解決。`git checkout --conflict=diff3 path` で祖先確認。機能単位で取込、都度ビルド・テスト
3. Git無し(ZIP等): 祖先/上流/ローカル3版を揃え `diff -ru`。`git merge-file` で統合案を作り内容確認後に採用。祖先不明なら独自を先に保全し上流へ再適用
4. 統合後: 差分と関連テストで回帰検証。取込版/保持変更/除外をCHANGELOG等へ記録
