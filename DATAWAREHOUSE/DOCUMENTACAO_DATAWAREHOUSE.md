# Data Warehouse com Sistema de Backup Automático

## 📋 Visão Geral

Sistema integrado que transforma seu backup de rede em um **Data Warehouse profissional** com:

✅ **Extração Automática**: Copia arquivos da rede (Z:) em backup diário
✅ **Transformação & Normalização**: Padroniza dados em 3ª forma normal (3NF)
✅ **Carga em Banco de Dados**: SQLite centralizado com relatórios estruturados
✅ **API REST**: Endpoints GET/POST para consultas com Pandas
✅ **Agendamento**: Executa automaticamente às 17:00 via Windows Startup

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│   Z:\ Network Share (16:00)          │
│   └─ 01.FO_Tejo/                    │
│      └─ 02.Night_Auditor/           │
│         ├─ Caixa.xlsx               │
│         └─ Relatorios_e_Ficheiros/  │
└─────────────┬───────────────────────┘
              │
              ▼ (17:00)
┌─────────────────────────────────────┐
│   backup_rede.bash                   │
│   (Cria pasta DD MMM)                │
└─────────────┬───────────────────────┘
              │
              ▼ (Imediato)
┌─────────────────────────────────────┐
│   scheduler_com_dw.py                │
│   ├─ Data Warehouse (ETL)            │
│   ├─ Normalização                    │
│   └─ Registra no SQLite              │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   data_warehouse.db (SQLite)         │
│   ├─ dim_datas                       │
│   ├─ fato_caixa                      │
│   ├─ fato_relatorios                 │
│   └─ auditoria_processamento         │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   api_rest.py (Flask)                │
│   HTTP Endpoints (GET/POST)          │
│   ├─ GET /api/caixa                  │
│   ├─ GET /api/resumo-diario          │
│   ├─ POST /api/processar-backup      │
│   └─ ...                             │
└─────────────────────────────────────┘
```

---

## 📁 Estrutura de Arquivos

### Novos Arquivos Criados

| Arquivo | Descrição | Tipo |
|---------|-----------|------|
| **data_warehouse.py** | Módulo ETL com normalização de dados | Python |
| **api_rest.py** | API REST com Flask (GET/POST) | Python |
| **scheduler_com_dw.py** | Scheduler integrado com DW | Python |
| **DOCUMENTACAO_DATAWARE HOUSE.md** | Esta documentação | Markdown |
| **test_data_warehouse.py** | Suite de testes | Python |
| **requirements.txt** | Dependências do projeto | Text |

### Arquivos Existentes (Compatíveis)

- `backup_rede.bash` - Script de backup (continua funcionando)
- `backup_scheduler.py` - Scheduler antigo (pode ser descontinuado)
- `iniciar_agendador.bat` - Starter do agendador
- `/z/git/rotina/` - Diretório base de backups

---

## 🚀 Instalação e Uso

### 1. Instalar Dependências

```bash
pip install flask flask-cors pandas openpyxl
```

### 2. Iniciar o Scheduler Integrado (Modo Contínuo)

```bash
# Terminal Git Bash ou PowerShell
python C:\Users\recep2\Documents\git\analise_py\scheduler_com_dw.py

# Ou via atalho de startup automático
# Coloque iniciar_agendador.bat em: C:\Users\recep2\AppData\Microsoft\Windows\Start Menu\Programs\Startup
```

### 3. Iniciar a API REST (em outro terminal)

```bash
python C:\Users\recep2\Documents\git\analise_py\api_rest.py

# Servidor estará disponível em:
# http://localhost:5000
```

### 4. Testar o Sistema

```bash
# Terminal 3: Executar testes
python C:\Users\recep2\Documents\git\analise_py\test_data_warehouse.py

