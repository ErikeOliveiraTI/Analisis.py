# 🔗 Cadeia de Dependências - Data Warehouse

**Versão:** 1.0 | **Data:** 29/03/2026 | **Status:** ✅ Documentado

---

## 📊 Diagrama de Dependências

```
┌─────────────────────────────────────────────────────────────┐
│                    REQUIREMENTS.TXT                         │
│  (1º: Instalar dependências externas)                      │
│  ├─ pandas>=1.3.0                                          │
│  ├─ flask>=2.0.0                                           │
│  ├─ openpyxl>=3.5.0                                        │
│  ├─ flask-cors>=3.0.10                                     │
│  └─ sqlite3 (stdlib)                                       │
└────────────────┬────────────────────────────────────────────┘
                 │ pip install -r requirements.txt
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              CONFIG_AVANCADA.PY                             │
│  (2º: Configurações centralizadas - Foundation)            │
│  ├─ Caminhos de rede (Windows/Linux)                       │
│  ├─ Horários de backup                                     │
│  ├─ Ports e endpoints                                      │
│  └─ Parâmetros globais                                     │
└────────────────┬────────────────────────────────────────────┘
                 │ from config_avancada import *
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            DATA_WAREHOUSE.PY                                │
│  (3º: Motor ETL - Extração, Transformação, Carga)          │
│  ├─ class DataWarehouse (Principal)                        │
│  ├─ Normalização (3NF)                                     │
│  ├─ Schema SQLite                                          │
│  ├─ Consultas com Pandas                                   │
│  └─ Logging estruturado                                    │
└─────┬────────────────────────────────────────────────────────┘
      │ from data_warehouse import DataWarehouse
      │
      ├──────────────┬──────────────────────────┐
      │              │                          │
      ▼              ▼                          ▼
┌───────────┐  ┌──────────────┐      ┌──────────────────┐
│ API_REST  │  │  SCHEDULER   │      │ TEST_DATA_WARE  │
│   .PY     │  │   COM_DW.PY  │      │   HOUSE.PY       │
└───────────┘  └──────────────┘      └──────────────────┘
      │              │                          │
      │              │                          │
      └──────────────┴──────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │  EXECUÇÃO EM PRODUÇÃO    │
        └──────────────────────────┘
```

---

## 📦 Ordem de Inicialização (Boot Sequence)

### Fase 1: Preparação (Setup)

```
1. ✅ pip install -r requirements.txt
   └─ Instalar: pandas, flask, openpyxl, flask-cors
```

### Fase 2: Validação (Validation)

```
2. ✅ python -c "import config_avancada; config_avancada.imprimir_config()"
   └─ Verificar configurações
   
3. ✅ python -c "from data_warehouse import DataWarehouse; print('OK')"
   └─ Testar importação
```

### Fase 3: Testes (Testing)

```
4. ✅ python test_data_warehouse.py
   └─ Suite completa de testes
   
5. ✅ python scheduler_com_dw.py --teste
   └─ Teste do scheduler sem esperar 17:00
```

### Fase 4: Produção (Production)

```
6. 🟢 python scheduler_com_dw.py
   └─ Terminal 1 - Scheduler (roda indefinidamente)
   
7. 🟢 python api_rest.py
   └─ Terminal 2 - API REST (porta 5000)
```

### Fase 5: Validação Final (Final Check)

```
8. ✅ curl http://localhost:5000/health
   └─ Verificar API respondendo
   
9. ✅ tail -f /z/git/rotina/log/scheduler_com_dw.log
   └─ Monitorar logs em tempo real
```

---

## 🔗 Dependências Lineares

### Nível 0: Externas

```
requirements.txt
  ├─ pandas          (leitura/processamento Excel)
  ├─ flask           (API REST)
  ├─ openpyxl        (escrita Excel)
  ├─ flask-cors      (cross-origin requests)
  └─ sqlite3         (banco de dados - stdlib)
```

### Nível 1: Foundation (Configuração)

```
config_avancada.py   ◄─ Sem dependências internas
  ├─ Caminhos principais
  ├─ Horários
  ├─ Portas
  └─ Parâmetros globais
```

