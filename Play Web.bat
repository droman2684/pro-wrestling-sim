@echo off
echo ==========================================
echo   Pro Wrestling Sim - Web UI
echo   Starting server...
echo   Open http://127.0.0.1:5000 in your browser
echo ==========================================
cd /d "%~dp0src\ui\web"
python app.py
pause
