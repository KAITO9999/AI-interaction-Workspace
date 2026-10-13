# ReForge Visuals implementation plan

> Project-specific planning document migrated from the public GitLab workspace. This is not a repository-wide AI instruction. Treat the status and API claims below as historical notes; verify against the target version and source before implementation.

Source file: `TASKS/ReForge_Visuals-Implementation-Plan.md` in the public GitLab workspace.

# ReForge Visuals 実装予定表（再設計版）

Status: PLANNED / IN_PROGRESS
Target: 3.18.0以降のライトシャフト軽量化・遠景キャッシュ基盤
Last reviewed: 2026-10-08

## 0. 基準

現行キャッシュで確認されている基準は ReForge Visuals 3.17.8 → 次版で、3.18.0への更新方針が既に記録されている。今回の予定表は、その上にライトシャフトの候補探索・間引き・キャッシュ・複数プレイヤー共有を追加する。

既存キャッシュで確認済み:
- 10色の LIGHT_PROFILES
- 45通りの MIXED_LIGHT_PROFILES
- 混色 block 360個（45×level 3〜10）
- playerSources / itemGroups の共通 compositeCell 経路
- custom_rain.json / default water settings
- BP/RP manifest version 3.17.8
- 次版 3.18.0 への更新方針

## 1. 今回の基本方針

### 1.1 探索と表示を完全に分離する

ライトシャフトの処理を以下の4層に分ける。

1. Surface/Candidate Cache
   - 「ライトシャフトを置ける可能性のあるブロック」の座標・必要な最小情報を保持。
   - 取得済みの biome 情報はここで再利用する。
   - 遠景ではこのキャッシュだけを使い、毎回ワールドを再探索しない。

2. Candidate Selection
   - プレイヤー位置・距離・視線方向・既存キャッシュから表示候補を絞る。
   - 5候補なら2〜3本など、一定の候補数を安定した疑似ランダムで間引く。
   - 真乱数ではなく座標/セル由来の deterministic hash を基本とし、tickごとのちらつきを防ぐ。

3. Shaft State
   - 現在表示中のライトシャフト、更新待ち、置換中を別状態として管理。
   - 更新時は新しいライトシャフトを先に生成し、生成確認後に旧ライトシャフトを消す。
   - 旧→新の瞬間的な空白を避ける。

4. Effect/Render Update
   - プレイヤーごとに表示判定を行う。
   - 同じキャッシュ候補を複数プレイヤーが参照する場合はキャッシュを共有する。
   - 実際のエフェクト状態はプレイヤー単位で持つ。
## 2. 距離・生成条件の分離

### 2.1 48 blocks をキャッシュ生成/検査の境界とする

48 blocks はプレイヤーからの**相対距離**で判定する。

- 0〜48 blocks:
  - 必要な候補探索・キャッシュ生成の対象。
  - 既存キャッシュ・既取得値は当然優先して再利用する。
  - 30 blocksは生成の禁止境界にはしない。
- 48 blocks超:
  - このプレイヤーを基準とした新規の候補生成・追加検査は対象外。
  - 既に共有region cacheへ保持されている候補は、遠景表示側から参照してよい。
- 「検出座標〜Y=0方向」の測定は、0〜48内で実際に候補として採用された座標だけに限定する。
- 既に検査した範囲は16 blocks単位へ外向きに丸め、チャンク境界と整合させる。
- 48境界は**キャッシュ生成/追加検査の対象境界**であり、既存cacheの即時消去境界ではない。

### 2.2 1〜24 blocks は「2次元候補計算」に置換

円形/四角形の面積をそのまま舐める方式を標準にしない。

- X/Zの2次元座標候補を作る。
- 各候補では、可能なら Dimension.getTopmostBlock({x,z}) を1回の表面取得として使用する。
- 取得した最大Yとプレイヤーの現在Y/必要高度を比較する。
- 最大値候補だけを周囲の充足判定へ送る。
- 周囲ブロックが規定の範囲まで埋まっていない候補は、原則としてエフェクト候補にしない。
- エフェクト生成は「最大値の座標 + 周囲の充足状態」が成立したときだけ許可する。

これにより、1〜24 blocksの検査を「面積全体の総当たり」から「2次元の候補座標 + 表面取得 + 小さい局所判定」へ落とす。

### 2.3 24 blocks周囲の精度補強

