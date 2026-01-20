# encoding: utf-8
# Script para agendar backup_producao.py no Windows Task Scheduler
# Executa todos os dias as 17:00

# Verificar privilégios de administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Este script requer privilégios de administrador." -ForegroundColor Red
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Variáveis
$taskName = "Backup-Rede-Diario"
$scriptPath = "z:\git\init_\analise_py\backup_producao.py"
$pythonExe = "python"
$logPath = "z:\git\rotina\log\agendador.log"

# Criar pasta de log
$logDir = Split-Path $logPath
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Verificar Python
try {
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado no PATH" -ForegroundColor Red
    exit 1
}

# Verificar script
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERRO: Script não encontrado em: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "========================================"  -ForegroundColor Green
Write-Host "Agendando Backup Diario" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tarefa: $taskName" -ForegroundColor Cyan
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Horario: 17:00 todos os dias" -ForegroundColor Cyan
Write-Host ""

# Remover tarefa existente
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removendo tarefa existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Start-Sleep -Seconds 2
}

# Criar ação
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "`"$scriptPath`"" `
    -WorkingDirectory "z:\git\init_\analise_py"

# Criar trigger
$trigger = New-ScheduledTaskTrigger -Daily -At 17:00

# Criar settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Registrar tarefa
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Backup de rede automático - backup_producao.py" `
        -RunLevel Highest `
        -Force | Out-Null
    
    Write-Host "Sucesso! Tarefa agendada." -ForegroundColor Green
    Write-Host ""
    
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "Estado: $($task.State)" -ForegroundColor White
    
    $info = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "Proxima execucao: $($info.NextRunTime)" -ForegroundColor White
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] Tarefa agendada com sucesso com backup_producao.py"
    
} catch {
    Write-Host "ERRO ao agendar: $($_.Exception.Message)" -ForegroundColor Red
    $timestamp = Get-Date -Format "yyyy-mm-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] ERRO: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Read-Host "Pressione ENTER para fechar"
