# 🏗️ Data Warehouse - Sistema de Backup e Análise de Dados

**Versão:** 1.0 | **Status:** ✅ Produção | **Última atualização:** 29/03/2026

---

## 📌 O Que É Este Projeto?

Sistema integrado que automatiza o backup diário da rede `Z:\` e transforma os dados em um **Data Warehouse profissional** com:

✅ **Backup Automático** - Copia arquivos às 17:00 diariamente  
✅ **Normalização de Dados** - Padroniza e limpa os dados (3ª Forma Normal)  
✅ **Banco de Dados Centralizado** - SQLite com tabelas estruturadas  
✅ **API REST** - Endpoints GET/POST para consultas com Pandas  
✅ **Sem Privilégios Admin** - Usa Startup folder ao invés de Task Scheduler  

---

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o Scheduler (Executa Backup às 17:00)

**Opção A: Executar no Terminal**

```bash
# Git Bash / PowerShell
python scheduler_com_dw.py
```

**Opção B: Executar Automaticamente no Startup**

1. Copie `iniciar_agendador.bat` para:
   ```
   C:\Users\recep2\AppData\Microsoft\Windows\Start Menu\Programs\Startup
   ```
2. Reinicie o computador ou execute o atalho
3. O scheduler será iniciado automaticamente

### 3. Iniciar a API REST (em outro terminal)

```bash
python api_rest.py

# Acessível em: http://localhost:5000
```

### 4. Testar o Sistema

```bash
# Teste rápido (processa backup de hoje)
python scheduler_com_dw.py --teste

# Suite de testes
python test_data_warehouse.py

# Consumir API
curl "http://localhost:5000/api/caixa?data_inicio=2024-01-01"
```

---

## 📚 Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| **data_warehouse.py** | Motor ETL - Extração, Transformação, Carga |
| **api_rest.py** | API REST com endpoints GET/POST |
| **scheduler_com_dw.py** | Scheduler que executa backup + DW |
| **test_data_warehouse.py** | Suite de testes |
| **DOCUMENTACAO_DATAWAREHOUSE.md** | Documentação completa |
| **requirements.txt** | Dependências do projeto |

---

## 🔗 Endpoints da API

### GET - Consultas

```bash
# Todos os dados de caixa
curl "http://localhost:5000/api/caixa"

# Caixa filtrado por período
curl "http://localhost:5000/api/caixa?data_inicio=2024-01-01&data_fim=2024-01-31"

# Resumo diário consolidado
curl "http://localhost:5000/api/resumo-diario?data=2024-01-13"

# Lista de relatórios processados
curl "http://localhost:5000/api/relatorios"

# Status do DW
curl "http://localhost:5000/status"
```

### POST - Processar Dados

```bash
# Processar um backup de um dia específico
curl -X POST http://localhost:5000/api/processar-backup \
  -H "Content-Type: application/json" \
  -d '{"data_pasta": "13 JAN"}'

# Consulta SQL customizada (avançado)
curl -X POST http://localhost:5000/api/consulta-customizada \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM fato_caixa WHERE valor_entrada > ? ORDER BY data DESC",
    "parametros": [100.0]
  }'
```

---

## 📊 Consultando Dados com Pandas

```python
from data_warehouse import DataWarehouse
import pandas as pd

dw = DataWarehouse()

# Retorna DataFrame com dados de caixa
df = dw.consultar_caixa('2024-01-01', '2024-01-31')

# Análises rápidas
print(df.describe())
print(df.groupby('metodo_pagamento')['valor_entrada'].sum())

# Resumo diário
resumo = dw.resumo_diario('2024-01-13')
print(f"Saldo: R$ {resumo['saldo_final']:.2f}")
```

---

## 📂 Localização dos Dados

```
Z:\
├─ git\
│  ├─ rotina\                          ← Base do DW
│  │  ├─ 13 JAN\                       ← Pasta diária
│  │  │  ├─ Caixa.xlsx                 ← Arquivo principal
│  │  │  └─ relatorios\                ← Relatórios
│  │  ├─ data_warehouse.db             ← Banco de dados centralizado
│  │  └─ log\                          ← Logs de processamento
│  │     ├─ scheduler_com_dw.log
│  │     ├─ data_warehouse.log
│  │     └─ backup_YYYY-MM-DD.log
│  │
│  └─ init_\analise_py\                ← Projeto
│     ├─ data_warehouse.py
│     ├─ api_rest.py
│     ├─ scheduler_com_dw.py
│     └─ (outros arquivos)
│
└─ 01.FO_Tejo\
   └─ 02.Night_Auditor\
      ├─ Caixa.xlsx                    ← Origem do backup
      └─ Relatorios_e_Ficheiros\
```

---

## ⚙️ Configuração

### Mudar Horário do Backup

**Arquivo:** `scheduler_com_dw.py`, linha ~30

```python
class ConfigScheduler:
    HORA_BACKUP = 17        # Mudar de 17 para desejado (0-23)
    MINUTO_INICIO = 0
    MINUTO_FIM = 2
```

### Mudar Intervalo de Verificação

```python
INTERVALO_VERIFICACAO = 30  # Mudar de 30 para X segundos
```

---

## 📝 Logs

```bash
# Ver logs do scheduler em tempo real
tail -f /z/git/rotina/log/scheduler_com_dw.log

# Ver logs do Data Warehouse
tail -50 /z/git/rotina/log/data_warehouse.log

