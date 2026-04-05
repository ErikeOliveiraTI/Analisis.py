# 📊 Modelo Entidade Relacionamento - Data Warehouse

**Data Warehouse - Sistema de Backup com ETL Pipeline**

---

## 🎯 Visão Geral

O modelo relacional foi projetado em **3ª Forma Normal (3NF)** para:
- ✅ Eliminar redundância de dados
- ✅ Garantir integridade referencial
- ✅ Otimizar performance de consultas
- ✅ Facilitar manutenção e atualizações

---

## 📐 Arquitetura do Modelo

### Camadas

```
┌─────────────────────────────────────┐
│   DIMENSÕES (Lookup Tables)         │
├─────────────────────────────────────┤
│  • dim_datas (calendário)           │
│  • dim_tipos_arquivo                │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      FATOS (Fact Tables)            │
├─────────────────────────────────────┤
│  • fato_backups                     │
│  • fato_caixa                       │
│  • fato_relatorios                  │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│    AUDITORIA (Transact Tables)      │
├─────────────────────────────────────┤
│  • auditoria_processamento          │
└─────────────────────────────────────┘
```

---

## 📋 Tabelas Dimensionais

### **DIM_DATAS** (Dimensão Temporal)

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| **id_data** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **data** | DATE | Data em formato YYYY-MM-DD | UK (Unique), NOT NULL |
| **dia** | INTEGER | Dia do mês (1-31) | NOT NULL |
| **mes** | INTEGER | Mês (1-12) | NOT NULL |
| **ano** | INTEGER | Ano | NOT NULL |
| **mes_nome** | TEXT | Nome do mês em texto (JAN, FEV...) | NOT NULL |
| **dia_semana** | TEXT | Nome do dia (SEGUNDA, TERÇA...) | NOT NULL |
| **criado_em** | TIMESTAMP | Data de criação | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
```sql
CREATE INDEX idx_datas_data ON dim_datas(data);
```

**Exemplo de dados:**
```
id_data | data       | dia | mes | ano  | mes_nome | dia_semana | criado_em
--------|------------|-----|-----|------|----------|------------|-------------------
1       | 2024-01-01 | 1   | 1   | 2024 | JAN      | SEGUNDA    | 2024-01-01 00:00:00
2       | 2024-01-02 | 2   | 1   | 2024 | JAN      | TERÇA      | 2024-01-02 00:00:00
```

---

### **DIM_TIPOS_ARQUIVO** (Dimensão de Tipos)

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| **id_tipo** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **tipo_arquivo** | TEXT | Tipo do arquivo (caixa, relatorio, etc) | UK, NOT NULL |
| **descricao** | TEXT | Descrição do tipo | |
| **criado_em** | TIMESTAMP | Data de criação | DEFAULT CURRENT_TIMESTAMP |

**Exemplo de dados:**
```
id_tipo | tipo_arquivo | descricao
--------|--------------|------------------------------------
1       | caixa        | Arquivo de Caixa (Caixa.xlsx)
2       | relatorio    | Arquivos de Relatórios
```

---

## 📊 Tabelas de Fatos

### **FATO_BACKUPS** (Log de Backups)

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| **id_backup** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **id_data** | INTEGER | FK para DIM_DATAS | FK, NOT NULL |
| **id_tipo** | INTEGER | FK para DIM_TIPOS_ARQUIVO | FK, NOT NULL |
| **nome_arquivo** | TEXT | Nome do arquivo processado | NOT NULL |
| **caminho_arquivo** | TEXT | Caminho completo do arquivo | NOT NULL |
| **hash_arquivo** | TEXT | Hash SHA256 para detecção de duplicatas | NOT NULL |
| **num_linhas** | INTEGER | Número de linhas no arquivo | NOT NULL |
| **num_colunas** | INTEGER | Número de colunas | NOT NULL |
| **status** | TEXT | Status do processamento (sucesso, erro) | NOT NULL |
| **criado_em** | TIMESTAMP | Data de processamento | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
```sql
CREATE INDEX idx_backups_data ON fato_backups(id_data);
```

