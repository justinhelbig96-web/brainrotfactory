@echo off
title Brainrot Video Factory
color 0D
echo.
echo  =====================================================
echo        BRAINROT VIDEO FACTORY  v1.0
echo        Startet Backend + Frontend in separaten Fenstern
echo  =====================================================
echo.

echo  [1/2] Starte Backend (Python FastAPI)...
start "Brainrot Backend" cmd /k "call start_backend.bat"

echo  [2/2] Starte Frontend (Next.js) in 3 Sekunden...
timeout /t 3 /nobreak >nul
start "Brainrot Frontend" cmd /k "call start_frontend.bat"

echo.
echo  ✓ Backend : http://localhost:8000
echo  ✓ Frontend: http://localhost:3000
echo  ✓ API Docs: http://localhost:8000/docs
echo.
echo  Browser wird in 5 Sekunden geöffnet...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo  Dieses Fenster kann geschlossen werden.
echo  Die eigentlichen Server laufen in den anderen Fenstern.
pause
