import yt_dlp
import subprocess
import tkinter as tk
from tkinter import messagebox

def download_video(url, download_path='.', download_type='video'):
    try:
        if download_type == 'audio':
            # ใช้ subprocess.run เพื่อดาวน์โหลดไฟล์เสียงในรูปแบบ mp3
            command = f'yt-dlp -f bestaudio --extract-audio --audio-format mp3 {url}'
            subprocess.run(command, shell=True, check=True)
            messagebox.showinfo("Success", "Audio has been downloaded successfully!")
        else:  # Default is to download as video
            # ใช้ yt-dlp API ในการดาวน์โหลดวิดีโอ
            ydl_opts = {
                'outtmpl': f'{download_path}/%(title)s.%(ext)s',  # ตั้งชื่อไฟล์ที่ดาวน์โหลด
                'format': 'bestvideo[height<=1080]+bestaudio/best',  # ดาวน์โหลดคุณภาพดีที่สุดที่มีความละเอียด 1080p
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Video has been downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def on_download_button_click():
    video_url = url_entry.get()
    download_type = download_type_var.get()

    if not video_url:
        messagebox.showwarning("Input Error", "Please enter a YouTube video URL.")
        return
    
    if download_type == 'audio':
        download_video(video_url, download_type='audio')
    else:
        download_video(video_url, download_type='video')

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Create URL input label and entry
url_label = tk.Label(root, text="Enter YouTube Video URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Create download type selection
download_type_var = tk.StringVar(value='video')
download_type_frame = tk.Frame(root)
download_type_frame.pack(pady=10)

audio_radio = tk.Radiobutton(download_type_frame, text="Audio", variable=download_type_var, value='audio')
audio_radio.pack(side=tk.LEFT, padx=10)
video_radio = tk.Radiobutton(download_type_frame, text="Video", variable=download_type_var, value='video')
video_radio.pack(side=tk.LEFT, padx=10)

# Create download button
download_button = tk.Button(root, text="Download", command=on_download_button_click)
download_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
