@echo off
REM ============================================================
REM MedIntel Forecasting Agent - One-Click Runner
REM Generates dataset, trains model, and launches API
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo     MedIntel Forecasting Agent - One-Click Runner
echo ============================================================
echo.

REM Set paths
set VENV_NAME=venv
set SCRIPT_DIR=%~dp0

REM Check if venv exists
if not exist "%SCRIPT_DIR%%VENV_NAME%" (
    echo ✗ Error: Virtual environment not found
    echo Please run install_dependencies.bat first
    echo.
    pause
    exit /b 1
)
REM Activate virtual environment
call venv\Scripts\activate
python agents/forecasting_agent/generate_dataset.py
python agents/forecasting_agent/train_model.py
uvicorn agents.forecasting_agent.service:app --reload --port 8001
@echo off
REM ============================================================
REM MedIntel Forecasting Agent - One-Click Runner
REM Generates dataset, trains model, and launches API
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo     MedIntel Forecasting Agent - One-Click Runner
echo ============================================================
echo.

REM Set paths
set VENV_NAME=venv
set SCRIPT_DIR=%~dp0

REM Check if venv exists
if not exist "%SCRIPT_DIR%%VENV_NAME%" (
    echo ✗ Error: Virtual environment not found
    echo Please run install_dependencies.bat first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call "%SCRIPT_DIR%%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo ✗ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Generate dataset
echo [2/4] Generating synthetic dataset...
echo Generating 730 days of hospital admission data...
cd /d "%SCRIPT_DIR%"
python generate_dataset.py
if errorlevel 1 (
    echo ✗ Failed to generate dataset
    pause
    exit /b 1
)
echo ✓ Dataset generation complete
echo.

REM Train model
echo [3/4] Training forecasting model...
echo This may take 1-2 minutes...
python train_model.py
if errorlevel 1 (
    echo ✗ Failed to train model
    pause
    exit /b 1
)
echo ✓ Model training complete
echo.

REM Start FastAPI service
echo [4/4] Starting FastAPI service...
echo.
echo ============================================================
echo ✓ ALL SYSTEMS READY!
echo ============================================================
echo.
echo Starting FastAPI server on http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn service:app --reload --port 8001 --host 0.0.0.0

REM If uvicorn stops, show message
echo.
echo ============================================================
echo FastAPI server stopped
echo ============================================================
echo.
pause
