# 📊 UML/MER v2.0 - Integration Summary

**Data:** 2026-04-01  
**Status:** ✅ COMPLETO - Pronto para Consulta  
**Documento Principal:** [UML_MER_DIAGRAMAS.md](UML_MER_DIAGRAMAS.md)

---

## 🎯 O que foi atualizado

### Phase 1: MER (Entity Relationship Diagram) ✅
**Mudança**: 7 entidades → **11 entidades** (4 novas)

#### Novas Entidades Adicionadas:
1. **dim_sincronizacao** - Rastreia tipos e status de sincronizações
   - id_sincronizacao (PK)
   - tipo_sync (UK): "local→rede", "rede→local", "validação", etc.
   - status: "iniciando", "sucesso", "falha", "skip"
   - timestamp

2. **dim_repositorios** - Mapeia localizações de storage
   - id_repositorio (PK)
   - caminho_local (UK): C:\Users\recep2\Documents\git\analise_py\DATAWAREHOUSE
   - caminho_rede (UK): Z:\git\rotina
   - tipo_repositorio: enum(local, rede)

3. **fato_sincronizacoes** - Registra cada operação de sincronização
   - id_sync (PK), id_backup (FK), id_data (FK)
   - origem, destino (caminhos)
   - status, tempo_ms, arquivo_count
   - hash_local, hash_remoto (para validação)

4. **fato_versoes_arquivo** - Rastreia evolução de arquivos
   - id_versao (PK), id_arquivo, id_repositorio (FK)
   - versao (número incremental)
   - hash (MD5 desta versão)
   - data_criacao, origem_repo

#### Novos Relacionamentos (3):
- **1:N** dim_sincronizacao → fato_backups
- **1:N** fato_backups → fato_sincronizacoes
- **1:N** dim_repositorios → fato_versoes_arquivo

#### Extensões Existentes:
- auditoria_processamento agora tem campo opcional: **id_sincronizacao (FK)**

---

### Phase 2: Use Cases (UML) ✅
**Mudança**: 4 casos → **8 casos** (4 NOVOS + 2 ESTENDIDOS)

#### Novos Casos de Uso:
1. **UC5: Sincronizar Arquivos (LOCAL ↔ REDE)**
   - Ator: Sistema de Sincronização
   - Duty: Detectar mudanças → Calcular hash → Copiar com shutil.copy2 → Registrar
   - Timing: Pós-ETL OU a cada 30 minutos
   - Registra em: `fato_sincronizacoes`

2. **UC6: Validar Integridade de Sincronização**
   - Ator: Monitor de Sincronização
   - Duty: Comparar hashes local vs remoto → Re-sincronizar se mismatch
   - Timing: 30min pós-sincronização
   - Registra em: `auditoria_processamento` + `fato_sincronizacoes`

3. **UC7: Versionar Arquivo**
   - Ator: Gestor de Versões (Git)
   - Duty: Criar entrada em fato_versoes_arquivo → Git commit → Git tag
   - Timing: Imediatamente pós-sincronização bem-sucedida
   - Formato tag: `v{YYYY}_{MM}_{DD}_{HHMM}` ex: v2026_04_01_1730

4. **UC8: Disponibilizar Backup em API**
   - Ator: API de Backup Automático
   - Duty: POST webhook → Notificar aplicações externas
   - Timing: Em tempo real após UC5 completar
   - Payload: { backup_id, data, registros_inseridos, status, timestamp }

#### Casos Estendidos:
- **UC2 (Processar Backup)**: Agora inclui passos 6-9 (sync → validar → versionar → webhook)
- **UC4 (Auditar)**: Agora registra id_sincronizacao quando aplicável

#### Novos Atores (5):
- 🆕 **Sistema de Sincronização** - Orquestra tudo
- 🆕 **Repositório em Rede** - Z:\git\rotina\
- 🆕 **Monitor de Sincronização** - Valida hash
- 🆕 **Gestor de Versões** - Git tracking
- 🆕 **API de Backup Automático** - Webhooks

---

### Phase 3: Component Diagram ✅
**Mudança**: 5 componentes → **8 componentes** (3 novos)

#### Novos Componentes:
1. **SyncManager** (new layer)
   - Métodos: detectar_mudancas(), calcular_hash(), copiar_para_rede(), registrar_sync()
   - Usa: Pandas, SQLite, shutil, hashlib

2. **NetworkRepository** (new layer)
   - Interface para Z:\git\rotina\
   - Features: Centralized storage, shared access, redundancy, version history

3. **VersionControl** (new layer)
   - Integração com Git
   - Operações: commit, tag, push, version tracking, rollback support

#### Fluxo de Componentes Atualizado:
```
Apps → API REST → DataWarehouse + SyncManager + VersionControl
          ↓
      Business Logic
          ↓
      Data Access (Pandas, SQLite, File Ops)
          ↓
      Local Storage + Network Repository (Git)
```

---

### Phase 4: Data Flow Diagram ✅
**Mudança**: 7 estágios → **10 estágios** (3 NOVOS)

#### Pipeline Completo:
1. **FONTE DE DADOS** - Z:\01.FO_Tejo\ (rede)
2. **SCHEDULER** - 17:00:00 (time-based trigger)
3. **ETL EXTRACT** - Ler arquivos Excel
4. **ETL TRANSFORM** - Normalizar dados
5. **ETL LOAD** - Inserir em SQLite local
6. **DATA WAREHOUSE** - SQLite atualizado
7. 🆕 **SYNC MANAGER** - Detectar mudanças → Calcular hash → Copiar
8. 🆕 **REPOSITÓRIO EM REDE** - Z:\git\rotina\ (dados replicados)
9. 🆕 **VALIDAÇÃO + VERSIONAMENTO** - Hash check + Git tracking
10. **NOTIFICAÇÕES E CONSULTA** - Webhook + Apps notificadas

