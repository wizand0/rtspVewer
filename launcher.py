import subprocess
import sys
import os
import json

CONFIG_DIR = "configs"
CONFIG_OPTIONS = {
    "1": "main_manual.json",
    "2": "main_enter.json"
}

def main():
    while True:
        print("\n==== SafeMonitor CLI Menu ====")
        print("1. View main cameras (main_manual.json)")
        print("2. View entry cameras (main_enter.json)")
        print("3. View other config")
        print("4. Add new registrator")
        print("5. Refresh config (check streams)")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()

        if choice in ["1", "2"]:
            config_name = CONFIG_OPTIONS[choice]
            config_path = os.path.join(CONFIG_DIR, config_name)
            if not os.path.exists(config_path):
                print(f"[ERROR] Config not found: {config_path}")
                continue

            print(f"✅ Loaded config: {config_path} with {count_streams(config_path)} streams")
            subprocess.run([sys.executable, "multi_rtsp_viewer_qt.py", config_path])

        elif choice == "3":
            path = input("Enter path to config: ").strip()
            if not os.path.exists(path):
                print(f"[ERROR] File not found: {path}")
                continue
            print(f"✅ Loaded config: {path} with {count_streams(path)} streams")
            subprocess.run([sys.executable, "multi_rtsp_viewer_qt.py", path])

        elif choice == "4":
            subprocess.run([sys.executable, "add_registrator.py"])

        elif choice == "5":
            subprocess.run([sys.executable, "refresh_config.py"])

        elif choice == "6":
            print("👋 Bye!")
            break

        else:
            print("❌ Invalid choice.")

def count_streams(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return len(json.load(f))
    except Exception:
        return 0

if __name__ == "__main__":
    main()
