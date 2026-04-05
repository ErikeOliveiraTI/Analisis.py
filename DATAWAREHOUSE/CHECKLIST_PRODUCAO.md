# ✅ CHECKLIST - Deploy em Produção

**Data:** 29/03/2026 | **Versão:** 1.0

---

## 📋 PRÉ-DEPLOYMENT

### Preparação do Ambiente

- [ ] Python 3.6+ instalado
  ```bash
  python --version
  ```

- [ ] Dependências instaladas
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Diretórios criados
  ```bash
  mkdir -p /z/git/rotina/log
  mkdir -p /z/git/rotina/dados
  ```

- [ ] Permissões configuradas (Windows)
  ```bash
  icacls "Z:\git\rotina" /grant "%USERNAME%":F /T
  ```

### Validação de Conectividade

- [ ] Acesso à rede Z:\ confirmado
  ```bash
  ls /z/git/rotina/
  ```

- [ ] Arquivo de origem encontrado
  ```bash
  ls /z/01.FO_Tejo/02.Night_Auditor/Caixa.xlsx
  ```

- [ ] Backup antigo funciona
  ```bash
  bash /z/git/init_/analise_py/backup_rede.bash
  ```

### Testes Locais

- [ ] Suite de testes passa
  ```bash
  python test_data_warehouse.py
  ```

- [ ] Data Warehouse inicializa
  ```bash
  python -c "from data_warehouse import DataWarehouse; dw = DataWarehouse(); print('OK')"
  ```

- [ ] Scheduler testa sem erro
  ```bash
  python scheduler_com_dw.py --teste
  ```

- [ ] API inicia sem erro
  ```bash
  python api_rest.py  # Ctrl+C após startup
  ```

---

## 🚀 DEPLOYMENT

### 1. Iniciar Scheduler

**Opção A: Terminal Manual**

```bash
# Abrir Git Bash ou PowerShell com privilégios normais (SEM admin)
cd C:\Users\recep2\Documents\git\analise_py
python scheduler_com_dw.py
```

Aguardar logs de confirmação:
```
✓ SCHEDULER COM DATA WAREHOUSE INICIALIZADO
✓ Horário de backup: 17:00
✓ Sistema aguardando...
```

- [ ] Scheduler iniciado com sucesso

**Opção B: Startup Automático**

1. ```bash
   copy iniciar_agendador.bat "C:\Users\recep2\AppData\Microsoft\Windows\Start Menu\Programs\Startup\"
   ```

2. Reiniciar computador

3. Verificar se scheduler está rodando:
   ```bash
   tasklist | findstr python
   ```

- [ ] Atalho criado na pasta Startup
- [ ] Scheduler inicia automaticamente após reboot

### 2. Iniciar API REST (Opcional)

**Em terminal separado:**

```bash
cd C:\Users\recep2\Documents\git\analise_py
python api_rest.py
```

Aguardar:
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

- [ ] API iniciada na porta 5000

### 3. Validar Inicialização

```bash
# Verificar scheduler rodando
tasklist | findstr scheduler_com_dw.py

# Verificar API rodando
tasklist | findstr api_rest.py

# Testar conexão
curl http://localhost:5000/health
```

- [ ] Scheduler rodando
- [ ] API respondendo (se iniciada)
- [ ] Banco de dados criado

---

## 🧪 TESTES EM PRODUÇÃO

### Teste 1: Backup Automático (Sem Esperar 17:00)

```bash
python scheduler_com_dw.py --teste
```

Verificar output:
- ✅ Arquivo Caixa.xlsx encontrado
- ✅ Dados normalizados
- ✅ Registros carregados no banco
- ✅ Logs criados

- [ ] Teste rápido funcionou

### Teste 2: Consulta de Dados

```bash
curl "http://localhost:5000/api/caixa?limite=5"
```

Esperado: JSON com dados de caixa

- [ ] Consulta retorna dados

### Teste 3: Resumo Diário

```bash
curl "http://localhost:5000/api/resumo-diario?data=2024-01-13"
```

Esperado: JSON com resumo do dia

- [ ] Resumo disponível

### Teste 4: Monitorar Logs

```bash
tail -f /z/git/rotina/log/scheduler_com_dw.log
```

- [ ] Logs sendo gerados
- [ ] Sem erros críticos

---

## 📅 OPERAÇÃO DIÁRIA

### Antes das 17:00

- [ ] PC ligado
- [ ] Conexão com rede Z:\ ativa
- [ ] Scheduler rodando (verificar logs)

### Às 17:00

- [ ] Backup iniciado automaticamente
- [ ] Logs mostram processamento
- [ ] Banco de dados atualizado

### Após 17:00

- [ ] Logs finalizados com sucesso
- [ ] Próximo backup agendado para amanhã
- [ ] Dados consultáveis via API

### Diariamente

```bash
# Verificar últimas linhas de log
tail -20 /z/git/rotina/log/scheduler_com_dw.log

# Validar banco de dados
sqlite3 /z/git/rotina/data_warehouse.db "SELECT COUNT(*) FROM fato_caixa;"

# Testar API (se rodando)
curl http://localhost:5000/status
```

- [ ] Rotina executada
- [ ] Dados consistentes
- [ ] API respondendo

---

## 🚨 TROUBLESHOOTING

### Problema: Scheduler Não Inicia

**Diagnóstico:**

```bash
python scheduler_com_dw.py
# Verificar erro exato

python -c "from data_warehouse import DataWarehouse; print('OK')"
# Se falhar: falta dependency
```

**Solução:**

```bash
pip install --upgrade pandas flask openpyxl
python scheduler_com_dw.py
```

- [ ] Resolvido ou escalado

