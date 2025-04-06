import tkinter as tk
import os
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
from PIL import Image
import torch
import numpy as np
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

# ตัวแปร global
image_to_process = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def load_model():
    """โหลดโมเดล Real-ESRGAN"""
    try:
        model_path = 'weights/RealESRGAN_x4plus.pth'
        
        # สร้างโฟลเดอร์ weights ถ้ายังไม่มี
        os.makedirs('weights', exist_ok=True)
        
        # ตรวจสอบว่าไฟล์โมเดลมีอยู่หรือไม่
        if not os.path.exists(model_path):
            result_label.config(text="❌ ไม่พบโมเดล กรุณาดาวน์โหลดก่อน")
            return None

        # ใช้โครงสร้างโมเดลที่ถูกต้อง (RRDBNet สำหรับ x4plus)
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        
        # โหลดน้ำหนักโมเดล
        loadnet = torch.load(model_path)
        if 'params' in loadnet:
            model.load_state_dict(loadnet['params'], strict=True)
        elif 'params_ema' in loadnet:
            model.load_state_dict(loadnet['params_ema'], strict=True)
        else:
            model.load_state_dict(loadnet, strict=True)
        
        model.eval()
        model = model.to(device)
        
        # สร้าง upsampler โดยกำหนด tile ในตอนเริ่มต้น
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            device=device,
            tile=400,  # กำหนด tile size ที่นี่
            tile_pad=20,
            pre_pad=0
        )
        
        result_label.config(text="✅ โหลดโมเดลสำเร็จ!")
        return upsampler
    except Exception as e:
        result_label.config(text=f"❌ เกิดข้อผิดพลาดขณะโหลดโมเดล: {str(e)}")
        return None

def enhance_image():
    try:
        global image_to_process
        if not image_to_process:
            result_label.config(text="❌ กรุณาเลือกไฟล์ภาพก่อน")
            return

        # โหลดโมเดล
        upsampler = load_model()
        if upsampler is None:
            return

        # เปิดภาพและตรวจสอบขนาด
        img = Image.open(image_to_process).convert('RGB')
        width, height = img.size
        
        # กำหนดขนาดสูงสุดที่ประมวลผลได้
        max_size = 1024
        if width > max_size or height > max_size:
            result_label.config(text="⏳ กำลังลดขนาดภาพก่อนประมวลผล...")
            root.update()
            img.thumbnail((max_size, max_size), Image.LANCZOS)
        
        result_label.config(text="⏳ กำลังปรับปรุงภาพ...")
        root.update()
        
        # แปลงเป็น numpy array
        img_array = np.array(img)
        
        # ประมวลผลภาพ - ไม่ส่งพารามิเตอร์ tile ไปอีกครั้ง
        output, _ = upsampler.enhance(
            img_array, 
            outscale=4  # ระบุเฉพาะ outscale
        )
        
        # แปลงกลับเป็น PIL Image
        output_img = Image.fromarray(output)
        
        # บันทึกผลลัพธ์
        base_name = os.path.splitext(os.path.basename(image_to_process))[0]
        output_dir = os.path.join(os.path.dirname(image_to_process), 'enhanced_results')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}_enhanced.png")
        output_img.save(output_path)
        
        result_label.config(text=f"✅ เสร็จสิ้น!\nไฟล์ถูกบันทึกที่:\n{output_path}")
        confirm_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.DISABLED)
        
    except Exception as e:
        result_label.config(text=f"❌ เกิดข้อผิดพลาด: {str(e)}")

def on_drop(event):
    global image_to_process
    # ลบวงเล็บปีกกาจากเส้นทางไฟล์หากมี
    file_path = event.data.strip('{}')
    if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
        image_to_process = file_path
        result_label.config(text=f"📁 ไฟล์ที่เลือก: {os.path.basename(image_to_process)}")
        confirm_button.config(state=tk.NORMAL)
        cancel_button.config(state=tk.NORMAL)
    else:
        result_label.config(text="❌ กรุณาลากไฟล์ภาพที่ถูกต้อง (PNG, JPG, JPEG, BMP, TIFF)")

def choose_file():
    global image_to_process
    filepath = filedialog.askopenfilename(
        title="เลือกไฟล์ภาพ",
        filetypes=[("ไฟล์ภาพ", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
    )
    if filepath:
        image_to_process = filepath
        result_label.config(text=f"📁 ไฟล์ที่เลือก: {os.path.basename(image_to_process)}")
        confirm_button.config(state=tk.NORMAL)
        cancel_button.config(state=tk.NORMAL)

def confirm_action():
    enhance_image()

def cancel_action():
    global image_to_process
    image_to_process = None
    result_label.config(text="❌ การดำเนินการถูกยกเลิก!")
    confirm_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.DISABLED)

# ตั้งค่า GUI
root = TkinterDnD.Tk()
root.title("เครื่องมือปรับปรุงภาพด้วย AI")
root.geometry("500x650")
root.resizable(False, False)

# กำหนดสไตล์
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Helvetica', 12), borderwidth=1, background="#4CAF50", foreground="white")
style.configure('TLabel', background="#f5f5f5", font=('Helvetica', 12), foreground="#333333")
style.configure('TLabelFrame', background="#f5f5f5", font=('Helvetica', 12), foreground="#333333")
style.configure('TFrame', background="#f5f5f5")

# เฟรมหลัก
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# ส่วนหัว
header = ttk.Label(
    main_frame, 
    text="เครื่องมือปรับปรุงภาพด้วย AI", 
    font=('Helvetica', 18, 'bold'), 
    foreground="#4CAF50", 
    background="#f5f5f5"
)
header.pack(pady=(0, 20))

# คำอธิบาย
description = ttk.Label(
    main_frame,
    text="ปรับปรุงความละเอียดภาพของคุณด้วย AI\nลากและวางไฟล์ภาพหรือเลือกจากคอมพิวเตอร์ของคุณ",
    font=('Helvetica', 12),
    justify=tk.CENTER,
    background="#f5f5f5"
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
    text="📁 ลากและวางภาพที่นี่", 
    font=('Helvetica', 12),
    justify=tk.CENTER,
)
drop_label.pack()

# ปุ่มเลือกไฟล์
choose_button = ttk.Button(
    drop_frame,
    text="เลือกไฟล์ภาพ",
    command=choose_file,
    style='TButton'
)
choose_button.pack(pady=10)

# ป้ายแสดงผล
result_label = ttk.Label(
    main_frame,
    text="",
    font=('Helvetica', 11),
    justify=tk.CENTER,
    wraplength=450,
    background="#f5f5f5"
)
result_label.pack(pady=20)

# เฟรมปุ่มดำเนินการ
button_frame = ttk.Frame(main_frame)
button_frame.pack()

confirm_button = ttk.Button(
    button_frame,
    text="ปรับปรุงภาพ",
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
footer_text = f"พัฒนาโดยใช้ Python และ Real-ESRGAN\nกำลังทำงานบน: {'GPU' if device == 'cuda' else 'CPU'}"
if device == 'cuda':
    footer_text += f"\nGPU: {torch.cuda.get_device_name(0)}"
footer_text += "\nโมเดลจะถูกดาวน์โหลดอัตโนมัติเมื่อใช้งานครั้งแรก"

footer = ttk.Label(
    main_frame,
    text=footer_text,
    font=('Helvetica', 9),
    foreground='gray',
    background="#f5f5f5"
)
footer.pack(pady=(20, 0))

# กำหนดการลากและวาง
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
