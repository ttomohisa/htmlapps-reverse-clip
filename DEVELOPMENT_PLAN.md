# Reverse Clip / 動画逆再生 — v0.1.0〜v1.0.0 開発計画

> **Status:** v0.1.4 experimental up-to-10s reverse; Android user-confirmed 1s / 5s (12.7s at long-edge720px); desktop 10s frame-exact; Android 10s not yet measured; iPhone deferred; original G1 pending  
> **作成日:** 2026-10-11  
> **正となる製品仕様:** [`APP_SPEC.md`](./APP_SPEC.md)  
> **目標:** スマートフォンで短い区間の逆再生／往復再生MP4を、ブラウザ内だけで安定して作る。

## 2026-10-12 — Android / PC優先への計画変更

**ユーザーの最新指示：iPhoneは当面対象外。** この節は、以下に残る当初の「iPhone Safari必須」「iPhone未検証なら先へ進まない」といった条件よりも優先する。元の受入項目は将来の再開用として保持し、**合格済みとして扱わない**。

- **現在の開発・確認対象：** Android Chrome実機、Windows Chrome/Edge、単一HTML・オフライン・CSP。日本語／英語のUIは維持する。
- **延期：** iPhone Safari実機、iPhone撮影HEVC MOV、iOS固有の保存UX・回転・メモリ測定。iPhone向けの確認依頼もいったん行わない。
- **実測済み（ユーザー報告）：** Androidで1秒、5秒・長辺360px、5秒・長辺720pxが成功。最後の5秒・長辺720pxは**12.7秒**。画質選択の「720px」は長辺の制限であり、**標準の1280×720（720p）とは異なる**。
- **Android-first継続判断：** 上記の成功によって実験的な機能実装を続行する根拠は得られた。ただしG1の旧クロスプラットフォーム判定は**未完了**、標準720p/10秒・1080p/5秒、実機の反復・メモリ・音声などを合格済みにはしない。
- **優先順位：** ① Androidでの再実行・キャンセル・端末メモリ・入力別エラー対策、② 最大10秒へ拡張するための境界・処理時間の検証、③ 往復再生、④ 恒久的なGPL対応ソース付きFFmpeg WASM配布、⑤ PCでの`file://`検証と日英UI／保存UX。
- **正式リリースの条件：** iPhoneの扱いを決めるまでは「iPhone対応」と表示しない。リリース対象プラットフォームと元のG1/G2/G3受入条件の最終変更は、安定版候補のレビュー時に明確に決める。期限付きActions成果物のまま正式公開しない。


### v0.1.4 technical experiment — 10-second reverse (Android-first)

- Extend **experimental** video-only selection from 5s to 10s without enlarging the per-chunk reverse frame buffer: at 15fps, split a 10s selection into five 2s segments.
- Apply the new dedicated Builder WASM `--frames N` and `--expected-frames N` public-libav validations. Refuse a segment or joined MP4 with unexpected encoded-frame count. In the previous binary, some non-frame-aligned ranges produced extra frames.
- Use `long edge 360px or 720px` labels; these are *not* standard 1280×720 output dimensions. Label >5s clearly as experimental and recommend 360px first on phones without automatically downscaling.
- Verify exact 10s/150 frames, 9.9s/149 frames, 0.1–9.87s/146 frames, cancellation and repeat runs with real WASM in Chromium. Confirm portrait input, Android-UA MEMFS staging and no runtime HTTP(S) or layout overflow.
- Android **5s** success remains user-reported, including **12.7s** at long-edge720px. Android **10s** remains **UNTESTED**, as do native-standard 720p10s, 1080p5s, VFR/HEVC, repeated real-device memory and direct `file://`.
- Keep Builder artifact temporary and Draft PRs unmerged. A permanent source-complete GPL release and separate stable-release acceptance decision are required. iPhone stays deferred.

## 2026-10-12 — ST / MT併用への新しい配布要求

