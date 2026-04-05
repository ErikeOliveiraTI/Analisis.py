# 🎯 GUIA DE INÍCIO RÁPIDO - Data Warehouse

**Data:** 29/03/2026 | **Status:** ✅ Pronto para Produção

---

## ⚡ 5 Minutos para Começar

### Passo 1: Instalar (1 min)

```bash
pip install -r requirements.txt
```

### Passo 2: Iniciar Scheduler (1 min)

```bash
# Terminal 1 - Executa backup às 17:00
python scheduler_com_dw.py
```

Verá logs como:
```
[2026-03-29 14:30:00] ✓ SCHEDULER COM DATA WAREHOUSE INICIALIZADO
[2026-03-29 14:30:00] Horário de backup: 17:00
[2026-03-29 14:30:05] Aguardando horário de backup...
```

### Passo 3: Iniciar API (1 min)

```bash
# Terminal 2 - Inicializa servidor REST
python api_rest.py
```

Verá:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Passo 4: Testar (1 min)

```bash
# Terminal 3 - Consultar dados
curl "http://localhost:5000/api/caixa"
curl "http://localhost:5000/status"
```

### Passo 5: Automático (1 min)

Copiar para Startup do Windows (opcional):
```
C:\Users\recep2\AppData\Microsoft\Windows\Start Menu\Programs\Startup\
```

Cole aqui:
- `iniciar_agendador.bat`
- `iniciar_agendador_background.bat` (alternativa silenciosa)

---

## 📦 O Que Foi Criado

### 🆕 5 Novos Arquivos (Principais)

| Arquivo | Tamanho | Função |
|---------|--------|--------|
| **data_warehouse.py** | ~700 linhas | Motor ETL completo |
| **api_rest.py** | ~500 linhas | API REST com 7 endpoints |
| **scheduler_com_dw.py** | ~400 linhas | Scheduler integrado |
| **test_data_warehouse.py** | ~450 linhas | Suite de testes |
| **config_avancada.py** | ~300 linhas | Configurações centralizadas |

### 📖 3 Documentos (Referência)

| Arquivo | Tempo de Leitura |
|---------|-----------------|
| **README_PT.md** | 10 min |
| **DOCUMENTACAO_DATAWAREHOUSE.md** | 30 min |
| **requirements.txt** | 1 min |

**Total:** ~3000 linhas de código + documentação

---

## 🔌 Endpoints Disponíveis

### Health & Status

```bash
GET /health
GET /status
```

### Consultar Dados (GET)

```bash
GET /api/caixa                          # Todos os dados
GET /api/caixa?data_inicio=2024-01-01&data_fim=2024-01-31  # Filtrado
GET /api/resumo-diario?data=2024-01-13 # Resumo
GET /api/relatorios                     # Listare latórios
```

### Processar & Atualizar (POST)

```bash
POST /api/processar-backup              # Processar backup de um dia
POST /api/consulta-customizada          # SQL avançada
```

---

## 📊 Estrutura do Banco de Dados

```
data_warehouse.db (SQLite)
│
├─ dim_datas                 (Dimensão: datas)
├─ dim_tipos_arquivo         (Dimensão: tipos de arquivo)
│
├─ fato_backups              (Fatos: cada backup processado)
├─ fato_caixa                (Fatos: transações de caixa)
├─ fato_relatorios           (Fatos: relatórios processados)
│
└─ auditoria_processamento   (Auditoria: log de ETL)
```

**Padrão:** 3ª Forma Normal (3NF) - Dados normalizados e estruturados

---

## 🔄 Fluxo Automático

```
┌─────────────────────┐
│  17:00 do dia       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ backup_rede.bash    │ ◄─ Executa (já existia)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ scheduler_com_dw.py │ ◄─ NOVO: Processa automaticamente
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │              │
     ▼              ▼
┌─────────┐   ┌──────────────┐
│ Extrai  │   │ Normaliza    │ ◄─ NOVO: ETL
│ Excel   │   │ Dados        │
└─────────┘   └──────────────┘
     │              │
     └──────┬───────┘
            │
            ▼
┌──────────────────────┐
│ Carrega no Banco     │
│ data_warehouse.db    │ ◄─ NOVO: SQLite centralizado
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ API REST disponível  │ ◄─ NOVO: Endpoints GET/POST
│ http://localhost:5000│
└──────────────────────┘
```

---

## 🎮 Exemplos de Uso

### Exemplo 1: Consultar Caixa de Hoje

```bash
curl "http://localhost:5000/api/caixa?data_inicio=$(date +%Y-%m-%d)"
```

### Exemplo 2: Ver Resumo de Um Dia Específico

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

### Exemplo 3: Processar Backup Manual

```bash
curl -X POST http://localhost:5000/api/processar-backup \
  -H "Content-Type: application/json" \
  -d '{"data_pasta": "13 JAN"}'
```

### Exemplo 4: Análise em Python

