@echo off
echo Setting up AI Financial Co-Pilot Backend...

cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo To start the server, run:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn main:app --reload
echo.
pause
