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

*   **Smart GPU Acceleration:** Automatically detects **NVIDIA (NVENC)**, **AMD (AMF)**, and **Intel (QSV)** GPUs to provide the best possible hardware acceleration without any configuration.
*   **Intuitive UI:** A clean and simple graphical user interface with Drag & Drop support.
*   **Auto-Subtitle Finder:** Automatically detects and loads matching `.ass` or `.srt` subtitle files.
*   **Custom Filename Templates:** Take full control of your output filenames with placeholders like `{filename}`, `{resolution}`, and `{codec}`.
*   **Standalone & Portable:** Comes bundled with FFmpeg. No installation required.
*   **Resolution Scaling:** Easily downscale videos to standard resolutions.
*   **Stable Time Trimming:** Encode specific segments with guaranteed audio and subtitle synchronization.
*   **Live Estimates:** See the **ETA** and **Estimated File Size** before and during encoding.
*   **Convenient Output Handling:** Instantly **Open Folder** or **Play Output** file with one click.

## 🖼️ Screenshot

![Screenshot of Sub-Zero Encoder](https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/Sub-Zero-Encoder-GUI.png)

## 🚀 Getting Started

### Prerequisites
*   Windows Operating System (7, 10, 11).
*   For GPU acceleration, a discrete or integrated GPU from **NVIDIA, AMD, or Intel** with up-to-date drivers is required.

### Installation & Usage
1.  Go to the [**Releases**](https://github.com/tonzsm/Sub-Zero-Encoder/releases) page.
2.  Download the latest `Sub-Zero-Encoder.zip` archive.
3.  Extract the archive to a folder of your choice.
4.  Run `Sub-Zero-Encoder.exe`.
5.  Drag and drop your files, adjust settings, and click **Start**!

## ⚠️ Known Issues

*   **Missing Fonts:** The `.ass` subtitle format sometimes requires specific fonts to be installed on your system. If a required font is not found, FFmpeg may produce an error. Please ensure you have the necessary fonts installed for best results.

## 🗺️ Roadmap

- [ ] Batch processing / Queue system
- [ ] Soft-subtitle support (for MKV/MP4)
- [ ] Audio/Subtitle track selection for files with multiple tracks

## ❤️ Credits

This application wouldn't be possible without these amazing open-source projects:
*   **FFmpeg**
*   **Python** & **Tkinter**
*   **ffmpeg-python**
*   **tkinterdnd2**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.