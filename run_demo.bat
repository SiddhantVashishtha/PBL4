@echo off
cd /d "%~dp0"
echo Starting Hand Tracking Demo...

REM Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo Using Virtual Environment Python...
    "venv\Scripts\python.exe" main.py
) else (
    echo Using System Python...
    python main.py
)

if %errorlevel% neq 0 (
    echo.
    echo Error occurred with exit code %errorlevel%.
)

echo.
echo Press any key to close this window...
pause >nul
