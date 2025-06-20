import os
import sys
import json
import subprocess

sys.argv.append("Camera Monitor")

# Переключение в директорию проекта
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_viewer(config_path):
    subprocess.run([sys.executable, "multi_rtsp_viewer.py", "--camera-monitor", config_path])

def run_refresh():
    subprocess.run([sys.executable, "refresh_config.py"])

def select_other_config():
    config_dir = "configs"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print("Создана папка configs. Добавьте туда .json конфигурации.")
        return

    files = [f for f in os.listdir(config_dir) if f.endswith(".json")]
    if not files:
        print("⚠️ Нет доступных конфигураций в папке configs.")
        return

    print("\n📂 Доступные конфигурации:")
    for i, f in enumerate(files):
        print(f"{i + 1}. {f}")

    choice = input("Выберите файл: ")
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(files):
        print("❌ Неверный выбор.")
        return

    selected = os.path.join(config_dir, files[int(choice) - 1])
    run_viewer(selected)

def main():
    while True:
        print("\n==== SafeMonitor CLI Menu ====")
        print("1. View main cameras (main_manual.json)")
        print("2. View entry cameras (main_enter.json)")  # ← новое
        print("3. View other config")
        print("4. Refresh config (check streams)")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            if not os.path.exists("configs/main_manual.json"):
                print("❗ configs/main_manual.json не найден.")
            else:
                run_viewer("configs/main_manual.json")

        elif choice == "2":
            if not os.path.exists("configs/main_enter.json"):
                print("❗ configs/main_enter.json не найден.")
            else:
                run_viewer("configs/main_enter.json")

        elif choice == "3":
            select_other_config()
        elif choice == "4":
            run_refresh()
        elif choice == "5":
            print("👋 Выход...")
            break
        else:
            print("❌ Неверный выбор.")

if __name__ == "__main__":
    main()
