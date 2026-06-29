@echo off
cd /d "%~dp0"
start "" powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"
echo Iniciando o servidor ColorIA em Node.js (JavaScript)...
npm start
