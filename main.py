# FILE: Subtitle Embedder v40.2 (Final Fix)
# --- START OF FULL CODE ---

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import queue
import time
from tkinterdnd2 import DND_FILES, TkinterDnD
import ffmpeg
import shutil
import sys

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FFmpegGUI:
    def __init__(self, master: TkinterDnD.Tk):
        self.master = master
        master.title("✨ Sub-Zero Encoder v40.2 (Final Fix) ✨")
        master.geometry("780x820")

        self.last_output_folder = None
        self.video_duration = 0.0
        self.queue = queue.Queue()
        self.ffmpeg_process = None
        self.progress_file = os.path.normpath(os.path.join(os.getcwd(), "ffmpeg_progress.log"))

        self.effective_duration = 0.0
        self.detected_audio_bitrate_bps = 0
        self.detected_gpu = 'CPU'
        self.original_video_height = 0
        self.gpu_status_var = tk.StringVar(value="(Detecting...)")

        self.video_path = tk.StringVar()
        self.subtitle_path = tk.StringVar()
        self.last_output_video_path = tk.StringVar()
        self.detected_bitrate_str = tk.StringVar(value="N/A")
        self.detected_audio_str = tk.StringVar(value="N/A")
        self.output_bitrate = tk.StringVar(value="15M")
        self.status_text = tk.StringVar(value="✅ Status: Ready | Drag & Drop files here!")
        self.use_gpu_var = tk.BooleanVar(value=True)
        self.codec_var = tk.StringVar()
        self.preset_var = tk.StringVar()
        self.audio_codec_var = tk.StringVar(value="copy")
        self.audio_bitrate_var = tk.StringVar(value="192k")
        self.progress_var = tk.DoubleVar()
        self.progress_text = tk.StringVar(value="")
        self.trim_var = tk.BooleanVar(value=False)
        self.start_time_var = tk.StringVar(value="00:00:00")
        self.end_time_var = tk.StringVar(value="")
        self.output_dir_mode = tk.StringVar(value="same")
        self.custom_output_dir = tk.StringVar()
        self.scale_var = tk.BooleanVar(value=False)
        self.resolution_var = tk.StringVar(value="Keep Original")
        self.filename_template_var = tk.StringVar(value="{filename}_subbed")
        self.resolutions = {
            "Keep Original": None, "2160p (4K UHD)": "-1:2160",
            "1440p (QHD)": "-1:1440", "1080p (Full HD)": "-1:1080", "720p (HD)": "-1:720"
        }
        self.estimated_size_var = tk.StringVar(value="Est. Size: N/A")
        self.eta_var = tk.StringVar(value="")

        if not self.check_ffmpeg_installed(): return
        
        self.create_widgets()
        self.detected_gpu = self.detect_hardware_acceleration()
        self.update_gpu_status_label()
        self.update_codec_options()

        for var in [self.video_path, self.trim_var, self.start_time_var, self.end_time_var, 
                    self.output_bitrate, self.audio_codec_var, self.audio_bitrate_var, self.scale_var, self.resolution_var]:
            var.trace_add("write", self.update_estimations)
        
        self.toggle_output_widgets()
        self.toggle_scale_widgets()
        self.toggle_trim_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        s = ttk.Style(); s.configure("Italic.TLabel", font=("Segoe UI", 9, "italic"))
        
        file_frame = ttk.LabelFrame(main_frame, text="📁 File Selection", padding="10"); file_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=5); file_frame.columnconfigure(1, weight=1)
        ttk.Label(file_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W); video_entry = ttk.Entry(file_frame, textvariable=self.video_path, state="readonly"); video_entry.grid(row=0, column=1, sticky=tk.EW, padx=5); ttk.Button(file_frame, text="Browse...", command=self.select_video).grid(row=0, column=2)
        ttk.Label(file_frame, text="Subtitle File (.ass, .srt):").grid(row=1, column=0, sticky=tk.W); subtitle_entry = ttk.Entry(file_frame, textvariable=self.subtitle_path, state="readonly"); subtitle_entry.grid(row=1, column=1, sticky=tk.EW, padx=5); ttk.Button(file_frame, text="Browse...", command=self.select_subtitle).grid(row=1, column=2)
        video_entry.drop_target_register(DND_FILES); video_entry.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, self.video_path)); subtitle_entry.drop_target_register(DND_FILES); subtitle_entry.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, self.subtitle_path))

        output_frame = ttk.LabelFrame(main_frame, text="📂 Output Settings", padding="10"); output_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5); output_frame.columnconfigure(1, weight=1)
        ttk.Radiobutton(output_frame, text="Save in the same folder as input", variable=self.output_dir_mode, value="same", command=self.toggle_output_widgets).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(output_frame, text="Save to a custom folder:", variable=self.output_dir_mode, value="custom", command=self.toggle_output_widgets).grid(row=1, column=0, sticky=tk.W)
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.custom_output_dir, state=tk.DISABLED); self.output_dir_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.output_dir_button = ttk.Button(output_frame, text="Browse...", command=self.select_output_dir, state=tk.DISABLED); self.output_dir_button.grid(row=1, column=2)
        ttk.Label(output_frame, text="Filename Template:").grid(row=2, column=0, sticky=tk.W, pady=(5,0))
        template_entry = ttk.Entry(output_frame, textvariable=self.filename_template_var); template_entry.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=(5,0))
        placeholder_text = "Placeholders: {filename} {codec} {resolution} {bitrate} {date}"; placeholder_label = ttk.Label(output_frame, text=placeholder_text, style="Italic.TLabel"); placeholder_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(0,5))
        
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Encoding Configuration", padding="10"); config_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5); config_frame.columnconfigure(1, weight=1)
        gpu_frame = ttk.Frame(config_frame); gpu_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        self.gpu_check = ttk.Checkbutton(gpu_frame, text="Use GPU Acceleration", variable=self.use_gpu_var, command=self.update_codec_options); self.gpu_check.pack(side=tk.LEFT)
        gpu_status_label = ttk.Label(gpu_frame, textvariable=self.gpu_status_var, style="Italic.TLabel"); gpu_status_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(config_frame, text="Detected Video:").grid(row=1, column=0, sticky=tk.W, pady=(5,0)); ttk.Label(config_frame, textvariable=self.detected_bitrate_str).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(5,0))
        ttk.Label(config_frame, text="Detected Audio:").grid(row=2, column=0, sticky=tk.W); ttk.Label(config_frame, textvariable=self.detected_audio_str).grid(row=2, column=1, columnspan=2, sticky=tk.W)
        scale_check = ttk.Checkbutton(config_frame, text="Enable Resolution Scaling", variable=self.scale_var, command=self.toggle_scale_widgets); scale_check.grid(row=3, column=0, sticky=tk.W, pady=(5,0))
        self.resolution_combo = ttk.Combobox(config_frame, textvariable=self.resolution_var, values=list(self.resolutions.keys()), state="readonly"); self.resolution_combo.grid(row=3, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Output Video Bitrate:").grid(row=4, column=0, sticky=tk.W, pady=(5,0)); ttk.Entry(config_frame, textvariable=self.output_bitrate).grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Video Codec:").grid(row=5, column=0, sticky=tk.W, pady=(5,0)); self.codec_combo = ttk.Combobox(config_frame, textvariable=self.codec_var, state="readonly"); self.codec_combo.grid(row=5, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Preset:").grid(row=6, column=0, sticky=tk.W, pady=(5,0)); self.preset_combo = ttk.Combobox(config_frame, textvariable=self.preset_var, state="readonly"); self.preset_combo.grid(row=6, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Audio Codec:").grid(row=7, column=0, sticky=tk.W, pady=(5,0))
        self.audio_codec_combo = ttk.Combobox(config_frame, textvariable=self.audio_codec_var, values=['copy', 'aac', 'ac3'], state="readonly"); self.audio_codec_combo.grid(row=7, column=1, sticky=tk.EW, pady=(5,0), padx=(0,5))
        self.audio_bitrate_entry = ttk.Combobox(config_frame, textvariable=self.audio_bitrate_var, width=8, values=['128k', '192k', '256k', '320k']); self.audio_bitrate_entry.grid(row=7, column=2, sticky=tk.W, pady=(5,0))
        
        trim_frame = ttk.LabelFrame(main_frame, text="✂️ Time Trimming", padding="10"); trim_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5); trim_frame.columnconfigure(1, weight=1)
        trim_check = ttk.Checkbutton(trim_frame, text="Enable Trimming", variable=self.trim_var, command=self.toggle_trim_widgets); trim_check.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(trim_frame, text="Start Time (HH:MM:SS):").grid(row=1, column=0, sticky=tk.W, padx=5); self.start_entry = ttk.Entry(trim_frame, textvariable=self.start_time_var); self.start_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(trim_frame, text="End Time (HH:MM:SS):").grid(row=2, column=0, sticky=tk.W, padx=5); self.end_entry = ttk.Entry(trim_frame, textvariable=self.end_time_var); self.end_entry.grid(row=2, column=1, sticky=tk.EW, padx=5)
        
        action_frame = ttk.Frame(main_frame); action_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(10, 5))
        button_group_frame = ttk.Frame(action_frame); button_group_frame.grid(row=0, column=0, sticky=tk.W)
        self.embed_button = ttk.Button(button_group_frame, text="🚀 Start", command=self.start_embedding_thread); self.embed_button.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_button = ttk.Button(button_group_frame, text="🛑 Stop", command=self.stop_process, state=tk.DISABLED); self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        self.log_button = ttk.Button(button_group_frame, text="Show Log", command=self.toggle_log_window); self.log_button.pack(side=tk.LEFT, padx=(0, 5))
        self.open_folder_button = ttk.Button(button_group_frame, text="📂 Open Folder", command=self.open_output_folder, state=tk.DISABLED); self.open_folder_button.pack(side=tk.LEFT, padx=(0, 5))
        self.play_button = ttk.Button(button_group_frame, text="▶️ Play Output", command=self.play_output_video, state=tk.DISABLED); self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        self.estimated_size_label = ttk.Label(action_frame, textvariable=self.estimated_size_var, anchor=tk.E); self.estimated_size_label.grid(row=0, column=1, sticky=tk.E)
        action_frame.columnconfigure(0, weight=0); action_frame.columnconfigure(1, weight=1) 
        
        progress_frame = ttk.Frame(main_frame); progress_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=10)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100); self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.eta_label = ttk.Label(progress_frame, textvariable=self.eta_var, width=12, anchor=tk.E); self.eta_label.pack(side=tk.RIGHT, padx=5)
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_text, width=8); self.progress_label.pack(side=tk.RIGHT, padx=5)

        status_bar = ttk.Label(self.master, textvariable=self.status_text, relief=tk.SUNKEN, anchor=tk.W, padding=5); status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        main_frame.columnconfigure(0, weight=1); self.log_window = None

    def _generate_output_filename(self):
        template = self.filename_template_var.get()
        video_in = self.video_path.get()
        video_basename = os.path.basename(video_in)
        name_without_ext, _ = os.path.splitext(video_basename)
        codec = self.codec_var.get().replace('_', '-').upper()
        resolution = ""
        if self.scale_var.get():
            res_text = self.resolution_var.get()
            if res_text and res_text != "Keep Original":
                resolution = res_text.split(' ')[0]
        else:
            if self.original_video_height > 0:
                resolution = f"{self.original_video_height}p"
        bitrate = self.output_bitrate.get()
        current_date = time.strftime("%Y-%m-%d")
        filename = template.replace("{filename}", name_without_ext)
        filename = filename.replace("{codec}", codec)
        filename = filename.replace("{resolution}", resolution)
        filename = filename.replace("{bitrate}", bitrate)
        filename = filename.replace("{date}", current_date)
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        filename = filename.replace('[]', '').replace('()', '')
        while '--' in filename or '__' in filename or '  ' in filename:
            filename = filename.replace('--', '-').replace('__', '_').replace('  ', ' ')
        return filename.strip().strip('-_ ')

    def update_estimations(self, *args):
        if not self.video_path.get() or self.video_duration <= 0: return
        start_s = self.time_to_seconds(self.start_time_var.get()) or 0.0 if self.trim_var.get() else 0.0
        end_s = self.time_to_seconds(self.end_time_var.get()) or self.video_duration if self.trim_var.get() else self.video_duration
        self.effective_duration = max(0, end_s - start_s)
        is_audio_recode = self.audio_codec_var.get() != 'copy' or self.trim_var.get()
        audio_bps = self._parse_bitrate_to_bps(self.audio_bitrate_var.get()) if is_audio_recode else self.detected_audio_bitrate_bps
        video_bps = self._parse_bitrate_to_bps(self.output_bitrate.get())
        total_bps = video_bps + audio_bps
        if total_bps > 0 and self.effective_duration > 0:
            estimated_bytes = (total_bps / 8) * self.effective_duration
            if estimated_bytes < 1024**2: size_str = f"{estimated_bytes / 1024:.1f} KB"
            elif estimated_bytes < 1024**3: size_str = f"{estimated_bytes / (1024**2):.1f} MB"
            else: size_str = f"{estimated_bytes / (1024**3):.2f} GB"
            self.estimated_size_var.set(f"Est. Size: {size_str}")
        else: self.estimated_size_var.set("Est. Size: N/A")
        self.eta_var.set("")

    def detect_hardware_acceleration(self):
        if shutil.which('nvidia-smi'): return 'NVIDIA'
        try:
            system32_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
            if os.path.exists(os.path.join(system32_path, "amfrt64.dll")): return 'AMD'
            if os.path.exists(os.path.join(system32_path, "libmfxhw64.dll")): return 'INTEL'
        except Exception as e: print(f"Error checking for GPU DLLs: {e}")
        return 'CPU'

    def update_gpu_status_label(self):
        if self.detected_gpu == 'NVIDIA': self.gpu_status_var.set("(Detected: NVIDIA NVENC)")
        elif self.detected_gpu == 'AMD': self.gpu_status_var.set("(Detected: AMD AMF)")
        elif self.detected_gpu == 'INTEL': self.gpu_status_var.set("(Detected: Intel QSV)")
        else:
            self.gpu_status_var.set("(GPU not available)");
            if hasattr(self, 'gpu_check'): self.use_gpu_var.set(False); self.gpu_check.config(state=tk.DISABLED)

    def update_codec_options(self, *args):
        use_gpu = self.use_gpu_var.get()
        if use_gpu and self.detected_gpu != 'CPU':
            if self.detected_gpu == 'NVIDIA':
                self.codec_combo['values'] = ['hevc_nvenc', 'h264_nvenc']; self.preset_combo['values'] = ['slow', 'medium', 'fast']
                self.codec_var.set('hevc_nvenc'); self.preset_var.set('slow')
            elif self.detected_gpu == 'AMD':
                self.codec_combo['values'] = ['hevc_amf', 'h264_amf']; self.preset_combo['values'] = ['quality', 'balanced', 'speed']
                self.codec_var.set('hevc_amf'); self.preset_var.set('quality')
            elif self.detected_gpu == 'INTEL':
                self.codec_combo['values'] = ['hevc_qsv', 'h264_qsv']; self.preset_combo['values'] = ['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster', 'veryfast']
                self.codec_var.set('hevc_qsv'); self.preset_var.set('medium')
        else:
            if self.detected_gpu == 'CPU': self.use_gpu_var.set(False)
            self.codec_combo['values'] = ['libx265', 'libx264']; self.preset_combo['values'] = ['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster', 'veryfast']
            self.codec_var.set('libx265'); self.preset_var.set('medium')
        self.update_estimations()

    def run_ffmpeg_process(self):
        if not self.video_path.get() or not self.subtitle_path.get() or not self.output_bitrate.get(): self.queue.put(("__ERROR__", "Missing input file, subtitle file, or bitrate.")); return
        video_in = os.path.normpath(self.video_path.get()); subtitle_in = os.path.normpath(self.subtitle_path.get()); bitrate = self.output_bitrate.get()
        _, extension = os.path.splitext(os.path.basename(video_in)); base_output_name = self._generate_output_filename(); output_filename = f"{base_output_name}{extension}"
        output_dir = os.path.dirname(video_in) if self.output_dir_mode.get() == "same" or not self.custom_output_dir.get() else os.path.normpath(self.custom_output_dir.get())
        video_out = os.path.join(output_dir, output_filename); self.last_output_folder = output_dir; self.last_output_video_path.set(video_out)
        command_parts = [self.ffmpeg_path, "-hide_banner", "-nostats"]
        if self.use_gpu_var.get() and self.detected_gpu != 'CPU':
            hwaccel_map = {'NVIDIA': 'cuda', 'INTEL': 'qsv', 'AMD': 'd3d11va'}; hwaccel_param = hwaccel_map.get(self.detected_gpu)
            if hwaccel_param: command_parts.extend(["-hwaccel", hwaccel_param])
        command_parts.extend(['-i', video_in])
        video_filter_chain = []; audio_filter_chain = []
        if self.scale_var.get():
            scale_value = self.resolutions.get(self.resolution_var.get());
            if scale_value: video_filter_chain.append(f"scale={scale_value}")
        subtitle_path_escaped = subtitle_in.replace('\\', '\\\\').replace(':', '\\:'); _, sub_ext = os.path.splitext(subtitle_in)
        if sub_ext.lower() == '.ass': video_filter_chain.append(f"ass=filename='{subtitle_path_escaped}'")
        elif sub_ext.lower() == '.srt': video_filter_chain.append(f"subtitles=filename='{subtitle_path_escaped}':charenc=UTF-8")
        else: self.queue.put(("__ERROR__", f"Unsupported subtitle format: {sub_ext}")); return
        selected_audio_codec = self.audio_codec_var.get()
        if self.trim_var.get():
            if selected_audio_codec == 'copy':
                messagebox.showwarning("Audio Codec Warning", "Audio must be re-encoded when trimming. Falling back to 'aac'."); selected_audio_codec = 'aac'; self.audio_codec_var.set('aac')
            start_s = self.time_to_seconds(self.start_time_var.get()); end_s = self.time_to_seconds(self.end_time_var.get()); trim_options = []
            if start_s is not None: trim_options.append(f"start={start_s}")
            if end_s is not None: trim_options.append(f"end={end_s}")
            if trim_options:
                trim_str = ":".join(trim_options); video_filter_chain.append(f"trim={trim_str}"); audio_filter_chain.append(f"atrim={trim_str}")
            video_filter_chain.append("setpts=PTS-STARTPTS"); audio_filter_chain.append("asetpts=PTS-STARTPTS")
        if selected_audio_codec == 'copy': audio_codec_parts = ["-c:a", "copy"]
        else: audio_codec_parts = ["-c:a", selected_audio_codec, "-b:a", self.audio_bitrate_var.get()]
        if video_filter_chain: command_parts.extend(['-vf', ",".join(video_filter_chain)])
        if audio_filter_chain: command_parts.extend(['-af', ",".join(audio_filter_chain)])
        command_parts.extend(["-c:v", self.codec_var.get(), "-b:v", bitrate, "-preset", self.preset_var.get()]); command_parts.extend(audio_codec_parts); command_parts.extend([video_out, "-y", "-progress", self.progress_file])
        print("--- Executing Command List: ---"); print(command_parts); print("--------------------------------")
        try:
            si = subprocess.STARTUPINFO();
            if os.name == 'nt': si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = subprocess.SW_HIDE
            self.ffmpeg_process = subprocess.Popen(command_parts, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, startupinfo=si, universal_newlines=True, encoding='utf-8', errors='ignore')
            threading.Thread(target=self.stream_log_reader, args=(self.ffmpeg_process.stderr,), daemon=True).start(); threading.Thread(target=self.monitor_progress, daemon=True).start()
        except Exception as e: self.queue.put(("__ERROR__", f"A Python error occurred:\n{e}"))
    def get_video_info(self, *args):
        self.original_video_height = 0
        video_file = self.video_path.get();
        if not video_file: return
        self.status_text.set("🔍 Status: Analyzing video..."); self.master.update_idletasks()
        try:
            probe = ffmpeg.probe(video_file, cmd=self.ffprobe_path); format_info = probe['format']
            if 'bit_rate' in format_info:
                bitrate_bps = int(format_info['bit_rate']); self.output_bitrate.set(f"{round(bitrate_bps / 1000000)}M"); self.detected_bitrate_str.set(f"{bitrate_bps / 1000:.0f} kbps ({bitrate_bps / 1000000:.2f} Mbps)")
            else:
                self.detected_bitrate_str.set("N/A"); self.output_bitrate.set("15M")
            self.video_duration = float(format_info.get('duration', 0.0))
            if self.end_time_var.get() == "": self.end_time_var.set(time.strftime('%H:%M:%S', time.gmtime(self.video_duration)))
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video' and not s.get('disposition', {}).get('attached_pic')), None)
            if video_stream:
                self.original_video_height = int(video_stream.get('height', 0))
                self.update_codec_options(); codec_name = video_stream.get('codec_name', '').lower()
                if self.use_gpu_var.get():
                    if 'h264' in codec_name: self.codec_var.set(self.codec_var.get().replace('hevc', 'h264'))
                else:
                    if 'h264' in codec_name: self.codec_var.set('libx264')
            audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            if audio_stream:
                audio_codec = audio_stream.get('codec_name', 'N/A'); self.detected_audio_bitrate_bps = int(audio_stream.get('bit_rate', 0)); audio_bitrate_kbps = self.detected_audio_bitrate_bps // 1000; channels = int(audio_stream.get('channels', 0))
                channel_str = {1: "mono", 2: "stereo", 6: "5.1"}.get(channels, f"{channels} channels")
                self.detected_audio_str.set(f"{audio_codec.upper()}, {audio_bitrate_kbps} kbps, {channel_str}"); self.audio_codec_var.set(audio_codec if audio_codec in ['aac', 'ac3'] else 'aac'); self.audio_bitrate_var.set(f"{audio_bitrate_kbps}k" if audio_bitrate_kbps > 0 else "192k")
            else:
                self.detected_audio_bitrate_bps = 0; self.detected_audio_str.set("No audio stream found")
            self.status_text.set("✅ Status: Ready"); self.update_estimations()
        except Exception as e:
            self.status_text.set("❌ Status: Error analyzing video"); messagebox.showerror("Analysis Error", f"Could not analyze video:\n\n{e}"); self.detected_audio_str.set("N/A")
    def play_output_video(self):
        video_file = self.last_output_video_path.get()
        if video_file and os.path.exists(video_file):
            try: os.startfile(video_file)
            except Exception as e: messagebox.showerror("Playback Error", f"Could not play the file:\n\n{e}")
        else: messagebox.showwarning("File Not Found", "Output video file not found or process has not been run yet.")
    def check_ffmpeg_installed(self):
        self.ffmpeg_path = get_resource_path(os.path.join("bin", "ffmpeg.exe")); self.ffprobe_path = get_resource_path(os.path.join("bin", "ffprobe.exe"))
        if not os.path.exists(self.ffmpeg_path) or not os.path.exists(self.ffprobe_path):
            self.master.after(100, self._show_ffmpeg_error_and_quit); return False
        return True
    def monitor_progress(self):
        start_time = time.time()
        while not os.path.exists(self.progress_file):
            if self.ffmpeg_process.poll() is not None: break
            if time.time() - start_time > 5: self.queue.put(("__LOG__", "Warning: Progress file not created.")); break
            time.sleep(0.5)
        process_start_time = time.time(); finishing_signal_sent = False
        while self.ffmpeg_process.poll() is None:
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines(); last_progress = {k: v for k, v in (l.strip().split('=', 1) for l in lines if '=' in l)}
                    if 'out_time_ms' in last_progress and self.effective_duration > 0:
                        processed_s = int(last_progress['out_time_ms']) / 1e6; progress = min(processed_s / self.effective_duration * 100, 100.0)
                        if progress >= 99.9 and not finishing_signal_sent:
                            self.queue.put(("__FINISHING__",)); finishing_signal_sent = True
                        elif not finishing_signal_sent:
                            eta_str = ""
                            if progress > 0.5:
                                elapsed_time = time.time() - process_start_time; total_time_estimated = elapsed_time / (progress / 100); eta_seconds = total_time_estimated - elapsed_time
                                if eta_seconds > 0: eta_str = f"ETA {time.strftime('%H:%M:%S', time.gmtime(eta_seconds))}"
                            self.queue.put(("__PROGRESS__", progress, eta_str))
            except Exception: pass
            time.sleep(0.5)
        return_code = self.ffmpeg_process.wait()
        self.queue.put(("__DONE__" if return_code == 0 else "__CANCELLED__",))
    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait(); msg_type = message[0]
                if msg_type == "__PROGRESS__":
                    progress_val = message[1]; self.progress_var.set(min(progress_val, 99.9)); self.progress_text.set(f"{min(progress_val, 99.9):.1f}%"); self.eta_var.set(message[2])
                elif msg_type == "__FINISHING__":
                    self.progress_var.set(99.9); self.progress_text.set("99.9%"); self.eta_var.set(""); self.status_text.set("⏳ Status: Finalizing video file (Muxing)...")
                elif msg_type == "__DONE__": self.on_ffmpeg_done(was_cancelled=False); return
                elif msg_type == "__CANCELLED__": self.on_ffmpeg_done(was_cancelled=True); return
                elif msg_type == "__ERROR__": self.on_ffmpeg_error(message[1]); return
                elif msg_type == "__LOG__": self.update_log_display(message[1])
        except queue.Empty: pass
        except (IndexError, TypeError): pass
        self.master.after(100, self.check_queue)
    def start_embedding_thread(self):
        self.update_estimations()
        if self.trim_var.get() and self.effective_duration <= 0: messagebox.showerror("Invalid Time Trim", "End time must be greater than start time."); return
        self.open_folder_button.config(state=tk.DISABLED); self.play_button.config(state=tk.DISABLED); self.cleanup_files()
        self.progress_var.set(0); self.progress_text.set(""); self.eta_var.set("")
        while not self.queue.empty(): self.queue.get()
        if self.log_window and self.log_window.winfo_exists(): self.log_text.config(state=tk.NORMAL); self.log_text.delete(1.0, tk.END); self.log_text.config(state=tk.DISABLED)
        self.embed_button.config(state="disabled"); self.stop_button.config(state="normal"); self.status_text.set("⏳ Status: Processing...")
        threading.Thread(target=self.run_ffmpeg_process, daemon=True).start(); self.master.after(100, self.check_queue)
    def on_ffmpeg_done(self, was_cancelled):
        self.embed_button.config(state="normal"); self.stop_button.config(state="disabled"); self.ffmpeg_process = None; self.eta_var.set("")
        if was_cancelled:
            self.status_text.set("🛑 Status: Operation stopped or failed."); self.progress_var.set(0); self.progress_text.set("")
        else:
            self.status_text.set("🎉 Status: Done! Output saved."); self.progress_var.set(100); self.progress_text.set("100.0%")
            self.open_folder_button.config(state=tk.NORMAL); self.play_button.config(state=tk.NORMAL)
            video_out = self.last_output_video_path.get()
            messagebox.showinfo("✅ Success!", f"Video created:\n\n{video_out}")
        self.cleanup_files()
    def on_ffmpeg_error(self, error_detail):
        self.embed_button.config(state="normal"); self.stop_button.config(state="disabled"); self.ffmpeg_process=None
        self.status_text.set("❌ Status: Error"); messagebox.showerror("Error",f"An error occurred:\n\n{error_detail}"); self.cleanup_files()
    def stop_process(self):
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            try: self.ffmpeg_process.stdin.write('q\n'); self.ffmpeg_process.stdin.flush()
            except (IOError, ValueError, BrokenPipeError): self.ffmpeg_process.terminate()
            finally: self.stop_button.config(state="disabled")
    def cleanup_files(self):
        if os.path.exists(self.progress_file):
            try: os.remove(self.progress_file)
            except PermissionError: pass
    def time_to_seconds(self, time_str):
        try:
            parts = str(time_str).split(':'); s=0.0
            if len(parts) == 3: s = int(parts[0])*3600+int(parts[1])*60+float(parts[2])
            elif len(parts) == 2: s = int(parts[0])*60+float(parts[1])
            elif len(parts) == 1 and parts[0]!='': s = float(parts[0])
            return s
        except (ValueError, IndexError): return None
    def handle_drop(self, event, target_var):
        filepath = event.data.strip('{}');
        if filepath:
            target_var.set(filepath)
            if target_var == self.video_path: self.get_video_info(); self.find_matching_subtitle(filepath)
    def find_matching_subtitle(self, video_path):
        if not video_path: return
        path_without_ext, _ = os.path.splitext(video_path)
        for ext in ['.ass', '.srt']:
            potential_sub_path = path_without_ext + ext
            if os.path.exists(potential_sub_path):
                self.subtitle_path.set(potential_sub_path); self.status_text.set(f"✅ Status: Found matching {ext} subtitle"); break
    def select_video(self):
        path = filedialog.askopenfilename(filetypes=(("Video Files", "*.mp4 *.mkv"), ("All files", "*.*")))
        if path: self.video_path.set(path); self.get_video_info(); self.find_matching_subtitle(path)
    def select_subtitle(self):
        path = filedialog.askopenfilename(filetypes=(("Subtitle Files","*.ass;*.srt"),("All files","*.*")))
        if path: self.subtitle_path.set(path)
    def select_output_dir(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path: self.custom_output_dir.set(path)
    def toggle_trim_widgets(self):
        state = tk.NORMAL if self.trim_var.get() else tk.DISABLED
        self.start_entry.config(state=state); self.end_entry.config(state=state)
        if self.trim_var.get() and self.audio_codec_var.get() == 'copy': self.audio_codec_var.set('aac')
    def toggle_scale_widgets(self): self.resolution_combo.config(state="readonly" if self.scale_var.get() else tk.DISABLED)
    def toggle_output_widgets(self):
        state = tk.NORMAL if self.output_dir_mode.get() == "custom" else tk.DISABLED
        self.output_dir_entry.config(state=state); self.output_dir_button.config(state=state)
    def open_output_folder(self):
        if self.last_output_folder and os.path.exists(self.last_output_folder): os.startfile(self.last_output_folder)
        else: messagebox.showwarning("Open Folder", "Output folder not found or process has not been run yet.")
    def stream_log_reader(self,pipe):
        try:
            for line in iter(pipe.readline, ''):
                if line: self.queue.put(("__LOG__", line.strip()))
        finally: pipe.close()
    def update_log_display(self,log_line):
        if self.log_window and self.log_window.winfo_exists():
            self.log_text.config(state=tk.NORMAL); self.log_text.insert(tk.END,log_line+'\n'); self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)
    def toggle_log_window(self):
        if self.log_window and self.log_window.winfo_exists(): self.log_window.deiconify(); self.log_window.lift()
        else:
            self.log_window=tk.Toplevel(self.master); self.log_window.title("Log"); self.log_window.geometry("900x500")
            log_frame=ttk.Frame(self.log_window,padding=5); log_frame.pack(fill=tk.BOTH,expand=True)
            self.log_text=tk.Text(log_frame,wrap=tk.WORD,state=tk.DISABLED,bg="#2b2b2b",fg="#d3d3d3",font=("Courier New",9))
            scrollbar=ttk.Scrollbar(log_frame,command=self.log_text.yview); self.log_text.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT,fill=tk.Y); self.log_text.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
            self.log_window.protocol("WM_DELETE_WINDOW",self.log_window.withdraw)
    def _parse_bitrate_to_bps(self, bitrate_str: str) -> int:
        bitrate_str = str(bitrate_str).strip().lower()
        try:
            if bitrate_str.endswith('k'): return int(float(bitrate_str[:-1]) * 1000)
            elif bitrate_str.endswith('m'): return int(float(bitrate_str[:-1]) * 1000000)
            else: return int(bitrate_str)
        except (ValueError, TypeError): return 0

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FFmpegGUI(root)
    def on_closing():
        if app.ffmpeg_process: app.stop_process()
        app.cleanup_files(); root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    if not hasattr(app, 'ffmpeg_path') or not app.ffmpeg_path: pass
    else: root.mainloop()