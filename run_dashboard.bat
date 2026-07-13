@echo off
REM ============================================================
REM Fraud Detection Dashboard - Quick Launcher
REM ============================================================
REM This batch file runs the Streamlit dashboard directly
REM Just double-click this file to start the app!
REM ============================================================

echo.
echo ========================================
echo 🛡️  Financial Fraud Detection Dashboard
echo ========================================
echo.
echo Starting dashboard (this may take 10-15 seconds)...
echo.

REM Navigate to the script directory
cd /d "%~dp0"

REM Run streamlit using python -m (avoids PATH issues)
python -m streamlit run app.py

REM If streamlit fails, show error message
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to start dashboard
    echo.
    echo Possible fixes:
    echo 1. Make sure Python/Anaconda is installed
    echo 2. Run: python -m pip install -r requirements.txt
    echo 3. Check that fraud_detection.db exists in this folder
    echo.
    pause
    exit /b 1
)
