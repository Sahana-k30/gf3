@echo off
REM Quick start script for GF(3) LDPC Error Correction System on Windows

echo.
echo ========================================
echo GF(3) LDPC Error Correction System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q

REM Run the backend
echo.
echo ========================================
echo Starting FastAPI Backend Server
echo ========================================
echo.
echo Server will be running at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