FFmpeg Filter BuilderのST/MTアーキテクチャを参考に、Reverse Clip専用Builderの両バリアントを**実WASMで別々に生成**する。GitHub Pagesは `/` をST、`/mt/` をMTとし、後者に同一オリジンのCOI Service Workerを置く。Browser KittyにはMT版だけを取り込み、専用ルートへCOOP/COEP/CORPを設定する。ST単一HTMLはfile://で利用でき、MT単一HTMLは分離されたHTTPS/localhostで使用する。STからMTへの性能改善は実測前に断定しない。PRのマージと本番公開はユーザーの判断とする。詳細は `docs/THREADING_DISTRIBUTION.md`。

## 1. 開発原則

1. **技術検証が先、UI完成は後。** 当面Android Chrome実機とWindowsブラウザーでMP4作成・保存を検証する。iPhoneは2026-10-12の方針変更により延期し、未検証を「非対応確定」とは扱わない。
2. すべての段階で「入力→出力」を壊さず、モバイル・日英UI・単一HTML・通信制約を後回しにしない。
3. このアプリには「短い区間の逆再生・往復再生」以外の動画編集機能を載せない。
4. **FFmpeg Builder本体の変更**と**Reverse Clipアプリの変更**を別々に管理する。既存プロファイルへ無理に流用しない。
5. それぞれの段階で実際のコミット、使用したBuilder Release、テスト入力、結果を記録。結果のない「対応済み」宣言をしない。
6. 実装時はその時点の `htmlapps-template` および対象リポジトリの現行状態を再確認する。
7. すべてのPRはユーザーのマージ待ちとし、ChatGPT側で自動マージしない。

## 2. 実装構成の予定

```text
[FFmpeg WASM Builder: video-reverse profileを新設]
  ├─ public libav reverse/areverse runner
  ├─ short-segment / bounded-memory processing
  ├─ MP4 H.264/AAC export, orientation handling
  ├─ browser smoke test, SOURCE/LICENSE, pinned release
  └─ immutable/versioned asset + SHA-256
                           |
                           v
[Reverse Clip: htmlapps-templateから作成]
  ├─ file/camera input + video inspect
  ├─ source preview + range UI + reverse/pingpong selection
  ├─ audio and quality settings
  ├─ Worker + embedded FFmpeg WASM
  ├─ output MP4 preview/download + cancellation
  └─ bilingual UI + single HTML + offline/CSP + tests
```

- 2026-10-11時点で `video-speed-changer` と `ffmpeg-filter-builder` プロファイルの `ffmpeg.flags` に `reverse`／`areverse` は入っていない。**未検証の既存APIをそのまま使える前提としない。**
- `video-reverse`は**仮のprofile名**。PoCで名称・フィルター・runner API・必要なライブラリ構成を確定する。
- ブラウザ実行時の外部ダウンロードを不要にするため、完成HTMLへ実行資産を埋め込む。
- 単一スレッド（ST）版を既定にする。MTの導入は、実機データ上必要な場合の別件検討とする。

## 3. Go / No-Go Gate

### Gate G1 — 当初のクロスプラットフォーム条件（未完了）

> **2026-10-12更新：** この節のiPhone必須条件は延期。Android/PC向けの実験開発はAndroid実機成功を根拠に継続する。ただし旧G1を合格済みとせず、未実施のiPhoneテストは将来の受入項目として残す。

**必ず試すこと**

- Windows Chrome/Edge、Android Chrome実機、iPhone Safari実機で、読み込んだ短い動画から映像を逆転させたMP4を生成・再生・保存。
- Android撮影MP4/H.264とiPhone撮影MOV/HEVCを検査。
- 720p/5秒を基本ケースとし、720p/10秒と1080p/5秒も試験。全体逆転で危険なら、分割逆転の最小PoCをこの段階で試す。
- 変換前後のフレーム順、画面向き、出力再生、メモリ失敗、処理時間を記録。
- 代表的な実機で720p/5秒が概ね90秒以内に完了することを製品継続の暫定判断に使う。
- Worker・WASM・`file://`・CSP・オフライン処理の成立性を確認する。

