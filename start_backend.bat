@echo off
echo Starting AI Financial Co-Pilot Backend Server...

cd backend
call venv\Scripts\activate
echo Backend server starting on http://0.0.0.0:8000
echo Access from mobile app using your computer's IP address
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
