# encoding: utf-8
# Script para agendar backup_rede.bash no Windows Task Scheduler
# Executa todos os dias as 17:00 (5 PM)

# Solicitar privilégios de administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Este script requer privilégios de administrador. Reiniciando..." -ForegroundColor Red
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Variáveis
$taskName = "Backup-Rede-Diario"
$scriptPath = "z:\git\init_\analise_py\backup_rede.bash"
$gitBashPath = "C:\Program Files\Git\bin\bash.exe"
$logPath = "z:\git\rotina\log\agendador.log"

# Criar pasta de log se não existir
$logDir = Split-Path $logPath
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Verificar se Git Bash está instalado
if (-not (Test-Path $gitBashPath)) {
    Write-Host "ERRO: Git Bash nao encontrado em: $gitBashPath" -ForegroundColor Red
    Write-Host "Por favor, instale Git Bash primeiro." -ForegroundColor Red
    exit 1
}

# Verificar se o script existe
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERRO: Script nao encontrado em: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "Agendando Backup Diario" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tarefa: $taskName" -ForegroundColor Cyan
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Horario: 17:00 (5 PM) todos os dias" -ForegroundColor Cyan
Write-Host "Log: $logPath" -ForegroundColor Cyan
Write-Host ""

# Remover tarefa existente se houver
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removendo tarefa existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Start-Sleep -Seconds 2
}

# Criar argumento para o bash
$taskArgument = "-c `"bash '$scriptPath'`""

# Criar ação agendada
$action = New-ScheduledTaskAction `
    -Execute $gitBashPath `
    -Argument $taskArgument `
    -WorkingDirectory "z:\git\init_\analise_py"

# Criar gatilho (trigger) para 17:00 todos os dias
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At 17:00

# Criar configurações da tarefa
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Registrar a tarefa
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Backup automático de rede para Z:\git\rotina" `
        -RunLevel Highest `
        -Force | Out-Null
    
    Write-Host "✓ Tarefa agendada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalhes da Tarefa:" -ForegroundColor Green
    
    $scheduledTask = Get-ScheduledTask -TaskName $taskName
    Write-Host "- Nome: $($scheduledTask.TaskName)" -ForegroundColor White
    Write-Host "- Estado: $($scheduledTask.State)" -ForegroundColor White
    Write-Host "- Próxima execução: $(($scheduledTask | Get-ScheduledTaskInfo).NextRunTime)" -ForegroundColor White
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Configuração Concluída!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # Log da criação
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] Tarefa agendada com sucesso: $taskName"
    
} catch {
    Write-Host "✗ ERRO ao agendar tarefa:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    # Log do erro
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] ERRO ao agendar: $($_.Exception.Message)"
    
    exit 1
}

# Perguntar se deseja testar agora
Write-Host ""
Write-Host "Tarefa agendada! Pressione ENTER para fechar." -ForegroundColor Cyan
Read-Host ""