# Procurar erros
grep "✗ Erro" /z/git/rotina/log/*.log

# Arquivo de backup específico
cat /z/git/rotina/log/backup_2024-01-13.log
```

---

## 🧪 Testes

```bash
# Teste rápido do scheduler (sem esperar 17:00)
python scheduler_com_dw.py --teste

# Suite completa de testes
python test_data_warehouse.py

# Verificar banco de dados
python -c "from data_warehouse import DataWarehouse; dw = DataWarehouse(); print('✓ OK')"
```

---

## ⚠️ Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install pandas openpyxl flask flask-cors
```

### "O banco de dados está travado"

```bash
# Fechar todas as conexões Python
# Reabrir o scheduler
python scheduler_com_dw.py
```

### "Scheduler não executa às 17:00"

```bash
# Verificar se está rodando
tasklist | findstr python

# Checar logs
tail -20 /z/git/rotina/log/scheduler_com_dw.log

# Verificar hora do sistema
systeminfo | findstr "Hora"
```

### "Arquivo Caixa.xlsx não encontrado"

```bash
# Verificar se arquivo existe na rede
ls /z/git/rotina/13\ JAN/Caixa.xlsx

# Verificar permissões
icacls /z /grant %USERNAME%:F
```

---

## 🎯 Próximos Passos

1. **Dashboard Web** - Visualizar dados com gráficos
2. **Alertas** - Email automático em caso de falhas
3. **Sincronização Cloud** - Backup em Azure/AWS
4. **Machine Learning** - Detecção de anomalias
5. **Auditoria Avançada** - Logs completos com assinatura digital

---

## 📄 Estrutura do Banco de Dados

```sql
-- Tabelas Principais

dim_datas              -- Dimensão temporal (DIA, MÊS, ANO)
dim_tipos_arquivo     -- Tipos de arquivo (Caixa, Relatório, etc)

fato_backups          -- Registro central de backups
fato_caixa            -- Transações de caixa normalizadas
fato_relatorios       -- Resumo de relatórios
auditoria_processamento  -- Log de auditoria (ETL)
```

---

## 📞 Suporte

**Verificar versões instaladas:**

```bash
python --version
pip show pandas flask
```

**Listar todos os logs recentes:**

```bash
ls -lht /z/git/rotina/log/ | head -10
```

**Validar banco de dados:**

```bash
sqlite3 /z/git/rotina/data_warehouse.db ".schema"
sqlite3 /z/git/rotina/data_warehouse.db "SELECT COUNT(*) FROM fato_caixa;"
```

---

## 📖 Documentação Completa

Veja `DOCUMENTACAO_DATAWAREHOUSE.md` para:

- ✅ Guia detalhado de API
- ✅ Schema completo do banco de dados
- ✅ Exemplos avançados com Pandas
- ✅ Performance e otimização
- ✅ Troubleshooting detalhado
- ✅ Roadmap de melhorias

---

## ✅ Checklist de Verificação

- [ ] Dependências instaladas: `pip install -r requirements.txt`
- [ ] Base do DW existe: `Z:\git\rotina\`
- [ ] Pasta `log` existe: `Z:\git\rotina\log\`
- [ ] Arquivo de backup encontrado: `Z:\01.FO_Tejo\02.Night_Auditor\Caixa.xlsx`
- [ ] Scheduler rodando ou atalho no Startup
- [ ] API REST online: `http://localhost:5000/health`
- [ ] Banco de dados criado: `Z:\git\rotina\data_warehouse.db`
- [ ] Testes passando: `python test_data_warehouse.py`

---

## 📊 Diagrama de Fluxo

```
REDE (Z:\)
    ↓ (17:00 - Daily)
backup_rede.bash
    ↓
/z/git/rotina/DD MMM/
    ├─ Caixa.xlsx
    └─ relatorios/
    ↓
scheduler_com_dw.py
    ↓ (ETL: Extract → Transform → Load)
Data Warehouse ETL
    ↓
data_warehouse.db (SQLite)
    ↓ (HTTP API)
api_rest.py (Flask)
    ↓
Endpoints (GET/POST)
    ↓ (Pandas Queries)
Análise & Relatórios
```

---

## 🎓 Exemplos Práticos

### Exemplo 1: Consultar Caixa de Hoje

```python
from data_warehouse import DataWarehouse
from datetime import datetime

dw = DataWarehouse()
hoje = datetime.now().strftime("%Y-%m-%d")
df = dw.consultar_caixa(hoje, hoje)
print(f"Operações de hoje: {len(df)}")
print(df[['descricao', 'valor_entrada', 'valor_saida', 'saldo']])
```

### Exemplo 2: Total de Entradas por Método

```python
df = dw.consultar_caixa()
totais = df.groupby('metodo_pagamento')['valor_entrada'].sum()
print(totais)
```

### Exemplo 3: Processar Backup Manualmente

```python
resultado = dw.processar_backup_diario("13 JAN")
print(f"Status: {resultado['status']}")
print(f"Registros: {resultado['total_registros']}")
```

---

## 🔐 Segurança

- ✅ Sem privilégios administrativos necessários
- ✅ Banco de dados local (sem nuvem por padrão)
- ✅ API com validação de entrada
- ⚠️ TODO: Implementar autenticação
- ⚠️ TODO: Criptografia de dados sensíveis

---

## 📄 Licença

Desenvolvido para análise de dados e backup automático. Usado como está, sem garantias.

---

**Desenvolvido com ❤️ para automação de backup's**  
**Versão 1.0 - Março 2026**
