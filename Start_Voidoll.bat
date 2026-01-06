
@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==========================================
echo   🤖 VOIDOLL SYSTEM LAUNCHING...
echo ==========================================

python desktop/voidoll_main.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Application exited with error.
    pause
)
