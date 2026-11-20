# Reverse Clip v1.1.1

## 変更点 / What's new

- 変換中は区間・画質・フレームレート・再生モード・音声の設定を無効にしました。途中で設定を変更する場合は「処理を中止」を押します。
- 無効な時刻を入力したときに、以前のタイムライン選択範囲が残る問題を修正しました。
- 日英切り替え時に、サムネイルと元動画のプレビュー表示も切り替わるようにしました。
- 「動画を選ぶ」「撮影して取り込む」のサイズを揃え、スマホの「ファイルから選択」を控えめにしました。
- v1.1.0公開後の共通UI変更と、単独配信可能なMT版の更新を含みます。

- Lock trim and output controls while encoding; use the explicit Cancel conversion action before changing settings.
- Clear stale timeline highlighting for invalid time input and relocalize transient thumbnail/preview messages.
- Equal-size Choose video and Record video buttons, with a subtler mobile file-picker fallback.
- Sync the current Pages UI and raw MT route with all four standalone downloads.

## Downloads

| File | Use |
| --- | --- |
| `reverse-clip-v1.1.1.html` | Single-thread standalone HTML for offline use |
| `reverse-clip-v1.1.1.self-extract.html` | Compressed single-thread standalone HTML |
| `reverse-clip-v1.1.1.mt.html` | Multi-thread HTML for cross-origin-isolated hosts |
| `reverse-clip-v1.1.1.mt.self-extract.html` | Compressed multi-thread HTML with the same hosting requirement |

Previous v1.1.0 downloads remain unchanged. Release assets include SHA-256 checksums and license notices. H.264 MP4 remains the primary verified input; native OS sharing and physical-phone high-resolution endurance are not certified by this release.

## Licenses and corresponding source

The app source is MIT-licensed. The bundled FFmpeg and x264 runtime is GPL-2.0-or-later. See [matching source archive](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/ffmpeg-wasm-sources-v1.10.6.tar.gz) and [GPL addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/VIDEO_REVERSE_LICENSE_ADDENDUM.md).
