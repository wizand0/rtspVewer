#!/bin/bash
set -e

echo "📦 Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Активация окружения
source .venv/bin/activate

# Подавление Qt ошибок под Wayland
export QT_QPA_PLATFORM=xcb

echo "📥 Installing dependencies..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "🚀 Launching CLI menu..."
python3 launcher.py