### Nível 2: Core (Motor)

```
data_warehouse.py    ◄─ Depende de: config_avancada.py, pandas, sqlite3
  ├─ Extração
  ├─ Transformação
  ├─ Carga
  └─ Consultas
```

### Nível 3: Aplicações (Consumers)

```
api_rest.py          ◄─ Depende de: data_warehouse.py, flask, flask-cors
  ├─ GET /api/caixa
  ├─ GET /api/resumo-diario
  ├─ POST /api/processar-backup
  └─ ...

scheduler_com_dw.py  ◄─ Depende de: data_warehouse.py, subprocess, time
  ├─ Verifica hora (17:00)
  ├─ Executa backup_rede.bash
  └─ Processa no DW

test_data_warehouse.py  ◄─ Depende de: data_warehouse.py, unittest
  ├─ Testa banco
  ├─ Testa extração
  ├─ Testa normalização
  └─ ...
```

---

## 🎯 Matriz de Dependências

| Arquivo | Nível | Depende De | Roda Em | Status |
|---------|-------|-----------|--------|--------|
| requirements.txt | 0 | Nenhum | PIP | ✅ |
| config_avancada.py | 1 | stdlib | Python | ✅ |
| data_warehouse.py | 2 | config, pandas, sqlite3 | Python | ✅ |
| api_rest.py | 3 | data_warehouse, flask | Python | ✅ |
| scheduler_com_dw.py | 3 | data_warehouse, subprocess | Python | ✅ |
| test_data_warehouse.py | 3 | data_warehouse, unittest | Python | ✅ |

---

## 🚀 Sequência Completa de Execução

### 1️⃣ Instalação (Nunca)

```bash
# Executar uma única vez
pip install -r DEV_ENVIRONMENT/requirements.txt
```

**O que acontece:**
- ✅ Pandas instalado
- ✅ Flask instalado
- ✅ Dependências resolvidas
- ✅ Pronto para uso

---

### 2️⃣ Validação (Toda vez)

```bash
# Antes de iniciar
python DEV_ENVIRONMENT/config_avancada.py

# Output esperado:
# ==============================================================================
# CONFIGURAÇÃO DO DATA WAREHOUSE
# ==============================================================================
# Sistema Operacional: Windows
# Base da Rede: z:\git\rotina
# Banco de Dados: z:\git\rotina\data_warehouse.db
# Horário Backup: 17:00-17:02
# API REST: http://0.0.0.0:5000
# ==============================================================================
```

**O que verifica:**
- ✅ Configurações carregadas
- ✅ Caminhos acessíveis
- ✅ Sistema operacional detectado

---

### 3️⃣ Testes (Antes de produção)

```bash
# Rodar todos os testes
python DEV_ENVIRONMENT/test_data_warehouse.py

# Output esperado:
# test_banco_criado ... ok
# test_tabelas_existem ... ok
# test_extrair_arquivo_inexistente ... ok
# ...
# Ran 18 tests in 2.345s
# OK ✅
```

**O que testa:**
- ✅ Banco criado corretamente
- ✅ Schema validado
- ✅ Funcionalidades principais

---

### 4️⃣ Teste Rápido (Optional)

```bash
# Testar sem esperar 17:00
python DEV_ENVIRONMENT/scheduler_com_dw.py --teste

# Output esperado:
# MODO TESTE: Processando backup de hoje...
# Data de teste: 29 MAR
# ✓ Backup processado com sucesso
# Arquivos processados: 5
# Total de registros: 1250
```

**O que faz:**
- ✅ Processa backup de hoje
- ✅ Valida pipeline completo
- ✅ Sem esperar 17:00

---

### 5️⃣ Scheduler (Terminal 1 - Contínuo)

