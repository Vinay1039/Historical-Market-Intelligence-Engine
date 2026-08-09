@echo off
title HMIE v1.0.0 — Historical Market Intelligence Engine

cd /d "%~dp0"

echo ===============================================================================
echo  HISTORICAL MARKET INTELLIGENCE ENGINE (HMIE v1.0.0)
echo ===============================================================================
echo [1/2] Checking Python environment...

if exist "..\.venv\Scripts\python.exe" (
    set PYTHON_EXE=..\.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

echo [2/2] Launching FastAPI REST Backend & Research Terminal Server...
echo Terminal URL: http://127.0.0.1:8000/library.html
echo.

%PYTHON_EXE% -m uvicorn api.main:app --host 127.0.0.1 --port 8000

echo [3/3] Waiting for Server Startup...
timeout /t 3 /nobreak > nul

echo [SUCCESS] Opening HMIE Governed Evidence Dashboard in default browser...
start http://127.0.0.1:8000/

echo.
echo =======================================================================
echo  HMIE 2.3.0 Server is LIVE at http://127.0.0.1:8000/
echo  Press any key to stop the server when finished.
echo =======================================================================
echo.
pause
