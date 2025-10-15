@echo off
setlocal enabledelayedexpansion
REM ===== Private Public Link via ngrok (requires ngrok installed) =====
REM Expect SULLY_APP_PASSWORD to be set (or default to 'changeme')
set SULLY_APP_PASSWORD=%SULLY_APP_PASSWORD%
if "%SULLY_APP_PASSWORD%"=="" set SULLY_APP_PASSWORD=changeme

REM Start the app in a new window
start "SullyBot" cmd /c "..\venv\Scripts\activate && streamlit run app\streamlit_app.py --server.address 0.0.0.0 --server.port 8501"

REM Protect with HTTP basic auth (user: sully / pass: your app password)
ngrok http 8501 --basic-auth="sully:%SULLY_APP_PASSWORD%"
