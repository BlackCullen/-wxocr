import os
import time
import tkinter as tk
from tkinter import Toplevel, Canvas
from tkinter.scrolledtext import ScrolledText
from PIL import ImageGrab
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID

wechat_ocr_dir = r"C:\Users\admin\AppData\Roaming\Tencent\WeChat\XPlugin\Plugins\WeChatOCR\7079\extracted\WeChatOCR.exe"
wechat_dir = r"D:\WeChat\[3.9.11.17]"

def ocr_result_callback(img_path, results):
    print(f"OCR result received for {img_path}")
    
    try:
        if 'ocrResult' in results and isinstance(results['ocrResult'], list):
            sorted_texts = sorted(results['ocrResult'], key=lambda x: x['location']['top'])
            sorted_texts_str = "\n".join([item['text'] for item in sorted_texts])
        else:
            sorted_texts_str = "Invalid OCR results format."
    except Exception as e:
        sorted_texts_str = f"Error processing OCR results: {str(e)}"
    
    output_window.config(state=tk.NORMAL)
    output_window.delete(1.0, tk.END)
    output_window.insert(tk.END, sorted_texts_str)
    output_window.config(state=tk.DISABLED)

def take_screenshot():
    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x_root, event.y_root
    
    def on_mouse_move(event):
        nonlocal start_x, start_y, rect
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x - canvas.winfo_rootx(), start_y - canvas.winfo_rooty(), event.x_root - canvas.winfo_rootx(), event.y_root - canvas.winfo_rooty(), outline='red', width=2)
    
    def on_mouse_up(event):
        nonlocal start_x, start_y, rect
        end_x, end_y = event.x_root, event.y_root
        screenshot_win.destroy()
        
        bbox = (start_x, start_y, end_x, end_y)
        screenshot = ImageGrab.grab(bbox)
        last_screenshot_path = os.path.join(os.getcwd(), "screenshot.png")
        screenshot.save(last_screenshot_path)
        
        # 直接在这里开始OCR任务
        ocr_manager.DoOCRTask(last_screenshot_path)

    screenshot_win = Toplevel(root)
    screenshot_win.attributes("-fullscreen", True)
    screenshot_win.attributes("-alpha", 0.3)
    screenshot_win.attributes("-topmost", True)

    canvas = Canvas(screenshot_win, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    rect = None
    start_x = start_y = 0

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

def create_gui_and_start_ocr():
    global ocr_manager, output_window, root, last_screenshot_path
    last_screenshot_path = os.path.join(os.getcwd(), "screenshot.png")

    root = tk.Tk()
    root.title("WXCOR")

    output_window = ScrolledText(root, state='disabled')
    output_window.pack(fill=tk.BOTH, expand=True)
    
    ocr_manager = OcrManager(wechat_dir)
    ocr_manager.SetExePath(wechat_ocr_dir)
    ocr_manager.SetUsrLibDir(wechat_dir)
    ocr_manager.SetOcrResultCallback(ocr_result_callback)
    
    ocr_manager.StartWeChatOCR()
    
    screenshot_button = tk.Button(root, text="点   击", command=take_screenshot)
    screenshot_button.pack(pady=10)
    
    return root

if __name__ == "__main__":
    root = create_gui_and_start_ocr()
    root.mainloop()