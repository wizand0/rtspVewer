# add_registrator.py
import os
import json
import av
from getpass import getpass

def is_stream_alive(url):
    try:
        container = av.open(url, timeout=2, options={"rtsp_transport": "tcp"})
        container.close()
        return True
    except Exception:
        return False

def main():
    print("=== Add New Registrator ===")
    name = input("📛 Name (used in filename): ").strip().replace(" ", "_")
    ip = input("🌐 IP address: ").strip()
    port = input("🔌 RTSP port [554]: ").strip() or "554"
    user = input("👤 Username: ").strip()
    password = getpass("🔑 Password (hidden): ").strip()

    max_channels = 32
    config = {}

    print(f"🔎 Scanning channels on {ip}...")
    for ch in range(1, max_channels + 1):
        rtsp_url = f"rtsp://{user}:{password}@{ip}:{port}/Streaming/Channels/{ch:02d}02"
        if is_stream_alive(rtsp_url):
            print(f"✅ Channel {ch} is alive")
            config[str(ch)] = rtsp_url
        else:
            print(f"❌ Channel {ch} not responding")

    if not config:
        print("🚫 No working streams found.")
        return

    os.makedirs("configs", exist_ok=True)
    output_path = f"configs/{name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"💾 Saved to {output_path}")

if __name__ == "__main__":
    main()
