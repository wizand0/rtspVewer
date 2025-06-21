@echo off
chcp 65001 >nul
setlocal

set VENV_DIR=.venv
set VENV_PY="%VENV_DIR%\Scripts\python.exe"

echo [*] Creating virtual environment using Python 3.13...

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python launcher 'py' not found!
    pause
    exit /b
)

py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.13 is not installed!
    pause
    exit /b
)

if not exist %VENV_DIR% (
    py -3.13 -m venv %VENV_DIR%
)

if not exist %VENV_PY% (
    echo [ERROR] Python executable not found in .venv!
    pause
    exit /b
)

echo [*] Installing requirements...
%VENV_PY% -m pip install --upgrade pip
%VENV_PY% -m pip install -r requirements_windows.txt

echo [*] Launching CLI...
%VENV_PY% launcher.py --camera-monitor

pause
