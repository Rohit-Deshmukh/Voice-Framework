@echo off
REM Voice Framework - One-Line Setup Script for Windows
REM Usage: setup.bat

echo ============================================
echo   Voice Framework - Quick Setup
echo ============================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q
echo [OK] pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
echo [OK] Dependencies installed
echo.

REM Optional: Install feature file support
set /p INSTALL_FEATURES="Install feature file support (behave)? [y/N] "
if /i "%INSTALL_FEATURES%"=="y" (
    echo Installing feature file support...
    pip install -r requirements-features.txt -q
    echo [OK] Feature file support installed
    echo.
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] .env file created (review and update as needed)
    ) else (
        echo [!] .env.example not found, skipping
    )
    echo.
)

echo.
echo ============================================
echo   Setup Complete! 
echo ============================================
echo.
echo Next steps:
echo.
echo   1. Start the API server:
echo      .venv\Scripts\activate
echo      uvicorn api.main:app --reload
echo.
echo   2. In another terminal, run a test:
echo      curl -X POST http://localhost:8000/test/run ^
echo        -H "Content-Type: application/json" ^
echo        -d "{\"test_id\":\"billing_inquiry_v1\",\"provider\":\"twilio\",\"mode\":\"simulation\"}"
echo.
echo   3. Or use the Streamlit dashboard:
echo      streamlit run streamlit_app.py
echo.
echo For more information, see README.md
echo.
pause
