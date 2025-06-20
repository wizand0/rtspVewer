import av
import cv2
import numpy as np
import datetime
import os
import time
import json
import sys
from concurrent.futures import ThreadPoolExecutor

monitoring_enabled = "--camera-monitor" in sys.argv
args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
CONFIG_PATH = args[0] if args else "config.json"

if not os.path.exists(CONFIG_PATH):
    print(f"[ERROR] Config not found: {CONFIG_PATH}")
    exit(1)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CAMERAS = json.load(f)

if not CAMERAS:
    print("[WARNING] Config is empty.")
    exit(1)

WIDTH, HEIGHT = 320, 240  # Сниженное разрешение

os.makedirs("logs", exist_ok=True)
log_path = "logs/disconnects.log"

def log_event(text: str):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {text}\n")
    print(f"{timestamp} {text}")

def draw_label(frame, text, status_ok=True, latency=None):
    cv2.putText(frame, text, (28, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 1, cv2.LINE_AA)
    if latency is not None:
        cv2.putText(frame, f"{latency:.1f}s", (WIDTH - 70, HEIGHT - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1, cv2.LINE_AA)
    color = (0, 255, 0) if status_ok else (0, 0, 255)
    cv2.circle(frame, (10, 15), 6, color, -1)
    return frame

class CameraStream:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.container = None
        self.connected = False
        self.last_frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        self.last_pts = None
        self.reconnect()

    def reconnect(self):
        try:
            if self.container:
                self.container.close()

            options = {
                # "rtsp_transport": "udp",  # включить для теста UDP
                "rtsp_transport": "tcp",    # по умолчанию TCP
                "fflags": "nobuffer",
                "flags": "low_delay",
                "max_delay": "100000"
            }

            self.container = av.open(self.url, options=options)
            self.stream = self.container.streams.video[0]
            self.stream.thread_type = 'AUTO'
            self.connected = True
            log_event(f"[CONNECTED] {self.name}")
        except Exception as e:
            self.connected = False
            log_event(f"[DISCONNECTED] {self.name} - {e}")

    def read(self):
        if not self.connected:
            self.reconnect()
            time.sleep(0.2)
            return False, self.last_frame, None

        latest_frame = None
        try:
            deadline = time.time() + 0.08  # максимум 80 мс
            for packet in self.container.demux(self.stream):
                for frame in packet.decode():
                    latest_frame = frame
                if latest_frame and time.time() > deadline:
                    break

            if latest_frame:
                img = latest_frame.to_ndarray(format='bgr24')
                resized = cv2.resize(img, (WIDTH, HEIGHT), interpolation=cv2.INTER_NEAREST)
                self.last_frame = resized

                # Вычисление задержки по PTS
                pts_time = float(latest_frame.pts * latest_frame.time_base) if latest_frame.pts else None
                if pts_time:
                    latency = time.time() - pts_time
                    return True, resized, latency
                else:
                    return True, resized, None
        except Exception as e:
            log_event(f"[ERROR] {self.name}: {e}")
            self.connected = False
            return False, self.last_frame, None

        return False, self.last_frame, None

    def release(self):
        if self.container:
            self.container.close()

streams = [CameraStream(name, url) for name, url in CAMERAS.items()]
camera_count = len(streams)
COLS, ROWS = (2, 2) if camera_count <= 4 else (3, 3)
PAGE_SIZE = COLS * ROWS
page = 0
total_pages = (camera_count + PAGE_SIZE - 1) // PAGE_SIZE

cv2.namedWindow("Camera Monitor", cv2.WINDOW_NORMAL)
fullscreen = False
TARGET_FPS = 10
FRAME_DELAY = 1 / TARGET_FPS
executor = ThreadPoolExecutor(max_workers=PAGE_SIZE)

while True:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    visible_streams = streams[start:end]

    def process_stream(stream):
        ret, frame, latency = stream.read()
        label = stream.name if ret else f"{stream.name}: no signal"
        return draw_label(frame, label, ret, latency)

    frames = list(executor.map(process_stream, visible_streams))
    rows = [np.hstack(frames[i:i + COLS]) for i in range(0, len(frames), COLS)]
    grid = np.vstack(rows)

    cv2.putText(grid, f"Page {page + 1}/{total_pages}", (10, grid.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Camera Monitor", grid)

    key = cv2.waitKey(1) & 0xFF
    time.sleep(FRAME_DELAY)

    if key == ord('q'):
        break
    elif key == ord('f'):
        fullscreen = not fullscreen
        mode = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
        cv2.setWindowProperty("Camera Monitor", cv2.WND_PROP_FULLSCREEN, mode)
    elif key == 83 or key == ord('d'):
        page = (page + 1) % total_pages
    elif key == 81 or key == ord('a'):
        page = (page - 1 + total_pages) % total_pages
    elif key == ord('p'):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{page+1}_{timestamp}.jpg"
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)
        cv2.imwrite(filepath, grid)
        print(f"[{timestamp}] Скриншот сохранён: {filepath}")

for stream in streams:
    stream.release()
executor.shutdown()
cv2.destroyAllWindows()
