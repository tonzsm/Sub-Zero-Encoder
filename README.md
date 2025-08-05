# Sub-Zero Encoder ✨

**The ultimate GUI for embedding and trimming subtitles with FFmpeg.**

Sub-Zero Encoder is a user-friendly graphical interface for FFmpeg, designed to make hardsubbing subtitles a simple and powerful experience. Whether you're a professional subtitler or a hobbyist, this tool streamlines the entire process of embedding, trimming, and encoding your videos with pixel-perfect subtitles.

https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/Sub-Zero-Encoder-GUI.png 
![Screenshot of a GUI Version](https://github.com/tonzsm/Sub-Zero-Encoder/blob/main/Sub-Zero-Encoder-GUI.png)

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

## 🛠️ Built With

*   **Python 3**
*   **Tkinter** (with `tkinterdnd2` for Drag & Drop)
*   **FFmpeg** (must be installed and in your system's PATH)
*   **ffmpeg-python** (for file analysis)

---

## 🚀 Getting Started

1.  **Ensure FFmpeg is installed:** You must have a working version of FFmpeg and FFprobe installed on your system and accessible via the system's PATH.
2.  **Install Python libraries:**
    ```bash
    pip install tkinterdnd2 ffmpeg-python
    ```
3.  **Run the application:**
    ```bash
    python your_script_name.py
    ```

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.

*(You can choose any license you like, MIT is a very common and permissive one.)*
