# Reverse Clip / 動画逆再生 — v0.1.0〜v1.0.0 開発計画

> **Status (updated 2026-10-19):** v0.9.0 RC PREPARATION integrated into `main` after PR #6. The dedicated Builder FFmpeg GPL source Release is public and ST/MT real-browser CI passed. The app itself has no release/tag; G3 is still OPEN, historic G2 remains NOT PASSED, and Browser Kitty integration is deferred until after v1.0.0. **Historical note (2026-10-16):** v0.9.0 RC PREPARATION started after successful v0.8.0 real ST/MT compatibility regression tests. Gate G2 hardware and Gate G3 release acceptance remain OPEN; no merge, tag or release. The earlier Pages mobile UI candidate has an owner-reported Android basic UX PASS. The previously failing sparse-VFR input now **USER-REPORTED PASS on PC and Android** after Builder 1.10.6 and [Pages PR #4](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/4). Real Chrome MT 10-second ×3 sparse tests PASS independently. Full G2 remains OPEN for general 720p/1080p real-camera coverage, memory/no-copy, audio listening, cancellation and permanent GPL source distribution. iPhone testing deferred.
> **作成日:** 2026-10-11  
> **正となる製品仕様:** [`APP_SPEC.md`](./APP_SPEC.md)  
> **目標:** スマートフォンで短い区間の逆再生／往復再生MP4を、ブラウザ内だけで安定して作る。

## 2026-10-17 — Right-sized RC test policy (owner requested)

The owner asked to revise unnecessarily strict verification conditions.
For the proposed initial **Windows Chrome + Android Chrome** release
scope, use [REVISED_ACCEPTANCE_SCOPE.md](docs/release/REVISED_ACCEPTANCE_SCOPE.md):
P0 safety/privacy/real basic-device workflow/valid MP4/immutable GPL
corresponding source remain mandatory; P1 additional browser/device
spot checks and P2 unadvertised 720p10s/1080p5s ×3 performance
research do not automatically block a limited-scope release.

Original G2 conditions are preserved as historical and NOT PASSED.
A bounded <=64MiB Android provider-copy fallback is a **proposed**
acceptable implementation condition when needed after a failed direct
read; no >64MiB whole-file fallback, data upload, unbounded memory
claims or silent errors. The exact release target and this revised
scope require final release review; no G3 approval now.

## 2026-10-16 — v0.9.0 RC preparation (G2/G3 stay OPEN)

The owner asked why the version had not advanced and approved continuing.
Advance the **development version** to v0.9.0 and begin collecting
release-candidate evidence. This is NOT an RC pass or release
authorization; Android v0.9 device QA, original Gate G2, Gate G3,
GPL corresponding-source permanence and deferred iPhone scope are
still incomplete. The milestone sequencing exception applies to
development only.

**Feature freeze:** preserve ST/MT H.264/AAC Reverse/Ping-pong,
mobile Video/Edit/Result, fail-closed invalid MP4, local-only
connect-src 'none', 15fps and experimental size/duration limits.
Do not introduce codecs or changes that undermine file://.
Review all APP_SPEC A-01–A-14 and mark evidence PASS/PARTIAL/PENDING
by exact environment; desktop Chrome does not certify Android/Edge.
Record in `docs/release/RC_CHECKLIST.md` and keep release notes
as DRAFT. No app/Builder PR merge, tag, GitHub Release or Browser
Kitty main repository change.

## 2026-10-16 — v0.8 extended rotation and HEVC fail-closed QA

