# 🚀 Guia Operacional - Kafka + Data Warehouse

**Data:** 05/04/2026 | **Status:** Pronto para Implementação

---

## 📋 Índice
1. [Setup Inicial](#setup-inicial)
2. [Iniciar Serviços](#iniciar-serviços)
3. [Monitoramento](#monitoramento)
4. [Troubleshooting](#troubleshooting)
5. [Fluxo Completo](#fluxo-completo)

---

## 🔧 Setup Inicial

### Fase 1: Instalar Dependências

```bash
# 1. Navegar para o diretório do projeto
cd c:\Users\recep2\Documents\git\analise_py\DATAWAREHOUSE\DEV_ENVIRONMENT

# 2. Instalar Kafka Python
pip install kafka-python

# 3. Instalar bibliotecas PDF
pip install pdfplumber openpyxl

# 4. Verificar instalação
python -c "from kafka import KafkaProducer, KafkaConsumer; print('✓ Kafka OK')"
python -c "import pdfplumber; print('✓ PDF OK')"
```

### Fase 2: Setup Docker (Kafka + Zookeeper)

**Opção A: Usando Docker Desktop**

```bash
# 1. Criar docker-compose.yml (ver arquivo KAFKA_ARQUITECTURA.md)
# 2. Iniciar containers
cd DATAWAREHOUSE
docker-compose up -d

# 3. Verificar se containers estão rodando
docker-compose ps
# Output esperado:
# NAME                   STATUS
# zookeeper              Up
# kafka                  Up
# kafka-ui               Up

# 4. Verificar Kafka UI
# Abrir: http://localhost:8080
```

**Opção B: Kafka Local (sem Docker)**

```bash
# 1. Download Kafka
# Link: https://kafka.apache.org/downloads
# Versão recomendada: 3.5.0 (Scala 2.13)

# 2. Extrair para C:\kafka_2.13-3.5.0

# 3. Terminal 1 - Zookeeper
cd C:\kafka_2.13-3.5.0
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

# 4. Terminal 2 - Kafka Broker
cd C:\kafka_2.13-3.5.0
.\bin\windows\kafka-server-start.bat .\config\server.properties

# 5. Verificar se Kafka está respondendo
python -c "from kafka import KafkaProducer; KafkaProducer(bootstrap_servers='localhost:9092'); print('✓ Kafka OK')"
```

### Fase 3: Criar Topics Kafka

```bash
# Criar topic: backup-events
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic backup-events \
  --partitions 3 \
  --replication-factor 1 \
  --retention-ms 2592000000  # 30 dias

# Criar topic: pdf-processing
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic pdf-processing \
  --partitions 2 \
  --replication-factor 1

# Criar topic: data-warehouse-events
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic data-warehouse-events \
  --partitions 1 \
  --replication-factor 1

# Criar topic: alerts
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic alerts \
  --partitions 1 \
  --replication-factor 1

# Listar topics criados
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
# Output esperado:
# __consumer_offsets
# alerts
# backup-events
# data-warehouse-events
# pdf-processing
```

---

## 🚀 Iniciar Serviços

### Arquitetura de Execução

```
Terminal 1: Kafka (ZK + Broker)
   ↓
Terminal 2: SchedulerKafka (Producer)
   ↓
Terminal 3: DW Consumer (Processor)
   ↓
Terminal 4: PDF Consumer (Converter)
   ↓
Terminal 5: Monitoring (Logs)
```

### Passo a Passo

#### **Terminal 1: Iniciar Kafka** (se não usando Docker)

```bash
# Apenas se NÃO estiver usando Docker
cd C:\kafka_2.13-3.5.0

# Zookeeper
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
# Aguardar mensagem: "binding to port 0.0.0.0/0.0.0.0:2181"

# (Então abrir outro terminal para Kafka Broker)
.\bin\windows\kafka-server-start.bat .\config\server.properties
# Aguardar mensagem: "started (kafka.broker.KafkaServer)"
```

#### **Terminal 1 (Alternativo): Docker Compose**

```bash
cd DATAWAREHOUSE
docker-compose up

# Aguardar:
# kafka_1          | [2026-04-05 17:00:00,000] INFO Replica started high watermark for partition...
```

#### **Terminal 2: Scheduler Producer**

```bash
# Abrir novo terminal
cd DEV_ENVIRONMENT

# Modo de aquecimento (testa sem esperar 17:00)
python scheduler_kafka.py --test

# Ou rodar normalmente (aguarda 17:00)
python scheduler_kafka.py

# Output esperado:
# ✓ Kafka Producer inicializado: localhost:9092
# ✓ SCHEDULER COM KAFKA INICIALIZADO
# SO: Windows
# Horário de backup: 17:00
# Kafka habilitado: True
# [14:30:05] Aguardando horário de backup...
# [14:30:35] Aguardando horário de backup...
```

#### **Terminal 3: DW Consumer**

```bash
# Abrir novo terminal
cd DEV_ENVIRONMENT

python dw_consumer_kafka.py

# Output esperado:
# ✓ DW Consumer Kafka inicializado
#   Consumer Group: dw-etl-consumer-group
#   Tópico Input: backup-events
#   Broker: localhost:9092
# ================================================================================
# DW CONSUMER KAFKA AGUARDANDO EVENTOS...
# ================================================================================
# Aguardando eventos em: kafka://localhost:9092/backup-events
```

#### **Terminal 4: PDF Processor Consumer**

```bash
# Abrir novo terminal
cd DEV_ENVIRONMENT

python pdf_processor_kafka.py

# Output esperado:
# ✓ PDF Processor Consumer inicializado
#   Broker: localhost:9092
#   Consumer Group: pdf-processor-group
# ✓ PDF Libs disponíveis (pdfplumber + openpyxl)
# ================================================================================
# PDF PROCESSOR CONSUMER AGUARDANDO EVENTOS...
# ================================================================================
```

#### **Terminal 5: Monitoramento (Opcional)**

```bash
# Abrir novo terminal para acompanhar logs

# Logs do Scheduler
tail -f z:/git/rotina/log/scheduler_kafka_2026-04-05.log

# Logs do DW Consumer
tail -f z:/git/rotina/log/dw_consumer_kafka_2026-04-05.log

# Logs do PDF Processor
tail -f z:/git/rotina/log/pdf_processor_kafka_2026-04-05.log
```

---

## 📊 Monitoramento

### Kafka UI (Browser)

```
URL: http://localhost:8080

Seções:
├─ Topics
│  ├─ backup-events (3 partições)
│  │  └─ Messages: 12 (crescendo conforme eventos chegam)
│  ├─ pdf-processing (2 partições)
│  ├─ data-warehouse-events (1 partição)
│  └─ alerts (1 partição)
│
├─ Consumer Groups
│  ├─ dw-etl-consumer-group
│  │  └─ lag: 0 (idealmente)
│  └─ pdf-processor-group
│     └─ lag: 0
│
└─ Brokers
   └─ Broker 1
      └─ Status: Leader of 4 partitions
```

### Linha de Comando - Monitorar Topics

```bash
# Ver mensagens em tempo real (topic backup-events)
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic backup-events \
  --from-beginning

# Output quando backup dispara:
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-04-05T17:00:05.123Z",
  "tipo": "backup_concluido",
  "data_pasta": "05 APR",
  "status": "sucesso"
}
```

### Verificar Consumer Lag

```bash
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group dw-etl-consumer-group \
  --describe

# Output esperado:
# GROUP                   TOPIC              PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# dw-etl-consumer-group   backup-events      0          12              12              0
# dw-etl-consumer-group   backup-events      1          8               8               0
# dw-etl-consumer-group   backup-events      2          9               9               0
```

---

## 🧪 Teste Completo (Simulação)

### Simular um Backup Completo

```bash
# 1. Ter as 4 janelas abertas (Kafka, Scheduler, DW Consumer, PDF Consumer)

# 2. No terminal 2 (Scheduler), forçar teste:
# Pressionar Ctrl+C para parar scheduler normal

python scheduler_kafka.py --test

# Ou injetar evento manual (terminal novo):
python -c "
from kafka import KafkaProducer
import json
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('backup-events', {
    'tipo': 'backup_concluido',
    'data_pasta': '05 APR',
    'timestamp': datetime.now().isoformat(),
    'status': 'sucesso'
})

print('✓ Evento test injetado em backup-events')
producer.flush()
"

# 3. Observar:
# - Terminal 3 (DW): Deve processar evento e fazer ETL
# - Terminal 4 (PDF): Deve converter PDFs da pasta "05 APR"
# - Terminal 5 (Logs): Mostrar atividade
# - Kafka UI: Contadores de mensagens incrementando
```

### Verificar Resultados

```bash
# 1. Verificar se banco foi atualizado
cd DATAWAREHOUSE\DEV_ENVIRONMENT
python -c "
import sqlite3
from pathlib import Path
import platform

if platform.system() == 'Windows':
    db_path = 'z:/git/rotina/data_warehouse.db'
else:
    db_path = '/mnt/z/git/rotina/data_warehouse.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar backups processados hoje
cursor.execute('''
    SELECT COUNT(*) FROM fato_backups 
    WHERE date(criado_em) = date('now')
''')
print(f'Backups processados hoje: {cursor.fetchone()[0]}')

# Verificar registros de Caixa
cursor.execute('''
    SELECT COUNT(*) FROM fato_caixa 
    WHERE date(criado_em) = date('now')
''')
print(f'Registros de Caixa hoje: {cursor.fetchone()[0]}')

conn.close()
"

# 2. Verificar pastas de Excel convertidas
ls -lh z:/git/rotina/05\ APR/*.xlsx

# 3. Verificar logs
tail -20 z:/git/rotina/log/dw_consumer_kafka_2026-04-05.log
```

---

## 🔧 Troubleshooting

### Problema: "Connection refused" ao conectar com Kafka

**Solução:**
```bash
# Verificar se Kafka está rodando
docker-compose ps
# ou
netstat -an | findstr 9092

# Se não estiver, iniciar
docker-compose up -d

# Testar conexão
python -c "from kafka import KafkaProducer; KafkaProducer(bootstrap_servers='localhost:9092'); print('OK')"
```

### Problema: Consumer fica "pendurado" sem processar

**Solução:**
```bash
# Consumer pode estar em error. Resetar offset:
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group dw-etl-consumer-group \
  --reset-offsets \
  --to-earliest \
  --execute \
  --all-topics

# Depois reiniciar consumer
# (Ctrl+C no terminal 3 e rodar novamente)
```

### Problema: "No topics or subscriptions registered"

**Solução:**
```bash
# Topics não foram criados. Criar manualmente:
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic backup-events \
  --partitions 3 \
  --replication-factor 1
```

### Problema: PDF não é convertido

**Solução:**
```bash
# 1. Verificar se pdfplumber está instalado
pip list | grep pdfplumber

# 2. Se não, instalar
pip install pdfplumber openpyxl

# 3. Reiniciar PDF Processor (Ctrl+C e rodar novamente)

# 4. Verificar logs
tail -50 z:/git/rotina/log/pdf_processor_kafka_2026-04-05.log
```

### Problema: Kafka UI não abre em localhost:8080

**Solução:**
```bash
# Verificar se container kafka-ui está rodando
docker-compose ps kafka-ui

# Se não, verificar logs
docker-compose logs kafka-ui

# Tentar acessar por IP do container
docker inspect kafka-ui | grep IPAddress
```

---

## 📈 Fluxo Completo em Ação

### Timeline: 17:00:00 a 17:05:00

```
17:00:00
├─ Scheduler verifica hora
│  └─ HORA DE BACKUP!
│
17:00:01
├─ Scheduler envia: "backup_iniciado"
│  └─ Topic: backup-events
│  └─ Partição: 0 (round-robin)
│
17:00:02
├─ Backup script executa
│  ├─ Copia Caixa.xlsx
│  ├─ Copia Relatorios
│  ├─ Copia PDFs
│  └─ Cria pasta: "05 APR"
│
17:00:45
├─ Backup concluído com sucesso
├─ Scheduler envia: "backup_concluido"
│  └─ Topic: backup-events
│  └─ Partição: 1
│
17:00:46
├─ DW Consumer recebe evento
│  ├─ Inicia ETL
│  ├─ Extrai Caixa.xlsx
│  ├─ Normaliza (3NF)
│  ├─ Insere em SQLite
│  └─ Envia: "data-warehouse-events"
│
17:00:47
├─ PDF Processor recebe evento
│  ├─ Encontra PDFs em "05 APR"
│  ├─ Converter Relatorio_Vendas.pdf → .xlsx
│  ├─ Converter Relatorio_Estoque.pdf → .xlsx
│  └─ Envia: "pdf-processing-complete"
│
17:01:30
├─ Alerting Consumer (opcional)
│  ├─ Resume sucesso
│  ├─ Envia notificação
│  └─ Log de auditoria
│
17:01:45
├─ Dashboard (API REST) atualizado
│  ├─ Mostra: +45 registros novos
│  ├─ Mostra: 2 PDFs convertidos
│  └─ Status: ✓ OK
```

---

## 📊 Métricas Esperadas

| Métrica | Esperado | Crítico |
|---------|----------|---------|
| Latência Backup → DW | < 5s | > 30s |
| Latência Backup → PDF | < 10s | > 60s |
| Consumer Lag | 0 | > 100 |
| Taxa Processamento | 100+ msg/min | < 10 msg/min |
| Taxa Sucesso | > 99% | < 95% |
| Tempo ETL | 5-10s | > 60s |

---

## 🛑 Parar Todos os Serviços

```bash
# Parar em ordem reversa

# Terminal 5: Parar monitoramento
# (Ctrl+C)

# Terminal 4: Parar PDF Processor
# (Ctrl+C)

# Terminal 3: Parar DW Consumer
# (Ctrl+C)

# Terminal 2: Parar Scheduler
# (Ctrl+C)

# Terminal 1: Parar Kafka
# (Ctrl+C)
# e
docker-compose down

# Verificar se tudo parou
docker-compose ps
# (Deve estar vazio ou "exited")
```

---

## 📚 Referências

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [pdfplumber Docs](https://github.com/jsvine/pdfplumber)
- [Docker Compose](https://docs.docker.com/compose/)