**GO:** 主要実機で逆再生MP4が再生・保存でき、継続不能なメモリ障害や顕著な性能問題がなく、720p10秒／1080p5秒に向けた安全な実装方式が実証された場合。

**NO-GO:** iPhoneまたはAndroidで主要な撮影動画を扱えない、変換が繰り返し異常終了する、短い区間でも著しく遅い、メモリ負荷を減らす現実的な方式が見つからない場合。技術上の切り分けと原因の記録を残して停止し、v0.2.0に進まない。

> G1で成功した組合せ／失敗した組合せ／使用端末／計測値は `docs/feasibility/G1.md` 等に表として保存する。単純な「技術的に可能」という文言だけでは合格としない。

### Gate G2 — v0.6.0完了時：**機能・性能が製品として成り立つか**

- Android／iPhoneの両方で、**720p・10秒**の逆再生・往復再生を連続3回実行できる。
- Android／iPhoneの両方で、**1080p・5秒**の逆再生・往復再生を連続3回実行できる。
- 逆音声選択時にずれ・ノイズが許容内。キャンセル・再試行が壊れない。
- 5〜10秒の動画を作る「小さなツール」として、処理時間が利用価値を失う水準ではない。
- 1 GiB以下の入力を扱う際に、**元ファイル全体のメモリコピーをしていない**ことをコード上で確認。

**GO:** 上記を達成した場合。**NO-GO / 仕様再審査:** 標準720p10秒に到達できない、実機で頻繁にクラッシュする等の場合。目標を無断で縮小せずユーザーへ技術結果と代替案を示す。

### Gate G3 — v0.9.0 RC完了時：**正式リリースできるか**

- [`APP_SPEC.md`](./APP_SPEC.md) の A-01〜A-14を合格とした検査表を提出。
- 日英の実UI、ヘルプ、README、画面幅320/360/390px、iPhone／Android／PC、単一HTML、ネットワーク、著作権表示を確認。
- 未解決の重大バグ・誤出力・動画送信・破損保存が0件。
- Gate G3が未合格なら v1.0.0 に進まない。

## 4. バージョン別マイルストーン

### v0.1.0 — Feasibility Spike / 技術成立性の検証

**目的：** UIに着手する前に「本当にスマホで逆再生MP4を作れるか」を証明する。

**実装・調査**

- 最新Builderの構成を読み、`reverse`、`areverse`、範囲処理、映像／音声エンコードに必要なフィルター・APIの追加箇所を特定。
- 専用public libav runnerの最小試作。FFmpeg CLI文字列の実行や任意コマンドパススルーに依存しない。
- 正しい時系列（先頭／末尾／キーフレーム境界）で逆再生MP4を出す。
- H.264 MP4／HEVC MOVのデコード、H.264 MP4の生成、縦向き処理、WORKERFS入力を試す。
- フレーム全件を保持する方式のメモリ使用特性を計測。720p10秒／1080p5秒が厳しければ区間分割反転の実証まで進める。
- 最小のテストページで `file://`、Worker/WASM、MP4保存、外部通信なしを確認。

**成果物**

- 専用Builderプロファイルの実験コード／テスト、再現可能なビルド手順。
- `docs/feasibility/G1.md`：端末・OS・ブラウザ・入力形式・対象秒数・出力形式・所要時間・失敗理由・スクリーンショット／ログ・GO/NO-GO。
- 安全に使える最短区間／解像度／処理方法の提案。

**完了判定：** Gate G1に合格。未合格なら「失敗理由の報告」をこの段階の最終成果とし、計画は停止する。

### v0.2.0 — App Foundation / アプリの土台