# Ou teste rápido do scheduler
python C:\Users\recep2\Documents\git\analise_py\scheduler_com_dw.py --teste
```

---

## 📚 API REST - Endpoints

### Health Check

#### `GET /health`
Verifica status da API

**Response:**
```json
{
  "status": "sucesso",
  "código": 200,
  "data": {
    "status": "conectado",
    "versão": "1.0"
  }
}
```

### Status do Data Warehouse

#### `GET /status`
Informações do banco de dados

**Response:**
```json
{
  "status": "sucesso",
  "data": {
    "banco_de_dados": "z:/git/rotina/data_warehouse.db",
    "existe": true,
    "tamanho_mb": 12.5
  }
}
```

### Consultas de Caixa

#### `GET /api/caixa`
Retorna dados de caixa com filtros

**Query Parameters:**
- `data_inicio`: YYYY-MM-DD (opcional)
- `data_fim`: YYYY-MM-DD (opcional)
- `limite`: max de linhas (opcional, padrão: 1000)

**Exemplos:**
```bash
# Todos os registros
curl "http://localhost:5000/api/caixa"

# Filtrar por período
curl "http://localhost:5000/api/caixa?data_inicio=2024-01-01&data_fim=2024-01-31"

# Limitar resultados
curl "http://localhost:5000/api/caixa?limite=100"
```

**Response:**
```json
{
  "status": "sucesso",
  "data": {
    "total_registros": 150,
    "limite": 1000,
    "caixa": [
      {
        "id_caixa": 1,
        "data": "2024-01-13",
        "descricao": "Entrada Caixa",
        "valor_entrada": 500.00,
        "valor_saida": null,
        "saldo": 500.00,
        "metodo_pagamento": "Dinheiro"
      },
      ... mais registros
    ]
  }
}
```

#### `GET /api/resumo-diario`
Resumo consolidado de caixa para um dia

**Query Parameters:**
- `data`: YYYY-MM-DD (obrigatório)

**Exemplo:**
```bash
curl "http://localhost:5000/api/resumo-diario?data=2024-01-13"
```

**Response:**
```json
{
  "status": "sucesso",
  "data": {
    "data": "2024-01-13",
    "num_operacoes": 45,
    "total_entrada": 5000.00,
    "total_saida": 1200.00,
    "saldo_final": 3800.00
  }
}
```

#### `GET /api/relatorios`
Lista de relatórios processados

**Query Parameters:**
- `data_inicio`: YYYY-MM-DD (opcional)
- `data_fim`: YYYY-MM-DD (opcional)
- `limite`: max de registros (padrão: 500)

**Exemplo:**
```bash
curl "http://localhost:5000/api/relatorios?data_inicio=2024-01-01"
```

### Processamento de Backup

#### `POST /api/processar-backup`
Processa um backup e carrega no DW

**Request Body (JSON):**
```json
{
  "data_pasta": "13 JAN"
}
```

**Exemplo (usando curl):**
```bash
curl -X POST http://localhost:5000/api/processar-backup \
  -H "Content-Type: application/json" \
  -d '{"data_pasta": "13 JAN"}'
