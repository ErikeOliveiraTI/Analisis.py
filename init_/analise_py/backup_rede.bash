#!/bin/bash
export PATH=/usr/bin:/bin

################################################################################
# Script: backup_rede.bash
# Executa backup de rede para /z/git/rotina, cria pasta diária e logs
# Compatível com Git Bash no Windows
# Uso: ./backup_rede.bash ou bash backup_rede.bash
################################################################################

set -o pipefail

# ================= LOG DIÁRIO AUTOMÁTICO =================
BASE_LOG_DIR="/z/git/rotina/log"
DATA_LOG=$(date +"%Y-%m-%d")
LOG_FILE="$BASE_LOG_DIR/backup_$DATA_LOG.log"

mkdir -p "$BASE_LOG_DIR"

# Redireciona TODA a saída (stdout e stderr) para o log
exec >>"$LOG_FILE" 2>&1

echo "================================================"
echo "Backup iniciado em: $(date)"
echo "================================================"
# =========================================================

# Variáveis de data
DATA=$(date +"%d %b" | tr 'a-z' 'A-Z')

# Ponto de montagem
#MOUNT_POINT="/z"

# Detectar automaticamente se o ponto de montagem é /z ou /mnt/z
if [ -d "/z" ]; then
    MOUNT_POINT="/z"
elif [ -d "/mnt/z" ]; then
    MOUNT_POINT="/mnt/z"
else
    echo "ERRO: Unidade Z não encontrada em /z nem /mnt/z"
    exit 1
fi


echo "=============================================="
echo "Verificando unidade de rede: $(date)"
echo "=============================================="
if [ ! -d "$MOUNT_POINT" ]; then
    echo "ERRO: O diretório $MOUNT_POINT não existe."
    exit 1
fi

if ! ls "$MOUNT_POINT" >/dev/null 2>&1; then
    echo "ERRO: /z está montado mas não responde."
    exit 1
fi
echo "Unidade /z verificada com sucesso."
echo ""

# Configuração de pastas
BASE_DIR="/z/git/rotina"
DATA=$(date +"%d %b" | tr 'a-z' 'A-Z')
DESTINO="$BASE_DIR/$DATA"
LOG_DIR="$BASE_DIR/log"

echo "Criando pasta destino: $DESTINO"
mkdir -p "$DESTINO"
mkdir -p "$LOG_DIR"

# Caminhos de origem (CORRIGIDO)
#ORIGEM="$MOUNT_POINT/01.FO_Tejo/02.Night_Auditor/'Relatorios /& Ficheiros'/Relatorios"
ORIGEM="$MOUNT_POINT/01.FO_Tejo/02.Night_Auditor/Relatorios_e_Ficheiros/Relatorios"


# Caminho da planilha (válido)
CAIXA="$MOUNT_POINT/Caixa.xlsx"

# Valida origem
if [ ! -d "$ORIGEM" ]; then
    echo "ERRO: Pasta de origem não existe: $ORIGEM"
    exit 1
fi

# Copiar Caixa.xlsx
if [ ! -f "$CAIXA" ]; then
    echo "ERRO: Arquivo Caixa.xlsx não encontrado em: $CAIXA"
else
    echo "Copiando Caixa.xlsx..."
    cp "$CAIXA" "$DESTINO/"
    echo "Caixa.xlsx copiado com sucesso."
fi

# Copiar relatórios
echo "Copiando relatórios..."
cp -r "$ORIGEM/"* "$DESTINO/"
if [ $? -eq 0 ]; then
    echo "Relatórios copiados com sucesso."
else
    echo "ERRO ao copiar relatórios."
fi

echo ""
echo "Ficheiros guardados em: $DESTINO"
echo "Rotina finalizada: $(date)"
echo "=============================================="
