#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Avançada - Data Warehouse
======================================

Arquivo de configuração centralizado para ajustes avançados.
Pode ser importado pelos módulos principais:

from config_avancada import *

"""

from pathlib import Path
import platform

# ============================================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================================

# Detectar SO
WINDOWS = platform.system() == "Windows"
LINUX = platform.system() == "Linux"
WSL = "microsoft" in platform.release().lower() if LINUX else False

# Caminhos base
if WINDOWS:
    # Windows com Git Bash ou nativo
    BASE_REDE = Path("z:/git/rotina")
    BASE_ORIGEM = Path("z:/01.FO_Tejo/02.Night_Auditor")
else:
    # Linux/WSL
    BASE_REDE = Path("/mnt/z/git/rotina")
    BASE_ORIGEM = Path("/mnt/z/01.FO_Tejo/02.Night_Auditor")

# Diretórios específicos
DIR_BACKUP = BASE_REDE
DIR_LOG = BASE_REDE / "log"
DIR_DADOS = BASE_REDE / "dados"
DB_PATH = BASE_REDE / "data_warehouse.db"

# Arquivos de origem
ARQUIVO_CAIXA = BASE_ORIGEM / "Caixa.xlsx"
DIR_RELATORIOS = BASE_ORIGEM / "Relatorios_e_Ficheiros" / "Relatorios"

# ============================================================================
# CONFIGURAÇÃO DO SCHEDULER
# ============================================================================

# Horário de executação
BACKUP_HORA = 17              # 17:00
BACKUP_MINIMO_INICIO = 0      # 17:00:00
BACKUP_MINIMO_FIM = 2         # 17:02:00

# Intervalo de verificação (segundos)
SCHEDULER_INTERVALO_SEG = 30

# Timeout para operações (segundos)
TIMEOUT_BACKUP = 3600         # 1 hora
TIMEOUT_EXCEL = 300           # 5 minutos por arquivo

# ============================================================================
# CONFIGURAÇÃO DA API REST
# ============================================================================

# Flask settings
FLASK_HOST = '0.0.0.0'        # Aceitar conexões externas
FLASK_PORT = 5000
FLASK_DEBUG = True
FLASK_THREADED = True

# Limites de API
API_MAX_REGISTROS_PADRAO = 1000
API_MAX_REGISTROS_LIMITE = 100000
API_MAX_QUERY_TAMANHO = 10000

# CORS
CORS_ORIGENS = '*'            # Aceitar de qualquer origem
CORS_METODOS = ['GET', 'POST', 'OPTIONS']

# ============================================================================
# CONFIGURAÇÃO DE BANCO DE DADOS
# ============================================================================

# SQLite
DB_TIMEOUT = 5                # Timeout de conexão (seg)
DB_JOURNAL_MODE = 'WAL'       # Write-Ahead Logging para performance
DB_SYNCHRONOUS = 'NORMAL'     # Balance entre velocidade e segurança

# Batch processing
BATCH_SIZE_INSERCAO = 100     # Inserir em lotes de 100
BATCH_SIZE_LEITURA = 1000     # Ler em lotes de 1000

# Índices (criar automaticamente)
CRIAR_INDICES = True
AUTO_VACUUM = True

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

# Níveis de log
LOG_LEVEL_CONSOLE = 'INFO'
LOG_LEVEL_ARQUIVO = 'DEBUG'

# Rotação de logs
LOG_MAX_BYTES = 10 * 1024 * 1024    # 10 MB
LOG_BACKUP_COUNT = 5                 # Manter 5 backups

# Formato
LOG_FORMATO = '[%(asctime)s] %(levelname)-8s %(name)s - %(message)s'
LOG_DATA_FORMATO = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# NORMALIZAÇÃO DE DADOS
# ============================================================================

# Charset para arquivos
CHARSET_PADRAO = 'utf-8'
CHARSET_SECUNDARIO = 'latin-1'

# Colunas esperadas em Caixa.xlsx
COLUNAS_CAIXA_ESPERADAS = [
    'descricao', 'data_operacao', 'valor_entrada', 'valor_saida',
    'saldo', 'metodo_pagamento', 'referencia_externa'
]

# Tipos de dados para conversão
TIPOS_NUMERICOS = ['valor_entrada', 'valor_saida', 'saldo']
TIPOS_DATAS = ['data_operacao', 'data']

# Remover duplicatas por colunas
COLUNAS_CHAVE_CAIXA = ['descricao', 'data_operacao', 'valor_entrada', 'saldo']

# ============================================================================
# VALIDAÇÃO DE DADOS
# ============================================================================

# Valores mínimos/máximos
VALOR_MIN = 0.00
VALOR_MAX = 999999999.99

# Datas
DATA_MIN = "1900-01-01"
DATA_MAX = "2100-12-31"

# Comprimento de texto
DESCRICAO_MIN_LEN = 1
DESCRICAO_MAX_LEN = 500

# ============================================================================
# ALERTAS E MONITORAMENTO
# ============================================================================

# Avisos de performance
TEMPO_ALARME_BACKUP_MS = 5000       # Alerta se > 5 segundos
TEMPO_ALARME_ETL_MS = 10000         # Alerta se > 10 segundos

# Limites de registros
MIN_REGISTROS_CAIXA = 10             # Alerta se < 10 registros
MAX_REGISTROS_CAIXA = 10000          # Alerta se > 10.000 registros

# Threshold de erro
MAX_ERROS_POR_DIA = 3                # Alertar após 3 erros
PERCENTUAL_ERRO = 10                 # Alertar se > 10% falham

# ============================================================================
# RETENÇÃO E LIMPEZA
# ============================================================================

# Retenção de dados
DIAS_RETENCAO_DADOS = 1095           # Manter 3 anos
DIAS_RETENCAO_LOGS = 90              # Manter 3 meses de logs
DIAS_RETENCAO_AUDITORIA = 365        # Manter 1 ano de auditoria

# Limpeza automática
AUTO_CLEANUP_HABILITADO = True
CLEANUP_HORA = 2                     # 02:00 (madrugada)

# ============================================================================
# BACKUP E DISASTER RECOVERY
# ============================================================================

# Backup automático do banco de dados
BACKUP_DB_HABILITADO = True
BACKUP_DB_FREQUENCIA_DIAS = 7        # Semanal
BACKUP_DB_DIRETORIO = BASE_REDE / "backups" / "db"
BACKUP_DB_MANTER_COPIAS = 4

# Export automático
EXPORT_AUTO_CSV = False
EXPORT_AUTO_JSON = False
EXPORT_FREQ_DIAS = 30                # Mensal

# ============================================================================
# SEGURANÇA
# ============================================================================

# Cript ografia (TODO: implementar)
USAR_CRIPTOGRAFIA = False
ALGORITMO_CRIPTO = 'AES-256'

# Autenticação API (TODO: implementar)
AUTENTICACAO_HABILITADA = False
TOKEN_EXPIRACAO_HORAS = 24
SECRET_KEY = 'sua-chave-secreta-aqui-mudar-em-producao'

# Rate limiting
RATE_LIMIT_REQUESTS = 1000           # 1000 requests
RATE_LIMIT_JANELA_SEG = 3600         # por hora

# Validação de entrada
VALIDAR_ENTRADA_SCRIPT_INJECTION = True
SANITIZAR_QUERIES = True

# ============================================================================
# INTEGRAÇÃO EXTERNA (TODO)
# ============================================================================

# Email para alertas
EMAIL_HABILITADO = False
EMAIL_SMTP_HOST = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587
EMAIL_USUARIO = 'seu-email@gmail.com'
EMAIL_SENHA = 'sua-senha'
EMAIL_DESTINATARIO = 'admin@empresa.com'

# Hooks webhook
WEBHOOK_HABILITADO = False
WEBHOOK_URL_SUCESSO = None
WEBHOOK_URL_ERRO = None

# Integração com Google Sheets (TODO)
GOOGLE_SHEETS_HABILITADO = False
GOOGLE_SHEETS_ID = None

# Integração com PowerBI (TODO)
POWERBI_HABILITADO = False
POWERBI_DATASET_ID = None

# ============================================================================
# DESENVOLVIMENTO E DEBUG
# ============================================================================

# Mode debug
DEBUG_MODE = False
VERBOSE = False

# Testes
TESTE_MODO_FIXTURE = True            # Usar dados de fixture em testes
TESTE_BANCO_TEMPORARY = True          # Usar banco temporário em testes

# Simulação
SIMULAR_BACKUP = False                # Não executar backup real
SIMULAR_PROCESSAMENTO = False         # Não processar dados

# ============================================================================
# PERFORMANCE
# ============================================================================

# Pool de conexões
DB_POOL_SIZE = 5
DB_POOL_TIMEOUT = 30

# Cache
CACHE_HABILITADO = True
CACHE_TTL_SEGUNDOS = 300              # 5 minutos

# Índices customizados
INDICES_CUSTOMIZADOS = True

# Otimização de query
QUERY_OPTIMIZATION = True
QUERY_LIMIT_PAGINA = 1000

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def garantir_diretorios():
    """Cria diretorios se não existem"""
    diretorios = [DIR_LOG, DIR_DADOS, BACKUP_DB_DIRETORIO]
    for d in diretorios:
        d.mkdir(parents=True, exist_ok=True)

def imprimir_config():
    """Imprime configuração atual"""
    print("\n" + "=" * 70)
    print("CONFIGURAÇÃO DO DATA WAREHOUSE")
    print("=" * 70)
    print(f"Sistema Operacional: {'Windows' if WINDOWS else 'Linux/WSL'}")
    print(f"Base da Rede: {BASE_REDE}")
    print(f"Banco de Dados: {DB_PATH}")
    print(f"Horário Backup: {BACKUP_HORA}:00-{BACKUP_HORA}:02")
    print(f"API REST: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"Debug: {DEBUG_MODE}")
    print("=" * 70 + "\n")

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

# Criar diretorios na importação
garantir_diretorios()

if __name__ == "__main__":
    imprimir_config()