**目的：** 最新テンプレートに基づくアプリ外形と、動画ファイルの安全な取込を完成させる。

**実装**

- 新しいアプリリポジトリをテンプレートから用意し、`APP_SPEC.md` / `AGENTS.md` / `app.config.json` 等を実装に合わせる。
- 日本語／英語、`#16624F`、SVG、favicon、基本ヘルプ、ライトテーマ。
- 1ファイル選択・ドラッグ&ドロップ、ソース置換、メディア検査、形式不正とファイルサイズ制限。
- `empty / inspecting / ready / error`、入力世代ID、不必要な元ファイル全体コピーの禁止。
- 1カラムのスマホ導線、PCの適応配置の基本骨格。
- アプリ用の固定FFmpeg資産取込・ビルド・CSP・`file://`確認。

**成果物：** 読み込み、ソースプレビューと情報、非対応エラーが使える単一HTML。

**完了判定：** スマホ実機で主要入力を選択でき、元動画置換や非対応入力で古い状態が残らない。

### v0.3.0 — Trim & Reverse / 区間指定と逆再生

**目的：** ユーザーが任意の短い区間を選び、逆再生MP4を取得できる。

**実装**

- 元動画のプレビュー、時間指定・シーク、範囲ハンドル（タッチ／キーボード）。
- 0.5〜10秒の区間制約、0.1秒精度の時刻入力、正規化とエラー説明。
- 動画のみ逆再生、最大720pでのMP4生成、保存前の簡易プレビュー。
- 元ファイルを変えた際の非同期結果破棄、出力名既定値、`.mp4`固定。
- 切出し先頭／終端が適切なフレーム順になることを合成動画で自動検証。

**成果物：** 「選ぶ→範囲を決める→逆再生→MP4保存」の縦方向MVP。

**完了判定：** 途中5秒の選択、開始0秒付近、動画終端付近で想定どおりの逆再生出力を得られる。

### v0.4.0 — Ping-Pong / 往復再生

**目的：** 1往復する動画を、フレーム境界の破綻なく作れる。

**実装**

- 「逆再生」「往復再生」の排他的モード選択。
- 通常区間＋逆方向区間の連結。折返し点の重複フレーム／静止感を抑える。
- 出力所要時間の概算表示、モード別ファイル名、モード変更時の既存結果との区別。
- 黒フレーム、繋ぎ目のギャップ、VFR素材の時刻ずれに対するテスト。

**成果物：** 2モードとも動画のみで出力可能。

**完了判定：** 色／番号付きフレーム動画で往路・復路の順序を検証し、ループ再生でも不自然な停止が目立たない。

### v0.5.0 — Audio Modes / 音声対応

**目的：** 音声を消すか、動きとともに逆再生するかを選べる。

**実装**

- 初期値「音なし」、入力に音声がある場合のみ「音声も逆再生」を許可。
- reverse時の音声反転、pingpong時の正方向＋逆方向音声の連結。
- 映像と音声の同期、長さ／終端調整、クリック音や明らかな無音区間の抑制。
- 無音動画・モノラル／ステレオ・サンプリングレート違い・短い音声を試験。
- 出力に音声が含まれるかどうか、結果情報へ表示。

**成果物：** v1.0.0予定の音声モードを実装。

**完了判定：** 音声素材の出力を聞いて確認し、映像／音声のずれが概ね150ms以内。

### v0.6.0 — Memory / Performance / Reliability

**目的：** 「試せる」から「スマホで継続利用できる」へ移行する。

**実装**

- v0.1で試した分割逆転などの負荷制御を完成、メモリの同時保持上限を抑える。
- フレーム境界・区切り位置の重複／欠落対策、出力時間・音声同期の再検証。
- Standard最大720p10秒、High最大1080p5秒の負荷制約と事前警告。上限超過時の自動トリム／自動画質変更は禁止。
- Workerのキャンセル・強制停止・クリーンアップ・再生成の再現性。
- 変換中の元動画置換、連打、処理中エラー、ブラウザタブ移動、再試行で古い結果が現れないこと。
- 必要ならメモリが大きい経路を迂回する。高速化のために`file://`実行を犠牲にしない。

