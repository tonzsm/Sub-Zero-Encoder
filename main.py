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

class FFmpegGUI:
    def __init__(self, master: TkinterDnD.Tk):
        self.master = master
        master.title("✨ Subtitle Embedder v33 (Resolution Scaling) ✨")
        master.geometry("740x750") # เพิ่มความสูงเล็กน้อยสำหรับ Scaling

        self.last_output_folder = None
        self.video_duration = 0.0
        self.queue = queue.Queue()
        self.ffmpeg_process = None
        self.progress_file = os.path.normpath(os.path.join(os.getcwd(), "ffmpeg_progress.log"))

        # GUI Variables
        self.video_path = tk.StringVar()
        self.subtitle_path = tk.StringVar()
        self.detected_bitrate_str = tk.StringVar(value="N/A")
        self.detected_audio_str = tk.StringVar(value="N/A")
        self.output_bitrate = tk.StringVar()
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

        # --- (v33) เพิ่ม GUI Variables สำหรับ Scaling ---
        self.scale_var = tk.BooleanVar(value=False)
        self.resolution_var = tk.StringVar(value="Keep Original")
        # Dictionary สำหรับแปลงชื่อที่จำง่ายไปเป็นค่าของ FFmpeg
        self.resolutions = {
            "Keep Original": None,
            "2160p (4K UHD)": "-1:2160",
            "1440p (QHD)": "-1:1440",
            "1080p (Full HD)": "-1:1080",
            "720p (HD)": "-1:720"
        }

        if not self.check_ffmpeg_installed():
            return

        self.create_widgets()
        self.update_codec_options()
        self.toggle_output_widgets()
        self.toggle_scale_widgets() # ตั้งค่าเริ่มต้น

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ... File, Output Frames ...
        file_frame = ttk.LabelFrame(main_frame, text="📁 File Selection", padding="10"); file_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=5); file_frame.columnconfigure(1, weight=1)
        ttk.Label(file_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W); video_entry = ttk.Entry(file_frame, textvariable=self.video_path, state="readonly"); video_entry.grid(row=0, column=1, sticky=tk.EW, padx=5); ttk.Button(file_frame, text="Browse...", command=self.select_video).grid(row=0, column=2)
        ttk.Label(file_frame, text="Subtitle File (.ass, .srt):").grid(row=1, column=0, sticky=tk.W); subtitle_entry = ttk.Entry(file_frame, textvariable=self.subtitle_path, state="readonly"); subtitle_entry.grid(row=1, column=1, sticky=tk.EW, padx=5); ttk.Button(file_frame, text="Browse...", command=self.select_subtitle).grid(row=1, column=2)
        video_entry.drop_target_register(DND_FILES); video_entry.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, self.video_path)); subtitle_entry.drop_target_register(DND_FILES); subtitle_entry.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, self.subtitle_path))
        
        output_frame = ttk.LabelFrame(main_frame, text="📂 Output Settings", padding="10"); output_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5); output_frame.columnconfigure(1, weight=1)
        ttk.Radiobutton(output_frame, text="Save in the same folder as input", variable=self.output_dir_mode, value="same", command=self.toggle_output_widgets).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(output_frame, text="Save to a custom folder:", variable=self.output_dir_mode, value="custom", command=self.toggle_output_widgets).grid(row=1, column=0, sticky=tk.W)
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.custom_output_dir, state=tk.DISABLED); self.output_dir_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.output_dir_button = ttk.Button(output_frame, text="Browse...", command=self.select_output_dir, state=tk.DISABLED); self.output_dir_button.grid(row=1, column=2)

        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Encoding Configuration", padding="10"); config_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5); config_frame.columnconfigure(1, weight=1)
        gpu_check = ttk.Checkbutton(config_frame, text="Use GPU Acceleration (Recommended)", variable=self.use_gpu_var,command=self.update_codec_options); gpu_check.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        ttk.Label(config_frame, text="Detected Video:").grid(row=1, column=0, sticky=tk.W, pady=(5,0)); ttk.Label(config_frame, textvariable=self.detected_bitrate_str).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(5,0))
        ttk.Label(config_frame, text="Detected Audio:").grid(row=2, column=0, sticky=tk.W); ttk.Label(config_frame, textvariable=self.detected_audio_str).grid(row=2, column=1, columnspan=2, sticky=tk.W)
        
        # --- (v33) เพิ่ม UI สำหรับ Scaling ---
        scale_check = ttk.Checkbutton(config_frame, text="Enable Resolution Scaling", variable=self.scale_var, command=self.toggle_scale_widgets); scale_check.grid(row=3, column=0, sticky=tk.W, pady=(5,0))
        self.resolution_combo = ttk.Combobox(config_frame, textvariable=self.resolution_var, values=list(self.resolutions.keys()), state="readonly"); self.resolution_combo.grid(row=3, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        # ------------------------------------

        ttk.Label(config_frame, text="Output Video Bitrate:").grid(row=4, column=0, sticky=tk.W, pady=(5,0)); ttk.Entry(config_frame, textvariable=self.output_bitrate).grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Video Codec:").grid(row=5, column=0, sticky=tk.W, pady=(5,0)); self.codec_combo = ttk.Combobox(config_frame, textvariable=self.codec_var, state="readonly"); self.codec_combo.grid(row=5, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Preset:").grid(row=6, column=0, sticky=tk.W, pady=(5,0)); self.preset_combo = ttk.Combobox(config_frame, textvariable=self.preset_var, state="readonly"); self.preset_combo.grid(row=6, column=1, columnspan=2, sticky=tk.EW, pady=(5,0))
        ttk.Label(config_frame, text="Audio Codec:").grid(row=7, column=0, sticky=tk.W, pady=(5,0))
        self.audio_codec_combo = ttk.Combobox(config_frame, textvariable=self.audio_codec_var, values=['copy', 'aac', 'ac3'], state="readonly"); self.audio_codec_combo.grid(row=7, column=1, sticky=tk.EW, pady=(5,0), padx=(0,5))
        self.audio_bitrate_entry = ttk.Combobox(config_frame, textvariable=self.audio_bitrate_var, width=8, values=['128k', '192k', '256k', '320k']); self.audio_bitrate_entry.grid(row=7, column=2, sticky=tk.W, pady=(5,0))

        # ... Trim, Action, Progress frames (เหมือนเดิม) ...
        trim_frame = ttk.LabelFrame(main_frame, text="✂️ Time Trimming", padding="10"); trim_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5); trim_frame.columnconfigure(1, weight=1)
        trim_check = ttk.Checkbutton(trim_frame, text="Enable Trimming", variable=self.trim_var, command=self.toggle_trim_widgets); trim_check.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(trim_frame, text="Start Time (HH:MM:SS):").grid(row=1, column=0, sticky=tk.W, padx=5); self.start_entry = ttk.Entry(trim_frame, textvariable=self.start_time_var); self.start_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(trim_frame, text="End Time (HH:MM:SS):").grid(row=2, column=0, sticky=tk.W, padx=5); self.end_entry = ttk.Entry(trim_frame, textvariable=self.end_time_var); self.end_entry.grid(row=2, column=1, sticky=tk.EW, padx=5); self.toggle_trim_widgets()
        action_frame = ttk.Frame(main_frame); action_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=5)
        self.embed_button = ttk.Button(action_frame, text="🚀 Start", command=self.start_embedding_thread); self.embed_button.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        self.stop_button = ttk.Button(action_frame, text="🛑 Stop", command=self.stop_process, state=tk.DISABLED); self.stop_button.grid(row=0, column=1, sticky=tk.EW, padx=(5, 5))
        self.log_button = ttk.Button(action_frame, text="Show Log", command=self.toggle_log_window); self.log_button.grid(row=0, column=2, sticky=tk.EW, padx=(5, 5))
        self.open_folder_button = ttk.Button(action_frame, text="📂 Open Folder", command=self.open_output_folder, state=tk.DISABLED); self.open_folder_button.grid(row=0, column=3, sticky=tk.EW, padx=(5, 0))
        action_frame.columnconfigure(0, weight=1); action_frame.columnconfigure(1, weight=1); action_frame.columnconfigure(2, weight=1); action_frame.columnconfigure(3, weight=1)
        progress_frame = ttk.Frame(main_frame); progress_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=10)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100); self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_text); self.progress_label.pack(side=tk.RIGHT, padx=5)
        status_bar = ttk.Label(self.master, textvariable=self.status_text, relief=tk.SUNKEN, anchor=tk.W, padding=5); status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        main_frame.columnconfigure(0, weight=1)
        self.log_window = None

    def run_ffmpeg_process(self):
        if not self.video_path.get() or not self.subtitle_path.get() or not self.output_bitrate.get(): self.queue.put("__ERROR__:Missing input file, subtitle file, or bitrate."); return
        video_in = os.path.normpath(self.video_path.get()); subtitle_in = os.path.normpath(self.subtitle_path.get()); bitrate = self.output_bitrate.get()
        video_basename = os.path.basename(video_in); name_without_ext, extension = os.path.splitext(video_basename); output_filename = f"{name_without_ext}_subbed{extension}"
        if self.output_dir_mode.get() == "custom" and self.custom_output_dir.get(): output_dir = os.path.normpath(self.custom_output_dir.get()); video_out = os.path.join(output_dir, output_filename)
        else: video_out = os.path.join(os.path.dirname(video_in), output_filename)
        video_out = os.path.normpath(video_out)
        self.last_output_folder = os.path.dirname(video_out)
        command_parts = ["ffmpeg", "-hide_banner", "-nostats"]
        if self.use_gpu_var.get(): command_parts.extend(["-hwaccel", "cuda"])
        command_parts.extend(['-i', video_in])
        
        video_filter_chain = []
        
        # --- (v33) เพิ่มฟิลเตอร์ Scaling ก่อนฟิลเตอร์อื่น ---
        if self.scale_var.get():
            selected_res = self.resolution_var.get()
            scale_value = self.resolutions.get(selected_res)
            if scale_value:
                video_filter_chain.append(f"scale={scale_value}")
        # -----------------------------------------------

        subtitle_path_escaped = subtitle_in.replace('\\', '\\\\').replace(':', '\\:'); _, sub_ext = os.path.splitext(subtitle_in)
        if sub_ext.lower() == '.ass': video_filter_chain.append(f"ass=filename='{subtitle_path_escaped}'")
        elif sub_ext.lower() == '.srt': video_filter_chain.append(f"subtitles=filename='{subtitle_path_escaped}':charenc=UTF-8")
        else: self.queue.put(f"__ERROR__:Unsupported subtitle format: {sub_ext}"); return
        
        audio_codec_parts = []; selected_audio_codec = self.audio_codec_var.get()
        if self.trim_var.get():
            if selected_audio_codec == 'copy': messagebox.showwarning("Audio Codec Warning", "Audio cannot be copied when trimming. Falling back to 'aac' codec."); selected_audio_codec = 'aac'; self.audio_codec_var.set('aac')
            start_time_str = self.start_time_var.get(); end_time_str = self.end_time_var.get(); trim_options = []
            if start_time_str and self.time_to_seconds(start_time_str) is not None: trim_options.append(f"start={self.time_to_seconds(start_time_str)}")
            if end_time_str and self.time_to_seconds(end_time_str) is not None: trim_options.append(f"end={self.time_to_seconds(end_time_str)}")
            if trim_options:
                video_trim_string = f"trim={':'.join(trim_options)}"; audio_trim_string = f"atrim={':'.join(trim_options)}"
                video_filter_chain.append(video_trim_string); video_filter_chain.append("setpts=PTS-STARTPTS")
                audio_filter_chain = [audio_trim_string, "asetpts=PTS-STARTPTS"]
                command_parts.extend(['-af', ",".join(audio_filter_chain)])
        if selected_audio_codec == 'copy': audio_codec_parts.extend(["-c:a", "copy"])
        else: audio_codec_parts.extend(["-c:a", selected_audio_codec, "-b:a", self.audio_bitrate_var.get()])
        command_parts.extend(['-vf', ",".join(video_filter_chain)]); command_parts.extend(["-c:v", self.codec_var.get(), "-b:v", bitrate, "-preset", self.preset_var.get()]); command_parts.extend(audio_codec_parts); command_parts.extend([video_out, "-y", "-progress", self.progress_file])
        print("--- Executing Command List: ---"); print(command_parts); print("--------------------------------")
        try:
            si = subprocess.STARTUPINFO();
            if os.name == 'nt': si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = subprocess.SW_HIDE
            self.ffmpeg_process = subprocess.Popen(command_parts, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, startupinfo=si, universal_newlines=True, encoding='utf-8', errors='ignore')
            threading.Thread(target=self.stream_log_reader, args=(self.ffmpeg_process.stderr,), daemon=True).start(); threading.Thread(target=self.monitor_progress, daemon=True).start()
        except Exception as e: self.queue.put(f"__ERROR__:A Python error occurred:\n{e}")

    # ... (โค้ดที่เหลือเหมือนเดิมทั้งหมด) ...
    def toggle_scale_widgets(self):
        """(v33) เปิด/ปิด Combobox สำหรับเลือกความละเอียด"""
        state = "readonly" if self.scale_var.get() else tk.DISABLED
        self.resolution_combo.config(state=state)
        
    def get_video_info(self):
        video_file = self.video_path.get()
        if not video_file: return
        self.status_text.set("🔍 Status: Analyzing video..."); self.master.update_idletasks()
        try:
            probe = ffmpeg.probe(video_file, cmd='ffprobe'); format_info = probe['format']
            if 'bit_rate' in format_info: bitrate_bps = int(format_info['bit_rate']); self.output_bitrate.set(f"{round(bitrate_bps / 1000 / 1000)}M"); self.detected_bitrate_str.set(f"{bitrate_bps / 1000:.0f} kbps ({bitrate_bps / 1000 / 1000:.2f} Mbps)")
            else: self.detected_bitrate_str.set("N/A"); self.output_bitrate.set("15M")
            self.video_duration = float(format_info.get('duration', 0.0))
            if self.end_time_var.get() == "": self.end_time_var.set(time.strftime('%H:%M:%S', time.gmtime(self.video_duration)))
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video' and not s.get('disposition', {}).get('attached_pic')), None)
            if video_stream:
                codec_name = video_stream.get('codec_name', '').lower()
                if 'h265' in codec_name or 'hevc' in codec_name: self.codec_var.set('hevc_nvenc' if self.use_gpu_var.get() else 'libx265')
                elif 'h264' in codec_name: self.codec_var.set('h264_nvenc' if self.use_gpu_var.get() else 'libx264')
            audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            if audio_stream:
                audio_codec = audio_stream.get('codec_name', 'N/A'); audio_bitrate = int(audio_stream.get('bit_rate', 0)) // 1000; channels = int(audio_stream.get('channels', 0))
                if channels == 1: channel_str = "mono"
                elif channels == 2: channel_str = "stereo"
                elif channels == 6: channel_str = "5.1"
                else: channel_str = f"{channels} channels"
                self.detected_audio_str.set(f"{audio_codec.upper()}, {audio_bitrate} kbps, {channel_str}")
                self.audio_codec_var.set(audio_codec if audio_codec in ['aac', 'ac3'] else 'aac'); self.audio_bitrate_var.set(f"{audio_bitrate}k" if audio_bitrate > 0 else "192k")
            else: self.detected_audio_str.set("No audio stream found")
            self.status_text.set("✅ Status: Ready")
        except Exception as e: self.status_text.set(f"❌ Status: Error analyzing video"); messagebox.showerror("Analysis Error", f"Could not analyze video:\n\n{e}"); self.detected_audio_str.set("N/A")
    def open_output_folder(self):
        if self.last_output_folder and os.path.exists(self.last_output_folder): os.startfile(self.last_output_folder)
        else: messagebox.showwarning("Open Folder", "Output folder not found or process has not been run yet.")
    def toggle_trim_widgets(self):
        is_trimming = self.trim_var.get(); state = tk.NORMAL if is_trimming else tk.DISABLED
        self.start_entry.config(state=state); self.end_entry.config(state=state)
        if is_trimming and self.audio_codec_var.get() == 'copy': self.audio_codec_var.set('aac')
        elif not is_trimming: self.audio_codec_var.set('copy')
    def toggle_output_widgets(self): state = tk.NORMAL if self.output_dir_mode.get() == "custom" else tk.DISABLED; self.output_dir_entry.config(state=state); self.output_dir_button.config(state=state)
    def check_ffmpeg_installed(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"): self.master.after(100, self._show_ffmpeg_error_and_quit); return False
        return True
    def _show_ffmpeg_error_and_quit(self): messagebox.showerror("Error", "FFmpeg/ffprobe not found."); self.master.destroy()
    def time_to_seconds(self, time_str):
        try:
            parts = str(time_str).split(':'); s=0
            if len(parts) == 3: s = int(parts[0])*3600+int(parts[1])*60+float(parts[2])
            elif len(parts) == 2: s = int(parts[0])*60+float(parts[1])
            elif len(parts) == 1 and parts[0]!='': s = float(parts[0])
            return s
        except (ValueError, IndexError): return None
    def select_output_dir(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path: self.custom_output_dir.set(path)
    def find_matching_subtitle(self, video_path):
        if not video_path: return
        path_without_ext, _ = os.path.splitext(video_path)
        potential_sub_path_ass = path_without_ext + ".ass"
        if os.path.exists(potential_sub_path_ass): self.subtitle_path.set(potential_sub_path_ass); self.status_text.set("✅ Status: Found matching .ass subtitle")
        else:
            potential_sub_path_srt = path_without_ext + ".srt"
            if os.path.exists(potential_sub_path_srt): self.subtitle_path.set(potential_sub_path_srt); self.status_text.set("✅ Status: Found matching .srt subtitle")
    def select_video(self):
        path = filedialog.askopenfilename(filetypes=(("Video Files", "*.mp4 *.mkv"), ("All files", "*.*")))
        if path: self.video_path.set(path); self.get_video_info(); self.find_matching_subtitle(path)
    def handle_drop(self, event, target_var):
        filepath = event.data.strip('{}')
        if filepath:
            target_var.set(filepath)
            if target_var == self.video_path: self.get_video_info(); self.find_matching_subtitle(filepath)
    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                if isinstance(message, float): self.progress_var.set(message); self.progress_text.set(f"{message:.1f}%")
                elif isinstance(message, str):
                    if message == "__DONE__": self.on_ffmpeg_done(was_cancelled=False); return
                    elif message == "__CANCELLED__": self.on_ffmpeg_done(was_cancelled=True); return
                    elif message.startswith("__ERROR__:"): self.on_ffmpeg_error(message.replace("__ERROR__:", "", 1)); return
                    elif message.startswith("__LOG__:"): self.update_log_display(message.replace("__LOG__:", "", 1))
        except queue.Empty: pass
        self.master.after(100, self.check_queue)
    def start_embedding_thread(self):
        self.open_folder_button.config(state=tk.DISABLED); self.cleanup_files()
        while not self.queue.empty(): self.queue.get()
        if self.log_window and self.log_window.winfo_exists(): self.log_text.config(state=tk.NORMAL); self.log_text.delete(1.0, tk.END); self.log_text.config(state=tk.DISABLED)
        self.embed_button.config(state="disabled"); self.stop_button.config(state="normal"); self.status_text.set("⏳ Status: Processing...")
        threading.Thread(target=self.run_ffmpeg_process, daemon=True).start(); self.master.after(100, self.check_queue)
    def monitor_progress(self):
        start_time = time.time()
        while not os.path.exists(self.progress_file):
            if self.ffmpeg_process.poll() is not None: break
            if time.time() - start_time > 5: self.queue.put("__LOG__:Warning: Progress file not created."); break
            time.sleep(0.5)
        while self.ffmpeg_process.poll() is None:
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    lines=f.readlines(); last_progress={k:v for k,v in (l.strip().split('=',1) for l in lines if'='in l)}
                    if 'out_time_ms' in last_progress and self.video_duration>0: self.queue.put(min(int(last_progress['out_time_ms'])/1e6/self.video_duration*100,100))
            except Exception: pass
            time.sleep(0.5)
        return_code = self.ffmpeg_process.wait(); self.queue.put("__DONE__" if return_code==0 else "__CANCELLED__")
    def on_ffmpeg_done(self, was_cancelled):
        self.embed_button.config(state="normal"); self.stop_button.config(state="disabled"); self.ffmpeg_process = None
        if was_cancelled: self.status_text.set("🛑 Status: Operation stopped or failed."); self.progress_var.set(0); self.progress_text.set("")
        else:
            self.status_text.set(f"🎉 Status: Done! Output saved."); self.progress_var.set(100); self.progress_text.set("100.0%")
            self.open_folder_button.config(state=tk.NORMAL)
            video_in = os.path.normpath(self.video_path.get()); video_basename = os.path.basename(video_in); name_without_ext, extension = os.path.splitext(video_basename); output_filename = f"{name_without_ext}_subbed{extension}"
            video_out = os.path.join(self.last_output_folder, output_filename)
            messagebox.showinfo("✅ Success!", f"Video created:\n\n{video_out}")
        self.cleanup_files()
    def on_ffmpeg_error(self, error_detail):
        self.embed_button.config(state="normal"); self.stop_button.config(state="disabled"); self.ffmpeg_process=None
        self.status_text.set("❌ Status: Error"); messagebox.showerror("Error",f"An error occurred:\n\n{error_detail}"); self.cleanup_files()
    def cleanup_files(self):
        if os.path.exists(self.progress_file):
            try: os.remove(self.progress_file)
            except PermissionError: pass
    def stop_process(self):
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            try: self.ffmpeg_process.stdin.write('q'); self.ffmpeg_process.stdin.flush()
            except (IOError, ValueError, BrokenPipeError): self.ffmpeg_process.terminate()
            finally: self.stop_button.config(state="disabled")
    def update_codec_options(self):
        use_gpu=self.use_gpu_var.get()
        if use_gpu: self.codec_combo['values']=['hevc_nvenc','h264_nvenc']; self.preset_combo['values']=['slow','medium','fast']; self.codec_var.set('hevc_nvenc'); self.preset_var.set('slow')
        else: self.codec_combo['values']=['libx265','libx264']; self.preset_combo['values']=['veryslow','slower','slow','medium','fast','faster','veryfast']; self.codec_var.set('libx265'); self.preset_var.set('medium')
    def select_subtitle(self):
        path = filedialog.askopenfilename(filetypes=(("Subtitle Files","*.ass;*.srt"),("All files","*.*")))
        if path: self.subtitle_path.set(path)
    def toggle_log_window(self):
        if self.log_window and self.log_window.winfo_exists(): self.log_window.deiconify(); self.log_window.lift()
        else:
            self.log_window=tk.Toplevel(self.master); self.log_window.title("Log"); self.log_window.geometry("900x500")
            log_frame=ttk.Frame(self.log_window,padding=5); log_frame.pack(fill=tk.BOTH,expand=True)
            self.log_text=tk.Text(log_frame,wrap=tk.WORD,state=tk.DISABLED,bg="#2b2b2b",fg="#d3d3d3",font=("Courier New",9))
            scrollbar=ttk.Scrollbar(log_frame,command=self.log_text.yview); self.log_text.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT,fill=tk.Y); self.log_text.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
            self.log_window.protocol("WM_DELETE_WINDOW",self.log_window.withdraw)
    def stream_log_reader(self,pipe):
        try:
            for line in iter(pipe.readline, ''):
                if line: self.queue.put(f"__LOG__:{line.strip()}")
        finally: pipe.close()
    def update_log_display(self,log_line):
        if self.log_window and self.log_window.winfo_exists():
            self.log_text.config(state=tk.NORMAL); self.log_text.insert(tk.END,log_line+'\n'); self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FFmpegGUI(root)
    def on_closing():
        if app.ffmpeg_process: app.stop_process()
        app.cleanup_files(); root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    if 'destroy' not in str(getattr(app, '_show_ffmpeg_error_and_quit', '')): root.mainloop()