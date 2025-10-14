@echo off
echo ============================================================
echo AI FINANCIAL CO-PILOT - COMPLETE SYSTEM STARTUP
echo ============================================================
echo.

echo Step 1: Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not running!
    echo Please start Ollama first: ollama serve
    echo Then run this script again.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Ollama is running
)

echo.
echo Step 2: Getting your IP address...
python get_current_ip.py

echo.
echo Step 3: Starting Backend Server...
echo Backend will start in a new window...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && echo Backend starting... && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 4: Testing backend connection...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Backend not responding yet, give it a moment...
) else (
    echo [SUCCESS] Backend is responding
)

echo.
echo ============================================================
echo SYSTEM STATUS
echo ============================================================
echo [CHECK] Ollama: Running on http://localhost:11434
echo [CHECK] Backend: Starting on http://localhost:8000
echo [CHECK] API Docs: http://localhost:8000/docs
echo [CHECK] Mobile IP: http://192.168.0.105:8000
echo.
echo NEXT STEPS:
echo 1. Wait for backend to fully start (check the backend window)
echo 2. Open mobile app in Android Studio/VS Code
echo 3. Run the mobile app on your device/emulator
echo 4. Test SMS parsing functionality
echo.
echo To run batch processing: python run_batch_processing.py
echo To start mobile app: start_mobile_app.bat
echo.
pause
