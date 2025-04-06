import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
from rembg import remove
from PIL import Image
import os

# ตัวแปรสำหรับเก็บข้อมูลภาพที่เลือก
image_to_process = None

def process_image():
    try:
        if image_to_process:
            # เปิดและลบพื้นหลัง
            input_image = Image.open(image_to_process)
            output_image = remove(input_image)

            # ตั้งชื่อไฟล์ output
            output_path = os.path.join(os.path.dirname(image_to_process), f"{os.path.splitext(os.path.basename(image_to_process))[0]}_no_bg.png")
            output_image.save(output_path)

            result_label.config(text=f"✅ ลบพื้นหลังเสร็จแล้ว! ไฟล์ถูกบันทึกไว้ที่: {output_path}")
            confirm_button.config(state=tk.DISABLED)  # ปิดใช้งานปุ่มยืนยัน
            cancel_button.config(state=tk.DISABLED)   # ปิดใช้งานปุ่มยกเลิก
        else:
            result_label.config(text="❌ กรุณาเลือกไฟล์ก่อนที่จะยืนยัน")
    except Exception as e:
        result_label.config(text=f"❌ เกิดข้อผิดพลาด: {e}")

def on_drop(event):
    global image_to_process
    image_to_process = event.data
    result_label.config(text=f"📁 ไฟล์ที่เลือก: {os.path.basename(image_to_process)}")
    confirm_button.config(state=tk.NORMAL)  # เปิดใช้งานปุ่มยืนยัน
    cancel_button.config(state=tk.NORMAL)   # เปิดใช้งานปุ่มยกเลิก

def choose_file():
    global image_to_process
    filepath = filedialog.askopenfilename(title="เลือกไฟล์ภาพ", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if filepath:
        image_to_process = filepath
        result_label.config(text=f"📁 ไฟล์ที่เลือก: {os.path.basename(image_to_process)}")
        confirm_button.config(state=tk.NORMAL)  # เปิดใช้งานปุ่มยืนยัน
        cancel_button.config(state=tk.NORMAL)   # เปิดใช้งานปุ่มยกเลิก

def confirm_action():
    process_image()

def cancel_action():
    global image_to_process
    image_to_process = None
    result_label.config(text="❌ การลบพื้นหลังถูกยกเลิก!")
    confirm_button.config(state=tk.DISABLED)  # ปิดใช้งานปุ่มยืนยัน
    cancel_button.config(state=tk.DISABLED)   # ปิดใช้งานปุ่มยกเลิก

# ตั้งค่า GUI
root = TkinterDnD.Tk()
root.title("ลบพื้นหลังภาพ")
root.geometry("500x600")

# สไตล์สำหรับปุ่มและป้าย
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Kanit', 12), borderwidth=1, background="#1877f2", foreground="white")
style.configure('TLabel', background="#ffffff", font=('Kanit', 12), foreground="#333333")
style.configure('TLabelFrame', background="#ffffff", font=('Kanit', 12), foreground="#333333")
style.configure('TFrame', background="#ffffff")  # Define background color for ttk.Frame

# เฟรมหลัก
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# หัวแอปพลิเคชัน
header = ttk.Label(
    main_frame, 
    text="เครื่องมือลบพื้นหลังภาพ", 
    font=('Kanit', 18, 'bold'), 
    foreground="#1877f2", 
    background="#ffffff"
)
header.pack(pady=(0, 20))

# โปรแกรมอธิบาย
description = ttk.Label(
    main_frame,
    text="ลบพื้นหลังออกจากภาพของคุณได้อย่างง่ายดาย\nเพียงลากไฟล์มาวางหรือเลือกไฟล์จากเครื่องของคุณ",
    font=('Kanit', 12),
    justify=tk.CENTER,
    background="#ffffff"
)
description.pack(pady=(0, 30))

# พื้นที่ลากและวาง
drop_frame = ttk.LabelFrame(
    main_frame, 
    text=" ลากไฟล์มาวางที่นี่ ", 
    padding=20,
    relief=tk.GROOVE,
    borderwidth=2,
   
)
drop_frame.pack(fill=tk.X, pady=(0, 20))

drop_label = ttk.Label(
    drop_frame, 
    text="📁 ลากไฟล์ภาพมาวางในกรอบนี้", 
    font=('Kanit', 12),
    justify=tk.CENTER,
)
drop_label.pack()

# ปุ่มเลือกไฟล์
choose_button = ttk.Button(
    drop_frame,
    text="เลือกไฟล์ภาพจากเครื่อง",
    command=choose_file,
    style='TButton'
)
choose_button.pack(pady=10)

# ป้ายแสดงผล
result_label = ttk.Label(
    main_frame,
    text="",
    font=('Kanit', 11),
    justify=tk.CENTER,
    wraplength=400,
)
result_label.pack(pady=20)

# เฟรมปุ่มดำเนินการ
button_frame = ttk.Frame(main_frame)
button_frame.pack()

confirm_button = ttk.Button(
    button_frame,
    text="ยืนยัน",
    command=confirm_action,
    state=tk.DISABLED,
    style='TButton'
)
confirm_button.pack(side=tk.LEFT, padx=10)

cancel_button = ttk.Button(
    button_frame,
    text="ยกเลิก",
    command=cancel_action,
    state=tk.DISABLED,
    style='TButton'
)
cancel_button.pack(side=tk.LEFT)

# ส่วนท้าย
footer = ttk.Label(
    main_frame,
    text="พัฒนาโดยใช้ Python และ rembg",
    font=('Kanit', 9),
    foreground='gray',
    background="#ffffff"
)
footer.pack(pady=(20, 0))

# รองรับการลากไฟล์มาวาง
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
