@echo off
TITLE HMIE 2.3.0 Production Server Launcher
COLOR 0A

echo =======================================================================
echo  HISTORICAL MARKET INTELLIGENCE ENGINE (HMIE 2.3.0) PRODUCTION LAUNCHER
echo  Oracle 11g/23c XE • FastAPI Server • Governed AI Evidence Engine
echo =======================================================================
echo.

cd /d "c:\Users\vinay\.gemini\Fyers_Hist"

echo [1/3] Verifying Python Environment...
if not exist "c:\Users\vinay\.gemini\.venv\Scripts\python.exe" (
    echo [ERROR] Python environment not found! Exiting.
    pause
    exit /b 1
)

echo [2/3] Starting FastAPI Server on http://127.0.0.1:8000 ...
echo [INFO] Logging output to logs/server.log

if not exist "logs" mkdir "logs"

start /b c:\Users\vinay\.gemini\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 > logs\server.log 2>&1

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