```python
from data_warehouse import DataWarehouse
import pandas as pd

dw = DataWarehouse()

# Consultar janeiro
df = dw.consultar_caixa('2024-01-01', '2024-01-31')

# Análises
print(f"Total de registros: {len(df)}")
print(f"Total de entrada: R$ {df['valor_entrada'].sum():.2f}")

# Agrupar por método
print(df.groupby('metodo_pagamento')['valor_entrada'].sum())
```

---

## ⚙️ Configuração Rápida

### Mudar Horário (Default: 17:00)

**Arquivo:** `scheduler_com_dw.py`

```python
HORA_BACKUP = 17  # Mudar para desejado (0-23)
```

### Mudar Porta da API (Default: 5000)

**Arquivo:** `api_rest.py`, final do arquivo:

```python
app.run(host='0.0.0.0', port=5000)  # Mudar porta aqui
```

### Mudar Intervalo de Verificação (Default: 30s)

**Arquivo:** `scheduler_com_dw.py`

```python
INTERVALO_VERIFICACAO = 30  # Mudar para X segundos
```

---

## 📋 Checklist de Verificação

**Antes de usar em produção:**

- [ ] `pip install -r requirements.txt` ✅
- [ ] Pasta `/z/git/rotina/` existe
- [ ] Arquivo de origem `/z/01.FO_Tejo/02.Night_Auditor/Caixa.xlsx` existe
- [ ] Backup antigo (`backup_rede.bash`) funciona
- [ ] `python scheduler_com_dw.py` inicia sem erros
- [ ] `python api_rest.py` inicia na porta 5000
- [ ] `curl http://localhost:5000/health` responde 200
- [ ] `python test_data_warehouse.py` passa com sucesso
- [ ] Logs criados em `/z/git/rotina/log/`

---

## 🚨 Se Algo Não Funcionar

### 1. Erro: "ModuleNotFoundError"

```bash
pip install pandas openpyxl flask flask-cors
```

### 2. API não responde

```bash
# Windows: verificar se porta 5000 está em uso
netstat -ano | findstr :5000

# Matar processo (se necessário)
taskkill /PID <PID> /F
```

### 3. Banco de dados travado

```bash
# Fechar todas as conexões Python
# Deletar o arquivo (recriará ao iniciar)
del /z/git/rotina/data_warehouse.db

# Reiniciar scheduler
python scheduler_com_dw.py
```

### 4. Scheduler não executa

```bash
# Verificar logs em tempo real
tail -f /z/git/rotina/log/scheduler_com_dw.log

# Teste rápido (sem esperar 17:00)
python scheduler_com_dw.py --teste
```

---

## 📚 Documentação por Profundidade

| Nível | Documento | Tempo |
|-------|-----------|-------|
| 🟢 Iniciante | Este arquivo (GUIA_RAPIDO.md) | 5 min |
| 🟡 Intermediário | README_PT.md | 10 min |
| 🔴 Avançado | DOCUMENTACAO_DATAWAREHOUSE.md | 30 min |
| 🔴 Desenvolvedor | Código comentado (*.py) | 60 min |

---

## 🎓 Próximas Etapas

### Hoje ✅

1. Instalar dependências
2. Iniciar scheduler
3. Testar API
4. Validar logs

### Essa Semana

5. Executar em produção (deixar rodando)
6. Verificar backup automático 17:00
7. Consultar dados na API
8. Executar suite de testes

### Esse Mês

9. Criar dashboard web
10. Configurar alertas de email
11. Backup automático do banco
12. Documentar processos

---

## 📬 Suporte Rápido

### Verificar Status

```bash
# Todo funcionando?
curl http://localhost:5000/status

# Dados no banco?
sqlite3 /z/git/rotina/data_warehouse.db "SELECT COUNT(*) FROM fato_caixa;"

# Scheduler rodando?
ps aux | grep python | grep scheduler_com_dw
```

### Ver Logs

```bash
# Últimas 20 linhas
tail -20 /z/git/rotina/log/scheduler_com_dw.log

# Procurar erros
grep "✗" /z/git/rotina/log/*.log

# Em tempo real
tail -f /z/git/rotina/log/data_warehouse.log
```

### Testar Localmente

```bash
python scheduler_com_dw.py --teste
python test_data_warehouse.py
python -c "from data_warehouse import DataWarehouse; print('OK')"
```

---

## 🏆 Pronto!

Seu sistema está ready para:

✅ **Backup automático** diário às 17:00  
✅ **Normalização** de dados em 3FN  
✅ **Consultas** via Pandas  
✅ **API REST** para integração  
✅ **Auditoria** completa com logs  

**Próximo passo:** Iniciar scheduler e deixar rodando!

```bash
python scheduler_com_dw.py
```

---

**Desenvolvido com ❤️ | Versão 1.0 | Março 2026**

Para dúvidas, consulte:
- 📖 README_PT.md (overview)
- 📚 DOCUMENTACAO_DATAWAREHOUSE.md (detalhes)
- 💬 Comentários no código (implementação)