#### Sub-fluxos Detalhados:
- **Sub-fluxo A: Sincronização em Tempo Real** (parte de UC5)
- **Sub-fluxo B: Validação de Integridade** (parte de UC6)
- **Sub-fluxo C: Versionamento com Git** (parte de UC7)

#### Timing Ciclo Completo:
```
[17:00:00] Scheduler inicia
   ↓ (30s)
[17:00:30] DW local completo
   ↓ (20s)
[17:00:50] Sync para rede completo
   ↓ (10s)
[17:01:00] Hash validation OK
   ↓ (15s)
[17:01:15] Git tag criada
   ↓ (15s)
[17:01:30] Apps notificadas ✓
```

---

## 📊 Estatísticas Completas (v2.0)

| Artefato | v1.0 | v2.0 | Mudança |
|----------|------|------|---------|
| **Entidades MER** | 7 | 11 | +4 (+57%) |
| **Relacionamentos** | 8 | 11 | +3 (+38%) |
| **Casos de Uso** | 4 | 8 | +4 (+100%) |
| **Atores** | 7 | 12 | +5 (+71%) |
| **Componentes** | 5 | 8 | +3 (+60%) |
| **Estágios Data Flow** | 7 | 10 | +3 (+43%) |
| **Sub-fluxos** | 0 | 3 | +3 (nova seção) |
| **Tempo Ciclo** | ~60s | ~90s | +30s (sync) |
| **Localizações** | 1 | 2 | +1 (rede) |
| **Linhas Doc.** | ~500 | ~1.200 | +700 linhas |

---

## 🔍 Arquivos Atualizados

### Principal
- ✅ **[UML_MER_DIAGRAMAS.md](UML_MER_DIAGRAMAS.md)** (1.200+ linhas)
  - MER v2.0 (11 entidades)
  - Use Cases v2.0 (8 casos)
  - Components v2.0 (8 componentes)
  - Data Flow v2.0 (10 estágios + 3 sub-fluxos)
  - RACI matrix atualizada
  - Roadmap para próximas fases

### Relacionados
- [MODELO_ENTIDADE_RELACIONAMENTO.md](MODELO_ENTIDADE_RELACIONAMENTO.md) - Referência para extensão
- [SCHEMA_SQL_COMPLETO.sql](SCHEMA_SQL_COMPLETO.sql) - (A ser atualizado com novo schema v2.0)
- [DEPENDENCY_CHAIN.md](DEPENDENCY_CHAIN.md) - Mostra deps de componentes

---

## 🚀 Próximas Fases (Implementação)

### Phase 2B: Criar SyncManager (não neste plano)
```python
# C:\Users\recep2\Documents\git\analise_py\DATAWAREHOUSE\DEV_ENVIRONMENT\sync_manager.py
class SyncManager:
    def detectar_mudancas(self, pasta_local, pasta_rede):
        # Comparar timestamps e hashes
        pass
    
    def copiar_para_rede(self, arquivo):
        # shutil.copy2 com registro
        pass
    
    def registrar_sync(self, origem, destino, status):
        # Insert em fato_sincronizacoes
        pass
```

### Phase 2C: Criar MonitorSincronizacao (não neste plano)
```python
# C:\Users\recep2\Documents\git\analise_py\DATAWAREHOUSE\DEV_ENVIRONMENT\monitor_sincronizacao.py
class MonitorSincronizacao:
    def validar_integridade(self, arquivo):
        # Compara hash local vs fato_versoes_arquivo
        pass
    
    def corrigir_mismatch(self, arquivo):
        # Refaz cópia se necessário
        pass
```

### Phase 2D: Integrar Git Hooks
```bash
# .git/hooks/post-commit
# Registra automaticamente em fato_versoes_arquivo
```

### Phase 3: Power BI Dashboard
- Visualizar status de sincronizações
- Alertas de mismatches
- Histórico de versões

---

## ✅ Verificação

- [x] MER com 11 entidades e 11+ relacionamentos
- [x] 8 casos de uso com fluxos completos (principals + alternativo + pré/pós)
- [x] 12 atores documentados com responsabilidades
- [x] 8 componentes com dependências mapeadas
- [x] 10 estágios de data flow + 3 sub-fluxos
- [x] RACI matrix com responsabilidades claras
- [x] Diagrama renderizável em GitHub/VS Code (Markdown)
- [x] Vocabulário consistente entre artefatos
- [x] Rastreabilidade: ator → UC → entidades → componentes
- [x] Roadmap de próximas fases documentado
- [x] Status version 2.0 marcado como PRONTO PARA IMPLEMENTAÇÃO

---

## 📝 Como Usar Este Documento

1. **Para Entender a Arquitetura**: Começar por [UML_MER_DIAGRAMAS.md](UML_MER_DIAGRAMAS.md) seção "Componentes do Sistema"

2. **Para Implementar Novos Casos**: Consultar tabela de Casos de Uso → MER → Componentes

3. **Para Debug**: Seguir Data Flow diagrama estágio por estágio

4. **Para Visão de Negócio**: Ver Matriz RACI e Component Diagram

5. **Para Desenvolvimento**: Ver código references nos UC5-8 (SyncManager, Git, shutil, etc)

---

**Criador:** GitHub Copilot  
**Versão:** 2.0 - Integrated Synchronization & Repository Layer  
**Status:** ✅ PRONTO PARA IMPLEMENTAÇÃO  
**Próxima Revisão:** 2026-04-15  
**Mantém:** Compatibilidade com v1.0 (nada foi removido, apenas estendido)
