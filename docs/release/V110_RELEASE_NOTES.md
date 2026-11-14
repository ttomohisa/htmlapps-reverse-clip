# Reverse Clip v1.1.0

## 変更点 / What's new

- 動画のサムネイルを見ながら区間を選べます。現在の再生位置の指定と、選択範囲周辺の拡大にも対応しました。
- 逆再生と往復再生をボタンで選べます。出力寸法と選択できる長さを表示します。
- 低解像度・無音の試作、結果のループ再生、対応端末でのMP4共有を追加しました。
- 長辺720px以下の設定で、最長5秒の選択区間を30fpsで書き出せます。試験機能です。既定は15fpsです。
- 開始0.2秒・終了0.7秒のような、ちょうど0.5秒の区間を選べないことがある不具合を修正しました。

- Select a range using timeline thumbnails, mark the current playback position, or zoom around the selection.
- Choose reverse or ping-pong and see the output size and selection limit before rendering.
- Render a silent low-resolution draft, loop the result, or share the MP4 on supported devices.
- Experimental 30fps export supports selections up to 5 seconds at presets with a long edge of 720px or less. The default is 15fps.
- Fixed a rounding issue that could reject an exactly half-second selection.

## Downloads

| File | Use |
| --- | --- |
| `reverse-clip-v1.1.0.html` | Single-thread standalone HTML for offline use |
| `reverse-clip-v1.1.0.self-extract.html` | Compressed single-thread standalone HTML |
| `reverse-clip-v1.1.0.mt.html` | Multi-thread HTML for a host with cross-origin isolation |
| `reverse-clip-v1.1.0.mt.self-extract.html` | Compressed multi-thread HTML with the same hosting requirement |

The release includes SHA-256 checksums and license notices. The main verified format is short H.264 MP4. Native sharing availability depends on the browser and device.

## Licenses and corresponding source

The app source is MIT-licensed. The bundled FFmpeg and x264 runtime is GPL-2.0-or-later. See [matching source archive](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/ffmpeg-wasm-sources-v1.10.6.tar.gz) and [GPL addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/VIDEO_REVERSE_LICENSE_ADDENDUM.md).
