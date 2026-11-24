@echo off
chcp 65001 >nul
title Установка Cyber Assistant (Кибер) // KINGSAID
color 0b

echo ================================================================
echo           CYBER ASSISTANT // МАСТЕР УСТАНОВКИ В 1 КЛИК
echo ================================================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\Cyber Assistant"
set "SRC_DIR=%~dp0"

echo [*] Создание рабочей директории...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [*] Копирование компонентов программы...
xcopy "%SRC_DIR%*.*" "%INSTALL_DIR%\" /E /I /Y /Q /EXCLUDE:%SRC_DIR%exclude.txt >nul 2>&1
copy "%SRC_DIR%*.*" "%INSTALL_DIR%\" /Y >nul 2>&1

echo [*] Настройка виртуального окружения и библиотек...
cd /d "%INSTALL_DIR%"
uv sync >nul 2>&1

echo [*] Создание ярлыка на Рабочем столе...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Cyber Assistant.lnk')); " ^
  "$s.TargetPath = 'powershell.exe'; " ^
  "$s.Arguments = '-NoProfile -WindowStyle Hidden -Command \"Set-Location \"\"' + '%INSTALL_DIR%' + '\"\" ; uv run python app.py\"'; " ^
  "$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s.Description = 'Cyber Assistant - Персональный голосовой помощник'; " ^
  "$s.Save()"

echo [*] Создание ярлыка в меню Пуск...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$startMenu = [Environment]::GetFolderPath('StartMenu'); " ^
  "$s = $ws.CreateShortcut([System.IO.Path]::Combine($startMenu, 'Cyber Assistant.lnk')); " ^
  "$s.TargetPath = 'powershell.exe'; " ^
  "$s.Arguments = '-NoProfile -WindowStyle Hidden -Command \"Set-Location \"\"' + '%INSTALL_DIR%' + '\"\" ; uv run python app.py\"'; " ^
  "$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s.Save()"

echo.
echo ================================================================
echo   [🎉 УСПЕХ!] Программа установлена!
echo   Ярлык «Cyber Assistant» создан на вашем Рабочем столе!
echo ================================================================
echo.
echo Запускаю Cyber Assistant...
start "" powershell.exe -NoProfile -WindowStyle Hidden -Command "Set-Location '%INSTALL_DIR%'; uv run python app.py"
exit