24 blocks以内は見た目の誤判定が目立つため、通常探索を増やすのではなく、候補が成立境界にあるときだけ精度補強する。

- topmost候補がある。
- プレイヤーY/最大高度との差が閾値付近。
- 周囲充足判定が不成立/曖昧。
- キャッシュが古い/dirty。

この条件のときだけ局所周囲を再確認する。

**「24 blocksだから毎回広域再探索」にはしない。**

### 2.4 初回48 blocks buffer

プレイヤーの初回読み込み時のみ、48 blocksを初期バッファとして優先取得する。

- 即時に取得処理を開始し、ロード初期のバッファとして確保する。
- 既存の共有cacheに存在する範囲は再取得しない。
- 検査領域は16 blocks境界へ丸める。
- 初回48 bufferの処理は、遠景用の5tick/2×2分散jobとは別扱いにする。
- 初回buffer完了後は差分/dirty更新へ移行する。
- 48 blocksを超えた新規追加検査は初回bufferの対象にしない。

### 2.5 256×256 region

永続キャッシュの物理的な管理単位は256×256 blocks。

- 16×16 chunk相当の固定regionとして扱う。
- regionの境界は16 blocks単位。
- region内部は密な全ブロック配列ではなく、最上層候補を中心とした疎な集合を保持する。
- 1 regionを複数プレイヤーで共有する。
- player-specific stateはregion cacheから分離する。

### 2.6 7日TTL

キャッシュ寿命はtick数ではなく実経過時間を優先する。

- lastVisitedAt / lastUsedAt を保存。
- 7日経過したregionは破棄候補。
- World.getAbsoluteTime()をTTLの主時計には使わない。
- 実時間stampを安全に永続化できる環境ならそれを使う。
- 実時間stampが安全に保存できない場合は、起動時/再訪時のTTL確認までに縮退する。
- プレイヤー不在時のプレイヤー依存状態は即時解放する。
- 共有region cache自体は、別プレイヤーが使っている場合は保持し、未使用かつTTL/距離条件を満たしたら破棄する。

## 3. 探査方式

### 3.1 4×4 local probe を基本単位にする

1〜4 blocksの近接形状判定は、4×4 blocksの局所probeを使う。

- プレイヤーを基準に、前後左右4方向を開始地点として回す。
- 4方向のprobeを同tickへ集中させず、**プレイヤー単位で3tick分散**する。
- 同じ4×4 tileの重複検査を禁止する。
- 各probeの結果は共有cacheへ保存する。
- player-specificな表示判定はprobe結果から別途行う。

4×4 probeは「4 blocks半径全域を毎tick総当たりする」意味ではなく、候補生成と局所形状判定のための小さな窓として扱う。

### 3.2 5tick/2×2 は遠景キャッシュの基本job

- 1 job = 2×2 blocks。
- 5tickを基本間隔として次のjobへ進む。
- Performance Engineの既存queue/budgetを使用。
- 同一座標/同一tileの重複投入を禁止。
- この分散方式は**遠景キャッシュ生成/補完を主対象**とする。
- 初回48 bufferの即時取得処理とは別の経路にする。
- 48 blocks超の新規探索へは使用しない。

### 3.3 16 blocks丸め

検査範囲はブロック座標のまま扱うが、探索job/region/cache keyは16 blocks境界へ丸める。

- 開始時にfloor/ceilで16 blocks単位へ整列。
- 探査中にプレイヤーが境界を跨いだ場合も、region/chunk単位で差分化。
- 4×4 local probeの結果をそのままregion構造へ詰めず、親chunk/regionへ収容する。
- これにより「同じ地形を細切れ座標として再取得する」ことを防ぐ。

## 4. 軽量検出とtopmost置換

### 4.1 getTopmostBlock を主経路へ

ライトシャフトの候補が地表/最上面を基準に作れるなら、Y方向総当たりを廃止し getTopmostBlock({x,z}) を主経路にする。

候補成立の順序:

1. X/Z候補座標を作る。
2. topmostを取得。
3. プレイヤー現在Y/最大高度との差を確認。
4. 近傍ブロックの充足状態を少数取得。
5. 成立時だけエフェクト候補化。
6. 必要な候補だけ下方向へ測定し最終的な地面位置を確定。

getTopmostBlockで仕様を満たせないケースだけ、局所getBlockへフォールバックする。

### 4.2 上空の誤判定

プレイヤー頭上が埋まっている場合、単純な真上の1点だけでは誤判定が起こる。

