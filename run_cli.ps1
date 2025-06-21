# run_cli.ps1
$venvPath = ".\.venv"
$venvPython = "$venvPath\Scripts\python.exe"

Write-Host "[*] Creating virtual environment using Python 3.13..."

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Error "[ERROR] Python launcher 'py' not found!"
    pause
    exit
}

$pythonCheck = py -3.13 --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ERROR] Python 3.13 is not installed!"
    pause
    exit
}

if (-not (Test-Path $venvPath)) {
    py -3.13 -m venv $venvPath
}

if (-not (Test-Path $venvPython)) {
    Write-Error "[ERROR] Python executable not found in .venv!"
    pause
    exit
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements_windows.txt
& $venvPython launcher.py --camera-monitor

pause
