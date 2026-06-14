@echo off
cd /d "%~dp0"
python -u main.py 2>&1
if errorlevel 1 (
    echo.
    echo Error occurred. Check output above.
    pause
)