**Exemplo de dados:**
```
id_backup | id_data | id_tipo | nome_arquivo    | hash_arquivo | num_linhas | status
-----------|---------|---------|-----------------|--------------|------------|--------
1          | 1       | 1       | Caixa.xlsx      | abc123...    | 1250       | sucesso
2          | 1       | 2       | Rel_Jan.xlsx    | def456...    | 850        | sucesso
```

---

### **FATO_CAIXA** (Detalhado - Transações de Caixa)

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| **id_caixa** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **id_backup** | INTEGER | FK para FATO_BACKUPS | FK |
| **id_data** | INTEGER | FK para DIM_DATAS | FK, NOT NULL |
| **data_operacao** | DATE | Data da operação | |
| **descricao** | TEXT | Descrição da transação | |
| **valor_entrada** | DECIMAL(12,2) | Valor de entrada (crédito) | |
| **valor_saida** | DECIMAL(12,2) | Valor de saída (débito) | |
| **saldo** | DECIMAL(12,2) | Saldo da operação | |
| **metodo_pagamento** | TEXT | Método (Dinheiro, Cartão, etc) | |
| **referencia_externa** | TEXT | Referência de comprovação | |
| **criado_em** | TIMESTAMP | Data de inserção | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
```sql
CREATE INDEX idx_caixa_data ON fato_caixa(id_data);
```

**Exemplo de dados:**
```
id_caixa | id_data | descricao          | valor_entrada | valor_saida | saldo   | metodo_pagamento
---------|---------|-------------------|---------------|-------------|---------|------------------
1        | 1       | Entrada Inicial    | 5000.00       | NULL        | 5000.00 | Dinheiro
2        | 1       | Compra Material    | NULL          | 250.50      | 4749.50 | Cartão Débito
3        | 1       | Venda Produto      | 1200.00       | NULL        | 5949.50 | PIX
```

---

### **FATO_RELATORIOS** (Sumário - Relatórios Processados)

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| **id_relatorio** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **id_backup** | INTEGER | FK para FATO_BACKUPS | FK |
| **id_data** | INTEGER | FK para DIM_DATAS | FK, NOT NULL |
| **nome_relatorio** | TEXT | Nome do relatório | NOT NULL |
| **tipo_relatorio** | TEXT | Tipo (vendas, estoque, etc) | |
| **total_registros** | INTEGER | Qtd de linhas no relatório | NOT NULL |
| **valor_total** | DECIMAL(15,2) | Valor total (se aplicável) | |
| **periodo_inicio** | DATE | Data inicial do período | |
| **periodo_fim** | DATE | Data final do período | |
| **criado_em** | TIMESTAMP | Data de processamento | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
```sql
CREATE INDEX idx_relatorios_data ON fato_relatorios(id_data);
```

**Exemplo de dados:**
```
id_relatorio | nome_relatorio    | tipo        | total_registros | valor_total | periodo_inicio
--------------|------------------|-------------|-----------------|-------------|---------------
1              | Rel_Vendas_Jan   | vendas      | 542             | 125000.00   | 2024-01-01
2              | Rel_Estoque      | estoque     | 1250            | 85500.00    | 2024-01-01
```

---

## 🔍 Tabela de Auditoria

### **AUDITORIA_PROCESSAMENTO** (Rastreabilidade)

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| **id_auditoria** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **id_backup** | INTEGER | FK para FATO_BACKUPS | FK |
| **id_data** | INTEGER | FK para DIM_DATAS | FK |
| **tipo_operacao** | TEXT | Tipo (INSERT, UPDATE, DELETE, EXTRACT) | NOT NULL |
| **descricao** | TEXT | Descrição da operação | |
| **status** | TEXT | Status (sucesso, erro, aviso) | NOT NULL |
| **tempo_processamento_ms** | INTEGER | Tempo em milissegundos | |
| **erro_mensagem** | TEXT | Mensagem de erro (se houver) | |
| **data_processamento** | TIMESTAMP | Quando foi processado | DEFAULT CURRENT_TIMESTAMP |

