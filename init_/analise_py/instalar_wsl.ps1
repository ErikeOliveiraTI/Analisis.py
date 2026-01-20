# Script para instalar WSL no Windows 10/11
# Execute como Administrador

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalador do WSL (Windows Subsystem for Linux)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verificar se e Administrador
$isAdmin = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Este script requer privilégios de administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instruções:" -ForegroundColor Yellow
    Write-Host "1. Abra PowerShell como Administrador" -ForegroundColor White
    Write-Host "2. Execute novamente este script" -ForegroundColor White
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit 1
}

Write-Host "Verificando versão do Windows..." -ForegroundColor Cyan
$osVersion = [System.Environment]::OSVersion.Version
Write-Host "Versão: Windows $($osVersion.Major).$($osVersion.Minor)" -ForegroundColor White
Write-Host ""

# Habilitar o recurso WSL
Write-Host "Habilitando o recurso WSL..." -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

Write-Host ""
Write-Host "Habilitando plataforma de máquina virtual..." -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host ""
Write-Host "Instalando WSL..." -ForegroundColor Cyan
wsl --install -d Ubuntu

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalação Concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximas etapas:" -ForegroundColor Yellow
Write-Host "1. Reinicie o computador" -ForegroundColor White
Write-Host "2. Após reiniciar, o Ubuntu vai abrir automaticamente" -ForegroundColor White
Write-Host "3. Configure o usuário e senha" -ForegroundColor White
Write-Host "4. Execute o configurador de cron:" -ForegroundColor White
Write-Host "   bash /mnt/z/git/init_/analise_py/configurar_cron_wsl.sh" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Reinicie seu computador agora!" -ForegroundColor Red
Write-Host ""
Read-Host "Pressione ENTER para sair"