### Problema: Banco Travado

**Diagnóstico:**

```bash
# Verificar se banco existe
ls -l /z/git/rotina/data_warehouse.db

# Tentar leitura
sqlite3 /z/git/rotina/data_warehouse.db ".schema"
```

**Solução:**

```bash
# Matar todos os Python
taskkill /IM python.exe /F

# Aguardar 5 segundos

# Reiniciar scheduler
python scheduler_com_dw.py
```

- [ ] Resolvido ou escalado

### Problema: Arquivo Não Encontrado

**Diagnóstico:**

```bash
# Verificar pasta de backup
ls /z/git/rotina/13\ JAN/

# Verificar arquivo de origem
ls /z/01.FO_Tejo/02.Night_Auditor/Caixa.xlsx
```

**Solução:**

```bash
# Verificar permissões
icacls "Z:\git\rotina" /grant "%USERNAME%":F /T

# Verificar mapeamento de rede
net use z:
```

- [ ] Resolvido ou escalado

### Problema: API Porta 5000 em Uso

**Diagnóstico:**

```bash
netstat -ano | findstr :5000
```

**Solução:**

```bash
# Opção 1: Matar processo
taskkill /PID <numero> /F

# Opção 2: Mudar porta em api_rest.py
# app.run(port=5001)
```

- [ ] Resolvido ou escalado

---

## 📊 MONITORAMENTO CONTÍNUO

### Semanal

- [ ] Logs revisados (sem erros frequentes)
- [ ] Tamanho do banco validado
  ```bash
  ls -lh /z/git/rotina/data_warehouse.db
  ```
- [ ] Backup completado todos os dias
  ```bash
  ls /z/git/rotina/log/scheduler_com_dw.log | wc -l
  ```

### Mensal

- [ ] Backup de produção realizado
  ```bash
  cp /z/git/rotina/data_warehouse.db /z/git/rotina/backups/db/data_warehouse_$(date +%Y%m%d).db
  ```

- [ ] Limpeza de logs antigos (mais de 90 dias)
  ```bash
  find /z/git/rotina/log -name "*.log" -mtime +90 -delete
  ```

- [ ] Análise de performance realizada
  ```bash
  tail -100 /z/git/rotina/log/scheduler_com_dw.log | grep "tempo_ms"
  ```

### Trimestral

- [ ] Revisão de schema banco de dados
  ```bash
  sqlite3 /z/git/rotina/data_warehouse.db ".schema" > schema_$(date +%Y%m%d).txt
  ```

- [ ] Teste de recovery de backup

- [ ] Upgrade de dependências Python
  ```bash
  pip install --upgrade pandas flask openpyxl
  ```

---

## 🔒 SEGURANÇA

### Acesso Controlado

- [ ] Apenas usuário autorizado pode executar scheduler
- [ ] Pasta `/z/git/rotina/` tem permissões restritas
- [ ] Logs contêm auditoria completa

### Backup e Disaster Recovery

- [ ] Backup do banco realizado semanalmente
  ```bash
  cp /z/git/rotina/data_warehouse.db /backup/
  ```

- [ ] Plano de recuperação documentado
- [ ] Teste de restauração realizado um trimestre

### Conformidade

- [ ] Logs mantidos conforme política (3 anos mínimo)
- [ ] Acesso auditado
- [ ] Dados sensíveis não expostos em logs

---

## ✨ OTIMIZAÇÕES (Opcional)

### Performance

- [ ] Índices criados
- [ ] Vacuuming realizado
- [ ] Query times monitorados

### Escalabilidade

- [ ] Plano de crescimento do banco definido
- [ ] Estratégia de particionamento documentada
- [ ] Limites de query ajustados conforme uso

### Confiabilidade

- [ ] Alertas de erro configurados
- [ ] Retry automático para falhas temporárias
- [ ] Graceful shutdown implementado

---

## 📋 CHECKLIST FINAL

### Go-Live Checklist

- [ ] Todos os testes verdes
- [ ] Ambiente validado
- [ ] Scheduler rodando
- [ ] API respondendo
- [ ] Logs gerados
- [ ] Documentação acessível
- [ ] Equipe treinada
- [ ] Plano de rollback preparado
- [ ] Suporte on-call disponível

### Assinatura de Aprovação

| Papel | Nome | Data | Assinatura |
|-------|------|------|-----------|
| Desenvolvedor | | | |
| QA | | | |
| DevOps | | | |
| Gerente | | | |

---

## 📞 SUPORTE

### Escalation

1. **Problema Local** → Logs locais
   ```bash
   tail /z/git/rotina/log/scheduler_com_dw.log
   ```

2. **Problema de Conectividade** → Network admin
   ```bash
   net use z:
   ```

3. **Problema de Permissões** → Windows admin
   ```bash
   icacls "Z:\git\rotina" /grant "%USERNAME%":F /T
   ```

4. **Erro de Código** → Developer

### Contato

- **Dev Lead:** [seu-email]
- **DevOps:** [seu-email]
- **Escalation:** [seu-email]

---

## 📄 Documentação Relacionada

- [README_PT.md](README_PT.md) - Overview do projeto
- [DOCUMENTACAO_DATAWAREHOUSE.md](DOCUMENTACAO_DATAWAREHOUSE.md) - Detalhes técnicos
- [GUIA_RAPIDO_DATAWAREHOUSE.md](GUIA_RAPIDO_DATAWAREHOUSE.md) - Guia rápido
- [requirements.txt](requirements.txt) - Dependências

---

**Última Revisão:** 29/03/2026  
**Próxima Revisão:** 29/04/2026  
**Status:** ✅ Aprovado para GO-LIVE
