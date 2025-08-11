<h1 align="center">Sub-Zero Encoder</h1>

<p align="center">
  A user-friendly GUI for hardcoding subtitles into video files, built with Python and powered by the mighty FFmpeg.
</p>

<p align="center">
  <a href="https://github.com/tonzsm/Sub-Zero-Encoder/releases/latest"><img alt="Latest Release" src="https://img.shields.io/github/v/release/tonzsm/Sub-Zero-Encoder?style=for-the-badge&logo=github"></a>
  <a href="https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/tonzsm/Sub-Zero-Encoder?style=for-the-badge"></a>
</p>

---

### 🚀 Key Features

*   **Dual Encoding Modes:**
    *   **Quality (CRF):** Focuses on maintaining consistent visual quality. (Recommended)
    *   **Bitrate:** Focuses on controlling the final file size.
*   **Smart CRF Recommendations:** Automatically suggests the optimal CRF range and sets a default value based on the video's resolution (SD, 720p, 1080p, 4K).
*   **GPU Acceleration Support:** Harness the power of NVIDIA (NVENC), AMD (AMF), and Intel (QSV) for lightning-fast encoding.
*   **Versatile Encoding Options:**
    *   Adjust Codec (H.264, H.265), Preset, and CRF/Bitrate.
    *   Scale video to standard resolutions (4K, 1440p, 1080p, 720p).
    *   Trim videos to encode only the specific segment you need.
    *   Configure audio codec and bitrate, or simply copy the original stream.
*   **User-Friendly Interface:**
    *   Drag & Drop support for both video and subtitle files.
    *   Automatically finds `.ass` or `.srt` subtitle files with matching video names.
    *   A real-time log window to monitor FFmpeg's progress.
*   **Customizable Output:**
    *   Choose between saving in the same folder or a custom directory.
    *   Use a filename template with useful placeholders like `{filename}`, `{codec}`, `{quality}`, and `{date}`.

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