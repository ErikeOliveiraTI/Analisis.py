@echo off
REM Script para agendar backup_rede.bash no Windows Task Scheduler
REM Executa todos os dias as 17:00

setlocal enabledelayedexpansion

REM Verificar se roda como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Este script requer privilégios de administrador.
    echo Clique com botão direito e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo.
echo ========================================
echo Agendador de Backup Diario
echo ========================================
echo.

set TASK_NAME=Backup-Rede-Diario
set SCRIPT_PATH=z:\git\init_\analise_py\backup_rede.bash
set GIT_BASH=C:\Program Files\Git\bin\bash.exe
set LOG_PATH=z:\git\rotina\log\agendador.log

REM Verificar Git Bash
if not exist "%GIT_BASH%" (
    echo ERRO: Git Bash nao encontrado em: %GIT_BASH%
    pause
    exit /b 1
)

REM Verificar script
if not exist "%SCRIPT_PATH%" (
    echo ERRO: Script nao encontrado em: %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Criar pasta de log
if not exist "z:\git\rotina\log\" mkdir z:\git\rotina\log\

REM Remover tarefa existente
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

echo Criando tarefa agendada...
echo.

REM Agendar tarefa
schtasks /create /tn "%TASK_NAME%" /tr "\"%GIT_BASH%\" -c \"bash '%SCRIPT_PATH%'\"" /sc daily /st 17:00 /rl highest /f

if %errorlevel% equ 0 (
    echo SUCESSO!
    echo.
    echo Tarefa: %TASK_NAME%
    echo Horario: 17:00 (5 PM)
    echo Status: Ativada
    echo.
    
    REM Log da criação
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
    echo [!mydate! !mytime!] Tarefa agendada com sucesso >> "%LOG_PATH%"
    
    echo Log: %LOG_PATH%
    echo.
    echo ========================================
) else (
    echo ERRO ao agendar tarefa
    echo Certifique-se que roda como administrador
    echo.
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
    echo [!mydate! !mytime!] ERRO ao agendar >> "%LOG_PATH%"
)

echo.
pause
