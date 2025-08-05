# Sub-Zero Encoder ✨

**The ultimate GUI for embedding and trimming subtitles with FFmpeg.**

Sub-Zero Encoder is a user-friendly graphical interface for FFmpeg, designed to make hardsubbing subtitles a simple and powerful experience. Whether you're a professional subtitler or a hobbyist, this tool streamlines the entire process of embedding, trimming, and encoding your videos with pixel-perfect subtitles.

[![Screenshot of Sub-Zero Encoder] ](https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/Sub-Zero-Encoder-GUI.png)

---

## 📥 Downloads

The latest stable and ready-to-use version of the application is available on the **[Releases Page](https://github.com/tonzsm/Sub-Zero-Encoder/releases)**.

Just download the `.zip` file from the latest release, extract it, and run the `.exe` file. No installation needed!

---

## 🔥 Key Features

*   **Seamless Subtitle Integration:** Burn `.ass` and `.srt` subtitles directly into your video files, creating a single, easy-to-share file.
*   **Precision Time Trimming:** Easily trim the start and end times of your video. The tool intelligently handles both video and audio streams to ensure perfect synchronization.
*   **High-Performance Encoding:**
    *   **GPU Acceleration:** Utilizes NVIDIA's NVENC (h264/hevc) for lightning-fast encoding.
    *   **CPU Encoding:** Supports high-quality software encoding with `libx264` and `libx265`.
*   **Smart File Analysis:**
    *   Automatically detects video and audio properties (bitrate, resolution, codecs) to provide intelligent default settings.
    *   Automatically finds matching subtitle files (`.ass` or `.srt`) in the same folder as your video.
*   **Advanced Audio Control:**
    *   Choose to **copy** the original audio for perfect quality when not trimming.
    *   Re-encode audio to popular formats like **AAC** or **AC3** with adjustable bitrate.
*   **Resolution Scaling:** Downscale your 4K videos to 1440p, 1080p, or 720p to save space and ensure compatibility.
*   **Intuitive User Interface:**
    *   Drag & Drop support for video and subtitle files.
    *   Real-time progress bar and status updates.
    *   A detailed FFmpeg log window for power users.

---

## 🚀 Getting Started

### For Users
1.  Go to the **[Releases Page](https://github.com/tonzsm/Sub-Zero-Encoder/releases)**.
2.  Download the `Sub-Zero-Encoder.zip` file from the latest release.
3.  Extract the zip file.
4.  Run `Sub-Zero-Encoder.exe`. That's it!

### For Developers
1.  **Ensure FFmpeg is installed:** You must have a working version of FFmpeg and FFprobe in your system's PATH, **OR** place `ffmpeg.exe` and `ffprobe.exe` inside a `bin` folder in the project directory.
2.  Clone the repository:
    ```bash
    git clone https://github.com/tonzsm/Sub-Zero-Encoder.git
    ```
3.  Install Python libraries:
    ```bash
    pip install tkinterdnd2 ffmpeg-python
    ```
4.  Run the application:
    ```bash
    python your_script_name.py
    ```

---

## 🛠️ Built With

*   **Python 3**
*   **Tkinter** (with `tkinterdnd2` for Drag & Drop)
*   **FFmpeg**
*   **ffmpeg-python** (for file analysis)
*   **PyInstaller** (for building the executable)

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.
