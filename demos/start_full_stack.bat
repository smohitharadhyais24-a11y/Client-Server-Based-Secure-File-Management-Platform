@echo off
REM OS File Server - Full Stack Startup Script (Windows)
REM Starts C server, Python API, and opens web dashboard

echo ==================================================
echo    OS FILE SERVER - FULL STACK STARTUP
echo ==================================================
echo.

REM Check if in WSL or need to use wsl command
where wsl >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starting services via WSL...
    
    REM Start C server in WSL
    echo [1/3] Starting C OS Core Server ^(port 8888^)...
    start "C Server" wsl bash -c "cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS' && ./build/file_server"
    timeout /t 2 /nobreak >nul
    
    REM Start Python API in WSL
    echo [2/3] Starting Python API Layer ^(port 5000^)...
    start "API Layer" wsl bash -c "cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS/api_layer' && python3 app.py"
    timeout /t 2 /nobreak >nul
    
    REM Open web dashboard
    echo [3/3] Opening Web Dashboard...
    start "" "%~dp0web_dashboard\index.html"
    
    echo.
    echo ==================================================
    echo    SYSTEM RUNNING
    echo ==================================================
    echo C Server: Running in WSL ^(port 8888^)
    echo API Layer: Running in WSL ^(port 5000^)
    echo Web Dashboard: Opened in browser
    echo.
    echo Check the opened terminal windows for logs
    echo Close terminal windows to stop services
    echo ==================================================
) else (
    echo [ERROR] WSL not found. Please install WSL or run in Linux.
    pause
    exit /b 1
)
