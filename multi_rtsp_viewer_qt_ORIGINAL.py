
# multi_rtsp_viewer_qt.py

import os
import sys
import json
import datetime
import time
import numpy as np
import av
from PyQt5.QtWidgets import (
    QApplication, QLabel, QGridLayout, QVBoxLayout, QMainWindow,
    QWidget, QToolBar, QAction, QFileDialog
)
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QSize
from concurrent.futures import ThreadPoolExecutor

CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "config.json"
WIDTH, HEIGHT = 320, 240
FPS = 10

# Лог-файл
os.makedirs("logs", exist_ok=True)
log_path = "logs/disconnects.log"

def log_event(text):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full = f"{timestamp} {text}"
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(full + "\n")
    print(full)

# Загрузка конфигурации
if not os.path.exists(CONFIG_PATH):
    print(f"[ERROR] Config not found: {CONFIG_PATH}")
    sys.exit(1)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CAMERAS = json.load(f)

if not CAMERAS:
    print("[WARNING] Config is empty.")
    sys.exit(1)

class CameraStream:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.container = None
        self.connected = False
        self.last_frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        self.last_latency = None
        self.reconnect()

    def reconnect(self):
        try:
            if self.container:
                self.container.close()
            self.container = av.open(self.url, options={
                "rtsp_transport": "tcp",
                "fflags": "nobuffer",
                "flags": "low_delay",
                "max_delay": "100000"
            })
            self.stream = self.container.streams.video[0]
            self.stream.thread_type = 'AUTO'
            self.connected = True
            log_event(f"[CONNECTED] {self.name}")
        except Exception as e:
            self.connected = False
            log_event(f"[DISCONNECTED] {self.name}: {e}")

    def read(self):
        if not self.connected:
            self.reconnect()
            time.sleep(0.2)
            return False, self.last_frame, None
        try:
            for packet in self.container.demux(self.stream):
                for frame in packet.decode():
                    img = frame.to_ndarray(format='bgr24')
                    self.last_frame = img
                    if frame.pts is not None and frame.time_base is not None:
                        pts_time = float(frame.pts * frame.time_base)
                        now = time.time()
                        if pts_time < now:
                            latency = now - pts_time
                            self.last_latency = latency
                            return True, img, latency
                    return True, img, None
        except Exception as e:
            self.connected = False
            log_event(f"[ERROR] {self.name}: {e}")
            return False, self.last_frame, None
        return False, self.last_frame, None

    def release(self):
        if self.container:
            self.container.close()

class CameraWidget(QLabel):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: black; color: white")
        self.setText(name)

    def update_frame(self, frame, latency=None):
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(img).scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
        if latency is not None:
            self.setToolTip(f"{self.name} | Latency: {latency:.2f}s")
        else:
            self.setToolTip(self.name)

class MainWindow(QMainWindow):
    def __init__(self, cameras):
        super().__init__()
        self.setWindowTitle("RTSP Camera Viewer (Qt)")
        self.setMinimumSize(640, 480)

        self.page = 0
        self.streams = [CameraStream(name, url) for name, url in cameras.items()]
        self.executor = ThreadPoolExecutor(max_workers=len(self.streams))

        self.grid = QGridLayout()
        self.widgets = []
        self.central = QWidget()
        self.central.setLayout(self.grid)
        self.setCentralWidget(self.central)

        self.PAGE_SIZE = 9
        self.total_pages = (len(self.streams) + self.PAGE_SIZE - 1) // self.PAGE_SIZE

        self.build_grid()

        self.toolbar = QToolBar("Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)

        fullscreen_action = QAction(QIcon(), "Fullscreen", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.toolbar.addAction(fullscreen_action)

        screenshot_action = QAction(QIcon(), "Screenshot", self)
        screenshot_action.triggered.connect(self.save_screenshot)
        self.toolbar.addAction(screenshot_action)

        exit_action = QAction(QIcon(), "Exit", self)
        exit_action.triggered.connect(self.close)
        self.toolbar.addAction(exit_action)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(int(1000 / FPS))

    def build_grid(self):
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                self.grid.removeWidget(widget)
                widget.deleteLater()
        self.widgets.clear()

        current = self.streams[self.page * self.PAGE_SIZE:(self.page + 1) * self.PAGE_SIZE]
        cols = 3
        for idx, stream in enumerate(current):
            widget = CameraWidget(stream.name)
            self.widgets.append(widget)
            self.grid.addWidget(widget, idx // cols, idx % cols)

    def update_frames(self):
        streams = self.streams[self.page * self.PAGE_SIZE:(self.page + 1) * self.PAGE_SIZE]
        results = self.executor.map(lambda s: s.read(), streams)
        for (ok, frame, latency), widget in zip(results, self.widgets):
            if ok:
                widget.update_frame(frame, latency)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def save_screenshot(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/screenshot_{self.page + 1}_{timestamp}.png"
        pixmap = self.centralWidget().grab()
        pixmap.save(filename)
        log_event(f"[SCREENSHOT] Saved: {filename}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
        elif event.key() in (Qt.Key_D, Qt.Key_Right):
            self.page = (self.page + 1) % self.total_pages
            self.build_grid()
        elif event.key() in (Qt.Key_A, Qt.Key_Left):
            self.page = (self.page - 1 + self.total_pages) % self.total_pages
            self.build_grid()
        elif event.key() == Qt.Key_F:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_P:
            self.save_screenshot()

    def closeEvent(self, event):
        self.executor.shutdown()
        for s in self.streams:
            s.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(CAMERAS)
    window.resize(1280, 720)
    window.show()
    sys.exit(app.exec_())
