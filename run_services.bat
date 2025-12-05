@echo off
echo Starting Services...

REM Start User Service
start "User Service" cmd /k "call .venv\Scripts\activate && cd services\user-services && uvicorn main:app --port 8000 --reload"

REM Start Booking Service
start "Booking Service" cmd /k "call .venv\Scripts\activate && cd services\booking-service && uvicorn main:app --port 8001 --reload"

echo Services started in separate windows.