```bash
# Inicia scheduler
python DEV_ENVIRONMENT/scheduler_com_dw.py

# Output esperado:
# ✓ SCHEDULER COM DATA WAREHOUSE INICIALIZADO
# ✓ Horário de backup: 17:00
# ✓ Sistema aguardando...
# [14:30:05] Aguardando horário de backup...
# [14:30:35] Aguardando horário de backup...
# ... (a cada 30 segundos)
# [17:00:01] ► HORA DE BACKUP! Iniciando rotina...
```

**Mantém:**
- ✅ Monitorando hora
- ✅ Executando backup às 17:00
- ✅ Carregando dados no DW

---

### 6️⃣ API REST (Terminal 2 - Contínuo)

```bash
# Inicia API
python DEV_ENVIRONMENT/api_rest.py

# Output esperado:
# ...
# * Running on http://0.0.0.0:5000
# * Press CTRL+C to quit
# [14:35:10] /api/caixa [GET] 200
# [14:35:25] /status [GET] 200
```

**Fornece:**
- ✅ Endpoints GET/POST
- ✅ Consultas dinâmicas
- ✅ Processamento de backups manual

---

## 🔄 Fluxo Típico de Uso

```
T0: Instalar
    └─> pip install -r requirements.txt

T1: Validar
    └─> python config_avancada.py
    └─> python -c "from data_warehouse import DataWarehouse; print('OK')"

T2: Testar
    └─> python test_data_warehouse.py
    └─> python scheduler_com_dw.py --teste

T3 (Produção): Terminal 1
    └─> python scheduler_com_dw.py
        └─ Roda indefinidamente até Ctrl+C
        └─ Executa às 17:00

T3 (Produção): Terminal 2
    └─> python api_rest.py
        └─ Servidor HTTP na porta 5000
        └─ Aguarda requisições

T4: Monitorar
    └─> curl http://localhost:5000/health
    └─> tail -f /z/git/rotina/log/scheduler_com_dw.log
    └─> sqlite3 /z/git/rotina/data_warehouse.db "SELECT COUNT(*) FROM fato_caixa;"
```

---

## ⚠️ Verificação de Dependências

### Verificar Pandas

```bash
python -c "import pandas; print(f'Pandas {pandas.__version__}')"
# Output: Pandas 1.3.5
```

### Verificar Flask

```bash
python -c "import flask; print(f'Flask {flask.__version__}')"
# Output: Flask 2.0.1
```

### Verificar SQLite

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
# Output: 3.37.0
```

### Verificar Todos

```bash
python -m pip list | grep -E "pandas|flask|openpyxl"
```

---

## 🚨 Se Algo Faltar

### Pandas não encontrado

```bash
pip install pandas openpyxl
```

### Flask não encontrado

```bash
pip install flask flask-cors
```

### Conflito de versão

```bash
pip install --upgrade -r requirements.txt
```

### Limpar cache

```bash
pip cache purge
pip install --force-reinstall -r requirements.txt
```

---

## 📋 Checklist de Dependências

Antes de iniciar produção:

- [ ] `pip show pandas` - Instalado?
- [ ] `pip show flask` - Instalado?
- [ ] `pip show openpyxl` - Instalado?
- [ ] `python config_avancada.py` - Config OK?
- [ ] `python test_data_warehouse.py` - Testes OK?
- [ ] `curl http://localhost:5000/health` - API OK?
- [ ] `/z/git/rotina/` acessível
- [ ] `/z/01.FO_Tejo/02.Night_Auditor/Caixa.xlsx` existe
- [ ] Backup antigo (`backup_rede.bash`) funciona

---

## 🎓 Próximas Dependências (Roadmap)

### Futuro: Dashboard

```
➕ matplotlib>=3.3.0
➕ seaborn>=0.11.0
➕ plotly>=5.0.0
```

### Futuro: Machine Learning

```
➕ scikit-learn>=0.24.0
➕ numpy>=1.20.0
```

### Futuro: Cloud

```
➕ azure-storage-blob
➕ boto3  (AWS)
```

### Futuro: Integração

```
➕ python-dotenv
➕ requests
➕ aiohttp
```

---

**Status:** ✅ Todas as dependências documentadas e testadas  
**Última atualização:** 29/03/2026  
**Próxima revisão:** 30/04/2026
