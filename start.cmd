@echo off
chcp 866 >nul
setlocal
cd /d "%~dp0"
set PORT=8000
set TLSPORT=8443

echo ============================================================
echo  Cyberpunk RED - локальная копия (тёмно-коричневая тема)
echo  Папка: %CD%
echo.
echo  Компьютер:             http://localhost:%PORT%/
echo  Телефон (та же сеть):   адреса ниже
echo.
echo  Как установить приложение на телефон (без интернета):
echo    1) на телефоне откройте  http://IP-компьютера:%PORT%/certs/rootCA.crt
echo       и установите скачанный сертификат (смотрите README, раздел
echo       "Установка на телефон")
echo    2) откройте  https://IP-компьютера:%TLSPORT%/app/
echo    3) меню браузера - "Установить приложение" / "На экран Домой"
echo    По http-адресу можно смотреть лист персонажа без установки.
echo.
echo ============================================================
echo.
echo  Адреса для телефона (той же сети):
powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.InterfaceAlias -notmatch 'tun|vpn|virtual|vethernet|wintun|tailscale|zerotier' } | ForEach-Object { '    http://' + $_.IPAddress + ':%PORT%/app/   (view)'; '    https://' + $_.IPAddress + ':%TLSPORT%/app/  (install)' }" 2>nul
echo.
echo  Закрытие этого окна остановит сервер.
echo ============================================================
echo.

where node >nul 2>nul
if %errorlevel%==0 (
  start "" "http://localhost:%PORT%/"
  node tools\serve.js "%CD%" %PORT%
  goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
  echo Node.js не найден - будет только http (установка на телефон недоступна).
  start "" "http://localhost:%PORT%/"
  python -m http.server %PORT% --bind 0.0.0.0
  goto :eof
)

where py >nul 2>nul
if %errorlevel%==0 (
  echo Node.js не найден - будет только http (установка на телефон недоступна).
  start "" "http://localhost:%PORT%/"
  py -m http.server %PORT% --bind 0.0.0.0
  goto :eof
)

echo Для запуска нужен Node.js (https://nodejs.org/) или Python (https://www.python.org/).
pause
