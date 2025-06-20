@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set VENV_DIR=.venv
set VENV_PY=%VENV_DIR%\Scripts\python.exe

echo Checking virtual environment...
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

if not exist "%VENV_PY%" (
    echo [ERROR] Python executable not found in .venv!
    pause
    exit /b
)

echo Installing dependencies...
"%VENV_PY%" -m pip install --upgrade pip >nul
"%VENV_PY%" -m pip install -r requirements.txt

echo Launching CLI menu with monitoring flag...
"%VENV_PY%" launcher.py --camera-monitor

pause
