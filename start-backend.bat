@echo off
echo ================================================
echo Starting Seenya Wireless Scanner Backend
echo ================================================

cd seenya-backend
call venv\Scripts\activate

echo.
echo Starting Flask server with SocketIO...
echo Backend will run on: http://localhost:5000
echo WebSocket endpoint: ws://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py
