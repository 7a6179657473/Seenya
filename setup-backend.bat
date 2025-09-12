@echo off
echo ================================================
echo Seenya Wireless Scanner - Backend Setup
echo Phase 1: MAC Address Detection Module
echo ================================================

echo.
echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo [2/4] Creating virtual environment...
cd seenya-backend
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Make sure you have Administrator privileges for packet capture libraries
    pause
    exit /b 1
)

echo.
echo [4/4] Setup complete!
echo.
echo ================================================
echo NEXT STEPS:
echo 1. Run 'setup-frontend.bat' to set up the frontend
echo 2. Run 'start-backend.bat' to start the backend server
echo 3. For packet capture, run as Administrator
echo ================================================
pause
