#!/bin/bash
set -e

echo "Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "Launching GUI..."
python3 gui_launcher.py
