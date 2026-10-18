@echo off
setlocal
chcp 866 >nul
cd /d "%~dp0"
set PORT=8000

echo ============================================================
echo  HTTPS-туннель для установки приложения на телефон
echo ============================================================
echo.
echo  СНАЧАЛА запустите start.cmd (сервер на порту %PORT%).
echo.
echo  Ниже появится адрес вида https://xxxx.tunnelmole.net
echo  Откройте его на телефоне с /app/ на конце, например:
echo      https://xxxx.tunnelmole.net/app/
echo  и установите приложение:
echo    Android (Chrome): меню "..." - "Установить приложение"
echo    iPhone (Safari):  Поделиться - "На экран Домой"
echo.
echo  Адрес меняется при каждом запуске этого файла.
echo  Окно нужно держать открытым; закрытие - отключает туннель.
echo ============================================================
echo.

where node >nul 2>nul
if not %errorlevel%==0 (
  echo Требуется Node.js: https://nodejs.org/
  pause
  goto :eof
)

npx --yes tunnelmole %PORT%
pause
