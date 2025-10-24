@echo off
echo ========================================
echo   AI Finance Manager - Simple Start
echo ========================================
echo.

echo Starting services in order...
echo.

echo [1/4] Starting Ollama AI Server...
start "Ollama" cmd /k "ollama serve"
timeout /t 5 /nobreak >nul

echo [2/4] Starting Backend Server...
start "Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 5 /nobreak >nul

echo [3/4] Starting Cloudflare Tunnel...
start "Cloudflare" cmd /k "C:\cloudflared\cloudflared.exe tunnel run ai-finance"
timeout /t 3 /nobreak >nul

echo [4/4] Ready for Flutter App!
echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Services running:
echo   - Ollama AI: http://localhost:11434
echo   - Backend API: http://localhost:8001
echo   - Global URL: https://ai-finance.sohamm.xyz
echo.
echo To start Flutter app, run:
echo   cd mobile_app
echo   flutter run
echo.
echo Press any key to exit...
pause >nul