```

**Response:**
```json
{
  "status": "sucesso",
  "código": 201,
  "data": {
    "data_pasta": "13 JAN",
    "status": "sucesso",
    "arquivos_processados": 5,
    "total_registros": 250,
    "tempo_ms": 1234
  }
}
```

#### `POST /api/consulta-customizada`
Executa consulta SQL customizada (usuários avançados)

**Request Body (JSON):**
```json
{
  "query": "SELECT * FROM fato_caixa WHERE valor_entrada > ? ORDER BY data DESC",
  "parametros": [100.0]
}
```

**Segurança:**
- Operações perigosas bloqueadas: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE
- Apenas consultas SELECT permitidas

**Response:**
```json
{
  "status": "sucesso",
  "data": {
    "total_registros": 25,
    "registros": [...]
  }
}
```

---

## 🗄️ Estrutura de Dados (Schema SQLite)

### Tabelas Dimensões (Lookup Tables)

#### `dim_datas`
Dimensão de tempo para análise de séries temporais

```sql
CREATE TABLE dim_datas (
    id_data INTEGER PRIMARY KEY,
    data DATE UNIQUE NOT NULL,
    dia INTEGER,
    mes INTEGER,
    ano INTEGER,
    nome_dia_semana TEXT,
    eh_fim_de_semana BOOLEAN,
    semana_do_ano INTEGER
);
```

#### `dim_tipos_arquivo`
Tipos de arquivo processados (Caixa, Relatório, etc)

```sql
CREATE TABLE dim_tipos_arquivo (
    id_tipo INTEGER PRIMARY KEY,
    nome_tipo TEXT UNIQUE NOT NULL,
    extensao TEXT,
    descricao TEXT
);
```

### Tabelas de Fatos (Agregadas)

#### `fato_backups`
Registro central de cada arquivo de backup processado

```sql
CREATE TABLE fato_backups (
    id_backup INTEGER PRIMARY KEY,
    id_data INTEGER NOT NULL,      -- FK dim_datas
    id_tipo INTEGER NOT NULL,      -- FK dim_tipos_arquivo
    nome_arquivo TEXT NOT NULL,
    caminho_relativo TEXT NOT NULL,
    hash_arquivo TEXT UNIQUE,      -- Detectar duplicatas
    tamanho_bytes INTEGER,
    numero_linhas INTEGER,
    numero_colunas INTEGER,
    status TEXT DEFAULT 'processado',
    data_importacao TIMESTAMP
);
```

#### `fato_caixa`
Cada transação de caixa normalizada e carregada

```sql
CREATE TABLE fato_caixa (
    id_caixa INTEGER PRIMARY KEY,
    id_backup INTEGER,             -- FK fato_backups
    id_data INTEGER NOT NULL,      -- FK dim_datas
    data_operacao DATE,
    descricao TEXT,
    valor_entrada DECIMAL(12, 2),
    valor_saida DECIMAL(12, 2),
    saldo DECIMAL(12, 2),
    metodo_pagamento TEXT,
    referencia_externa TEXT,
    criado_em TIMESTAMP
);
```

#### `fato_relatorios`
Resumo de cada relatório processado

```sql
CREATE TABLE fato_relatorios (
    id_relatorio INTEGER PRIMARY KEY,
    id_backup INTEGER,             -- FK fato_backups
    id_data INTEGER NOT NULL,      -- FK dim_datas
    nome_relatorio TEXT,
    tipo_relatorio TEXT,
    total_registros INTEGER,
    valor_total DECIMAL(15, 2),
    periodo_inicio DATE,
    periodo_fim DATE,
    criado_em TIMESTAMP
);
```

#### `auditoria_processamento`
Log de auditoria para debugging e conformidade

```sql
CREATE TABLE auditoria_processamento (
    id_auditoria INTEGER PRIMARY KEY,
    id_backup INTEGER,             -- FK fato_backups
    id_data INTEGER,               -- FK dim_datas
    tipo_operacao TEXT,            -- 'LEITURA', 'TRANSFORMACAO', 'CARGA'
    descricao TEXT,
    status TEXT,                   -- 'SUCESSO', 'AVISO', 'ERRO'
    tempo_processamento_ms INTEGER,
    erro_mensagem TEXT,
    data_processamento TIMESTAMP
);
```

---

## 🔄 Fluxo de ETL (Extract-Transform-Load)

### 1️⃣ EXTRAÇÃO (Extract)

```python
from data_warehouse import DataWarehouse

dw = DataWarehouse()

# Extrai arquivo Excel da rede
df = dw.extrair_arquivo_excel(Path("/z/git/rotina/13 JAN/Caixa.xlsx"))
print(f"Linhas extraídas: {len(df)}")
```

**O que acontece:**
- Lê arquivo .xlsx usando Pandas
- Mantém estrutura original dos dados
- Registra em log qualquer erro

### 2️⃣ TRANSFORMAÇÃO (Transform)

```python
# Normaliza dados
df_normalizado = dw.normalizar_caixa(df)
```

**O que acontece:**
- Remove linhas vazias e duplicatas
- Padroniza nomes de colunas (lowercase)
- Converte tipos de dados (datas, decimais)
- Trata valores ausentes (NaN)
- Garante formato uniforme

**Antes:**
```
Descrição      | Entrada    | Saída       | Saldo
Entrada Caixa  | 500,00     | NaN         | 500
entrada caixa  | 500.00     | <vazio>     | 500.00
```

**Depois:**
```
descricao      | valor_entrada | valor_saida | saldo
entrada_caixa  | 500.00        | NULL        | 500.00
entrada_caixa  | 500.00        | NULL        | 500.00
```

### 3️⃣ CARGA (Load)

```python
# Registra no banco de dados
dw.carregar_caixa(df_normalizado, id_backup=1, id_data=5)
```

**O que acontece:**
- Insere cada linha em fato_caixa
- Mantém referências às dimensões (datas, tipos)
- Cria índices para performance
- Valida integridade referencial

### Execução Automática

```python
# Processa backup completo de um dia
resultado = dw.processar_backup_diario("13 JAN")