**成果物：** `docs/feasibility/G2.md`、負荷測定・端末別テスト結果・既知制限。

**完了判定：** Gate G2合格。満たせなければ仕様と商品価値を再審査し、v0.7.0に進まない。

### v0.7.0 — Mobile UX / Save Flow

**目的：** 初見のスマホ利用者が迷わず操作・保存できる。

**実装**

- 「動画／編集／結果」の3画面導線と固定バーの安全領域対応。
- 端末に応じた「撮影して取り込む」導線（機種で保証できない場合の代替説明つき）。
- プレビューのそばで時刻調整、音声と品質のシンプルな二次設定。
- 結果プレビュー／時間・サイズ・解像度表示／ファイル名編集／保存。
- 成功・失敗・完了・空状態の文言。必要な確認ダイアログ、古い結果の区別、操作の手戻り。
- 320/360/390px、iOS Safari、Android Chrome、ソフトキーボード、長い日本語／英語名でレイアウト確認。

**成果物：** スマホでも完成された一連の作業導線。

**完了判定：** 初見の人が説明なしに、選ぶ→数秒を指定→逆再生→保存を完了できる。

### v0.8.0 — Compatibility / Hardening

**目的：** 実ファイル・各種異常条件に耐えられる状態へ。

**実装**

- Android H.264／iPhone HEVC MOV、縦動画回転、VFR、30/60fps、元動画が短い場合、複数音声、音なしを再検証。
- HDR/10-bitの注意喚起または非対応判断。誤った色や真っ黒映像を成功扱いしない。
- 不正なコンテナ／拡張子偽装／壊れた動画／巨大ファイル／ブラウザ非対応を正しいエラーメッセージで表示。
- 音声ずれ、出力末尾・再生不能MP4、出力ファイル名、Safari保存方法を確認。
- 回帰テスト（ソース世代ID／キャンセル後に復帰／設定変更中の古い結果）。
- `file://`単一HTML、自己展開版、CSP、Worker、ランタイム通信遮断を繰り返し検証。

**成果物：** 対応形式表、既知制限、QAログ、安定したリリース候補。

**完了判定：** 既知の重大バグが0件で、主要入力形式の成否を事実ベースで説明できる。

### v0.9.0 — Release Candidate / 公開前最終確認

**目的：** 機能追加を止め、製品仕様とリリース成果物を一致させる。

**実装・検証**

- [`APP_SPEC.md`](./APP_SPEC.md) のA-01〜A-14を全件チェック、結果と端末名を残す。
- README・README.ja・CHANGELOG・LICENSE・`THIRD_PARTY_NOTICES.md`、対応形式、制限、プライバシー説明を更新。
- 日英スクリーンショット、同一デザインのSVG favicon、実際の生成単一HTMLを確認。
- 単一HTMLと自己展開版の起動・全機能・保存・外部通信ゼロを確認。
- GitHub Actionsのビルド、必要資産、lock/SHA、CSP、バージョン整合、スクリーンショット／アセットを確認。
- PR Previewと実機で、画面のはみ出し、固定バー、ヘルプ最下部、フォーカス移動、空状態・失敗状態を点検。

**成果物：** `docs/release/RC_CHECKLIST.md`、確認ログ、リリースノート案。

**完了判定：** Gate G3合格。RCで新機能を追加しない。

### v1.0.0 — Stable Release / 正式版

**目的：** 検証済み仕様を正式版として公開する。

**実装・運用**

