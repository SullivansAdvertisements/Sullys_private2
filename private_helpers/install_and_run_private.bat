@echo off
setlocal enabledelayedexpansion
REM ===== Private Local Run (LAN only) =====
REM Set your password here (or set SULLY_APP_PASSWORD in your system env)
set SULLY_APP_PASSWORD=%SULLY_APP_PASSWORD%
if "%SULLY_APP_PASSWORD%"=="" (
  echo [*] No SULLY_APP_PASSWORD set. Using default 'changeme' for this session.
  set SULLY_APP_PASSWORD=changeme
)

cd /d "%~dp0.."
if not exist "venv" (
  python -m venv venv || (echo [!] Failed to create venv & pause & exit /b 1)
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

set PORT=8501
echo.
echo [*] Launching on http://0.0.0.0:%PORT% (password protected)
echo     Password: %SULLY_APP_PASSWORD%
echo.
set SULLY_APP_PASSWORD=%SULLY_APP_PASSWORD%
streamlit run app/streamlit_app.py --server.address 0.0.0.0 --server.port %PORT%