**Exemplo de dados:**
```
id_auditoria | tipo_operacao | status | tempo_ms | erro_mensagem
-------------|---------------|--------|----------|----------------
1            | EXTRACT       | sucesso| 245      | NULL
2            | TRANSFORM     | sucesso| 512      | NULL
3            | INSERT_CAIXA  | sucesso| 1200     | NULL
```

---

## 🔗 Chaves e Relacionamentos

### Chaves Primárias (PK)

| Tabela | Coluna | Tipo |
|--------|--------|------|
| DIM_DATAS | id_data | INTEGER AUTOINCREMENT |
| DIM_TIPOS_ARQUIVO | id_tipo | INTEGER AUTOINCREMENT |
| FATO_BACKUPS | id_backup | INTEGER AUTOINCREMENT |
| FATO_CAIXA | id_caixa | INTEGER AUTOINCREMENT |
| FATO_RELATORIOS | id_relatorio | INTEGER AUTOINCREMENT |
| AUDITORIA_PROCESSAMENTO | id_auditoria | INTEGER AUTOINCREMENT |

### Chaves Estrangeiras (FK)

```
FATO_BACKUPS → DIM_DATAS (id_data)
FATO_BACKUPS → DIM_TIPOS_ARQUIVO (id_tipo)
FATO_CAIXA → FATO_BACKUPS (id_backup)
FATO_CAIXA → DIM_DATAS (id_data)
FATO_RELATORIOS → FATO_BACKUPS (id_backup)
FATO_RELATORIOS → DIM_DATAS (id_data)
AUDITORIA_PROCESSAMENTO → FATO_BACKUPS (id_backup)
AUDITORIA_PROCESSAMENTO → DIM_DATAS (id_data)
```

### Chaves Únicas (UK)

```
DIM_DATAS.data (não repetir mesma data)
DIM_TIPOS_ARQUIVO.tipo_arquivo (tipos únicos)
```

---

## 📈 Normalized Form (3NF)

### Eliminação de Anomalias

**1ª Forma Normal (1NF):**
- ✅ Todos os valores são atômicos (indivisíveis)
- ✅ Sem repetição de grupos
- ✅ Cada linha tem uma chave primária

**2ª Forma Normal (2NF):**
- ✅ 1NF + Dependência funcional completa
- ✅ Todos os atributos não-chave dependem da chave primária inteira
- ✅ Sem dependência parcial

**3ª Forma Normal (3NF):**
- ✅ 2NF + Sem dependência transitiva
- ✅ Sem dados derivados
- ✅ Máxima normalização para OLTP

---

## 🎯 Padrões de Design

### Star Schema
```
                    DIM_DATAS
                        ↓
    DIM_TIPOS_ARQUIVO → FATO_BACKUPS ← FATO_CAIXA
                        ↑
                   FATO_RELATORIOS
```

### Dimensão de Tempo
- ✅ Suporta análises por período
- ✅ Facilita JOIN com outras tabelas
- ✅ Permite pré-cálculos de agregações

### Fatos Granulares
- ✅ FATO_CAIXA: detalhe máximo (cada transação)
- ✅ FATO_RELATORIOS: agregado (sumário)
- ✅ FATO_BACKUPS: metadados de processamento

---

## 🔐 Integridade de Dados

### Integridade Referencial
```sql
-- Todas as FKs precisam de PK existente
-- SQLite com FOREIGN KEYS habilitadas
PRAGMA foreign_keys = ON;
```

### Validação de Dados
- ✅ Tipos de dados estritos (VARCHAR, DECIMAL, DATE)
- ✅ NOT NULL em campos críticos
- ✅ UNIQUE em dados sensíveis
- ✅ DEFAULT VALUES para timestamps