- RC以降は重大不具合修正のみ。変更による回帰テストを追加。
- 安定したBuilderの固定済みReleaseを使用し、最終ビルドのハッシュ・ライセンス・配布ファイルを確認。
- `app.config.json`、UI、README、CHANGELOG、生成HTMLの版数を `v1.0.0` にそろえる。
- リポジトリ上のPRをレビューできる状態にする。マージはユーザー本人。
- マージ後、タグ／GitHub Pagesなど対象リポジトリで設定した公開経路の本番確認を行う。
- Browser Kitty本体への登録は**別タスク**。本体の現在コード／設定／公開HTMLパス等を確認してからPR化し、既存トップページコピーを勝手に変更しない。

**成果物：** v1.0.0ソース、再現可能ビルド、独立した単一HTML配布版、日英ドキュメント、検証記録。

**完了判定：** 全Gateと受入項目に合格、公開版で逆再生／往復再生／MP4保存まで完走する。

## 5. v1.0.0品質確認マトリクス

| ケース | Windows Chrome/Edge | Android Chrome実機 | iPhone Safari実機 | 主要確認点 |
|---|---|---|---|---|
| H.264 MP4 / 720p / 5秒 / mute | 必須 | 必須 | 必須 | 基本処理・向き・再生・保存 |
| H.264 MP4 / 720p / 10秒 / reverse | 必須 | 必須 | 必須 | 標準品質の最大長・メモリ |
| H.264 MP4 / 720p / 10秒 / pingpong | 必須 | 必須 | 必須 | 折返し・最大出力20秒相当 |
| H.264 MP4 / 1080p / 5秒 | 必須 | 必須 | 必須 | 高画質モードの成立性 |
| HEVC MOV / 5秒 / 縦撮り | 試験 | 試験 | **必須** | iPhone撮影動画の実利用 |
| 30/60fps、VFR | 必須 | 必須 | 必須 | fps変更・指定時間・音声ずれ |
| 音声なし／音声逆再生 | 必須 | 必須 | 必須 | 音声選択・同期 |
| 非対応／破損／HDR | 必須 | 必須 | 必須 | 誤出力防止と説明 |
| キャンセル→再実行 | 必須 | 必須 | 必須 | Worker後片付け・結果整合 |
| `file://`単一HTML | 必須 | 可能なら | 可能なら | ネットワーク非依存の配布 |
| 画面幅320/360/390px | エミュレート | 必須 | 必須 | UI欠け／タップ／ダイアログ |

**追加ケース:** 解像度・ファイルサイズ上限、1 GiBに近い入力（元ファイル全体コピーの有無）、長いファイル名、空状態、処理中のソース差替え、同じ設定での3回連続出力、バックグラウンド移行と復帰。

**計測フォーマット:** `device | OS | browser | source codec/container | source WxH/fps/duration/bytes | selected interval | mode/audio/quality | output WxH/fps/duration/bytes | elapsed | peak memory indicator | result | issue link`。

## 6. 受入項目と担当マイルストーンの対応

| APP_SPEC受入項目 | 主な実装段階 | 最終検証段階 |
|---|---|---|
| A-01 フレーム逆順 | v0.1 / v0.3 | v0.8 / v0.9 |
| A-02 往復フレーム境界 | v0.4 / v0.6 | v0.8 / v0.9 |
| A-03 区間の開始・終了 | v0.3 / v0.6 | v0.8 / v0.9 |
| A-04 音声仕様・同期 | v0.5 / v0.6 | v0.8 / v0.9 |
| A-05 回転・VFR | v0.1 / v0.3 | v0.8 / v0.9 |
| A-06 再生可能MP4 | v0.1 / v0.3 | v0.8 / v0.9 |
| A-07 古い結果の混入防止 | v0.2 / v0.6 | v0.8 / v0.9 |
| A-08 状態の見分けやすさ | v0.2 / v0.7 | v0.9 |
| A-09 モバイル・長文・モーダル | v0.2 / v0.7 | v0.9 |
| A-10 日英対応 | v0.2 / v0.7 | v0.9 |
| A-11 ランタイム外部通信なし | v0.1 / v0.2 | v0.8 / v0.9 |
| A-12 standalone / CSP / file | v0.2 / v0.6 | v0.9 |
| A-13 ドキュメント・資産・CI | v0.2 / v0.9 | v1.0 |
| A-14 結果・設定の整合 | v0.3 / v0.6 | v0.8 / v0.9 |

