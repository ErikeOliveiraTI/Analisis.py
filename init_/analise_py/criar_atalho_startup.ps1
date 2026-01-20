# Script para criar atalho automático na pasta Startup
# Não requer privilégios administrativos

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Configurador de Startup Automático" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Encontrar pasta Startup
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

if (-not (Test-Path $startupFolder)) {
    Write-Host "ERRO: Pasta Startup não encontrada!" -ForegroundColor Red
    Write-Host "Caminho esperado: $startupFolder" -ForegroundColor Red
    exit 1
}

Write-Host "Pasta Startup encontrada:" -ForegroundColor Cyan
Write-Host "$startupFolder" -ForegroundColor White
Write-Host ""

# Caminho do script batch que inicia o agendador
$scriptBatch = "z:\git\init_\analise_py\iniciar_agendador.bat"

if (-not (Test-Path $scriptBatch)) {
    Write-Host "ERRO: Script batch não encontrado em:" -ForegroundColor Red
    Write-Host "$scriptBatch" -ForegroundColor Red
    exit 1
}

Write-Host "Script batch encontrado:" -ForegroundColor Cyan
Write-Host "$scriptBatch" -ForegroundColor White
Write-Host ""

# Criar atalho
$atalhoPath = "$startupFolder\Agendador-Backup.lnk"

try {
    # Usar COM para criar atalho (compatível com PowerShell)
    $WshShell = New-Object -ComObject WScript.Shell
    $atalho = $WshShell.CreateShortcut($atalhoPath)
    $atalho.TargetPath = $scriptBatch
    $atalho.WorkingDirectory = "z:\git\init_\analise_py"
    $atalho.Description = "Agendador de Backup Automático"
    $atalho.WindowStyle = 7  # Minimized
    $atalho.Save()
    
    Write-Host "SUCESSO! Atalho criado:" -ForegroundColor Green
    Write-Host "$atalhoPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Detalhes do atalho:" -ForegroundColor Cyan
    Write-Host "- Alvo: $scriptBatch" -ForegroundColor White
    Write-Host "- Diretório: z:\git\init_\analise_py" -ForegroundColor White
    Write-Host "- Descrição: Agendador de Backup Automático" -ForegroundColor White
    Write-Host "- Janela: Minimizada" -ForegroundColor White
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Configuração Completa!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Reinicie o computador (ou faça login novamente)" -ForegroundColor White
    Write-Host "2. O agendador vai iniciar automaticamente" -ForegroundColor White
    Write-Host "3. Verifique os logs em: z:\git\rotina\log\scheduler.log" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "ERRO ao criar atalho:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Read-Host "Pressione ENTER para sair"
