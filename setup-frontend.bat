@echo off
echo ================================================
echo Seenya Wireless Scanner - Frontend Setup
echo Angular with Material Design
echo ================================================

echo.
echo [1/3] Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo [2/3] Installing dependencies...
cd seenya-frontend
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install npm dependencies
    pause
    exit /b 1
)

echo.
echo [3/3] Setup complete!
echo.
echo ================================================
echo NEXT STEPS:
echo 1. Run 'start-frontend.bat' to start the frontend
echo 2. Make sure backend is running first
echo 3. Open http://localhost:4200 in your browser
echo ================================================
pause
