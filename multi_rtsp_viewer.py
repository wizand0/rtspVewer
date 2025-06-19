import cv2
import numpy as np

# Названия и ссылки камер
CAMERAS = {

}

# Размер превью каждой камеры
WIDTH, HEIGHT = 320, 240

caps = []
for name, url in CAMERAS.items():
    cap = cv2.VideoCapture(url)
    caps.append((name, cap))

def draw_label(frame, text):
    cv2.putText(frame, text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return frame

while True:
    frames = []
    for name, cap in caps:
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            draw_label(frame, f"{name}: нет сигнала")
        else:
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            draw_label(frame, name)
        frames.append(frame)

    # Сетка 3x3
    rows = [np.hstack(frames[i:i+3]) for i in range(0, len(frames), 3)]
    grid = np.vstack(rows)

    cv2.imshow("📷 Мониторинг 9 камер", grid)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for _, cap in caps:
    cap.release()
cv2.destroyAllWindows()
