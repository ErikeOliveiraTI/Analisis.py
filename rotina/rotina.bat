@echo off
setlocal enabledelayedexpansion

REM Caminho para Git Bash
SET GIT="C:/Program Files/Git/bin/bash.exe"

REM Caminho do script bash
SET SCRIPT="/z/git/rotina/backup_rede.bash"

echo.
echo ==================================================
echo Iniciando rotina de backup: %DATE% %TIME%
echo ==================================================

REM Executar script bash
"%GIT%" -c "%SCRIPT%"

echo ==================================================
echo Rotina concluída: %DATE% %TIME%
echo ==================================================
pause
