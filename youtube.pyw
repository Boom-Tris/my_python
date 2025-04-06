import os
import threading
import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import customtkinter as ctk

# ตั้งค่าสีธีม
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video Downloader")
        self.geometry("900x750")
        self.minsize(800, 700)
        
        # ตัวแปรสำหรับติดตามสถานะ
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        self.current_file_var = tk.StringVar(value="")
        self.download_type_var = tk.StringVar(value="video")
        self.path_var = tk.StringVar(value=os.path.expanduser('~/Downloads'))
        
        # สร้างส่วนประกอบ GUI
        self.create_widgets()
        
        # อัปเดตรายการไฟล์ครั้งแรก
        self.update_downloaded_files_list()
    
    def create_widgets(self):
        # ส่วนหัว
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=20, pady=10)
        
        self.header_label = ctk.CTkLabel(
            self.header_frame, 
            text="YouTube Downloader",
            font=("Arial", 20, "bold")
        )
        self.header_label.pack(pady=10)
        
        # ส่วนป้อน URL
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.pack(fill="x", padx=20, pady=10)
        
        self.url_label = ctk.CTkLabel(
            self.url_frame, 
            text="Enter YouTube URL or magnet link:"
        )
        self.url_label.pack(anchor="w")
        
        self.url_entry = ctk.CTkEntry(self.url_frame, height=35)
        self.url_entry.pack(fill="x", pady=5)
        
        # ส่วนเลือกโฟลเดอร์
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(fill="x", padx=20, pady=10)
        
        self.path_label = ctk.CTkLabel(self.path_frame, text="Save downloads to:")
        self.path_label.pack(anchor="w")
        
        self.path_entry_frame = ctk.CTkFrame(self.path_frame, fg_color="transparent")
        self.path_entry_frame.pack(fill="x")
        
        self.path_entry = ctk.CTkEntry(
            self.path_entry_frame, 
            textvariable=self.path_var,
            height=35
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            self.path_entry_frame, 
            text="Browse", 
            width=100,
            command=self.browse_folder
        )
        self.browse_button.pack(side="left")
        
        # ส่วนความคืบหน้า
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.current_file_label = ctk.CTkLabel(
            self.progress_frame,
            textvariable=self.current_file_var,
            text_color="#1E90FF"  # สีน้ำเงินสว่าง
        )
        self.current_file_label.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            variable=self.progress_var,
            height=20
        )
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            textvariable=self.status_var
        )
        self.status_label.pack(anchor="w")
        
        # ส่วนตัวเลือกการดาวน์โหลด
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(fill="x", padx=20, pady=10)
        
        self.video_radio = ctk.CTkRadioButton(
            self.options_frame,
            text="Video (MP4)",
            variable=self.download_type_var,
            value="video"
        )
        self.video_radio.pack(side="left", padx=10)
        
        self.audio_radio = ctk.CTkRadioButton(
            self.options_frame,
            text="Audio (MP3)",
            variable=self.download_type_var,
            value="audio"
        )
        self.audio_radio.pack(side="left", padx=10)
        
        # ปุ่มดาวน์โหลด
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=20)
        
        self.download_button = ctk.CTkButton(
            self.button_frame,
            text="Download",
            height=40,
            font=("Arial", 14),
            command=self.start_download
        )
        self.download_button.pack(pady=10)
        
        # ส่วนรายการดาวน์โหลด
        self.downloads_frame = ctk.CTkFrame(self)
        self.downloads_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview สำหรับแสดงรายการไฟล์
        self.tree_frame = ctk.CTkFrame(self.downloads_frame)
        self.tree_frame.pack(fill="both", expand=True)
        
        # สร้าง Treeview ด้วย tkinter (เนื่องจาก CustomTkinter ยังไม่มี Treeview)
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("filename", "size", "date"),
            show="headings",
            selectmode="browse"
        )
        
        # กำหนดสไตล์ให้เข้ากับ CustomTkinter
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                      background="#2a2d2e",
                      foreground="white",
                      rowheight=25,
                      fieldbackground="#2a2d2e",
                      bordercolor="#343638",
                      borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        
        style.configure("Treeview.Heading",
                      background="#3b8ed0",
                      foreground="white",
                      relief="flat")
        style.map("Treeview.Heading",
                background=[('active', '#1f6aa5')])
        
        self.tree.heading("filename", text="File Name", anchor=tk.W)
        self.tree.heading("size", text="Size", anchor=tk.CENTER)
        self.tree.heading("date", text="Date Modified", anchor=tk.CENTER)
        
        self.tree.column("filename", width=400, anchor=tk.W)
        self.tree.column("size", width=150, anchor=tk.CENTER)
        self.tree.column("date", width=200, anchor=tk.CENTER)
        
        self.tree.pack(fill="both", expand=True, side=tk.LEFT)
        
        # Scrollbar (กำหนดให้สวยงามและเข้ากับธีม)
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # ปรับแต่งสไตล์ของ Scrollbar
        style.configure("Vertical.TScrollbar",
                        gripcount=0,
                        background="#4B4B4B", 
                        darkcolor="#3D3D3D",
                        lightcolor="#6A6A6A")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ส่วนท้าย
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=20, pady=10)
        
        self.footer_label = ctk.CTkLabel(
            self.footer_frame,
            text="YouTube Downloader v1.0 | © 2023"
        )
        self.footer_label.pack()
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_var.set(folder_selected)
            self.update_downloaded_files_list()
    
    def update_downloaded_files_list(self):
        # ล้างรายการเก่าทั้งหมด
        for item in self.tree.get_children():
            self.tree.delete(item)

        # อ่านไฟล์ในโฟลเดอร์ที่กำหนด
        download_path = self.path_var.get()
        if os.path.exists(download_path):
            files = os.listdir(download_path)
            for file in sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True):
                filepath = os.path.join(download_path, file)
                if os.path.isfile(filepath):
                    # กรองเฉพาะไฟล์เสียงและวีดีโอ
                    if file.endswith('.mp3') or file.endswith('.mp4'):
                        # เก็บข้อมูลไฟล์
                        size = os.path.getsize(filepath) / (1024*1024)  # ขนาดเป็น MB
                        mtime = os.path.getmtime(filepath)
                        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

                        # เพิ่มเข้า Treeview
                        self.tree.insert("", "end", values=(file, f"{size:.2f} MB", date))
    
    def start_download(self):
        video_url = self.url_entry.get()
        download_type = self.download_type_var.get()
        download_path = self.path_var.get()

        if not video_url:
            messagebox.showwarning("Input Error", "Please enter a YouTube video URL.")
            return
        
        # รีเซ็ตค่าก่อนดาวน์โหลด
        self.current_file_var.set("Starting download...")
        self.progress_var.set(0)
        self.status_var.set("Starting download...")

        # เริ่มดาวน์โหลดใน thread แยกเพื่อไม่ให้ GUI ค้าง
        threading.Thread(
            target=self.download_video,
            args=(video_url, download_path, download_type),
            daemon=True
        ).start()
    
    def download_video(self, url, download_path, download_type):
        try:
            ydl_opts = {
                'outtmpl': f'{download_path}/%(title)s.%(ext)s',
                'progress_hooks': [self.progress_hook],
            }

            if download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                })
            else:
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                self.current_file_var.set(os.path.basename(filename))

            messagebox.showinfo("Success", "Download completed successfully!")
            self.update_downloaded_files_list()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.progress_var.set(0)
            self.status_var.set("Ready")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = float(d.get('_percent_str', '0%').strip('%'))
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')

            # อัปเดตเปอร์เซ็นต์ความคืบหน้า
            self.progress_var.set(percent / 100)

            # อัปเดตสถานะการดาวน์โหลด
            self.status_var.set(f"Downloading: {percent:.1f}% | Speed: {speed} | ETA: {eta}")

            # อัปเดต GUI จาก thread หลัก
            self.after(1, self.update)
        
        elif d['status'] == 'finished':
            self.status_var.set("Download completed!")
            self.progress_var.set(100)
            self.update()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
