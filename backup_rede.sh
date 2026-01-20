#!/bin/bash
export PATH=/usr/bin:/bin

# ================= LOG =================
BASE_LOG_DIR="/z/git/rotina/log"
DATA_LOG=$(date +"%Y-%m-%d")
LOG_FILE="$BASE_LOG_DIR/backup_$DATA_LOG.log"

mkdir -p "$BASE_LOG_DIR"
exec >>"$LOG_FILE" 2>&1

echo "================================================"
echo "Backup iniciado em: $(date)"
echo "================================================"

# ================= MONTAGEM =================
if [ -d "/z" ]; then
    MOUNT_POINT="/z"
elif [ -d "/mnt/z" ]; then
    MOUNT_POINT="/mnt/z"
else
    echo "ERRO: Unidade Z não encontrada."
    exit 1
fi

if ! ls "$MOUNT_POINT" >/dev/null 2>&1; then
    echo "ERRO: Unidade Z não responde."
    exit 1
fi

echo "Unidade de rede OK: $MOUNT_POINT"

# ================= DESTINO =================
BASE_DIR="$MOUNT_POINT/git/rotina"
DATA=$(date +"%Y-%m-%d")
DESTINO="$BASE_DIR/$DATA"

mkdir -p "$DESTINO"
echo "Destino criado: $DESTINO"

# ================= ORIGEM =================
ORIGEM="$MOUNT_POINT/01.FO_Tejo/02.Night_Auditor/Relatorios_e_Ficheiros/Relatorios"
CAIXA="$MOUNT_POINT/Caixa_1.xlsx"
MAPA_TRANSFER="$MOUNT_POINT/Mapa transfer_tours_1.xlsx"

if [ ! -d "$ORIGEM" ]; then
    echo "ERRO: Origem não existe: $ORIGEM"
    exit 1
fi

echo "Origem encontrada."

# ================= CÓPIAS =================
if [ -f "$CAIXA" ]; then
    echo "Copiando Caixa.xlsx"
    cp -v "$CAIXA" "$DESTINO/"
else
    echo "AVISO: Caixa.xlsx não encontrado"
fi

if [ -f "$MAPA_TRANSFER" ]; then
    echo "Copiando Mapa transfer_tours"
    cp -v "$MAPA_TRANSFER" "$DESTINO/"
else
    echo "AVISO: Mapa transfer não encontrado"
fi

echo "Copiando relatórios..."
cp -av "$ORIGEM/." "$DESTINO/"

echo "Backup finalizado com sucesso em: $(date)"
echo "================================================"
