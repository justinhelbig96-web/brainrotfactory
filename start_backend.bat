@echo off
title Brainrot Video Factory — Backend
color 0A
echo.
echo  =========================================
echo   Brainrot Video Factory - Backend
echo  =========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [FEHLER] Python nicht gefunden!
    echo  Installiere Python 3.10+ von https://python.org
    pause
    exit /b 1
)

:: Check if venv exists, create if not
if not exist ".venv" (
    echo  [INFO] Erstelle virtuelles Environment...
    python -m venv .venv
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install dependencies
echo  [INFO] Installiere/prüfe Abhängigkeiten...
pip install -r backend\requirements.txt -q

:: Check FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [WARNUNG] FFmpeg nicht gefunden!
    echo  Download: https://www.gyan.dev/ffmpeg/builds/
    echo  Entpacken und ffmpeg.exe zum PATH hinzufügen.
    echo.
    pause
)

:: Copy .env if needed
if not exist ".env" (
    if exist ".env.example" (
        echo  [INFO] .env.example nach .env kopiert. Bitte API Keys eintragen!
        copy .env.example .env
    )
)

echo.
echo  [INFO] Starte Backend auf http://localhost:8000
echo  [INFO] API Docs: http://localhost:8000/docs
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
