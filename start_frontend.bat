@echo off
title Brainrot Video Factory — Frontend
color 0B
echo.
echo  =========================================
echo   Brainrot Video Factory - Frontend
echo  =========================================
echo.

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo  [FEHLER] Node.js nicht gefunden!
    echo  Installiere Node.js von https://nodejs.org (LTS-Version)
    pause
    exit /b 1
)

cd frontend

:: Install if node_modules missing
if not exist "node_modules" (
    echo  [INFO] Installiere npm-Pakete (einmalig, dauert ~1-2 Minuten)...
    npm install
)

echo.
echo  [INFO] Starte Frontend auf http://localhost:3000
echo.

npm run dev
pause
