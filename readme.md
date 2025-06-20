<h1 align="center">📹 rtspViewer</h1>

<p align="center">
  <b>Кроссплатформенное Python-приложение для одновременного просмотра RTSP-потоков</b><br>
  <i>Создано как лёгкая альтернатива iVMS-4200, особенно для Linux</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-green" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>

---

## ⚙️ Возможности

- 📌 Отдельный режим для приоритетных камер (`main_manual.json`)
- 🎥 Просмотр до 9 камер одновременно
- 🔁 Автоматическое переподключение при потере потока
- 🧵 Многопоточность и оптимизация памяти
- 🔄 Автообновление конфигурации с исключением недоступных камер
- 🖥️ GUI (Tkinter) и CLI-меню
- 🌐 Windows + Linux поддержка
- 📁 Работа с JSON-файлами конфигурации
- 📦 Простая установка и запуск

---

## 🔍 Зачем создан проект?

На момент создания проекта не существовало удобного рабочего аналога **iVMS-4200** под Linux.  
А оригинальная iVMS-4200 для Windows — тяжеловесная и неповоротливая.

Мне был нужен:
- простой RTSP-клиент;
- минимальная задержка;
- стабильное отображение 9+ камер;
- хорошая производительность на слабом ПК.

---

## 📊 Сравнение с iVMS-4200

Сравнение производилось с помощью моего утилиты мониторинга:  
👉 [github.com/wizand0/monitoring](https://github.com/wizand0/monitoring)

Тестировались параметры:
- **CPU**
- **Память**
- **Потоки**

### CPU
![CPU Comparison](images/comparison_cpu.png)

### Memory
![Memory Comparison](images/comparison_mem.png)

### Threads
![Threads Comparison](images/comparison_threads.png)

---

## 🚀 Быстрый старт

### ⬇️ Windows

```bat
run_gui.bat   # Запуск GUI
run_cli.bat   # Запуск CLI
```

### 🐧 Linux

```bash
chmod +x run_gui.sh && ./run_gui.sh
# или
chmod +x run_cli.sh && ./run_cli.sh
```

### 🔄 Запуск определённого конфига

```bash
python multi_rtsp_viewer.py configs/main_manual.json
```

---

## 📁 Структура проекта

```
rtspViewer/
├── configs/
│   └── main_manual.json           # Приоритетные камеры
├── multi_rtsp_viewer.py          # Основной видеопросмотрщик
├── gui_launcher.py               # Графический лаунчер
├── launcher.py                   # CLI-меню
├── refresh_config.py             # Обновление конфигов
├── run_gui.bat / .sh             # Запуск GUI
├── run_cli.bat / .sh             # Запуск CLI
├── requirements.txt              # Зависимости
└── README.md
```

---

## 🧪 Пример конфига

```json
{
  "Серверная": "rtsp://web:pass@192.168.13.252:554/Streaming/Channels/202",
  "Лестница (лев)": "rtsp://web:pass@192.168.13.252:554/Streaming/Channels/302"
}
```

---

## 💡 Планы

- 🌐 Web-интерфейс
- 📲 Telegram-уведомления при обрывах
- 📈 Поддержка более 32 камер (страницы)
- ⚙️ Интеграция с GStreamer и GPU-декодированием