[Real ST/isolated MT Chrome CI #38863445237](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38863445237)
ALL SUCCESS, [PR preview #38863445204](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38863445204)
SUCCESS. The v0.8 test matrix now covers 180°/270° QuickTime
display rotation with actual asymmetric color-marker pixels matching
autorotated source reference (mean RGB MAE 0.46 in each ST/MT
fixture), in addition to the previous 90° case. The MP4 outputs
have upright coded frames and no residual display-matrix tag.

Native generated HEVC/H.265 8-bit and PQ/BT.2020-tagged 10-bit MOV
are both refused by this desktop Chrome build's preview decoder
without enabling stale MP4 downloads. This is expected safe
failure on one browser configuration, **not HEVC/HDR support**.

Physical Android/iPhone source compatibility, HDR color fidelity,
input audio track selection, original G2 RAM/no-copy and full-HD
endurance, and a durable matching GPL Builder corresponding-source
Release remain OPEN. Do not mark v0.8 accepted yet or advance to
v0.9 RC; do not merge Draft PRs, tag or publish.

## 2026-10-16 — H.264 MOV / 90° rotation / corrupt MP4 / dual AAC QA

[CI #38857118532](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38857118532) and
[PR preview #38857118536](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38857118536) ALL SUCCESS.
Real Chrome ST and isolated MT confirmed H.264 MOV decoding and
reverse MP4; a genuine 90° MOV display matrix was handled as browser
portrait preview 90×160 and upright coded 90×160 output without
residual display rotation; a 128-byte plausible ISO BMFF truncated
source could not activate Result/Save; and a source with two AAC
tracks exported **zero** audio tracks under the default mute setting.
These are synthetic browser fixtures, not HEVC/iPhone/real Android
endurance proof. No codec, FFmpeg binary, network or privacy changes.

The v0.8 matrix documents remaining 180/270°/HDR/10-bit, actual
source-track selection, file-provider and G2 phone gaps.
No app/Builder PR merge, tag, public release or Browser Kitty import.

## 2026-10-16 — v0.8.0 Compatibility / Hardening development start

The owner explicitly requested progression to the v0.8.0 milestone.
On the existing, unmerged application Draft PR #2 only, the app version
advances to `0.8.0` (development, no tag or release). Its scope is the
original plan's **Compatibility / Hardening**: genuine H.264 30/60fps,
short sources, MOV/HEVC, VFR, portrait rotation, HDR/10-bit caveats,
silent/multi-track audio, invalid/truncated/oversized inputs, MP4
integrity and local-only standalone operation.

First implemented changes: decodable input below 0.5 seconds reports a
specific localized minimum-duration error rather than the misleading
"unsupported or damaged" status; the source panel includes collapsed
JA/EN explanations that source color/HDR/10-bit fidelity is **not
detected or guaranteed**, 30/60fps is resampled to 15fps rather than
preserved, and multi-track audio selection is not implemented.
No new codec, media network connection or WASM dependency is added.

[Actual ST/isolated MT Chrome CI #38853679777](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38853679777)
**ALL SUCCESS**: locally generated 0.27-second H.264 rejected with
the correct translated message, genuine 30fps and 60fps H.264 inputs
each output as 15-frame, 1-second H.264 MP4 verified by ffprobe.
[PR preview #38853679768](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38853679768) also PASS.
Testing of genuine HDR/10-bit color, HEVC MOV, physical-device rotation,
multi-audio-track selection and iPhone Safari is still **OPEN**;
a disclosure is not color-fidelity validation. See
`docs/feasibility/V080_COMPATIBILITY_MATRIX.md` for case-by-case evidence.

The same documented owner-directed milestone-order exception used
for v0.7.0 permits v0.8.0 **development** while formal
**G2 remains INVESTIGATE / NOT PASSED**. This does not waive Android
high-resolution ×3, provider memory-copy constraints, audio seam
listening or the v0.9/v1.0 release gates. Do not merge PR #1/#2 or
Builder #16, tag, release or change the Browser Kitty site.

## 2026-10-16 — v0.7.0 UX code-complete checkpoint

The 3-step phone workflow, localized successful/silent/AAC/ping-pong
MP4 results and errors, truthful downloads, accessible labels, explicit
source-replacement guard, processing navigation lock, short viewport
and keyboard-focus safeguards are implemented on the existing Draft.
[Actual ST and isolated MT browser CI #38850394911](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38850394911) and
[PR preview #38850394895](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38850394895) PASS. Browser acceptance is
not a claim of Android or iPhone acceptance for this new branch.
G2 real-device repeats/RAM/source-provider/audio listening and a
permanent matching GPL Builder Release remain open; iPhone deferred.
No merge, GitHub release or Browser Kitty integration.

## 2026-10-16 — v0.7.0 development approved by owner; G2 carried forward

**Decision:** Following the owner's explicit request, start the **v0.7.0 development milestone on Draft PR #2** despite the open G2 checklist. This is a documented **development-sequence exception**, not a GO decision for G2, a stable v0.7 release, or a change in v1.0 acceptance.

G2 is not formally passed because the original matrix requires Android **and iPhone** 720p10s and 1080p5s Reverse/Ping-pong three consecutive times; iPhone testing was explicitly deferred; Android real-camera repetitions, timing/RAM, audible AAC joins and cancellation/provider checks lack complete evidence. The <=64MiB Android MEMFS fallback still copies the entire input and violates the original strict no-whole-source-copy condition. The owner-reported Android Video/Edit/Result/Download success confirms the **basic workflow** on an older pinned Pages v0.6.0 snapshot, not those untested scenarios.

The matching Builder 1.10.6 GPL binary-and-source archive remains a temporary review artifact. A reviewed permanent GPL corresponding-source Release is a **separate production distribution requirement**, not one of the original G2 performance checklist bullets, and does not need to block further v0.7 UI development.

**Scope and invariants:** develop and test Video → Edit → Result, truthful download, JA/EN, touch, cancel/error states and standalone ST/isolated MT. Preserve H.264/AAC, original Reverse/Ping-pong behavior, file-processing locality, quality/duration limits and strict incomplete-output rejection. Formal G2 remains **INVESTIGATE / NOT PASSED** until evidence or an explicit scope change. G3, stable release, Builder public distribution and Browser Kitty integration remain separately gated. No merges, tag or release.

This user-directed exception supersedes only the earlier plan's ban on **starting** v0.7 before G2 passes. Historical acceptance outcomes are not retroactively changed.

## 2026-10-16 — Pages実公開・Android操作のユーザー確認

- [Pages専用PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5)はユーザーがマージ済み。 [デプロイ／公開実Chrome検証 #38834461219](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38834461219)の準備・公開・本番MT実変換はすべて成功。
- ユーザーは求められたAndroidの**動画選択→区間編集→結果の確認・MP4保存**について「androidもOK」と報告。**公開テスト版の基本UXは実機ユーザー報告でPASS**とするが、機種・ブラウザー詳細、ファイル提供元、品質・所要時間・RAM・音声・3回連続等の個別データは未確認。
- 公開されたHTMLはアプリコミット`e5f66428c501090513b6fa0da925b1d1bffbbfb8`から固定生成したもの。後続の10月16日修正（結果再生の停止、数値編集中の旧結果失効、44pxボタン拡張）はDraft PR #2側のCIでPASSしているが、このAndroid結果の対象ではない。
- G2本体は継続して未合格。iPhone実機は延期。バージョンはv0.6.0のまま、Draft PRやBuilderのマージ・Release・Browser Kittyへの導入なし。

## 2026-10-15 — スマホ導線・診断折りたたみの実ブラウザ回帰完了

- [アプリ CI #38688780206](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38688780206) はビルド／Node／実Chrome ST・隔離MT動画変換・AAC・フレーム数・キャンセル・通常動画・低fps動画の全ジョブ成功。スマホ用320/360/390pxの横スクロール、44pxタップ、長い日本語ファイル名、JA/EN切替、動画→編集→結果の遷移と古い結果の失効もチェックした。
- 編集以外の「動作テスト」「開発中の機能と制限」を標準では閉じたネイティブ折りたたみにし、変換エラー時は診断保存へ誘導する。これらの既存機能自体は削除せず、必要なときに開ける。ローカルChromeでもH.264保存・結果情報と診断開閉を確認済み。
- [Pages UI確認専用 PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5) は、Draft PR #2の検証済み単一HTMLのみをGitHub Pagesのテスト版へ反映する。マージはユーザーが行う。修正版の実公開URLでのChrome検証とAndroid実機の新UI確認はマージ後に実施する。
- G2の旧64MiB Android全量コピー救済経路、端末別RAM、高解像度・音声・キャンセルの実機受入、恒久GPL配布は未合格。v0.7.0の版数へは進めず、iPhone実機も引き続き延期する。

## 2026-10-15 — v0.7.0 Mobile UX / Save Flow 準備実装（v0.6.0のまま）

- v0.6.0でPC/Android実機の低fps動画成功が報告されたため、機能を維持したまま**スマホ幅600px以下の「動画→編集→結果」3段階の作業導線**を先行実装する。正式なGate G2合格やv0.7.0へのバージョン更新ではなく、Draft PR #2上のUX準備実装とする。
- モバイルでは動画選択が終わるまで編集・結果のナビを無効にし、動画プレビューと区間編集が準備できたら編集へ進む。実際のMP4 Blob・再生用メタデータの検査が成功した場合だけ結果へ進む。編集に戻って設定を変えたときは生成済み結果を破棄して、古いMP4を保存できないようにする。
- 実行中エラー・キャンセル・元ファイル差替えでは結果を無効化し、エラー詳細の閲覧を妨げない。PCでは既存の連続画面を維持し、WebAssemblyの動画処理は変更しない。
- 44px以上のタップ領域、安全なヘッダー直下のStickyナビ、固定下部UIの不使用、320/360/390px、日本語／英語、長いファイル名、結果の寸法・保存先案内を検証する。保存ボタンはブラウザーダウンロードを開始するだけで、OSの保存成功を確約しない。
- 細かな状態のチェックと実Chrome ST/MTのMP4保存回帰を `tests/feasibility/v030-ui.test.mjs` / `browser-video-smoke.py` に追加。実機AndroidでのUIの受入、ソフトキーボード・デバイス別保存先は別途確認が必要。
- Gate G2には、高画質全モードの実機反復、音声折返しの聞き取り、キャンセル・クラウドファイル取込、元ファイルの全体コピー禁止、恒久GPL配布が残る。iPhoneは引き続き延期。UI改善だけでG2やv0.7.0を完了と扱わない。

## 2026-10-15 — 修正版MTのPC・Android実機成功を報告（特定不具合は改善）

- [Pages PR #4](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/4)をユーザーがマージし、[実公開URLのChrome CI #38667384368](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38667384368)でMT分離・2秒58フレーム・10秒298フレームの合成スライド型MP4保存・デコードが成功。
- **実機ユーザー報告：「PCもAndroidも成功したよ」**。前にMTで `expected=30 actual=24` と失敗した元動画について、修正版で両環境の成功が確認できた。今回は動画や端末名・処理秒数・3回それぞれの詳細ログを取得していないため、**元動画の特定不具合のユーザー受入成功**として記録し、他の試験項目まで一括で合格扱いしない。
- G2は引き続き残課題を記録：実機カメラ動画の720p10秒・1080p5秒の各モード反復、音声折返しの聞き取り・同期、キャンセル再実行、Androidファイル提供元ごとの元ファイルコピー例外、性能記録、対応ソース付き恒久GPL Release。iPhone実機は延期。
- **進行判断：** 従来の低fps重大ブロッカーは解消見込み。ただし全G2を正式に閉じるまではv0.7.0へのバージョン移行を完了扱いにしない。v0.7.0 UI/保存フローの準備作業は残条件の整理と切り離して検討できる。

## 2026-10-15 — 低fps動画の修正とMTの実Chrome 3連続検証が成功（G2実機は未受入）

- 元動画と同様の **H.264 High／1920×1080／39フレーム／37.806089秒／平均約1.03fps** のスライド型VFR合成ファイルで旧版の出力フレーム不足を再現した。Builder 1.10.6で元動画の表示時刻を15fpsに正規化してから区間をフレーム境界で切り出し、厳密な出力フレーム数検査は維持する。MTのpthread Workerを区間終了後に解放する処理も追加した。
- [アプリ実Chrome CI #38618083612](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38618083612) が全ジョブ成功。新しいChromeでのST／MT変換、同一MTページからの**10秒往復再生×3回**と保存・フレーム数照合に成功。通常の動画・音声・キャンセル・オフライン検証も成功した。
- さらに多数の異なる動画を同一Chromeプロセスで変換した場合の負荷検証は別途残るため、テストを `mt-real-source-regression.py --phase isolated/repeat/extended` に分けた。通常CIから一度きりの3連続高負荷実行は外し、必要なときに手動で再実行できる。
- [Pages公開更新PR #4](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/4) は開発PR #1／#2をマージせず、SHA固定した1.10.6バイナリだけを公開テスト用に更新する。公開後は実URLから2秒・10秒のスライド型VFR往復再生を確認する。
- **G2は未合格**。ユーザーの実際のMP4とAndroid実機での3回連続、メモリ・音声・ファイル読み込みの受入が必要。iPhone延期中。対応ソース付きレビュー候補は [Builder #38617100332](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38617100332) で検証済みだが、恒久Releaseと法的レビューは未完了。v0.7.0への移行は保留。

## 2026-10-14 — 実機MTの出力フレーム数不一致（G2ブロック中）

- ユーザーからGitHub Pagesの**ST成功・MT失敗**報告。MTの実エラーは `Stage: video-segments`、`Reverse frame count mismatch: expected=30 actual=24`。元動画の表示情報は長さ37.89秒、396kb/s。MTの2秒・15fps区間で6フレーム不足している。原因はまだ未確定で、メモリ不足と決めつけない。
- 当該エラーは不完全なMP4を公開しないための正常な保護検査。**検査を緩めず、MTとSTを黙って入れ替えない**。
- 原因調査用に37.89秒相当の29.97fps/Bフレーム・可変フレームレートのH.264を生成し、実ST/MTの逆再生・往復再生を比較するChrome回帰を追加。元動画そのものを要求しない。
- アプリのエラー詳細を失敗時に自動展開し、失敗区間番号／先頭時刻／方向／MT・ST判定と期待・実フレーム数を診断JSONへ記録する。次のテスト用公開版へ反映するまでは既存Pages版には適用されない。
- 物理AndroidおよびPCでのMTの主要機能が失敗したため、**G2は未合格、v0.7.0への移行も停止**。修正・回帰検証が必要。

## 2026-10-14 — v0.6.0 Android入力の不要なメモリコピーを抑制（実機未受入）

- **CI受入（デスクトップのみ）：** [Actions #38493664787](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38493664787)がすべて成功。Android UA模擬ChromeでWorkerFSの10秒・150フレーム逆再生と、強制Worker読取失敗からMEMFS救済経路での1秒・15フレーム逆再生を、実MP4保存と診断ログのtransport値で検証。ST/MTの従来音声・往復再生等も回帰成功。実Androidの写真/クラウドプロバイダーや物理メモリは未受入。


- 従来のAndroid 64MiB以下の動画ファイルを毎回一括コピーする方式に対して、専用Workerで先頭・末尾32バイトのみを`FileReaderSync`で試し、正常な場合は元の`File`をWORKERFSで使う。読み取れない場合は旧64MiB以下のMEMFS救済コピーを残す。失敗時の変換中再試行も維持。
- Worker probeは最大2.5秒で終了し、キャンセル・ソース差替え・元動画の読込タイムアウトで停止してBlob URLを解放する。入力全体をサーバーへ送らず、IndexedDB等にも保存しない。
- Nodeでprobe成功・失敗・中断・リソース解放を試験。ChromeのAndroid UA模擬では本当のMP4出力と診断JSONの`workerfs`／`memory`経路をそれぞれ検証する。
- **なおG2の元動画の完全無コピー基準は未達。** 64MiB以下のプロバイダー失敗時には全体コピーを使用するため、Android実機での可用性・メモリ比較・例外仕様を別途判断する。これだけでGate G2合格やv0.7.0移行としない。

## 2026-10-14 — v0.6.0 分離されたMTの高解像度実行

- GitHub Actions [#38464029860](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38464029860) でCOOP/COEP有効のChrome実MTが成功。720p級10秒・AAC付きPing-pongは298フレーム／約19.867秒を11.20秒で出力。1080p級5秒・無音Reverseは75フレーム／5.000秒を5.87秒で出力。双方ともMP4の保存・デコード・全出力フレームの元フレーム照合が成功。
- 参考RSSはChrome関連プロセスの合計で約3,203MiB／2,846MiB。ただし**共有ページの二重計上があり、実機メモリ使用量やSTとの速度比較に使用しない**。次回の試験ツールではLinux PSS/USSも収集できる構成に変更。
- 今回は2シナリオ各1回のみ。高解像度MTの連続3回／キャンセル復帰、実Androidのメモリ・速度、音質試聴、元動画コピー排除は未実施。iPhone検証は延期中。**Gate G2は未合格。**
- 詳細: `docs/feasibility/V060_DESKTOP_MT_MEASUREMENTS.md`。高負荷MTジョブはGitHub Actionsの消費を抑えるため、手動実行時の明示フラグがある場合だけ起動するよう戻した。
- 出力Blob作成後の元WASM出力ArrayBufferを早期に解放する小改善も実装（実ピーク低下は別途測定）。

## 2026-10-13 — v0.6.0 デスクトップ ST 高解像度測定

- 実バイナリ内包の単一HTML（app commit `b26ebc8b77e407a7a267b11bcd74666912b2e471`、CI artifact `11801040425`）をLinux Chromiumで実際に実行。720p級10秒と1080p級5秒、映像のみ/AAC、逆再生/往復再生を**合計11回**保存・ffprobe・全動画デコードし成功した。
- 無音Ping-pongは720p/1080pともに3回連続成功。処理時間は720p約18〜21秒、1080p約20〜21秒。各実行のブラウザー関連子プロセス合計RSSは概ね727〜891MiB（実端末ピークメモリではない）。
- 合成動画の逆再生・折返しについて、全出力フレームを縮小グレースケール化し、意図した元フレームが隣接フレームより一致することを実測。AACのストリーム時間が両解像度で動画と一致。
- 720p10秒AAC往復再生の変換中、区間1/10の処理中にキャンセルし、不完全な結果が保存できないこと、直後の再実行で正しいMP4が得られることを確認。
- **制約：** STのみ、Linuxデスクトップ合成入力のみ、コンテナのナビゲーション規制により `page.set_content` の実行。高解像度MT・Android実機・音質試聴・カメラMOV/VFR・正確なRSS/WASMピーク・元動画全体コピー排除は未検証。G2は未合格。
- 詳細: `docs/feasibility/V060_DESKTOP_ST_MEASUREMENTS.md`。専用高解像度テスト `tests/feasibility/v060-stress-browser-smoke.py` に全フレームの順序比較を追加（通常CIで自動実行せず、構文のみ確認）。

## 2026-10-13 — v0.6.0 分割メモリ制御と復帰動作の実装開始

- 720p級（短辺720px・長辺1280px・最大10秒）と1080p級（短辺1080px・長辺1920px・最大5秒）を追加。15fps、元動画の拡大なし。区間超過時は自動短縮・自動画質変更をしない。
- 既存FFmpeg ST/MTバイナリの契約を変えず、分割プランの推定YUV420フレーム保持目標を48MiB/区間に抑える。実メモリ上限ではないため、別途実機のRSSやWASMの計測を必須とする。
- 音声トラックの検査WASMを映像エンコード開始前に停止し、必要な場合は変換終了後に再検査。重複起動、失敗プレビューと戻る操作後の古いURL・Worker再利用を防止する。
- 0.5〜10秒/0.5〜5秒の分割計画について、逆再生・往復再生のフレーム数・折返し境界のNode試験を追加。
- 実720p10秒/1080p5秒、各3回連続、音声クリック試聴、Android実機、iPhone（延期）、1GiB入力経路、恒久GPL対応ソース付き配布が未受入。G2判定はINVESTIGATEのまま。詳細は docs/feasibility/G2.md。

## 2026-10-13 — v0.5.0 音声付きST/MT MP4検証結果

- [App CI 38358181120](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38358181120) がST/MT両方で成功。音声あり/なしのH.264 MP4、0.5秒・1秒のモノラルAAC、5秒ステレオ逆再生、10秒ステレオ往復（出力298フレーム・約19.867秒）を保存・ffprobe/PCMデコードで検査。左右独立440Hz/660Hzの順序も保持。
- [Builder CI 38357268611](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38357268611)も両スレッド版のブラウザA/Vテスト合格。短いチャンクの120フレーム制約を完成MP4へ誤適用していた不具合を修正し、出力は最大960フレームかつ予定数完全一致で検査。
- ソース音声検査、AAC正逆変換、H.264へのAAC結合まで実装。実験版では初期値「音声なし」を維持する。
- **未受入**：Android実機・リスニングによるクリック音/無音区間、44.1kHz等のサンプルレート、回転/HDR実撮影、720p10秒/1080p5秒の負荷、GPL対応ソース付き恒久Release。現WASM Actions成果物は2026-10-20に失効。
- 機能としてのデスクトップ成功と製品Gate G1/G2/G3の合格は区別する。詳細は `docs/feasibility/V050_AUDIO_ACCEPTANCE.md`。Browser Kittyへの取込は完成後。

## 2026-10-13 — v0.5.0 AAC検査・結合フローの試験

- 検証済みの`audio-mux`ランタイム能力を要求してから音声オプションを解放する。端末内のFFmpegを使って動画の音声コーデック/チャンネルを軽量に確認する。ソース変更・中止で古い音声検査の結果を破棄する。
- 選択動画のAAC音声を正方向／逆方向に生成し、`--mux-audio`で完成したH.264 MP4へAACトラックだけを結合。旧サイレント変換は変更せず、結合不良は部分結果を保存させない。
- `audio-browser-smoke.py`は二音階の合成動画で実AACデコード/音声の向きを解析し、Silent入力・保存・キャンセルをST/MTで確認する。ビルダーのコンパイル成功だけで公開せず、**実CIと音声波形検証を受入条件**にする。

## 2026-10-13 — v0.5.0 音声モードの開発を開始

- 「音声なし」を既定として維持し、日英UIへ音声選択欄を追加する。現在のv0.4専用WASMでは音声入力の選択を無効とし、映像のみの出力は従来どおり正常に動作させる。
- 専用Builderに正方向／逆方向の音声区間AAC変換を実装。音声トラックがない入力を音声変換成功と誤認しない。大きい元動画全体をブラウザメモリへ一括コピーしない。
- 本番機能として有効化する条件：ST/MT両版の実WASMで、音声トラック検出、動画＋AACのMP4結合、出力の動画長と音声長、折り返し・末尾のクリック音、0.5/5/10秒、モノラル／ステレオ／無音入力の失敗閉鎖を検証する。検証済み新バイナリを個別SHA-256で固定し、`audio-mux`能力をロックに記述して初めてUIを有効化する。
- 現時点ではv0.5.0の開発開始のみ。音声機能の完了承認、G1/G2/G3合格、正式公開やBrowser Kittyへの取り込みを意味しない。

## 2026-10-13 — v0.4.0 Ping-pongの実装・Chrome回帰検証

- 専用Builderコミット `fa52f86b...` はST/MT両方を作成し、正方向→逆方向の実WASM H.264 MP4をブラウザで生成。対応するバイナリとJSのSHA-256を `reverse-runtime.lock.json` に固定して往復モードを有効化済み。
- [Reverse Clip CI 38347758127](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38347758127) でST/MT両方の15→28、31→60、150→298、最短0.5秒、VFR、意図的な黒フレーム、縦長90×160の実MP4生成・保存・デコードを確認。表示・英日切替、10秒逆再生とオフラインSTも回帰確認。
- テスト結果と未検証項目を [v0.4.0受入記録](docs/feasibility/V040_PINGPONG_ACCEPTANCE.md) に分離した。これはデスクトップChromeの結果で、物理Android実機の証拠ではない。
- 注意：今のWASMは2026年10月20日に期限切れのActions成果物。GPL対応ソースを含む恒久Release、Android実機のMT・メモリと高解像度、回転メタデータは別の受入ゲートとして残す。Browser Kittyへの取り込みPRは作らず、ユーザーが手動マージするまでDraft継続。

## 2026-10-13 — v0.4.0 Ping-pongの実装を開始

- 専用Builderへ `--direction forward|reverse` の安全な定義済みチャンク処理と最大16チャンク結合を追加。旧Reverseモードはデフォルト `reverse` のままとし、指定可能な出力fps/サイズ/フレーム数上限は維持する。
- 往復再生のフレーム構成は `0..N-1, N-2..1` の `2N-2` 個。0.5秒／31フレーム／5秒／10秒／非整数時刻を、共通純粋計画関数で検証する。
- Reverse Clip UIにモード選択、往復時の出力予定時間・進捗・保存名・結果表示を追加する。ビルダーの新しいST/MTバイナリを両方ハッシュ固定するまでは往復オプションを無効化して安全にする。
- Builder WASMとブラウザの実MP4再生・保存・フレーム順テストを通した後に往復モードを有効化する。恒久的な対応ソース付きGPLリリースは別途審査し、Android実機のMT・高解像度、VFR・回転素材を検証する。
- これをG1/G2/G3達成やv1.0.0公開とはせず、Browser Kittyには取り込まない。

## 2026-10-13 — v0.3.0 Trim & Reverseの実装を開始

- v0.3.0へ進み、動画の直下の開始・終了ハンドル、数字入力との同期、キーボード操作、選択範囲の**元動画**再生を実装。逆再生結果の確認と編集可能なMP4保存を維持する。
- STとMTの実Chromeで、先頭／途中／終端の短い選択区間、フレーム逆順・15fpsの時間軸・保存名を検証する。320/360/390pxのはみ出しとヘルプの背景スクロールも検査する。
- 言語切替はEN/JAへ。提供されたSVGを両アイコンへ取り込み、ヘッダーを用途が伝わる説明に変更し、フッターの旧版説明を削除する。
- 本マイルストーンのAndroid実機受入および従来のG1/G2/G3は未合格。音声・往復再生・1080p目標は別の予定マイルストーンで維持し、Builder恒久配布も未完了。Browser Kitty PRの追加・マージはしない。

## 2026-10-13 — v0.2.0 動画取込の失敗回復を強化

- 先頭32BのISO-BMFF/QuickTime検査で明らかな拡張子偽装を排除。巨大ファイルの全量コピーは行わない。
- 30秒の読み込みタイムアウト、世代IDでの古い結果拒否、URL/動画の解放、日英エラー表示、元動画名に基づく保存名を追加。
- ST/MTのブラウザ試験に壊れたヘッダー／デコード不能動画／遅延した旧動画読込／応答しない読込／正常動画への再切替・手動の読込中止・複数ドロップの拒否を追加。320/360/390px/PCの横方向表示も自動検証。Android実機については `docs/feasibility/ANDROID_V020_MATRIX.md` に対象ケースと証跡欄を設ける。
- 引き続きG1は未合格、v0.2.0実機受入未完了。正式版やBrowser Kittyへの取り込みは行わない。

## 2026-10-13 — v0.2.0 App Foundationを開始

- v0.1.xで実動画のST/MT WASM逆再生、ローカル単一HTML、10秒分割処理、キャンセル/再試行のブラウザ試験に成功したため、技術スパイクからv0.2.0アプリ基盤の実装へ進む。細かなv0.1.xバージョンを無期限に重ねない。
- **G1は未完了**。バージョン移行はG1合格宣言ではない。優先プラットフォームであるAndroid実機の取込・差し替え・不正ファイル・保存/再試行を検証し、v0.2.0完了判定を別途行う。
- `empty / inspecting / ready / error` 状態を明示し、ファイル世代IDを使って古い非同期結果を捨てる。形式不正、0バイト、デコード不能を日英で区別し、元動画を差し替えると出力を必ず無効化する。
- GitHub Pages ST/MTと直開きSTを継続検証。Android/Windows優先・iPhone延期・Builder恒久配布未完了は維持する。
- Browser Kittyの本体更新や取り込みPRはアプリ完成まで行わない（PR #41は未マージでクローズ済み）。

## 2026-10-13 — v0.1.7 720p級出力の試験範囲

- 長辺720pxの従来設定とは別に、標準720p級の画質（最大長辺1280px）を新設。横1280×720／縦720×1280相当（元動画の拡大なし）を**最大5秒まで**試験する。
- まずデスクトップChrome ST/MTで実1280×720 H.264入力→1秒出力のデコード、正しい寸法・フレーム数・再生可能性を確認する。続いてAndroid実機の720p級5秒、反復・メモリ・キャンセルを検証したうえで720p10秒へ進む。
- 現時点の720p10秒、1080p5秒、音声・往復再生と物理Android MT性能は未完成。Browser Kittyへの取り込みは完成後。

## 2026-10-13 — 取り込み順序の修正・v0.1.6の信頼性改善

- Browser Kittyへの取り込みは**Reverse Clip完成後**。実装中のBrowser Kitty PRは作らない。先行して作成したBrowser Kitty PR #41は未マージでクローズ済み。今後はBuilderとReverse Clipのコード、CI、実機検証を優先する。
- v0.1.6: WASMローダーの遅延完了、処理中の中止、入力ファイル変更時のジョブ所有権を修正。古いジョブのrunnerを必ず解放し、新しい処理のrunnerには触れない。出力動画のメタデータ読み込みもキャンセル可能にする。
- STとMTの実Chrome試験で初期化中キャンセル→差し替え→再変換→MP4保存の一連の動作を確認する。実Android MT性能、長時間反復、標準720p/1080p・音声・往復再生は別途検証する。
- 期限付きActions WASMの恒久配布、FFmpeg/x264/Emscriptenの対応ソース・ライセンスは安定版公開の必須条件。Android/iPhoneの合否やG1～G3を未実施のまま合格扱いにしない。

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

**完了判定（正式なG2基準）：** Gate G2合格。未達の場合は仕様と商品価値を再審査する。**2026-10-16のユーザー指示により、G2未合格のままv0.7.0開発開始だけを例外的に許可。** G2の未受入条件は保持し、G3やv1.0正式リリースの要件を緩めない。

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