対策:

- 上側と下側の支持状態を別々に取得。
- 候補Yが近い場合は、座標差分を追加判定。
- 4 blocks以内の相互近傍が存在する極近接ケースでは、4×4 local probeの結果を併用。
- 近傍が「光の通り道」と整合する場合のみ候補を復帰。
- それ以外は遮蔽扱い。

### 4.3 5本ray方式

Dimension.getBlockFromRay() を、ダミーentityの代替となる**補助ゲート**として使う。

- 最大5本程度。
- 4方向を中心に、必要時のみ斜め/上向き成分を追加。
- 8 / 16 / 24 blocksの近距離境界推定に使う。
- maxDistanceを小さく設定し、近距離だけを見る。
- includePassableBlocks / includeLiquidBlocks は用途別に明示する。
- rayで得た遮蔽方向はN-way方向maskへ変換する。

5本rayは最終候補を生成する主探索ではなく、「どこから先をcache探索へ渡すか」「どの方向を閉じるか」を決めるために使う。

### 4.4 ダミーentity方式

透明ダミーを5体飛ばす方式は、第一実装には採用しない。

理由は、検出のためだけにentityのspawn/despawn・移動・ライフサイクルを維持するため。

同等の情報がrayで取れる場合は、entity方式よりray方式を優先比較する。

### 4.5 N-way方向判定

シャフトの方向は「候補がある/ない」だけでなく、衝突方向をbitmask化する。

- 4-wayを基本。
- 4-wayで曖昧な場合だけ8-wayへ拡張。
- blocked north/east/south/west等を記録。
- blocked方向へはシャフトを生成しない。
- 開口方向だけを終端候補として束ねる。
- プレイヤーが近くへ来ない限り、この方向判定は再計算せずcacheへ保持する。

## 5. キャッシュ構造・更新

### 5.1 共有cache

cache key:

dimension + region + chunk + cell/coordinate

保持情報:

- candidate coordinate
- topmost Y
- eligibility
- biome
- foliage/glass分類
- attenuation inputs
- direction mask
- lastVerifiedAt/Tick
- lastUsedAt
- dirty
- residency tier

player側:

- visible candidate set
- active shaft set
- effect state
- last position/cell
- last velocity
- last direction
- current sun/time factor

### 5.2 変更通知

再探索ではなくdirty化を主経路にする。

- playerPlaceBlock
- playerBreakBlock
- piston
- explosion
- 必要な追加変更イベント

イベントで変更を捕捉した座標だけをdirty化し、未変更領域を再走査しない。

### 5.3 近傍優先

更新優先度:

1. 現在表示中のshaft
2. 0〜24の既取得値/近接候補
3. 24〜48の未取得/dirty候補
4. 24 blocks以内の曖昧候補の精度補強
5. 48超は新規検査せず既存共有cacheの参照のみ
6. eviction

## 6. 透過・遮蔽・ブロック分類

### 6.1 葉っぱ

葉を一般solidと同一扱いにしない。

優先順位:

1. 既知のfoliage/leafタグ分類
2. 必要ならtypeIdの静的lookup
3. 既存のRP側分類との整合確認

葉っぱ等の透過では:

- 完全遮蔽より弱い減衰。
- 木本体などの不透過ブロックより低い阻害強度。
- 十字1ブロックだけで閉じず、必要なら1ブロック先まで光路候補を維持。

ただし、Script APIだけでRPのculling定義そのものを「配置済みか」と照会できるとは確認できていないため、runtimeでculling存在を推測しない。

### 6.2 culling情報

Microsoft Learnでは、custom blockのminecraft:geometry.cullingおよびculling_layer:leaves、block culling rulesが定義可能。

そのため:

- RP側に既知のculling定義がある場合は、その仕様を静的な分類表として利用する。
- runtimeから未確認のculling情報を直接読める前提にはしない。
- 「leaf専用cullingが置かれているか」は実装前にRP定義を確認してから確定する。

### 6.3 ガラス

ガラス系は「完全遮蔽ブロック」として扱わない。

- 通常ガラスはray/column走査のスキップ候補。
- 色付きガラスは同じく光路を継続し、色だけを微量付与する。
- ガラスを抜けた後、さらに先の地面/最上面を再取得する。
- 同一座標でガラスを何度も読まないよう、分類結果をcacheする。
- 透明/透過の厳密度は既存RPのmaterial/culling設定と照合して確定する。

