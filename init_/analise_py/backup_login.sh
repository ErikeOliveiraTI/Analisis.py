#!/bin/bash

# Script: backup_diario_login.sh
# Executa o backup automaticamente quando o usuario faz login
# Coloque um atalho deste script na pasta Inicialização do Windows

SCRIPT_PATH="/z/git/init_/analise_py/backup_rede.bash"
LOG_PATH="/z/git/rotina/log/backup_login.log"

# Criar pasta de log
mkdir -p "$(dirname "$LOG_PATH")"

# Verificar se ja rodou hoje
DATA_HOJE=$(date +"%Y-%m-%d")
ULTIMA_EXECUCAO=$(tail -1 "$LOG_PATH" 2>/dev/null | grep -oP "^\[\K[^]]*")

if [ "$ULTIMA_EXECUCAO" == "$DATA_HOJE" ]; then
    echo "[$(date)] Backup ja foi executado hoje. Ignorando..."
    exit 0
fi

# Verificar se ja esta em horario de backup (17:00 ou depois)
HORA_ATUAL=$(date +"%H")
if [ "$HORA_ATUAL" -ge 17 ]; then
    echo "[$(date)] Iniciando backup..."
    bash "$SCRIPT_PATH"
else
    echo "[$(date)] Aguardando horario de backup (17:00)"
fi