print(resultado)
# {
#   "data_pasta": "13 JAN",
#   "status": "sucesso",
#   "arquivos_processados": 5,
#   "total_registros": 1250,
#   "tempo_ms": 2345
# }
```

---

## 📊 Exemplos de Consultas com Pandas

```python
from data_warehouse import DataWarehouse
import pandas as pd

dw = DataWarehouse()

# 1. Consultar toda a caixa de janeiro
df_jan = dw.consultar_caixa("2024-01-01", "2024-01-31")
print(df_jan.describe())

# 2. Resumo diário
resumo = dw.resumo_diario("2024-01-13")
print(f"Saldo: R$ {resumo['saldo_final']:.2f}")

# 3. Análise customizada com Pandas
df_caixa = dw.consultar_caixa()
media_entrada = df_caixa['valor_entrada'].mean()
print(f"Média de entrada: R$ {media_entrada:.2f}")

# 4. Agrupar por método de pagamento
df_por_metodo = df_caixa.groupby('metodo_pagamento').agg({
    'valor_entrada': 'sum',
    'valor_saida': 'sum'
})
print(df_por_metodo)
```

---

## 🧪 Testes e Validação

### Teste Rápido do Scheduler

```bash
# Processa backup de hoje sem esperar 17:00
python scheduler_com_dw.py --teste
```

### Suite de Testes Completa

```bash
python test_data_warehouse.py
```

**Cobre:**
- ✅ Criação de banco de dados
- ✅ Extração de arquivos
- ✅ Normalização de dados
- ✅ Carga no banco
- ✅ Consultas com Pandas
- ✅ Endpoints da API

### Validar Banco de Dados

```bash
# Ver estrutura das tabelas
sqlite3 z:\git\rotina\data_warehouse.db ".schema"

# Contar registros
sqlite3 z:\git\rotina\data_warehouse.db "SELECT COUNT(*) FROM fato_caixa;"

# Ver últimas transações
sqlite3 z:\git\rotina\data_warehouse.db \
  "SELECT * FROM fato_caixa ORDER BY criado_em DESC LIMIT 5;"
```

---

## 🔧 Ajustes e Configuração

### Mudar Horário do Backup

**Arquivo:** `scheduler_com_dw.py`

```python
# Linha ~30
class ConfigScheduler:
    HORA_BACKUP = 17        # Mudar de 17 para desejado (0-23)
    MINUTO_INICIO = 0
    MINUTO_FIM = 2          # Executar entre 17:00 e 17:02
```

### Mudar Intervalo de Verificação

```python
INTERVALO_VERIFICACAO = 30  # Mudar de 30 para X segundos
```

### Mudar Caminho da Rede

**Arquivo:** `data_warehouse.py`

```python
class ConfigDW:
    if platform.system() == "Windows":
        BASE_DIR = Path("z:/git/rotina")           # Mudar se necessário
        DB_PATH = Path("z:/git/rotina/data_warehouse.db")
```

---

## 📝 Logs e Auditoria

### Arquivos de Log

| Arquivo | Descrição |
|---------|-----------|
| `/z/git/rotina/log/data_warehouse.log` | Log do ETL |
| `/z/git/rotina/log/scheduler_com_dw.log` | Log do scheduler |
| `/z/git/rotina/log/backup_YYYY-MM-DD.log` | Log do backup diário |

### Ler Logs Recentes

```bash
# Últimas 50 linhas do DW
tail -50 /z/git/rotina/log/data_warehouse.log