### Auditoria
- ✅ Todos os INSERTs registrados
- ✅ Tempo de processamento rastreado
- ✅ Erros capturados

---

## 📊 Estatísticas Esperadas

| Tabela | Linhas/Dia | Crescimento | Tamanho (6 meses) |
|--------|------------|-------------|-------------------|
| DIM_DATAS | 1 | 365/ano | ~360 linhas |
| FATO_BACKUPS | 2-5 | 60-150/mês | ~600 linhas |
| FATO_CAIXA | 1000-5000 | 30K-150K/mês | ~500K linhas |
| FATO_RELATORIOS | 10-50 | 300-1500/mês | ~5K linhas |
| AUDITORIA | 5-10 | 150-300/mês | ~3K linhas |

---

## 🚀 Índices para Performance

```sql
-- Dimensões (Lookups)
CREATE INDEX idx_datas_data ON dim_datas(data);
CREATE INDEX idx_tipos_arquivo ON dim_tipos_arquivo(tipo_arquivo);

-- Fatos (joins e filtros)
CREATE INDEX idx_backups_data ON fato_backups(id_data);
CREATE INDEX idx_caixa_data ON fato_caixa(id_data);
CREATE INDEX idx_caixa_operacao ON fato_caixa(data_operacao);
CREATE INDEX idx_relatorios_data ON fato_relatorios(id_data);

-- Auditoria (filtering)
CREATE INDEX idx_auditoria_backup ON auditoria_processamento(id_backup);
```

---

## 🔄 Fluxo de ETL vs Modelo

```
BACKUP FILES (Caixa.xlsx, Relatórios)
     ↓
[EXTRACT] → Pandas DataFrame
     ↓
[TRANSFORM] → Normalizar, limpar, validar
     ↓
[LOAD] → Inserir em Tabelas
     ↓
MODELO RELACIONAL ATUALIZADO
     ↓
[QUERY] → API REST / PowerQuery / BI Tools
```

---

## 📋 Casos de Uso de Consultas

### Caso de Uso 1: Resumo Diário de Caixa
```sql
SELECT 
    d.data,
    COUNT(*) as num_operacoes,
    SUM(fc.valor_entrada) as total_entrada,
    SUM(fc.valor_saida) as total_saida,
    SUM(fc.valor_entrada) - SUM(fc.valor_saida) as saldo_diario
FROM fato_caixa fc
JOIN dim_datas d ON fc.id_data = d.id_data
WHERE d.data = DATE('now')
GROUP BY d.data;
```

### Caso de Uso 2: Auditoria de Processamento
```sql
SELECT 
    d.data,
    fb.nome_arquivo,
    ap.tipo_operacao,
    ap.status,
    ap.tempo_processamento_ms,
    ap.erro_mensagem
FROM auditoria_processamento ap
JOIN fato_backups fb ON ap.id_backup = fb.id_backup
JOIN dim_datas d ON ap.id_data = d.id_data
ORDER BY ap.data_processamento DESC
LIMIT 100;
```

### Caso de Uso 3: Análise de Período
```sql
SELECT 
    d.mes_nome,
    d.ano,
    COUNT(*) as operacoes,
    SUM(fc.valor_entrada) as entrada_total,
    SUM(fc.valor_saida) as saida_total
FROM fato_caixa fc
JOIN dim_datas d ON fc.id_data = d.id_data
WHERE d.ano = 2024
GROUP BY d.mes, d.ano, d.mes_nome
ORDER BY d.ano, d.mes;
```

---

## 🎯 Conclusão

Este modelo relacional oferece:
- ✅ Escalabilidade
- ✅ Integridade referencial
- ✅ Rastreabilidade completa
- ✅ Performance otimizada
- ✅ Facilidade de manutenção

**Versão:** 1.0  
**Status:** Production-Ready ✅
