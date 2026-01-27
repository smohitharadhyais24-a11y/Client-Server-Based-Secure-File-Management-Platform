@echo off
REM DEMO SCRIPT FOR WINDOWS (WSL Required)
REM Run this in WSL terminal or Git Bash

echo ==========================================
echo  FULL DEMO SCRIPT - Windows Compatible
echo ==========================================
echo.

echo Make sure you have WSL installed!
echo Server should be running in another terminal.
echo.
pause

echo.
echo ==========================================
echo  PART 1: Basic Upload/Download
echo ==========================================
timeout /t 1 >nul

echo.
echo [UPLOAD] Uploading test1.txt...
python client/client.py UPLOAD test_files/test1.txt
timeout /t 1 >nul

echo.
echo [LIST] Listing files...
python client/client.py LIST
timeout /t 1 >nul

echo.
echo [DOWNLOAD] Downloading test1.txt...
python client/client.py DOWNLOAD test1.txt downloaded_test1.txt
timeout /t 1 >nul

echo.
echo ==========================================
echo  PART 2: Multiple Files
echo ==========================================
timeout /t 1 >nul

echo.
echo [UPLOAD] Uploading test2.txt...
python client/client.py UPLOAD test_files/test2.txt
timeout /t 1 >nul

echo.
echo [LIST] Listing all files...
python client/client.py LIST
timeout /t 1 >nul

echo.
echo ==========================================
echo  PART 3: Logs and Locks
echo ==========================================
timeout /t 1 >nul

echo.
echo [LOGS] Viewing audit logs...
python client/client.py LOGS
timeout /t 1 >nul

echo.
echo [LOCKS] Viewing current locks...
python client/client.py LOCKS
timeout /t 1 >nul

echo.
echo ==========================================
echo  DEMO COMPLETE!
echo ==========================================
echo.
echo Key OS Concepts Demonstrated:
echo   - UNIX File I/O (open, read, write)
echo   - TCP Socket IPC
echo   - File Locking (fcntl)
echo   - Deadlock Prevention (bounded transfers)
echo   - Thread Management (pthread)
echo.
pause