# Procurar erros
grep "✗ Erro" /z/git/rotina/log/scheduler_com_dw.log

# Ver processamento de hoje
grep "2024-03-29" /z/git/rotina/log/scheduler_com_dw.log
```

---

## ⚠️ Troubleshooting

### Problema: "Módulo pandas não encontrado"

**Solução:**
```bash
pip install pandas openpyxl
```

### Problema: "Banco de dados está travado"

**Solução:**
```bash
# Fechar todas as conexões Python abertas
# Verificar que apenas um scheduler está rodando
# Reiniciar o scheduler

python scheduler_com_dw.py
```

### Problema: API retorna 503 "Data Warehouse não disponível"

**Solução:**
```bash
# Verificar se data_warehouse.py pode ser importado
python -c "from data_warehouse import DataWarehouse; print('OK')"

# Verificar banco de dados existe
ls -lh /z/git/rotina/data_warehouse.db
```

### Problema: Backup não executa às 17:00

**Debug:**
```bash
# Executar scheduler em modo teste
python scheduler_com_dw.py --teste

# Verificar logs
tail -20 /z/git/rotina/log/scheduler_com_dw.log

# Verificar se PC estava ligado
# Verificar se hora do sistema está correta
```

### Problema: Arquivos Excel não aparecem no banco

**Debug:**
```bash
# Verificar se pasta de backup existe
ls /z/git/rotina/

# Verificar se Caixa.xlsx está presente
ls /z/git/rotina/13\ JAN/Caixa.xlsx

# Processar manualmente
python scheduler_com_dw.py --teste
```

---

## 🚀 Performance e Escalabilidade

### Índices para Otimização

O sistema cria índices automaticamente:
```sql
CREATE INDEX idx_datas_data ON dim_datas(data);
CREATE INDEX idx_backups_data ON fato_backups(id_data);
CREATE INDEX idx_caixa_data ON fato_caixa(id_data);
```

### Limite de Registros por Consulta

```python
# API limita a 1000 registros por padrão
# Pode aumentar via parâmetro 'limite'
curl "http://localhost:5000/api/caixa?limite=10000"
```

### Limpeza Periódica (Opcional)

```bash
# Remover dados anteriores a 2023
sqlite3 /z/git/rotina/data_warehouse.db \
  "DELETE FROM fato_caixa WHERE id_data IN 
   (SELECT id_data FROM dim_datas WHERE ano < 2023);"
```

---

## 📞 Suporte

### Verificar Versão

```bash
python --version
pip show pandas flask
```

### Relatório de Sistema

```bash
# Windows
systeminfo | findstr "OS Version"

# Linux/WSL
uname -a
```

### Contato

Em caso de problemas, consulte os logs completos:

```bash
# Log do scheduler do último backup
cat /z/git/rotina/log/scheduler_com_dw.log | tail -100

# Log de erro
grep "✗" /z/git/rotina/log/data_warehouse.log
```

---

## 📄 Licença e Disclaimer

Este projeto foi desenvolvido para análise de dados e backup automático. Usado como está, sem garantias.

**Requisitos:**
- Python 3.6+
- Pandas, Flask, openpyxl
- Acesso à rede Z:\
- Windows 7+ ou Linux/WSL

**Compatibilidade:**
- ✅ Git Bash
- ✅ PowerShell
- ✅ WSL/WSL2
- ✅ Linux nativo (com caminhos ajustados)

---

## 🎓 Próximas Melhorias

- [ ] Dashboard web com gráficos
- [ ] Alertas por email para falhas
- [ ] Sincronização com Google Sheets
- [ ] Machine Learning para detecção de anomalias
- [ ] Backup incremental (apenas deltas)
- [ ] Criptografia de dados sensíveis
- [ ] Replicação em nuvem (Azure/AWS)

---

**Última atualização:** 2026-03-29
**Versão:** 1.0
**Status:** ✅ Produção
