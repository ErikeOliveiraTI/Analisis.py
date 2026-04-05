#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler com Integração Kafka - Producer
============================================

Responsável por:
  ✓ Coordenar execução de blackups
  ✓ Enviar eventos para Kafka (backup-events)
  ✓ Manter compatibilidade com scheduler antigo
  ✓ Logging estruturado

Uso:
  python scheduler_kafka.py
  
Eventos Publicados:
  - backup_iniciado: Quando scheduler decide executar
  - backup_concluido: Quando backup termina com sucesso
  - backup_erro: Quando backup falha

Consumidores:
  - dw_consumer_kafka.py (processa no DW)
  - alerting_consumer_kafka.py (gera alertas)
  - logging_consumer_kafka.py (auditoria)
"""

import subprocess
import time
import json
import uuid
import logging
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

try:
    from kafka import KafkaProducer
    KAFKA_DISPONIVEL = True
except ImportError:
    KAFKA_DISPONIVEL = False
    print("⚠️  Kafka não instalado. Modo fallback para logging apenas.")

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class ConfigScheduler:
    """Configuração centralizada"""
    
    # Detectar SO e ajustar caminhos
    if platform.system() == "Windows":
        BASE_DIR = Path("z:/git/rotina")
        BACKUP_SCRIPT = Path("z:/git/init_/analise_py/backup_rede.bash")
        LOG_DIR = Path("z:/git/rotina/log")
    else:  # Linux/WSL
        BASE_DIR = Path("/mnt/z/git/rotina")
        BACKUP_SCRIPT = Path("/mnt/z/git/init_/analise_py/backup_rede.bash")
        LOG_DIR = Path("/mnt/z/git/rotina/log")
    
    # Kafka
    KAFKA_BROKERS = "localhost:9092"  # Ajustar para seu ambiente
    KAFKA_ENABLED = KAFKA_DISPONIVEL
    
    # Log
    LOG_FILE = LOG_DIR / f"scheduler_kafka_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Scheduler
    HORA_BACKUP = 17
    MINUTO_INICIO = 0
    MINUTO_FIM = 2  # Executar entre 17:00 e 17:02
    
    # Retry
    RETRY_TIMEOUT = 3600  # 1 hora


# ============================================================================
# LOGGER
# ============================================================================

def configurar_logger():
    """Configura logging com arquivo e console"""
    ConfigScheduler.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("SchedulerKafka")
    logger.setLevel(logging.DEBUG)
    
    # Handler arquivo
    fh = logging.FileHandler(ConfigScheduler.LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    # Handler console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # Formato
    formato = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formato)
    ch.setFormatter(formato)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = configurar_logger()


# ============================================================================
# PRODUCER KAFKA
# ============================================================================

class KafkaEventProducer:
    """Gerencia envio de eventos para Kafka"""
    
    def __init__(self):
        """Inicializa producer se Kafka disponível"""
        self.habilitado = ConfigScheduler.KAFKA_ENABLED
        self.producer = None
        
        if self.habilitado:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=ConfigScheduler.KAFKA_BROKERS,
                    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                    acks='all',  # Garantir que todos os replicas confirmem
                    retries=3,
                    request_timeout_ms=30000
                )
                logger.info(f"✓ Kafka Producer inicializado: {ConfigScheduler.KAFKA_BROKERS}")
            except Exception as e:
                logger.warning(f"⚠️  Não consegui conectar ao Kafka: {str(e)}")
                logger.warning("   → Continuando em modo fallback (logs apenas)")
                self.habilitado = False
    
    def enviar_evento(self, topico: str, evento: Dict[str, Any]) -> bool:
        """
        Envia evento para Kafka (com fallback em logs)
        
        Args:
            topico: Nome do tópico Kafka
            evento: Dict com dados do evento
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Adicionar metadados ao evento
            evento_completo = {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **evento
            }
            
            if self.habilitado and self.producer:
                # Enviar para Kafka
                future = self.producer.send(topico, evento_completo)
                record_metadata = future.get(timeout=10)
                
                logger.debug(
                    f"✓ Evento enviado: {topico} "
                    f"[partition={record_metadata.partition}, offset={record_metadata.offset}]"
                )
                return True
            else:
                # Modo fallback: apenas log
                logger.info(f"[KAFKA FALLBACK] Evento para '{topico}': {json.dumps(evento_completo, indent=2)}")
                return True
                
        except Exception as e:
            logger.error(f"✗ Erro ao enviar evento para Kafka: {str(e)}")
            return False
    
    def close(self):
        """Fecha producer do Kafka"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka Producer finalizado")


# ============================================================================
# SCHEDULER COM KAFKA
# ============================================================================

class SchedulerComKafka:
    """Scheduler que integra Kafka event streaming"""
    
    def __init__(self):
        """Inicializa scheduler"""
        self.producer = KafkaEventProducer()
        self.ultima_execucao = None
        
        logger.info("=" * 80)
        logger.info("SCHEDULER COM KAFKA INICIALIZADO")
        logger.info(f"SO: {platform.system()}")
        logger.info(f"Horário de backup: {ConfigScheduler.HORA_BACKUP:02d}:00")
        logger.info(f"Backup script: {ConfigScheduler.BACKUP_SCRIPT}")
        logger.info(f"Kafka habilitado: {self.producer.habilitado}")
        logger.info("=" * 80)
    
    def executar_backup_script(self) -> Dict[str, Any]:
        """
        Executa script de backup
        
        Returns:
            Dict com resultado da execução
        """
        try:
            logger.info("▶ Iniciando script de backup...")
            
            comando = f'bash "{str(ConfigScheduler.BACKUP_SCRIPT)}"'
            resultado = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                timeout=ConfigScheduler.RETRY_TIMEOUT
            )
            
            if resultado.returncode == 0:
                logger.info("✓ Script de backup concluído com sucesso")
                return {
                    "status": "sucesso",
                    "codigo_retorno": 0,
                    "stdout": resultado.stdout[-200:],  # Últimas 200 chars
                    "duracao_segundos": 0
                }
            else:
                logger.error(f"✗ Script retornou erro: {resultado.returncode}")
                logger.error(f"   STDERR: {resultado.stderr}")
                return {
                    "status": "erro",
                    "codigo_retorno": resultado.returncode,
                    "erro": resultado.stderr[-500:],
                    "duracao_segundos": 0
                }
                
        except subprocess.TimeoutExpired:
            logger.error("✗ Script de backup excedeu timeout!")
            return {
                "status": "erro",
                "codigo_retorno": -1,
                "erro": f"Timeout após {ConfigScheduler.RETRY_TIMEOUT}s"
            }
        except Exception as e:
            logger.error(f"✗ Erro ao executar script: {str(e)}")
            return {
                "status": "erro",
                "codigo_retorno": -2,
                "erro": str(e)
            }
    
    def detectar_data_pasta(self) -> str:
        """
        Detecta a pasta de hoje (ex: "05 APR")
        
        Returns:
            String com formato "DD MMM"
        """
        return datetime.now().strftime("%d %b").upper()
    
    def processar_backup_diario(self):
        """Processa um backup diário completo com Kafka"""
        
        data_pasta = self.detectar_data_pasta()
        logger.info(f"Data da pasta: {data_pasta}")
        
        # 1️⃣ Enviar evento: backup_iniciado
        self.producer.enviar_evento('backup-events', {
            'tipo': 'backup_iniciado',
            'data_pasta': data_pasta,
            'horario': datetime.now().isoformat(),
            'scheduler_version': '2.0-kafka'
        })
        
        # 2️⃣ Executar script de backup
        tempo_inicio = datetime.now()
        resultado_backup = self.executar_backup_script()
        duracao = (datetime.now() - tempo_inicio).total_seconds()
        
        # 3️⃣ Enviar evento: backup_concluido ou backup_erro
        if resultado_backup['status'] == 'sucesso':
            self.producer.enviar_evento('backup-events', {
                'tipo': 'backup_concluido',
                'data_pasta': data_pasta,
                'status': 'sucesso',
                'duracao_segundos': int(duracao),
                'detalhes': resultado_backup
            })
            logger.info("✓ Evento 'backup_concluido' enviado para Kafka")
            
        else:
            self.producer.enviar_evento('backup-events', {
                'tipo': 'backup_erro',
                'data_pasta': data_pasta,
                'status': 'erro',
                'duracao_segundos': int(duracao),
                'erro': resultado_backup.get('erro', 'Erro desconhecido'),
                'detalhes': resultado_backup
            })
            logger.error("✗ Evento 'backup_erro' enviado para Kafka")
            
            # Enviar alerta
            self.producer.enviar_evento('alerts', {
                'severidade': 'error',
                'tipo': 'backup_falhou',
                'titulo': f'Backup falhou em {data_pasta}',
                'descricao': resultado_backup.get('erro', 'Erro desconhecido'),
                'acao': 'Verificar logs em /z/git/rotina/log/'
            })
        
        self.ultima_execucao = datetime.now()
    
    def iniciar(self):
        """Loop principal do scheduler"""
        
        try:
            while True:
                try:
                    now = datetime.now()
                    
                    # Verificar se é hora de backup
                    if (now.hour == ConfigScheduler.HORA_BACKUP and 
                        ConfigScheduler.MINUTO_INICIO <= now.minute <= ConfigScheduler.MINUTO_FIM):
                        
                        # Verificar se não foi executado hoje ainda
                        if (self.ultima_execucao is None or 
                            self.ultima_execucao.date() < now.date()):
                            
                            logger.info("")
                            logger.info("🔔 HORA DE BACKUP!")
                            logger.info("")
                            self.processar_backup_diario()
                            logger.info("")
                    
                    # Sleep 30 segundos antes de próxima verificação
                    time.sleep(30)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"✗ Erro no loop do scheduler: {str(e)}")
                    time.sleep(30)  # Esperar antes de retry
                    
        except KeyboardInterrupt:
            logger.info("\n▪ Scheduler interrompido pelo usuário (Ctrl+C)")
        finally:
            self.producer.close()
            logger.info("Scheduler finalizado")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    scheduler = SchedulerComKafka()
    
    try:
        scheduler.iniciar()
    except Exception as e:
        logger.critical(f"Erro crítico: {str(e)}")
        sys.exit(1)
