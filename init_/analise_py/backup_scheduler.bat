@echo off
REM Script de Agendamento de Backup - Versao Batch
REM Executa o backup automaticamente as 17:00 todos os dias
REM Nao requer privilégios administrativos

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Agendador de Backup Iniciado
echo ========================================
echo Execucao diaria: 17:00 (5 PM)
echo.

set SCRIPT_PATH=z:\git\init_\analise_py\backup_rede.bash
set LOG_PATH=z:\git\rotina\log\scheduler_batch.log

REM Criar pasta de log
if not exist "z:\git\rotina\log\" mkdir z:\git\rotina\log\

REM Loop infinito para monitorar a hora
:LOOP

REM Obter hora atual
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (
    set HORA=%%a
    set MINUTO=%%b
)

REM Verificar se é 17:00
if %HORA%==17 (
    if %MINUTO%==00 (
        REM Registrar no log
        for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATA=%%c-%%a-%%b)
        for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set HORA_ATUAL=%%a:%%b)
        
        echo [!DATA! !HORA_ATUAL!] Iniciando backup... >> "%LOG_PATH%"
        echo Executando backup as !HORA_ATUAL!...
        
        REM Executar backup
        bash "%SCRIPT_PATH%"
        
        echo [!DATA! !HORA_ATUAL!] Backup concluido >> "%LOG_PATH%"
        echo Backup concluido!
        echo.
        
        REM Aguardar 1 minuto para nao executar novamente
        timeout /t 60 /nobreak
    )
)

REM Verificar hora a cada 30 segundos
timeout /t 30 /nobreak

goto LOOP
