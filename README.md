<p align="center">
  <img src="https://raw.githubusercontent.com/tonzsm/Sub-Zero-Encoder/main/images/logo.png" width="200" alt="Sub-Zero Encoder Logo">
</p>

<h1 align="center">Sub-Zero Encoder</h1>

<p align="center">
  A user-friendly GUI for hardcoding subtitles into video files, built with Python and powered by the mighty FFmpeg.
</p>

<p align="center">
  <a href="https://github.com/tonzsm/Sub-Zero-Encoder/releases/latest"><img alt="Latest Release" src="https://img.shields.io/github/v/release/tonzsm/Sub-Zero-Encoder?style=for-the-badge&logo=github"></a>
  <a href="https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/tonzsm/Sub-Zero-Encoder?style=for-the-badge"></a>
</p>

---

## ✨ Features

Sub-Zero Encoder is packed with features designed to make your workflow as smooth as possible.

*   **Intuitive UI:** A clean and simple graphical user interface.
*   **Drag & Drop:** Full drag and drop support for both video and subtitle files.
*   **Auto-Subtitle Finder:** Automatically detects and loads matching `.ass` or `.srt` subtitle files.
*   **GPU Acceleration:** Utilizes NVIDIA NVENC for blazing-fast encoding speeds.
*   **Standalone & Portable:** Comes bundled with FFmpeg. No external dependencies or installation required. Just extract and run!
*   **Resolution Scaling:** Easily downscale your videos to standard resolutions like 1080p or 720p.
*   **Stable Time Trimming:** Encode only the specific segments you need. The output is **guaranteed** to have perfect audio and subtitle synchronization.
*   **Live Pre-computation:**
    *   **ETA:** Displays the estimated time remaining during the encoding process.
    *   **Estimated File Size:** See the final output file size in real-time as you adjust your settings.
*   **Convenient Output Handling:**
    *   **Open Folder:** Instantly opens the destination folder.
    *   **Play Output:** Plays the finished video with your default media player directly from the app.

## 🖼️ Screenshot

![Screenshot of Sub-Zero Encoder](https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/Sub-Zero-Encoder-GUI.png)

## 🚀 Getting Started

### Prerequisites
*   Windows Operating System (7, 10, 11).
*   An **NVIDIA GPU** is required to use the GPU Acceleration mode. The application will still function in CPU mode without it.

### Installation & Usage
1.  Go to the [**Releases**](https://github.com/tonzsm/Sub-Zero-Encoder/releases) page.
2.  Download the latest `.zip` archive (e.g., `Sub-Zero-Encoder.zip`).
3.  Extract the archive to a folder of your choice.
4.  Run `Sub-Zero-Encoder.exe`.
5.  Drag and drop your files or use the "Browse..." buttons.
6.  Adjust your settings and click **Start**!

## ⚠️ Known Issues

*   **Missing Fonts:** The `.ass` subtitle format sometimes requires specific fonts to be installed on your system. If a required font is not found, FFmpeg may throw an error or substitute the font, potentially affecting the subtitle's appearance. **Please ensure you have the necessary fonts installed for best results.**

## 🗺️ Roadmap

This project is actively developed. Here are some features planned for the future:
- [ ] Batch processing / Queue system
- [ ] Soft-subtitle support (for MKV/MP4)
- [ ] Audio/Subtitle track selection for files with multiple tracks
- [ ] Configuration profiles (Save/Load settings)

## ❤️ Credits

This application wouldn't be possible without these amazing open-source projects:
*   **FFmpeg:** The core of all video and audio processing.
*   **Python:** The programming language used to build the app.
*   **Tkinter / tkinterdnd2:** For the graphical user interface.
*   **ffmpeg-python:** A helpful Python wrapper for FFmpeg.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.