@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set VENV_PY=.\.venv\Scripts\python.exe

echo Checking virtual environment...
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

if not exist %VENV_PY% (
    echo ❌ Python executable not found in .venv!
    pause
    exit /b
)

echo Installing dependencies...
%VENV_PY% -m pip install --upgrade pip >nul
%VENV_PY% -m pip install -r requirements.txt

echo Launching CLI menu...
%VENV_PY% launcher.py
pause
