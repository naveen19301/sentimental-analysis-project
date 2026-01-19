@echo off
REM Customer Sentiment Dashboard - Quick Start Script (Windows)
REM This script will install dependencies and run the dashboard

echo ============================================================
echo  Customer Sentiment Analytics Dashboard - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [X] Failed to install packages. Please check your internet connection.
    pause
    exit /b 1
)

echo [OK] All packages installed successfully
echo.

REM Check if data file exists
if not exist "training_data_cs.xlsx" (
    echo [X] Data file 'training_data_cs.xlsx' not found!
    echo Please place the data file in the same directory as this script.
    pause
    exit /b 1
)

echo [OK] Data file found
echo.

REM Run the dashboard
echo ============================================================
echo  Starting the dashboard...
echo  Default password: sentiment2024
echo  Dashboard will open in your browser automatically
echo.
echo  Press Ctrl+C to stop the dashboard
echo ============================================================
echo.

streamlit run customer_sentiment_dashboard.py

pause
