@echo off
title Launching WinOptima...
cd /d "%~dp0"

:: Check for Administrative Permissions
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :RunApp
) else (
    goto :Elevate
)

:Elevate
echo Requesting Administrator privileges...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs -WorkingDirectory '%~dp0'"
exit /b

:RunApp
start "" pythonw main.py
if %errorlevel% neq 0 (
    python main.py
)
exit /b
