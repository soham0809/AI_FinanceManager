@echo off
echo Starting AI Financial Co-Pilot Backend Server...

cd backend
call venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
