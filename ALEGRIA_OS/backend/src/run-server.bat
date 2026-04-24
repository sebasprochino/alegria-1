@echo off
TITLE ALEGRIA OS - Backend Server
CD /D "%~dp0"

REM Matar procesos en puerto 8000
FOR /F "tokens=5" %%a IN ('netstat -aon ^| findstr :8000') DO taskkill /F /PID %%a >nul 2>&1

REM Activar entorno y ejecutar
IF EXIST "venv\Scripts\activate.bat" CALL venv\Scripts\activate.bat
python src\server.py
PAUSE