# 📹 rtspViewer

**rtspViewer** — кроссплатформенное Python-приложение для одновременного просмотра RTSP-потоков с камер наблюдения.

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

## 🚀 Быстрый старт

### ⬇️ Установить зависимости и запустить (Windows)

```bat
run_gui.bat   - для запуска GUI
run_cli.bat   - для запуска текстового меню
```
### 🐧 В Linux
```commandline
chmod +x run_gui.sh
./run_gui.sh
```
или
```commandline
chmod +x run_cli.sh
./run_cli.sh
```

### Запуск определенного конфига:
```commandline
python multi_rtsp_viewer.py configs/main_manual.json
```

### **refresh_config.py** Скрипт для: проверки всех потоков из .json; исключения неработающих камер;
```commandline
python multi_rtsp_viewer.py configs/main_manual.json
```

## 📁 Структура проекта

```commandline
SafeMonitor/
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

## 🧪 Пример main_manual.json
```commandline
{
  "Серверная": "rtsp://web:passwrd@192.168.13.252:554/Streaming/Channels/202",
  "Лестница (лев)": "rtsp://web:passwrd@192.168.13.252:554/Streaming/Channels/302"
}

```

## 💡 Планы на будущее
```commandline
- GUI + CLI интерфейсы
- Автопереподключение к потокам
- Обновление конфигов
- Telegram-уведомления при обрыве
- Web-интерфейс
- Поддержка страниц (для 32+ камер)
```