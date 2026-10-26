@echo off
setlocal
cd /d "%~dp0"
title APAAR Platform Controller - Starting Services...

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1" %*
set SCRIPT_EXIT=%ERRORLEVEL%

if %SCRIPT_EXIT% neq 0 (
    echo.
    echo [ERROR] Startup finished with error code %SCRIPT_EXIT%.
    echo Check the messages above for troubleshooting steps.
)

echo.
pause
exit /b %SCRIPT_EXIT%