## 7. 主要リスクと対応

| リスク | 起こる問題 | 先手の対処 | 判定点 |
|---|---|---|---|
| 逆再生フレームの保持でメモリ不足 | スマホSafariのタブ終了、WASM失敗 | 1〜数秒単位の反転→逆順結合PoC、品質／区間上限 | G1 / G2 |
| フレーム分割境界の重複・欠落 | 往復動画が一瞬止まる／飛ぶ | 番号付きテスト動画で完全照合、境界の時間スタンプ検証 | v0.3 / v0.4 / v0.6 |
| 音声と映像のずれ | 往復部が不自然、末尾が無音 | 音声専用経路・タイムスタンプ検査、AAC終端調整 | v0.5 / G2 |
| iPhoneのHEVC MOV／回転 | モバイル主要入力が処理不可、映像が横倒し | 実機撮影ファイルをv0.1から使う | G1 / v0.8 |
| HDR / Dolby Vision | 色が極端に変わる | 検出・事前警告・未保証入力は拒否 | v0.8 |
| FFmpeg WASMの容量・負荷 | HTMLが巨大／初回準備が遅い | 専用profileで最小化、埋込圧縮、size report | v0.2 / G2 |
| アプリだけ先にできてBuilder未完成 | 結合できず機能が動かない | Builder独立release・smokeを先に通し、バージョン固定 | G1 / v0.2 |
| スマホ撮影／保存UIの差 | 撮影できない／写真に見当たらない | ファイル選択fallback、保存先の説明、実機UI確認 | v0.7 / G3 |
| 外部通信またはCSP例外 | ローカル処理の説明と実装が矛盾 | 初期から通信監査、`connect-src 'none'`、`file://` | v0.2 / G3 |

## 8. GitHub・CI・リリース手順

- **未依頼のリポジトリ作成やPR作成は、この仕様策定の成果には含まれない。** 実装開始指示時に現状を見て着手する。
- テンプレート現行 `AGENTS.md`／`APP_SPEC.md`／CIを優先し、本計画の古いファイル名・設定が将来変わっていた場合は最新ソースで調整する。
- Builderの `video-reverse` プロファイル追加・smoke/release → asset version pin → アプリ実装PR、の順に依存関係を管理する。
- ビルド時に同梱資産ハッシュ・README／license・生成HTML実体・CSP・日本語／英語・favicon・出力名ルール・オフラインを検査する。
- スマホ検証はエミュレーターだけでは完了にしない。PR Preview等と実機で確認。
- 完成基準は**リリース番号ではなくGate G3およびAPP_SPEC受入項目に合格したこと**とする。

## 9. 改訂・中止時の記録

Gateまたは必須試験に失敗した場合は、次の項目を残す。

```text
Gate / version:
Date:
Repository commit / Builder release:
Device / OS / browser:
Source codec, resolution, duration, size:
Selected interval / mode / audio / output quality:
Observed result / timing / error:
Reproduction steps:
Root cause (confirmed vs hypothesis):
Mitigations tested:
Decision: GO / INVESTIGATE / NO-GO
Changes needed in APP_SPEC:
```

**「動かなかったから品質を黙って落とす」「対応しているように見せる」「アプリのために外部アップロードを追加する」は行わない。**

---

**現在の次の着手点：** Android/PC向けの短時間動画の安定化・10秒への段階的拡張・往復再生・Builderの恒久配布。iPhoneは延期し、旧G1が未完了であることは維持したまま、Android-first実験版を継続する。
