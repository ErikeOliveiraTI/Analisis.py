# 📊 UML e MER - Data Warehouse System

## 📋 Índice
1. [Use Case Diagram (UML)](#use-case-diagram)
2. [Entity Relationship Diagram (ERD/MER)](#entity-relationship-diagram)
3. [Fluxo de Dados](#fluxo-de-dados)
4. [Componentes do Sistema](#componentes-do-sistema)

---

## Use Case Diagram

### Atores Principais (12 atores - v2.0 com integração de sincronização)

| Ator | Descrição | Responsabilidades |
|------|-----------|-------------------|
| **Usuário Final** | Pessoa que consulta dados | Fazer queries, gerar relatórios |
| **Sistema de Backup** | Automação de backup da rede | Copiar arquivos para Z:/ |
| **Scheduler** | Agendador automático | Ativar ETL diariamente |
| **Data Warehouse** | Sistema centralizado | Armazenar dados normalizados |
| **API REST** | Interface HTTP | Fornecer endpoints de consulta |
| **ETL Pipeline** | Motor de transformação | Extrair, transformar, carregar |
| **Banco de Dados** | SQLite | Persistência de dados |
| 🆕 **Sistema de Sincronização** | Orquestra sincronizações | Copiar entre local e rede |
| 🆕 **Repositório em Rede** | Storage centralizado | Armazenar dados compartilhados |
| 🆕 **Monitor de Sincronização** | Valida integridade | Detectar e corrigir divergências |
| 🆕 **Gestor de Versões** | Rastreador de mudanças | Manter histórico de versões |
| 🆕 **API de Backup Automático** | Interface de automação | Disparar backups via webhook |

### Casos de Uso

#### Use Case 1: Consultar Dados

**Ator:** Usuário Final

**Fluxo Principal:**
1. Usuário solicita consulta via API ou SQL
2. API valida requisição
3. Data Warehouse consulta banco
4. Resultados retornados em JSON/DataFrame

**Fluxo Alternativo:**
- Se dados não existem → Retorna vazio
- Se erro na consulta → Retorna mensagem de erro

**Pré-condição:** Dados já foram carregados no DW

**Pós-condição:** Dados retornados corretamente

---

#### Use Case 2: Processar Backup

**Ator:** Scheduler

**Fluxo Principal:**
1. Scheduler detecta hora 17:00
2. Executa script de backup
3. Copia arquivos de Z:/ para pasta do dia
4. ETL inicia processamento
5. Dados carregados no Data Warehouse
6. Auditoria registra sucesso

**Fluxo Alternativo:**
- Se arquivo não existe → Log warning
- Se erro na transformação → Log error
- Se falta disk space → Cancelar e registrar erro

**Pré-condição:** Scheduler está rodando

**Pós-condição:** Banco atualizado com novos dados ou erro registrado

---

#### Use Case 3: Normalizar Dados

**Ator:** ETL Pipeline

**Fluxo Principal:**
1. Extrair arquivo Excel
2. Validar estrutura (colunas esperadas)
3. Remover acentos dos nomes
4. Converter tipos de dados
5. Remover duplicatas
6. Aplicar business rules

**Fluxo Alternativo:**
- Se coluna falta → Criar com NULLs
- Se valores inválidos → Substituir por NULL
- Se duplicatas → Manter primeira ocorrência

**Pré-condição:** Arquivo foi extraído com sucesso

**Pós-condição:** DataFrame normalizado pronto para carregar

---

#### Use Case 4: Auditar Processamento

**Ator:** Sistema de Auditoria

**Fluxo Principal:**
1. Cada operação ETL registra início
2. Registra tempo de execução
3. Se sucesso → Registra "sucesso"
4. Se erro → Registra erro e mensagem
5. Timestamp de quando ocorreu
6. 🆕 Se envolveu sincronização → Registra id_sincronizacao

**Pré-condição:** Operação ETL foi executada

**Pós-condição:** Registro de auditoria criado com rastreamento de sync (se aplicável)

---

#### 🆕 Use Case 5: Sincronizar Arquivos (LOCAL ↔ REDE)

**Ator:** Sistema de Sincronização

**Fluxo Principal:**
1. Detectar modificação em pasta local (`C:\Users\recep2\Documents\git\analise_py\DATAWAREHOUSE\`)
2. Calcular hash MD5 do arquivo local
3. Comparar com versão em rede (`Z:\git\rotina\data_warehouse.db`)
4. Se diferente:
   - Copiar arquivo para rede (usando `shutil.copy2`)
   - Registrar em `fato_sincronizacoes`
   - Log: `[YYYY-MM-DD HH:MM:SS] SYNC OK: arquivo_name (hash_local → hash_rede)`
5. Se idêntico:
   - Log: `[YYYY-MM-DD HH:MM:SS] SKIP: arquivo_name (já sincronizado)`

**Fluxo Alternativo:**
- Se erro de permissão → Log warning, retry em próximo ciclo
- Se arquivo em uso → Log warning, pular arquivo
- Se disco cheio em Z:\ → Log error, cancelar sincronização

**Pré-condição:** Pasta local foi modificada após último backup

**Pós-condição:** Arquivo replicado em rede E `fato_sincronizacoes` registrado

**Timing:** A cada 30 minutos OU depois de ETL completo

---

#### 🆕 Use Case 6: Validar Integridade de Sincronização

**Ator:** Monitor de Sincronização

**Fluxo Principal:**
1. Carregar última sincronização registrada em `fato_sincronizacoes`
2. Comparar hash local com hash em `fato_versoes_arquivo`
3. Se mismatch detectado:
   - Recalcular hash do arquivo local
   - Re-sincronizar para rede com `shutil.copy2`
   - Log warning: `[YYYY-MM-DD HH:MM:SS] MISMATCH CORRIGIDO: arquivo_name`
   - Registrar nova entrada em `fato_sincronizacoes` com status "corrigido"
4. Se sucesso (hashes iguais):
   - Log info: `[YYYY-MM-DD HH:MM:SS] VALIDACAO OK: arquivo_name`

**Fluxo Alternativo:**
- Se erro persistente após 3 tentativas → Escalate para auditoria
- Se arquivo deletado → Registrar remoção em `fato_sincronizacoes`

**Pré-condição:** Sincronização foi concluída

**Pós-condição:** Status de integridade verificado E auditado

**Timing:** Diariamente após 17:30 (pós-backup)

---

#### 🆕 Use Case 7: Versionar Arquivo

**Ator:** Gestor de Versões (Git + Manual)

**Fluxo Principal:**
1. Detectar novo arquivo ou mudança significativa em arquivo existente
2. Criar entrada em `fato_versoes_arquivo`:
   - id_arquivo (gerado automaticamente)
   - versao = contador incremental (1, 2, 3...)
   - hash = MD5 do arquivo nesta versão
   - data_criacao = timestamp atual
   - origem_repo = origem (local ou rede)
3. Se usando Git:
   - Commit automático: `git commit -m "v{YYYY_MM_DD_HHMM}: arquivo_name"`
   - Tag: `git tag -a v2026_04_01_1700 -m "Sincronização de 01 APR 17:00"`
4. Log: `[YYYY-MM-DD HH:MM:SS] VERSAO {numero} REGISTRADA: arquivo_name`

**Fluxo Alternativo:**
- Se versão já existe (mesmo hash) → Skip versionamento
- Se arquivo deletado → Registrar versão "deletada"

**Pré-condição:** Arquivo foi sincronizado com sucesso

**Pós-condição:** Versão registrada em `fato_versoes_arquivo` E Git tag criada

**Timing:** Imediatamente após sincronização bem-sucedida

---

#### 🆕 Use Case 8: Disponibilizar Backup em API

**Ator:** API de Backup Automático

**Fluxo Principal:**
1. Sincronização completada (UC5 sucesso)
2. API dispara webhook ou notificação
3. Verificar se dados estão prontos em SQLite
4. POST `/api/webhook/backup-completo`:
   ```json
   {
     "backup_id": 12345,
     "data": "2026-04-01",
     "tipo_backup": "Caixa + Relatorios",
     "registros_inseridos": 15,
     "timestamp": "2026-04-01T17:30:45Z",
     "status": "sucesso"
   }
   ```
5. Aplicações consumidoras recebem notificação
6. Status em `fato_sincronizacoes`: "disponível para API"

**Fluxo Alternativo:**
- Se dados incompletos → Webhook com status "parcial"
- Se erro na sincronização → Webhook com status "falha"

**Pré-condição:** Sincronização completada E dados carregados no DW

**Pós-condição:** Aplicações externas notificadas de novos dados disponíveis

**Timing:** Em tempo real após UC5 completar

---

#### 🔄 Use Case 2 (ESTENDIDO): Processar Backup - com Sincronização

**Fluxo Modificado (v2.0):**
1. Scheduler detecta hora 17:00
2. Executa script de backup
3. Copia arquivos de Z:/ para pasta do dia
4. ETL inicia processamento
5. Dados carregados no Data Warehouse
6. 🆕 **Sistema de Sincronização inicia UC5** (Sincronizar dados para rede)
7. 🆕 **Monitor de Sincronização inicia UC6** (Validar integridade)
8. 🆕 **Gestor de Versões inicia UC7** (Registrar versões)
9. 🆕 **API dispara UC8** (Notificar aplicações)
10. Auditoria registra sucesso INCLUINDO id_sincronizacao

**Pós-condição:** Backup completo COM replicação em rede, versionamento e notificações

---

## Entity Relationship Diagram

### Visão Geral (11 Entidades - Star Schema com Synchronization Layer)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DIMENSÕES (4 tabelas)                          │
├─────────────────────────────────────────────────────────────────────┤
│ dim_datas           dim_tipos_arquivo    dim_sincronizacao         │
│ ├─ id_data (PK)     ├─ id_tipo (PK)      ├─ id_sincronizacao (PK) │
│ ├─ data (UK)        ├─ tipo_arquivo (UK) ├─ tipo_sync (UK)        │
│ ├─ dia, mes, ano    └─ descricao         ├─ status                │
│ └─ mes_nome                              └─ timestamp             │
│                                                                       │
│                    dim_repositorios                                 │
│                    ├─ id_repositorio (PK)                          │
│                    ├─ caminho_local (UK)                           │
│                    ├─ caminho_rede (UK)                            │
│                    └─ tipo_repositorio                             │
└──────────────────────────────────────┬─────────────────────────────┘
                                       │
                                       ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   CENTRO (Hub - fato_backups)                        │
├──────────────────────────────────────────────────────────────────────┤
│  ├─ id_backup (PK)                                                  │
│  ├─ id_data (FK) → dim_datas                                        │
│  ├─ id_tipo (FK) → dim_tipos_arquivo                                │
│  ├─ id_sincronizacao (FK opt) → dim_sincronizacao                   │
│  ├─ nome_arquivo, caminho_arquivo                                   │
│  ├─ hash_arquivo, num_linhas, num_colunas                           │
│  └─ status                                                           │
└──────┬────────────────┬──────────────────┬──────────────┬────────────┘
       │                │                  │              │
       ↓                ↓                  ↓              ↓
  ┌──────────┐   ┌─────────────┐   ┌──────────────┐   ┌────────────┐
  │fato_caixa│   │fato_relatos │   │fato_sincrons │   │fato_versoes│
  ├─────────┤   ├────────────┤   ├─────────────┤   ├───────────┤
  │id_caixa  │   │id_rel      │   │id_sync (PK) │   │id_versao  │
  │id_backup │   │id_backup   │   │id_backup(FK)│   │id_arquivo │
  │id_data   │   │id_data     │   │id_data (FK) │   │id_reposit │
  │data_op   │   │nome_rel    │   │origem       │   │versao(num)│
  │descr     │   │total_reg   │   │destino      │   │hash       │
  │val_entr  │   │valor_tot   │   │status       │   │data_criacao
  │val_saida │   │periodo     │   │tempo_ms     │   │origem_repo│
  │saldo     │   │(sumário)   │   │arquivo_count│   └────────────┘
  │metodo    │   └────────────┘   └─────────────┘
  │refer     │
  └──────────┘
       │
       ↓
  ┌──────────────────────┐
  │auditoria_processamento
  ├────────────────────┤
  │id_auditoria (PK)   │
  │id_backup (FK)      │
  │id_data (FK)        │
  │id_sincronizacao(FK)│ ← NEW LINK TO SYNC
  │tipo_operacao       │
  │status              │
  │tempo_ms            │
  │erro_msg            │
  └────────────────────┘
```

### Relacionamentos (11 relacionamentos documentados)

#### ✅ RELACIONAMENTOS ORIGINAIS (mantidos de versão anterior)

#### 1:N - dim_datas → fato_backups
- Uma data pode ter vários backups
- Cada backup ocorre em uma data específica

#### 1:N - dim_tipos_arquivo → fato_backups
- Um tipo de arquivo pode ter vários backups
- Cada backup é de um tipo específico

#### 1:N - fato_backups → fato_caixa
- Um backup pode gerar várias transações de caixa
- Cada transação é originária de um backup

#### 1:N - fato_backups → fato_relatorios
- Um backup pode conter vários relatórios
- Cada relatório é originário de um backup

#### 1:N - fato_backups → auditoria_processamento
- Um backup é auditado em várias operações
- Cada auditoria é ligada a uma operação de backup

#### 1:N - dim_datas → fato_caixa
- Uma data pode ter várias transações
- Cada transação ocorre em uma data

#### 1:N - dim_datas → fato_relatorios
- Uma data pode ter vários relatórios
- Cada relatório é de uma data

#### 1:N - dim_datas → auditoria_processamento
- Uma data pode ter várias auditorias
- Cada auditoria é registrada em uma data

---

#### 🆕 NOVOS RELACIONAMENTOS (Synchronization Layer - v2.0)

#### 1:N - dim_sincronizacao → fato_backups
- Uma configuração de sincronização pode desencadear vários backups
- Cada backup pode estar associado a um tipo de sincronização
- **Exemplo**: Sincronização "local→rede" dispara backup automático
- **Uso**: Rastrear qual tipo de sync originou qual backup

#### 1:N - fato_backups → fato_sincronizacoes
- Um backup pode conter várias operações de sincronização
- Cada sincronização está relacionada a um backup específico
- **Exemplo**: Um backup de 01 APR sincroniza Caixa.xlsx + Relatórios (2 sincronizações)
- **Uso**: Detalhar quais arquivos foram sincronizados em cada backup
- **Cardinalidade**: 1 backup : N sincronizações (1:N)

#### 1:N - dim_repositorios → fato_versoes_arquivo
- Um repositório pode ter múltiplas versões de arquivos
- Cada versão de arquivo é originária de um repositório
- **Exemplo**: Repositório "Z:\\git\\rotina" tem 50 versões de Caixa.xlsx
- **Uso**: Rastrear evolução de arquivos entre local e rede
- **Cardinalidade**: 1 repositório : N versões (1:N)

#### 0:1 - dim_sincronizacao → auditoria_processamento (OPCIONAL)
- Uma sincronização pode ter múltiplas auditorias de processamento
- Cada auditoria pode registrar uma sincronização específica
- **Exemplo**: Sync de Caixa.xlsx gera 1 auditoria "cópia" + 1 auditoria "validação hash"
- **Uso**: Auditoria detalhada de cada operação de sincronização
- **Cardinalidade**: 0 ou 1 sincronização : N auditorias (0|1:N)

---

## Fluxo de Dados

### 🔄 Fluxo Completo: Backup → ETL → DW → SYNC → REDE (v2.0)

#### Fluxo Principal (9 Estágios)

```
┌─ ESTÁGIO 1: FONTE DE DADOS ─┐
│  Z:\01.FO_Tejo\02.Night_Auditor\Relatorios_e_Ficheiros\
│  ├─ Caixa.xlsx
│  ├─ Relatorios_e_Ficheiros/
│  │  ├─ Rel_Vendas.xlsx
│  │  ├─ Rel_Estoque.xlsx
│  │  └─ ...
│  └─ (outros arquivos)
└────────────────┬────────────────────────────────────────────┘
                 │ UC2: Backup acionado em 17:00
                 ↓
┌─ ESTÁGIO 2: SCHEDULER (Time-based trigger) ─┐
│ ⏰ Detectar 17:00:00 todos os dias
│ └─ python scheduler_com_dw.py
└────────────┬──────────────────────────────────────────────┘
             │
             ↓
┌─ ESTÁGIO 3: ETL EXTRACT ─┐
│ 📂 Ler arquivos
│ ├─ pd.read_excel(Caixa.xlsx)
│ ├─ pd.read_excel(Rel_*.xlsx)
│ └─ (retorna DataFrames)
└────────────┬──────────────────────────────────────────────┘
             │
             ↓
┌─ ESTÁGIO 4: ETL TRANSFORM ─┐
│ 🔧 Normalizar dados
│ ├─ Remover acentos: "Descrição" → "descricao"
│ ├─ Converter tipos: "100.00" (str) → 100.00 (float)
│ ├─ Remover duplicatas
│ ├─ Validar e limpar
│ └─ (business rules)
└────────────┬──────────────────────────────────────────────┘
             │
             ↓
┌─ ESTÁGIO 5: ETL LOAD ─┐
│ 💾 Inserir no banco
│ ├─ INSERT INTO fato_caixa (...)
│ ├─ INSERT INTO fato_relatorios (...)
│ ├─ INSERT INTO fato_sincronizacoes (init)
│ ├─ INSERT INTO auditoria_processamento (...)
│ └─ COMMIT
└────────────┬──────────────────────────────────────────────┘
             │
             ↓
┌─ ESTÁGIO 6: DATA WAREHOUSE (LOCAL) ─┐
│ 🏢 SQLite Database
│ Location: C:\...\DATAWAREHOUSE\DEV_ENVIRONMENT\data_warehouse.db
│ Synced to: Z:\git\rotina\data_warehouse.db
│ ├─ dim_datas (atualizada)
│ ├─ fato_backups (novo registro)
│ ├─ fato_caixa (novos registros)
│ ├─ fato_relatorios (novos registros)
│ ├─ 🆕 fato_sincronizacoes (status="iniciando")
│ ├─ 🆕 fato_versoes_arquivo (preparado)
│ └─ auditoria_processamento (logs)
└────────────┬──────────────────────────────────────────────┘
             │ UC5: Sincronizar iniciado
             ↓
┌─ 🆕 ESTÁGIO 7: SYNC MANAGER ─┐
│ 🔄 Sincronizar Local → Rede
│ ├─ Detectar mudanças em:
│ │  ├─ C:\...\DATAWAREHOUSE\DEV_ENVIRONMENT\data_warehouse.db
│ │  ├─ Relatórios processados
│ │  └─ Logs e metadados
│ │
│ ├─ Para cada arquivo:
│ │  1. Calcular hash MD5 (local)
│ │  2. Comparar com Z:\git\rotina\data_warehouse.db
│ │  3. Se diferente → Copiar com shutil.copy2
│ │  4. Registrar em fato_sincronizacoes
│ │
│ └─ Log: [2026-04-01 17:30:15] SYNC: data_warehouse.db
└────────────┬──────────────────────────────────────────────┘
             │
             ↓
┌─ 🆕 ESTÁGIO 8: REPOSITÓRIO EM REDE ─┐
│ 💾 Z:\git\rotina\ (Storage centralizado)
│ ├─ Z:\git\rotina\data_warehouse.db (atualizado)
│ ├─ Z:\git\rotina\01 APR\ (pasta do dia)
│ ├─ Z:\git\rotina\log\sync_2026-04-01.log (novo)
│ └─ 🆕 Status de sincronização registrado
└────────────┬──────────────────────────────────────────────┘
             │ UC6: Validar integridade
             │ UC7: Versionar arquivo
             ↓
┌─ 🆕 ESTÁGIO 9: VALIDAÇÃO + VERSIONAMENTO ─┐
│ ✅ Monitor de Sincronização (UC6)
│ ├─ Comparar hash local vs rede
│ ├─ Se mismatch → Re-sincronizar
│ └─ Log: [2026-04-01 17:31:00] VALIDACAO OK
│
│ 📝 Gestor de Versões (UC7)
│ ├─ Criar entrada fato_versoes_arquivo
│ ├─ Git commit: "v2026_04_01_1730: data_warehouse.db"
│ ├─ Git tag: v2026_04_01_1730
│ └─ Log: [2026-04-01 17:31:30] VERSAO 145 REGISTRADA
└────────────┬──────────────────────────────────────────────┘
             │ UC8: Webhook
             ↓
┌─ ESTÁGIO 10: NOTIFICAÇÕES E CONSULTA ─┐
│ 🔔 API de Backup Automático dispara webhook
│ POST /webhook/backup-completo
│
│ 📊 Aplicações Consumidoras
│ ├─ Python: dw.consultar_caixa()
│ ├─ API REST: GET /api/caixa?data=2026-04-01
│ ├─ SQL: SELECT * FROM fato_caixa WHERE data='2026-04-01'
│ ├─ Power BI: Conexão direta (refresh automático)
│ └─ Excel: Power Query (novos dados disponíveis)
└─────────────────────────────────────────────────────────┘
      Ciclo completo = ~90 segundos
      17:00:00 (start) → 17:01:30 (fim)
```

---

#### 🆕 Sub-fluxo A: Sincronização em Tempo Real

**Trigger**: Após ETL LOAD bem-sucedido OR a cada 30 minutos

```
UC5: Sincronizar Arquivos
├─ 1. Detectar modificação em C:\...\ DATAWAREHOUSE\
├─ 2. Calcular hash MD5 (local)
├─ 3. Comparar com Z:\git\rotina\ (remoto)
├─ 4a. Se DIFERENTE:
│   ├─ Copiar arquivo (shutil.copy2)
│   ├─ Registrar fato_sincronizacoes (status="sucesso")
│   └─ continue
├─ 4b. Se IDÊNTICO:
│   ├─ Skip cópia
│   ├─ Registrar fato_sincronizacoes (status="skip")
│   └─ continue
└─ 5. Log: [YYYY-MM-DD HH:MM:SS] SYNC {status}: {arquivo}

Logs: /z/git/rotina/log/sync_2026-04-01.log
```

---

#### 🆕 Sub-fluxo B: Validação de Integridade

**Trigger**: 30 minutos após sincronização OR manualmente via API

```
UC6: Validar Integridade de Sincronização
├─ 1. Carregar última sync de fato_sincronizacoes
├─ 2. Recuperar hash de fato_versoes_arquivo
├─ 3. Recalcular hash do arquivo local (agora)
├─ 4a. Se hashes IGUAIS:
│   ├─ Log info: [YYYY-MM-DD] VALIDACAO OK
│   └─ continue
├─ 4b. Se hashes DIFERENTES:
│   ├─ RE-SINCRONIZAR (voltar a UC5)
│   ├─ Registrar novo fato_sincronizacoes (reconhecimento)
│   ├─ Log WARNING: [YYYY-MM-DD] MISMATCH CORRIGIDO
│   └─ continue
└─ 5. Atualizar auditoria_processamento com resultado

Frequência: Daily post-backup (17:30)
Retry: Até 3x se falhar (exponential backoff)
```

---

#### 🆕 Sub-fluxo C: Versionamento com Git

**Trigger**: Imediatamente após UC5 bem-sucedido

```
UC7: Versionar Arquivo
├─ 1. Detectar modificação em arquivo
├─ 2. Criar entrada fato_versoes_arquivo:
│   ├─ id_arquivo = FK do arquivo
│   ├─ versao = contador (1, 2, 3...)
│   ├─ hash = MD5 desta versão
│   ├─ data_criacao = NOW()
│   └─ origem_repo = "local" ou "rede"
├─ 3. Git operations (if enabled):
│   ├─ git add . (somar mudanças)
│   ├─ git commit -m "v{TIMESTAMP}: {arquivo}"
│   ├─ git tag -a v2026_04_01_1730 -m "Sync de 01 APR"
│   └─ git push (se remoto configurado)
├─ 4. Log: [YYYY-MM-DD HH:MM:SS] VERSAO {num} REGISTRADA: {arquivo}
└─ 5. Registrar fato_sincronizacoes (status="versionado")

Tags formato: v{YYYY}_{MM}_{DD}_{HHMM}
Commits: "[AUTO] {timestamp}: {num} arquivo(s) sincronizado(s)"
```

---

#### 🔄 Ciclo Completo de Integração

```
[17:00:00] Scheduler detecta hora backup
   ↓
[17:00:05] Ler arquivos da rede (EXTRACT)
   ↓
[17:00:10] Normalizar dados (TRANSFORM)
   ↓
[17:00:15] Inserir em SQLite local (LOAD)
   ↓
[17:00:30] DW local atualizado
   ↓
[17:00:31] 🆕 SyncManager inicia (UC5)
   ↓
[17:00:50] Arquivos copiados para Z:\git\rotina\
   ↓
[17:01:00] 🆕 Monitor valida (UC6) - hashes OK
   ↓
[17:01:15] 🆕 Gestor cria versão (UC7) - Git tag criada
   ↓
[17:01:30] 🆕 API webhook dispara (UC8) - Apps notificadas
   ↓
[17:01:35] Ciclo concluído - Pronto para consultas
```

---

## Componentes do Sistema

### 🎯 Component Diagram (v2.0 com Synchronization & Repository Layer)

```
┌────────────────────────────────────────────────────────────────────┐
│                   APLICAÇÕES CONSUMIDORAS                          │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐│
│  │  Python  │  │ Power BI │  │  Excel w/PQ  │  │  Aplicações  ││
│  │  Scripts │  │ Desktop  │  │              │  │  Externas    ││
│  └──────────┘  └──────────┘  └──────────────┘  └──────────────┘│
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ↓ (consume endpoints)
┌────────────────────────────────────────────────────────────────────┐
│                    API REST LAYER                                  │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Flask API - Port 5000                                       │ │
│  │  GET  /api/caixa                                             │ │
│  │  GET  /api/resumo-diario                                     │ │
│  │  GET  /api/versoes-arquivo                                   │ │
│  │  POST /api/processar-backup                                  │ │
│  │  POST /api/sincronizar-agora                        🆕       │ │
│  │  POST /api/consulta-customizada                              │ │
│  │  POST /webhook/backup-completo                      🆕       │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────┬───────────────────┬──────────────────┬────────────────────┘
        │                   │                  │
        ↓                   ↓                  ↓
┌───────────────┐   ┌─────────────┐   ┌──────────────────┐
│   DataWare    │   │  SyncManager│   │ VersionControl   │
│   house       │   │     🆕      │   │     (Git) 🆕     │
│   Component   │   └─────────────┘   └──────────────────┘
├─────────────────┤   ├─────────────┤   ├──────────────────┤
│ Class Methods:  │   │ Métodos:    │   │ Operações:       │
│ • extrair_     │   │ • detectar_ │   │ • git commit     │
│   arquivo_    │   │   mudancas()│   │ • git tag        │
│   excel()      │   │ • calcular_ │   │ • git push       │
│ • normalizar_  │   │   hash()    │   │ • version        │
│   caixa()      │   │ • copiar_   │   │   tracking       │
│ • carregar_    │   │   para_rede()   │ • rollback       │
│   caixa()      │   │ • registrar │   │   suporte        │
│ • consultar_   │   │   sync()    │   └──────────────────┘
│   caixa()      │   ├─────────────┤
│ • processar_   │   │ Integrado   │
│   backup_      │   │ com:        │
│   diario()     │   │ • Pandas    │
│ • resumo_      │   │ • SQLite    │
│   diario()     │   │ • shutil    │
└─────────────────┘  └─────────────┘
        │                   │
        ├───────────┬───────┤
        │           │       │
        ↓           ↓       ↓
┌←─────────────────────────────────────→┐
│   BUSINESS LOGIC LAYER (ESTENDIDO)    │
├───────────────────────────────────────┤
│                                       │
│  ┌───────────────────────────────┐   │
│  │  ETL Pipeline + Scheduler     │   │
│  │  • executar_backup()          │   │
│  │  • processar_backup_no_dw()   │   │ ◄── Orquestra
│  │  • executar_indefinidamente() │   │     tudo
│  │  • verificar_hora_backup()    │   │
│  └───────────────────────────────┘   │
│                                       │
└───────────────┬───────────────────────┘
                │
                ↓
┌────────────────────────────────────────────────────────────────────┐
│               DATA ACCESS & STORAGE LAYER                          │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │  Pandas      │  │  SQLite 3    │  │  File Ops        │        │
│  │  DataFrame   │  │  Connection  │  │  • shutil.copy2  │        │
│  │  Operations  │  │  & Queries   │  │  • hashlib (MD5) │        │
│  │              │  │              │  │  • pathlib       │        │
│  └──────────────┘  └──────────────┘  └──────────────────┘        │
└─────────┬──────────────┬────────────────┬───────────────────────────┘
          │              │                │
          ↓              ↓                ↓
┌─────────────────────┬──────────────────────────────────┐
│   DATA LAYER        │  NETWORK REPOSITORY (🆕)        │
├─────────────────────┼──────────────────────────────────┤
│ SQLite Database     │ Z:\git\rotina\                   │
│ (LOCAL)             │ ├─ data_warehouse.db (SYNCED)    │
│                     │ ├─ {DD MMM}\ (backup folders)   │
│ C:\...\DATAWAREHOUSE│ ├─ log\                          │
│ \DEV_ENVIRONMENT\   │ │  ├─ backup_*.log             │
│ data_warehouse.db   │ │  ├─ sync_*.log       🆕       │
│                     │ │  └─ scheduler.log             │
│ Tabelas:            │ └─ .git\ (version history) 🆕   │
│ • 4 dimensões       │                                  │
│ • 4 fatos           │ Features:                        │
│ • 1 auditoria       │ • Centralized storage            │
│ • 4 views           │ • Shared access (rede)           │
│                     │ • Redundancy/backup              │
│                     │ • Version history (fato_versoes) │
└─────────────────────┴──────────────────────────────────┘
```

---

### 🔗 Relacionamentos entre Componentes (Data Flow)

```
┌─ TRIGGER (17:00:00) ─────────────────────────────────┐
│  Scheduler verifica hora                             │
└─────────────┬────────────────────────────────────────┘
              │ calls
              ↓
┌─ EXTRACTION ──────────────────────────────────────────┐
│  DataWarehouse.extrair_arquivo_excel(pasta_dia)      │
│  → Retorna: Caixa + Relatórios (DataFrames)          │
└─────────────┬────────────────────────────────────────┘
              │ data passed
              ↓
┌─ TRANSFORMATION ──────────────────────────────────────┐
│  DataWarehouse.normalizar_caixa(df)                  │
│  DataWarehouse.normalizar_relatorios(df)             │
│  → Retorna: DataFrames limpos (3NF)                  │
└─────────────┬────────────────────────────────────────┘
              │ data passed
              ↓
┌─ LOADING ─────────────────────────────────────────────┐
│  DataWarehouse.carregar_caixa(df_limpo)              │
│  DataWarehouse.carregar_relatorios(df_limpo)         │
│  → Executa: INSERT + FK validation + COMMIT          │
│  → Cria: auditoria_processamento record              │
└─────────────┬────────────────────────────────────────┘
              │ database persisted
              ↓
┌─ SYNCHRONIZATION 🆕 ─────────────────────────────────┐
│  SyncManager.detectar_mudancas()                     │
│  → Lista arquivos alterados em local                 │
│  SyncManager.copiar_para_rede()                      │
│  → Copia para Z:\git\rotina\ via shutil              │
│  → Registra em: fato_sincronizacoes                  │
└─────────────┬────────────────────────────────────────┘
              │ files replicated
              ↓
┌─ VALIDATION 🆕 ───────────────────────────────────────┐
│  Monitor.validar_integridade()                       │
│  → Compara hash local vs remoto                      │
│  → Se mismatch: refaz cópia                          │
│  → Registra resultado em auditoria                   │
└─────────────┬────────────────────────────────────────┘
              │ integrity verified
              ↓
┌─ VERSIONING 🆕 ────────────────────────────────────────┐
│  VersionControl.registrar_versao()                   │
│  → Cria entry em fato_versoes_arquivo               │
│  → Git commit + tag: v2026_04_01_1730               │
│  → Logs para auditoria                               │
└─────────────┬────────────────────────────────────────┘
              │ version tracked
              ↓
┌─ NOTIFICATION 🆕 ──────────────────────────────────────┐
│  API.webhook_backup_completo()                       │
│  → POST para aplicações externas                     │
│  → Status: "sucesso + {num_registros} sincronizad"   │
│  → Analytics/Monitoring systems updated              │
└─────────────┬────────────────────────────────────────┘
              │ external apps notified
              ↓
┌─ QUERY READY ──────────────────────────────────────────┐
│  DataWarehouse pronto para consultas                 │
│  • Python: dw.consultar_caixa(data='2026-04-01')    │
│  • API: GET /api/caixa?data=2026-04-01              │
│  • Power BI: Nova data disponível (auto-refresh)    │
│  • Excel: Power Query detecta atualização            │
└────────────────────────────────────────────────────────┘
```

---

## Matriz RACI - Responsabilidades (v2.0 com Synchronization)

| Ator | Backup | ETL | DW | Sync | Rede | Versão | API | Auditoria |
|------|--------|-----|----|----|------|--------|-----|-----------|
| Usuário Final | - | - | C | - | - | - | R | C |
| Scheduler | R,A | R,A | S | - | - | - | - | S |
| Sistema Backup | R | S | - | - | - | - | - | - |
| ETL Pipeline | - | R,A | R | S | - | - | S | A |
| API REST | - | - | S | S | - | - | R,A | S |
| 🆕 SyncManager | - | - | - | R,A | R | S | - | A |
| 🆕 Monitor Sync | - | - | - | S | S | - | - | R |
| 🆕 VersionControl | - | - | - | - | S | R,A | - | S |
| 🆕 API Webhook | - | - | - | - | - | - | R,A | - |
| Database Admin | - | - | R,A | S | - | - | - | S |

**Ordem de precedência**:
- **R**esponsible: Faz o trabalho (quem executa)
- **A**ccountable: Aprova (quem aprova/valida)
- **C**onsulted: Consultado (quem aconselha)
- **S**upported: Suporta (quem ajuda)

**Key Changes v2.0:**
- SyncManager é R,A para Sync (orquestra tudo)
- Monitor é R para validação (garante integridade)
- VersionControl é R,A para versionamento
- API Webhook é R,A para notificações

---

## 🎯 Conclusão

Esta arquitetura v2.0 oferece:

✅ **Separação de Responsabilidades**
- Cada componente tem função clara
- Facilita manutenção e testes
- 🆕 Sincronização como camada separada (não misturando com ETL)

✅ **Escalabilidade**
- Dimensões de tempo para crescimento
- Fatos granulares para detalhes
- 🆕 Suporte a múltiplos repositórios (local + rede + Git)

✅ **Rastreabilidade Completa**
- Auditoria de ETL operations
- 🆕 Rastreamento de sincronizações (fato_sincronizacoes)
- 🆕 Histórico de versões (fato_versoes_arquivo)
- Registro de erros e avisos

✅ **Flexibilidade**
- Múltiplas formas de consulta (Python, API, SQL, Power BI)
- Fácil adicionar novas fontes
- 🆕 Webhook notifications para aplicações externas

✅ **Performance**
- Índices estratégicos em chaves
- Views para operações comuns
- 3NF para integridade referencial
- 🆕 Hash caching para validação rápida de sincronização

✅ **Redundância & Disaster Recovery**
- 🆕 Dados sincronizados em duas localidades (C:\ + Z:\)
- 🆕 Git history para rollback de versões
- 🆕 Auditoria de todas as mudanças

✅ **Automatização Integrada**
- Backup automático 17:00
- 🆕 Sincronização automática pós-ETL
- 🆕 Validação automática 30min pós-sync
- 🆕 Webhook notifications para terceiros

---

## 📊 Estatísticas da Arquitetura v2.0

| Aspecto | Versão 1.0 | Versão 2.0 | Mudança |
|--------|-----------|-----------|---------|
| **Entidades MER** | 7 | 11 | +4 (2 dim + 2 fatos) |
| **Relacionamentos** | 8 | 11 | +3 (sync layer) |
| **Casos de Uso** | 4 | 8 | +4 (UC5-8) |
| **Atores Principais** | 7 | 12 | +5 novos |
| **Estágios Data Flow** | 7 | 10 | +3 (sync/validate/version) |
| **Componentes** | 5 | 8 | +3 (Sync/Versioning/API) |
| **Tempo Ciclo** | ~60s | ~90s | +30s (sync integrado) |
| **Localizações Storage** | 1 (local) | 2 | +1 (rede) |

---

## 🔄 Roadmap de Próximas Fases

### ✅ COMPLETO (Fase 1: Diagramas)
- [x] MER estendido (11 entidades)
- [x] Use Cases ampliados (8 casos)
- [x] Component diagram atualizado
- [x] Data Flow com 10 estágios
- [x] Sub-fluxos de sincronização

### 🚀 PRÓXIMAS FASES (Não-neste-plano)
- **Fase 2B**: Criar `sync_manager.py` (orquestra sincronização)
- **Fase 2C**: Criar `monitor_sincronizacao.py` (validação)
- **Fase 2D**: Integrar Git hooks para `fato_versoes_arquivo`
- **Fase 3**: Implementar webhook notifications na API
- **Fase 4**: Power BI dashboards para sync monitoring

---

**Versão:** 2.0 - Integrated Synchronization & Repository Layer
**Status:** ✅ Diagramas Documentados - Pronto para Implementação
**Data Atualização:** 2026-04-01
**Próxima Revisão:** 2026-04-15
