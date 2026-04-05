#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consumer Kafka → Data Warehouse ETL
====================================

Responsável por:
  ✓ Escutar tópico 'backup-events' do Kafka
  ✓ Processar eventos de backup
  ✓ Executar ETL (Extração, Transformação, Carga)
  ✓ Atualizar banco de dados com dados normalizados
  ✓ Logging de auditoria

Uso:
  python dw_consumer_kafka.py
  
Consumer Group:
  dw-etl-consumer-group

Tópicos Consumidos:
  - backup-events (INPUT)
  
Tópicos Publicados:
  - data-warehouse-events (OUTPUT - status do processamento)
  - alerts (OUTPUT - erros críticos)
"""

import json
import logging
import platform
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import sqlite3

try:
    from kafka import KafkaConsumer, KafkaProducer
    KAFKA_DISPONIVEL = True
except ImportError:
    KAFKA_DISPONIVEL = False
    print("⚠️  Kafka não instalado. Execute: pip install kafka-python")
    sys.exit(1)

# Importar módulo de DW existente
try:
    from data_warehouse import DataWarehouse
except ImportError:
    print("✗ Erro: data_warehouse.py não encontrado")
    sys.exit(1)

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class ConfigDWConsumer:
    """Configuração centralizada"""
    
    if platform.system() == "Windows":
        LOG_DIR = Path("z:/git/rotina/log")
    else:
        LOG_DIR = Path("/mnt/z/git/rotina/log")
    
    LOG_FILE = LOG_DIR / f"dw_consumer_kafka_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Kafka
    KAFKA_BROKERS = "localhost:9092"
    CONSUMER_GROUP = "dw-etl-consumer-group"
    TOPICO_INPUT = "backup-events"
    TOPICO_OUTPUT = "data-warehouse-events"
    TOPICO_ALERTAS = "alerts"
    
    # Processamento
    AUTO_COMMIT = False  # Commit manual após sucesso


# ============================================================================
# LOGGER
# ============================================================================

def configurar_logger():
    """Configura logging"""
    ConfigDWConsumer.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("DWConsumerKafka")
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(ConfigDWConsumer.LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
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
# CONSUMER KAFKA + DW ETL
# ============================================================================

class DWConsumerKafka:
    """Consome eventos de backup e processa no Data Warehouse"""
    
    def __init__(self):
        """Inicializa consumer e DW"""
        try:
            # Inicializar consumer Kafka
            self.consumer = KafkaConsumer(
                ConfigDWConsumer.TOPICO_INPUT,
                bootstrap_servers=ConfigDWConsumer.KAFKA_BROKERS,
                group_id=ConfigDWConsumer.CONSUMER_GROUP,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=ConfigDWConsumer.AUTO_COMMIT,
                session_timeout_ms=30000
            )
            
            # Inicializar producer (para enviar status)
            self.producer = KafkaProducer(
                bootstrap_servers=ConfigDWConsumer.KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all'
            )
            
            # Inicializar Data Warehouse
            self.dw = DataWarehouse()
            
            logger.info("✓ DW Consumer Kafka inicializado")
            logger.info(f"  Consumer Group: {ConfigDWConsumer.CONSUMER_GROUP}")
            logger.info(f"  Tópico Input: {ConfigDWConsumer.TOPICO_INPUT}")
            logger.info(f"  Broker: {ConfigDWConsumer.KAFKA_BROKERS}")
            
        except Exception as e:
            logger.error(f"✗ Erro ao inicializar: {str(e)}")
            raise
    
    def processar_backup_concluido(self, evento: Dict[str, Any]) -> bool:
        """
        Processa evento de backup concluído
        
        Args:
            evento: Dict com dados do evento
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            data_pasta = evento.get('data_pasta')
            logger.info(f"▶ Processando backup concluído: {data_pasta}")
            
            tempo_inicio = datetime.now()
            
            # 1️⃣ Processar backup no DW
            resultado = self.dw.processar_backup_diario(data_pasta)
            
            tempo_processamento = (datetime.now() - tempo_inicio).total_seconds()
            
            # 2️⃣ Enviar evento de sucesso
            self.producer.send(ConfigDWConsumer.TOPICO_OUTPUT, {
                'tipo_operacao': 'BACKUP_PROCESSADO',
                'data_pasta': data_pasta,
                'status': 'sucesso',
                'tempo_processamento_ms': int(tempo_processamento * 1000),
                'registros_processados': resultado.get('total_registros', 0),
                'detalhes': resultado
            })
            
            logger.info(f"✓ Backup processado com sucesso em {tempo_processamento:.2f}s")
            logger.info(f"  Registros processados: {resultado.get('total_registros', 0)}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro ao processar backup: {str(e)}")
            
            # Enviar alerta
            self.producer.send(ConfigDWConsumer.TOPICO_ALERTAS, {
                'severidade': 'error',
                'tipo': 'dw_processamento_erro',
                'titulo': 'Erro ao processar backup no DW',
                'descricao': str(e),
                'data_pasta': evento.get('data_pasta')
            })
            
            return False
    
    def processar_backup_erro(self, evento: Dict[str, Any]) -> bool:
        """
        Processa evento de erro no backup
        
        Args:
            evento: Dict com dados do evento
            
        Returns:
            Sempre True (para não parar o consumer)
        """
        try:
            data_pasta = evento.get('data_pasta')
            erro = evento.get('erro', 'Erro desconhecido')
            
            logger.warning(f"⚠️  Backup com erro: {data_pasta}")
            logger.warning(f"   Erro: {erro}")
            
            # Registrar auditoria
            self.dw._registrar_auditoria(
                tipo_operacao='BACKUP_ERROR',
                descricao=f"Backup error para {data_pasta}: {erro}",
                status='erro'
            )
            
            # Enviar alerta
            self.producer.send(ConfigDWConsumer.TOPICO_ALERTAS, {
                'severidade': 'error',
                'tipo': 'backup_error',
                'titulo': f'ERRO: Backup falhou em {data_pasta}',
                'descricao': erro,
                'acao': 'Verificar logs em /z/git/rotina/log/'
            })
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro no processamento de backup_erro: {str(e)}")
            return True
    
    def processar_evento(self, evento: Dict[str, Any]) -> bool:
        """
        Processa evento genérico de backup
        
        Args:
            evento: Dict com dados do evento
            
        Returns:
            True se sucesso, False se erro
        """
        tipo = evento.get('tipo', 'desconhecido')
        
        if tipo == 'backup_concluido':
            return self.processar_backup_concluido(evento)
        elif tipo == 'backup_erro':
            return self.processar_backup_erro(evento)
        elif tipo == 'backup_iniciado':
            logger.info(f"ℹ️  Backup iniciado: {evento.get('data_pasta')}")
            return True
        else:
            logger.warning(f"⚠️  Tipo de evento desconhecido: {tipo}")
            return True
    
    def iniciar(self):
        """Loop principal do consumer"""
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("DW CONSUMER KAFKA AGUARDANDO EVENTOS...")
        logger.info("=" * 80)
        logger.info(f"Aguardando eventos em: kafka://{ConfigDWConsumer.KAFKA_BROKERS}/{ConfigDWConsumer.TOPICO_INPUT}")
        logger.info("Pressione Ctrl+C para parar")
        logger.info("=" * 80)
        logger.info("")
        
        contador_eventos = 0
        
        try:
            for mensagem in self.consumer:
                try:
                    evento = mensagem.value
                    contador_eventos += 1
                    
                    logger.info("")
                    logger.info(f"[Evento #{contador_eventos}] {evento.get('tipo', 'unknown')}")
                    logger.debug(f"Conteúdo: {json.dumps(evento, indent=2)}")
                    
                    # Processar evento
                    sucesso = self.processar_evento(evento)
                    
                    if sucesso:
                        # Commit manual após sucesso
                        self.consumer.commit()
                        logger.info(f"✓ Evento processado e commitado")
                    else:
                        logger.error(f"✗ Erro ao processar evento - sem commit")
                    
                except Exception as e:
                    logger.error(f"✗ Erro ao processar mensagem: {str(e)}")
                    logger.error(f"Mensagem raw: {mensagem}")
                    
        except KeyboardInterrupt:
            logger.info("\n▪ Consumer interrompido (Ctrl+C)")
        finally:
            self.finalizar()
    
    def finalizar(self):
        """Encerra consumer e producer"""
        try:
            self.consumer.close()
            self.producer.close()
            logger.info("✓ DW Consumer Kafka finalizado")
        except Exception as e:
            logger.error(f"Erro ao finalizar: {str(e)}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    # Verificar disponibilidade de Kafka
    if not KAFKA_DISPONIVEL:
        logger.error("✗ Kafka não disponível")
        sys.exit(1)
    
    # Iniciar consumer
    consumer = DWConsumerKafka()
    
    try:
        consumer.iniciar()
    except Exception as e:
        logger.critical(f"Erro crítico: {str(e)}")
        sys.exit(1)
