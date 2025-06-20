import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Переключение в директорию проекта
os.chdir(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = "configs"
MAIN_CONFIG = os.path.join(CONFIG_DIR, "main_manual.json")

# Создание папки и основного конфига, если нужно
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(MAIN_CONFIG):
    with open(MAIN_CONFIG, "w", encoding="utf-8") as f:
        json.dump({
            "Серверная": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/202",
            "Лестница (лев)": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/302",
            "Лестница (прав)": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/602",
            "Техники": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/1002",
            "Энергоцентр": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/2102",
            "Руководство": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/2302",
            "Бухгалтерия": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/2402",
            "Мастерская": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/2502",
            "Коридор": "rtsp://web:Triton2073@10.15.13.252:554/Streaming/Channels/2602"
        }, f, indent=2, ensure_ascii=False)

def run_viewer(config_path):
    subprocess.run([sys.executable, "multi_rtsp_viewer.py", config_path])

def run_refresh():
    subprocess.run([sys.executable, "refresh_config.py"])

def open_file():
    file_path = filedialog.askopenfilename(initialdir=CONFIG_DIR, title="Выберите конфиг",
                                           filetypes=(("JSON files", "*.json"),))
    if file_path:
        run_viewer(file_path)


ENTRY_CONFIG = os.path.join(CONFIG_DIR, "main_enter.json")

def launch_entry():
    if not os.path.exists(ENTRY_CONFIG):
        messagebox.showerror("Ошибка", "main_enter.json не найден.")
        return
    run_viewer(ENTRY_CONFIG)

def launch_main():
    if not os.path.exists(MAIN_CONFIG):
        messagebox.showerror("Ошибка", "main_manual.json не найден.")
        return
    run_viewer(MAIN_CONFIG)

def gui():
    root = tk.Tk()
    root.title("SafeMonitor GUI")
    root.geometry("300x200")

    tk.Label(root, text="Выберите действие:", font=("Arial", 12)).pack(pady=10)

    tk.Button(root, text="Основные камеры", width=25, command=launch_main).pack(pady=5)
    tk.Button(root, text="Входная зона (4 камеры)", width=25, command=launch_entry).pack(pady=5)  # ← новая
    tk.Button(root, text="Открыть другой конфиг", width=25, command=open_file).pack(pady=5)
    tk.Button(root, text="Обновить список камер", width=25, command=run_refresh).pack(pady=5)
    tk.Button(root, text="Выход", width=25, command=root.quit).pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    gui()