### 6.4 海・水面特殊条件

海の上などの専用探索は、見た目への寄与が小さいなら標準探索から外す。

- water/liquidはrayのstop条件を用途ごとに設定。
- 水面専用の広域地形探索を新規に増やさない。
- 既存biome判定を最終ライトシャフト生成時に再利用する。

## 7. ライトシャフトの近接形状

### 7.1 開始位置

検出はプレイヤーの**頭位置の1ブロック上**を基準に開始する。

Script APIにはEntity.getHeadLocation()があるため、固定Yオフセットだけを前提にせず、頭位置から基準点を作る。

### 7.2 1〜4 blocksを基本半径

標準の近接シャフトは1〜4 blocksを最大基準とする。

- 1〜4は完全成立範囲。
- 5 blocks付近で自然に消える。
- 1〜9を標準最大値にはしない。
- 1〜6 / 1〜7 / 1〜9は既定値から外し、必要時の比較用にのみ残す。

### 7.3 充足率で減衰

「ブロックが埋まった領域」を減衰の主入力にする。

基本プロファイル値:

| 半径 | 透明度/表示強度候補 |
|---|---:|
| 1 | 65% |
| 2 | 100% |
| 3 | 80% |
| 4 | 60% |
| 5 | 0%（消失） |

注意:
- この数値がalphaなのかtransparencyなのかは、現行テクスチャ/RPの意味に照らして実装時に確定する。
- 表記値の意味を勝手に反転しない。

### 7.4 中心遮蔽と外周遮蔽

中心が埋まった場合:

- 強く減衰。
- シャフト中心を開口方向へ少し外へ移す。
- 近傍の開口が別方向へ分かれたら分岐候補化。

外周が埋まった場合:

- 3 blocks周辺の開口へ寄せる方向を優先。
- 開口が1つなら1束。
- 2つなら2束。
- 3つに分離した場合は3-way候補を論理上生成してもよいが、通常renderでは2束を上限とし、追加設定時だけ3-wayを許可する。

これにより、通常負荷を増やさず「穴が多段で分離した場合だけ分岐する」。

## 8. 太陽時刻・方向・明るさ

### 8.1 World timeを方向補助に使う

World.getTimeOfDay()で0〜24000 tickの時刻を取得できる。

- 朝/昼/夕方で方向バイアスを変える。
- プレイヤー位置・candidate終端との差ベクトルと合成する。
- 厳密な太陽ベクトルAPIが確認できていないため、最初は**近似的なworld-time bias**として扱う。
- 見た目が合わない場合は、方向変化量を小さくして地形終端を優先する。

### 8.2 3tickごとの方向更新

- candidate終端とプレイヤー位置との差から基準方向を算出。
- 3tickごとに目標方向を更新。
- 表示側は前回方向から目標方向へ補間し、急旋回を避ける。
- 理論上成立しない角度は拒否。
- 近づくほど2束の表示強度を上げ、最終的に不要な束を削減して自然に減光する。

### 8.3 2×3 texture unit

直線状の最大テクスチャ単位は2×3を上限とする。

- 真っすぐなshaftは2×3 unitを優先。
- 方向が曲がる場合は複数unitの継ぎ合わせへ落とす。
- 1×4以上の単一unitへ膨張させない。
- 既存RPで2×3が表現可能かは実装前に確認する。

## 9. 回折光・4 blocks近傍補助

### 9.1 デフォルトOFFの設定

「回折光の強化」を独立設定として用意する。

- default: OFF
- OFF時は通常の直進/近似束ねのみ。
- ON時のみ4 blocks近傍の回り込み判定を有効化。

### 9.2 4 blocks相互検査

極近接で光が存在する場合:

- 対向方向から4 blocks以内を取得。
- 相互の候補をcache。
- 回り込み成立条件を満たす方向のみ許可。
- **30tickは目標間隔**とし、固定タイマーを新設しない。
- 既存Performance Engineの**Mix-Tick判定箇所へこの処理を代入**し、Mix-Tick側のbudget/順序に従って実行する。
- playerごと・candidateごとに個別判定する。
- プレイヤーが近づいていない状態では再計算しない。
- Mix-Tickが遅延した場合は30tickを厳密なdeadlineとせず、次に許可されたMix-Tick枠でcatch-upする。

### 9.3 表示

回折成立時:

