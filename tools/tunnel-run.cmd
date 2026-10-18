@echo off
chcp 866 >nul
rem Detached launcher for the tunnelmole HTTPS tunnel (used by the session / advanced users).
cd /d "%~dp0.."
"C:\Program Files\nodejs\npx.cmd" --yes tunnelmole 8000 > "%~dp0tunnel.log" 2>&1
