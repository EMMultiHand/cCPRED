@echo off
rem Detached launcher for the local static server (http + https).
chcp 866 >nul
cd /d "%~dp0.."
"C:\Program Files\nodejs\node.exe" tools\serve.js "%CD%" 8000 > "%~dp0server.log" 2>&1