- 天井にわずかにめり込む開始位置を許容。
- ただしめり込みで黒色化しない。
- 可能なら通常より少し広いshaftを使う。
- 2-way/3-way分離は形状が明確な場合のみ。

render methodやmaterialが色/alphaを暗化する可能性はあるため、RP実装時に実ワールドで確認する。

## 10. 束ね・間引き・終端

### 10.1 deterministic thinning

5候補なら2〜3候補などの間引きを行う。

- tickごとのMath.random()は使わない。
- 座標/region/candidate ID/固定seed等からdeterministic hashを作る。
- 空間分散を先に行い、その後hashで選ぶ。

### 10.2 終端比較

中間候補すべてを保持せず、始点と終端を比較して統合する。

- 終端が近い → 1束。
- 終端方向が分離 → 2束。
- 明確な3-way回折時だけ3候補を論理保持し、通常renderでは2束へ縮退可能。

## 11. 更新・置換

更新順序:

1. 新candidate決定
2. 新shaft生成
3. 新shaftの成立状態を確認
4. 旧shaft削除
5. 旧state解放

更新中の空白を作らない。

また、candidateが無効になっても即座に全消去せず、

- 新shaftを上側/有効位置へ生成
- 旧shaftを即時に短時間で解放
- 次のstateへ移行

として、ちらつきを抑える。

## 12. Player-specific effect

- cacheは共有。
- effect stateはplayerごと。
- 表示候補はplayer position + view direction + active stateから決定。
- getViewDirection()は候補順位付けに使うが、毎tickの完全視錐台計算はしない。
- 複数playerが同じcandidateを見る場合、探索は共有し、表示状態だけ分離する。

## 13. 高速移動

速度が約5 blocks/s以上の場合:

- 新規遠景探索を延期。
- 現在表示中のeffectを維持。
- 差分cacheのみ最低限処理。
- 速度低下後にcatch-up。

速度はEntity.getVelocity()から取得し、毎tickで同じ値を再計算しない。

## 14. Performance Engine / Performance Tier

### 14.1 既存Performance Engineを使用

新schedulerを増やさない。

優先順:

1. active effect update
2. shaft replacement
3. local 4×4 probe
4. dirty candidate
5. 30超〜48のcache generation
6. 48超prefetch
7. 7日TTL/eviction

各jobは既存queue/budgetへ入れる。

### 14.2 Performance Tier gate

高負荷環境への配慮として:

- Performance Tier 1〜2では、この高度なReForge Visuals機能を**デフォルトOFF**。
- userがONにした場合のみTier 2〜5の処理範囲を利用可能にする。
- Tier 3〜5は同じ1〜4 blocks基本半径を土台とする。
- Tierによる差は、最大半径を1〜6/1〜7/1〜9へ増やす方向ではなく、検査頻度・候補数・分岐許可などで調整する。
- Tier 1〜2でONにしても、budget超過時は自動的に遠景探索から縮退する。

これにより、視覚サイズをPerformance Tierに連動させすぎず、負荷だけを制御する。

## 15. 廃止/縮小

- 毎tickの48 blocks全面走査
- 1〜24の円/四角面積総当たり
- 0〜30の新規cache生成
- Y方向の総当たり（topmost代替可能な場合）
- 5体dummy entityを常駐させる検出
- 毎更新の真乱数
- 変更されていないregionの再検証
- ガラスを何度も同じ座標で再判定
- 1〜9を標準最大半径にすること
- 旧shaftを先に消す置換順序

## 16. 実装順序

### Phase 0 — 基礎監査

- [ ] 現行shaft生成経路を特定
- [ ] 現行候補探索APIと呼出頻度を計測
- [ ] 現行Performance Engine queue/budgetを確認
- [ ] 現行biome経路を確認
- [ ] 現行RPでshaftがblock/entity/particleのどれで描画されるか確認
- [ ] 既存LIGHT_PROFILES / MIXED_LIGHT_PROFILESのTier対応を確認
- [ ] 透明度65/100/80/60の意味を確認
- [ ] 16 block丸めが既存cache keyと衝突しないか確認
- [ ] 実時間stampの保存方式を確認
- [ ] RP culling定義の有無を確認

Done:
- 現行の重さ・描画方式・保存方式を根拠付きで説明できる。

### Phase 1 — 30/16/256 cache境界

