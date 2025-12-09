@echo off
REM Source Code Risk Radar - Quick Setup Script for Windows

echo.
echo ==========================================
echo Source Code Risk Radar - Setup
echo ==========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python not found. Please install Python 3.9 or higher
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Activated
echo.

REM Install requirements
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Run test analysis
echo Running test analysis...
python main.py --use-dummy-data --output-format html
echo Test analysis complete
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Open: reports\risk_dashboard_*.html
echo 2. Review the interactive dashboard
echo 3. Analyze your code: python main.py --repo-path C:\path\to\repo
echo.
echo For more help, read QUICKSTART.md
echo.
pause
