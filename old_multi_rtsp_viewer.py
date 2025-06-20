import cv2
import numpy as np
import datetime
import os
import time
import json
import sys
from concurrent.futures import ThreadPoolExecutor

CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "config.json"

if not os.path.exists(CONFIG_PATH):
    print(f"[ERROR] Config not found: {CONFIG_PATH}")
    exit(1)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CAMERAS = json.load(f)

if not CAMERAS:
    print("[WARNING] Config is empty.")
    exit(1)

WIDTH, HEIGHT = 320, 240

os.makedirs("logs", exist_ok=True)
log_path = "logs/disconnects.log"

def log_event(text: str):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {text}\n")
    print(f"{timestamp} {text}")

def draw_label(frame, text, status_ok=True):
    cv2.putText(frame, text, (28, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 1, cv2.LINE_AA)
    color = (0, 255, 0) if status_ok else (0, 0, 255)
    cv2.circle(frame, (10, 15), 6, color, -1)
    return frame

class CameraStream:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.cap = None
        self.connected = False
        self.connect()

    def connect(self):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.url)
        self.connected = self.cap.isOpened()
        if self.connected:
            log_event(f"[CONNECTED] {self.name}")
            for _ in range(5):  # Прогрев — получаем ключевые кадры
                self.cap.read()
                time.sleep(0.1)

    def read(self):
        if not self.cap or not self.cap.isOpened():
            self.connected = False
            self.connect()
            time.sleep(0.2)
            return False, np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        for _ in range(3):
            ret, frame = self.cap.read()
            if ret and frame is not None:
                if not self.connected:
                    log_event(f"[RECOVERED] {self.name}")
                self.connected = True
                return True, frame
            time.sleep(0.05)

        if self.connected:
            log_event(f"[DISCONNECTED] {self.name}")
        self.connected = False
        return False, np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    def release(self):
        if self.cap:
            self.cap.release()

streams = [CameraStream(name, url) for name, url in CAMERAS.items()]

PAGE_SIZE = 9
page = 0
total_pages = (len(streams) + PAGE_SIZE - 1) // PAGE_SIZE

cv2.namedWindow("Camera Monitor", cv2.WINDOW_NORMAL)
fullscreen = False

while True:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    visible_streams = streams[start:end]

    def process_stream(stream):
        ret, frame = stream.read()
        frame = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_NEAREST)
        label = stream.name if ret else f"{stream.name}: no signal"
        return draw_label(frame, label, ret)

    with ThreadPoolExecutor(max_workers=9) as executor:
        frames = list(executor.map(process_stream, visible_streams))

    cols = 3
    rows = [np.hstack(frames[i:i+cols]) for i in range(0, len(frames), cols)]
    grid = np.vstack(rows)

    cv2.putText(grid, f"Page {page + 1}/{total_pages}", (10, grid.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Camera Monitor", grid)

    key = cv2.waitKey(100) & 0xFF
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

for stream in streams:
    stream.release()
cv2.destroyAllWindows()
