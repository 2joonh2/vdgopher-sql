@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Start backend server in a new window
echo Starting backend server...
start "VDGopher Backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && python main.py"

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start frontend dev server in a new window
echo Starting frontend dev server...
start "VDGopher Frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm install && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