- [ ] 0〜48 cache generation
- [ ] 48超の新規検査対象外
- [ ] 検査範囲16 blocks丸め
- [ ] 256×256 region
- [ ] 共有cache
- [ ] 7日real-time TTL
- [ ] 256超eviction
- [ ] player-specific state即時解放

Pass:
- 同一座標の重複生成がなく、cache境界がplayer距離と混同されない。

### Phase 2 — topmost/2D候補

- [ ] 1〜24を2D候補計算へ
- [ ] getTopmostBlock主経路
- [ ] player Y / max height比較
- [ ] 近傍充足判定
- [ ] 下方向〜Y=0の必要時測定
- [ ] 上空埋まり誤判定対策

Pass:
- 面積全面走査よりAPI呼出を削減し、candidate結果を維持。

### Phase 3 — local 4×4 / 2×2分散

- [ ] 4方向4×4 probe
- [ ] player単位3tick分散
- [ ] 2×2 / 5tick遠景job
- [ ] 既存cache再利用
- [ ] queue dedupe

Pass:
- 近距離の精度を上げつつ広域jobが同tickへ集中しない。

### Phase 4 — ray/N-way

- [ ] 5本ray
- [ ] 8/16/24境界判定
- [ ] includePassable/includeLiquid条件を確定
- [ ] N-way方向mask
- [ ] dummy entityとの比較

Pass:
- 現行方式より軽い、または同等負荷で精度が上がる場合のみ採用。

### Phase 5 — foliage/glass

- [ ] leaf priority
- [ ] culling静的分類
- [ ] glass skip
- [ ] stained glass color bias
- [ ] 追加先の地面再取得
- [ ] biome再利用

Pass:
- 葉/ガラスで過剰遮蔽・不要再計算が発生しない。

### Phase 6 — 1〜4 visual base

- [ ] 1〜4 blocks base
- [ ] 65/100/80/60 profile
- [ ] 5 blocksで消失
- [ ] center occlusion shift
- [ ] outer occlusion split
- [ ] 2束通常上限
- [ ] 3-wayは回折ON時のみ許可

Pass:
- 1〜9による過大表示を避け、近距離の自然な減衰を再現。

### Phase 7 — sun/time direction

- [ ] getTimeOfDay
- [ ] world-time bias
- [ ] 3tick方向更新
- [ ] 方向補間
- [ ] 成立角度のみ採用
- [ ] 2×3 texture unit

Pass:
- 太陽時刻による方向/明るさ差が急変せず、成立しない角度へshaftが伸びない。

### Phase 8 — refraction optional

- [ ] 回折光設定 default OFF
- [ ] 4 blocks相互判定
- [ ] 30tick目標 / Mix-Tick判定枠へ組み込み / playerごと・candidateごと
- [ ] ceiling overlap
- [ ] blackening確認
- [ ] wider/2-way/3-way表現

Pass:
- OFF時の負荷・見た目を増やさず、ON時だけ回折表現が有効。

### Phase 9 — Performance Tier

- [ ] Tier 1〜2 default OFF
- [ ] explicit ONでTier 2〜5
- [ ] Tier 3〜5は1〜4 base
- [ ] 遠景からbudget縮退
- [ ] 5 blocks/s高速度延期

Pass:
- 低Tier環境で機能を強制有効化せず、高Tierでのみ拡張が動く。

## 17. 最終軽量化判断

優先順位を更新する。

1. 再探索を発生させない
2. 48超の新規cache生成を起こさない
3. 16 block/chunk/region単位で重複を排除
4. topmostでY探索を消す
5. 1〜24を2D候補化する
6. 4×4/2×2を分散queueする
7. rayで近距離境界/方向だけを見る
8. leaf/glassを軽量分類する
9. candidate数をdeterministic thinning
10. 終端で束ねる
11. Tierで頻度・分岐を制御する
12. 最後に数式を微調整する

「計算を速くする」より「計算を呼ばない」を最優先とする。

## 18. 未確定事項

