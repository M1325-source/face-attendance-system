@echo off
echo ======================================
echo Face Attendance System Setup
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
echo Virtual environment created!
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist "data\faces" mkdir data\faces
if not exist "data\attendance" mkdir data\attendance
if not exist "models" mkdir models
echo Directories created!
echo.

echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run the app: python app.py
echo 3. Open browser: http://localhost:5000
echo.
echo To deactivate virtual environment: deactivate
echo.
pause
