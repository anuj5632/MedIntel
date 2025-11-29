@echo off
REM ============================================================
REM MedIntel Forecasting Agent - Dependency Installer
REM Installs all required packages in a virtual environment
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo     MedIntel Forecasting Agent - Setup Script
echo ============================================================
echo.

REM Set paths
set VENV_NAME=venv
set SCRIPT_DIR=%~dp0
set REQUIREMENTS_FILE=%SCRIPT_DIR%requirements.txt

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
python --version
echo ✓ Python found
echo.
echo [2/5] Creating virtual environment...
if exist "%SCRIPT_DIR%%VENV_NAME%" (
    echo ✓ Virtual environment already exists
) else (
    python -m venv "%SCRIPT_DIR%%VENV_NAME%"
    if errorlevel 1 (
        echo ✗ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
)
echo.
echo [3/5] Activating virtual environment...
call "%SCRIPT_DIR%%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo ✗ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo ✗ Failed to upgrade pip
    pause
    exit /b 1
)
echo ✓ pip upgraded
echo.
echo [5/5] Installing dependencies from requirements.txt...
if not exist "%REQUIREMENTS_FILE%" (
    echo ✗ Error: requirements.txt not found at %REQUIREMENTS_FILE%
    pause
    exit /b 1
)

pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo ✗ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ All dependencies installed successfully
echo.
echo ============================================================
echo ✓ SETUP COMPLETE!
echo ============================================================
echo.
echo Virtual environment created at: %SCRIPT_DIR%%VENV_NAME%
echo.
echo Next steps:
echo   1. Run: run_all.bat
echo   2. This will generate dataset, train model, and start API
echo.
echo To manually activate the environment later, run:
echo   %SCRIPT_DIR%%VENV_NAME%\Scripts\activate.bat
echo.
pause
@echo off
REM ============================================================
REM MedIntel Forecasting Agent - Dependency Installer
REM Installs all required packages in a virtual environment
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo     MedIntel Forecasting Agent - Setup Script
echo ============================================================
echo.

REM Set paths
set VENV_NAME=venv
set SCRIPT_DIR=%~dp0
set REQUIREMENTS_FILE=%SCRIPT_DIR%requirements.txt

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
python --version
echo ✓ Python found
echo.

echo [2/5] Creating virtual environment...
if exist "%SCRIPT_DIR%%VENV_NAME%" (
    echo ✓ Virtual environment already exists
) else (
    python -m venv "%SCRIPT_DIR%%VENV_NAME%"
    if errorlevel 1 (
        echo ✗ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
)
echo.

echo [3/5] Activating virtual environment...
call "%SCRIPT_DIR%%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo ✗ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

echo [4/5] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo ✗ Failed to upgrade pip
    pause
    exit /b 1
)
echo ✓ pip upgraded
echo.

echo [5/5] Installing dependencies from requirements.txt...
if not exist "%REQUIREMENTS_FILE%" (
    echo ✗ Error: requirements.txt not found at %REQUIREMENTS_FILE%
    pause
    exit /b 1
)

pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo ✗ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ All dependencies installed successfully
echo.

echo ============================================================
echo ✓ SETUP COMPLETE!
echo ============================================================
echo.
echo Virtual environment created at: %SCRIPT_DIR%%VENV_NAME%
echo.
echo Next steps:
echo   1. Run: run_all.bat
echo   2. This will generate dataset, train model, and start API
echo.
echo To manually activate the environment later, run:
echo   %SCRIPT_DIR%%VENV_NAME%\Scripts\activate.bat
echo.
pause