- [ ] 0〜48 blocks内のY=0測定の実際の既存経路
- [ ] Performance EngineのMix-Tick判定箇所の正式な実装位置
- [ ] 16 block丸めが現在のcache設計と完全互換か
- [ ] 1〜4の65/100/80/60がalpha/transparencyのどちらの意味か
- [ ] getTopmostBlockで全shaft候補を表現できるか
- [ ] current RPがblock/entity/particleのどれでshaftを描画しているか
- [ ] getBlockFromRay()が実際の現行探索より軽いか
- [ ] 5本rayの最適本数
- [ ] 4×4 probeの具体的な4方向順序
- [ ] leavesの静的分類表
- [ ] stained glassの色付与量
- [ ] 3-way logical splitを通常renderで2束へ縮退する条件
- [ ] world timeから算出する方向補正量
- [ ] ceiling overlapで黒色化しないmaterial構成
- [ ] 7日TTLのreal-time timestamp永続化方式
- [ ] Tier 2〜5の細かなbudget差分

## 19. 完了条件

- [ ] 0〜48で必要なcache生成が可能
- [ ] 48超で新規検査が発生しない
- [ ] 48超の既存共有cacheは必要に応じて参照できる
- [ ] 検査領域が16 block/chunkへ整列
- [ ] 256×256 regionで共有cacheされる
- [ ] 7日実時間TTLが機能する
- [ ] 初回48 bufferが遠景5tick/2×2分散とは分離された経路で取得される
- [ ] 遠景cache generationのみ2×2/5tick分散される
- [ ] 1〜24が2D候補計算へ移行する
- [ ] 4×4 local probeが3tick分散される
- [ ] topmost優先で不要なY探索が減る
- [ ] 葉/ガラスが通常solidと同一扱いされない
- [ ] shaftの近接基準が1〜4
- [ ] 65/100/80/60 + 5で消失の基準が実表示に反映される
- [ ] direction maskで閉塞方向へ生成しない
- [ ] 太陽時刻に応じた方向補正が急変しない
- [ ] 回折設定はdefault OFF
- [ ] 回折ON時のみ30tick目標でMix-Tick判定枠から局所判定
- [ ] player別effectとshared cacheが分離
- [ ] 5 blocks/s以上で重い新規探索を延期
- [ ] Performance Tier 1〜2 default OFF / explicit ONで2〜5
- [ ] 旧shaftを先に消す空白がない
- [ ] Performance Engine budgetを越えない
- [ ] 静的検証と実ワールド検証の両方を行う

## 20. 外部仕様確認

2026-10-08時点でMicrosoft Learnを確認した。

### Script API

- Dimension.getTopmostBlock({x,z})
- Dimension.getBlock()
- Dimension.getBlocks()
- Dimension.getBlockFromRay()
- BlockRaycastOptions.maxDistance
- BlockRaycastOptions.includePassableBlocks
- BlockRaycastOptions.includeLiquidBlocks
- BlockFilter.excludeTypes / excludeTags / includeTypes / includeTags
- Block.getTags()
- Block.hasTag()
- Block.isAir / isLiquid / isSolid
- Entity.getHeadLocation()
- Entity.getVelocity()
- Entity.getViewDirection()
- World.getAllPlayers()
- World.getTimeOfDay()
- World.getAbsoluteTime()
- System.runJob()

System.runJob()はgeneratorへtickごとのtime sliceを与えるため、長い探索を分割する候補として使用できる。

### Rendering / Molang / culling

- Particle minecraft:particle_motion_parametric はMolangでdirection/rotation/relative_positionを毎frame評価できる。
- MolangVariableMap.setVector3() / setSpeedAndDirection() でdirection系変数を渡せる。
- Particle emitter initializationにはper-update expressionがある。
- query.time_of_day はdimensionの時刻を0〜1で返す。
- Block geometryにはculling / culling_layer / culling_shapeがあり、foliageではminecraft:culling_layer.leavesが使える。
- Block culling rulesはrender時の面隠しを定義するため、Script側でruntimeに「このculling定義が現在効いているか」を読むAPIとは区別する。

### 設計上の結論

- ダミーentity5体方式は標準経路にしない。
- topmost + 2D候補 + 小局所probeを主経路にする。
- rayは補助ゲート/N-way判定。
- 1〜4を標準visual baseにし、1〜6/1〜7/1〜9は既定値から外す。
- Performance Tierは「見た目の半径」より「計算頻度・候補数・分岐許可」を制御する。
- API採用確定前に、実際のReForge Visuals実装側のScript API/RP方式と対象バージョンを照合する。

Sources:
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension
- https://learn.microsoft.com/ja-jp/minecraft/creator/scriptapi/minecraft/server/blockraycastoptions
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/system
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/particlesreference/examples/particlecomponents/particle_motion_parametric
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_geometry
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockcullingreference/examples/blockcullingrules/block_culling

