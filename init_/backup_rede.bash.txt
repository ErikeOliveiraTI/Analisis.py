@echo off
REM ===================================================
REM Executa o script rotina.sh no Git Bash (Windows)
REM Caminho do script: /z/git/rotina/rotina.sh
REM ===================================================

REM Caminho para o Git Bash (ajuste se estiver instalado em outro local)
SET GIT_BASH="C:\Program Files\Git\bin\bash.exe"

REM Caminho do script no formato Linux (Git Bash)
SET SCRIPT="/z/git/rotina/backup_rede.sh"

REM Executa o script
echo Iniciando rotina: %DATE% %TIME%
%GIT_BASH% -c "%SCRIPT%"

REM Mensagem final
echo Rotina finalizada: %DATE% %TIME%
pause