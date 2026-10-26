@echo off
setlocal
cd /d "%~dp0"
title APAAR Platform Controller - Restarting Services...

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\restart.ps1" %*
set SCRIPT_EXIT=%ERRORLEVEL%

if %SCRIPT_EXIT% neq 0 (
    echo.
    echo [ERROR] Restart finished with error code %SCRIPT_EXIT%.
    echo Check the messages above for details.
)

echo.
pause
exit /b %SCRIPT_EXIT%
