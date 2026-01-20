#!/bin/bash
export PATH=/usr/bin:/bin

################################################################################
# Script: backup_rede.bash
# Executa backup de rede para /z/git/rotina, cria pasta diária e logs
# Compatível com Git Bash no Windows
################################################################################

# ================= LOG DIÁRIO AUTOMÁTICO =================
#LOG_BASE="/z/git/rotina/log"
#mkdir -p "$LOG_BASE"

#LOG_FILE="$LOG_BASE/backup_$(date +%Y-%m-%d).log"

# Redireciona TODA a saída do script para o log
#exec >>"$LOG_FILE" 2>&1
# =========================================================

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


# Detectar automaticamente o ponto de montagem
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

# Testa se o ponto de montagem responde
if ! ls "$MOUNT_POINT" >/dev/null 2>&1; then
    echo "ERRO: Unidade Z está presente mas não responde."
    exit 1
fi

echo "Unidade de rede verificada com sucesso."
echo ""

# Configuração das pastas
BASE_DIR="$MOUNT_POINT/git/rotina"
DATA=$(date +"%d %b" | tr 'a-z' 'A-Z')
DESTINO="$BASE_DIR/$DATA"


echo "Criando pastas..."
mkdir -p "$DESTINO"


# Caminho **CORRIGIDO** da pasta de relatórios
# CONFIRME se o nome EXATO é "Relatorios /& Ficheiros"
ORIGEM="$MOUNT_POINT/01.FO_Tejo/02.Night_Auditor/Relatorios_e_Ficheiros/Relatorios"

# Arquivo Caixa.xlsx
CAIXA="$MOUNT_POINT/Caixa_1.xlsx"

#Arquivo Excel Mapa transfer_tours_.xlsx
MAPA_TRANSFER="$MOUNT_POINT/Mapa transfer_tours_1.xlsx"#

echo ""
echo "Validando origem..."
if [ ! -e "$ORIGEM" ]; then
    echo "ERRO: Pasta de origem não existe:"
    echo "      $ORIGEM"
    ls "$MOUNT_POINT/01.FO_Tejo/02.Night_Auditor"
    exit 1
fi
echo "Origem encontrada."

# Copiar Caixa.xlsx
if [ -f "$CAIXA" ]; then
    echo "Copiando Caixa.xlsx..."
    cp "$CAIXA" "$DESTINO/" || echo "ERRO AO COPIAR CAIXA.XLSX"
    #echo "Caixa.xlsx copiado com sucesso."
    #AVISO cp "$CAIXA" :"$DESTINO/" || echo "ERRO AO COPIAR CAIXA.XLSX""
else
    echo "AVISO: Caixa.xlsx não encontrado em:"
    echo "       $CAIXA"
fi

# Copiar relatórios
echo "Copiando relatórios..."
if cp -r "$ORIGEM/"* "$DESTINO/" 2>/dev/null; then
    echo "Relatórios copiados com sucesso."
else
    echo "ERRO ao copiar relatórios. Verifique permissões ou nomes com caracteres especiais."
fi

echo ""
echo "Ficheiros guardados em: $DESTINO"
echo "Rotina finalizada: $(date)"
echo "=============================================="
