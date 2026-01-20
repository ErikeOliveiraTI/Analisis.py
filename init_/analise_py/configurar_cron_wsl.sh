#!/bin/bash
# Configuração de Cron no WSL para Backup Automático
# Siga os passos abaixo

echo "=========================================="
echo "Configurador de Cron - Backup Automatico"
echo "=========================================="
echo ""

# Verificar se WSL está disponível
if [ ! -d "/mnt" ]; then
    echo "ERRO: WSL nao detectado neste sistema"
    echo "Este script funciona apenas no Windows Subsystem for Linux (WSL)"
    echo ""
    echo "Para instalar WSL:"
    echo "  1. Abra PowerShell como Administrador"
    echo "  2. Execute: wsl --install"
    echo "  3. Reinicie o computador"
    exit 1
fi

echo "WSL detectado com sucesso!"
echo ""

# Verificar se cron está instalado
if ! command -v crontab &> /dev/null; then
    echo "AVISO: crontab nao encontrado"
    echo "Instalando cron..."
    sudo apt-get update
    sudo apt-get install -y cron
fi

# Iniciar cron se não estiver rodando
echo "Iniciando servico cron..."
sudo service cron start 2>/dev/null || sudo /etc/init.d/cron start 2>/dev/null

echo ""
echo "=========================================="
echo "Abrindo editor de cron..."
echo "=========================================="
echo ""
echo "Siga os passos:"
echo "1. Uma janela do editor (nano) vai abrir"
echo "2. Vá para o final do arquivo"
echo "3. Adicione a linha:"
echo ""
echo "   0 17 * * * bash /mnt/z/git/init_/analise_py/backup_rede.bash"
echo ""
echo "4. Salve com: CTRL+X, Y, ENTER"
echo ""
echo "Isto vai executar o backup todos os dias as 17:00"
echo ""
read -p "Pressione ENTER para continuar..."

# Abrir crontab
crontab -e

echo ""
echo "=========================================="
echo "Crontab configurado!"
echo "=========================================="
echo ""
echo "Para verificar:"
echo "  crontab -l"
echo ""
echo "Para remover:"
echo "  crontab -r"
echo ""
