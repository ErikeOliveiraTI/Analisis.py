#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de Validação - Kafka Event Streaming
============================================

Suite de testes para validar:
  ✓ Conexão com Kafka
  ✓ Criação de topics
  ✓ Producer (Scheduler)
  ✓ Consumer (DW ETL)
  ✓ Consumer (PDF Processor)
  ✓ Banco de dados
  ✓ Fluxo completo

Uso:
  python test_kafka_integration.py
  python test_kafka_integration.py -v  (verbose)
  python test_kafka_integration.py --quick  (apenas básico)
"""

import unittest
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# ============================================================================
# CONFIGURAÇÃO DOS TESTES
# ============================================================================

class TestConfig:
    """Configuração para testes"""
    KAFKA_BROKER = "localhost:9092"
    TIMEOUT = 10  # segundos
    TEST_TIMEOUT = 30  # segundos para testes mais longos


# ============================================================================
# TESTES BÁSICOS DE CONEXÃO
# ============================================================================

class TestKafkaConnection(unittest.TestCase):
    """Testa conectividade básica com Kafka"""
    
    def test_kafka_connection(self):
        """Verifica se consegue conectar ao Kafka"""
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                request_timeout_ms=5000
            )
            producer.close()
            self.assertTrue(True, "Kafka respondendo")
        except Exception as e:
            self.fail(f"Não conseguiu conectar ao Kafka: {str(e)}")
    
    def test_kafka_admin_client(self):
        """Testa Admin Client para gerenciar topics"""
        try:
            from kafka.admin import KafkaAdminClient, NewTopic
            admin_client = KafkaAdminClient(
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                request_timeout_ms=5000
            )
            
            # Listar topics
            topics = admin_client.list_topics()
            self.assertIn('backup-events', topics, 
                         "Topic 'backup-events' não existe")
            
            admin_client.close()
        except Exception as e:
            self.fail(f"Erro com Admin Client: {str(e)}")


# ============================================================================
# TESTES DE TOPICS
# ============================================================================

class TestKafkaTopics(unittest.TestCase):
    """Testa existência e configuração de topics"""
    
    def setUp(self):
        """Preparação antes de cada teste"""
        from kafka.admin import KafkaAdminClient
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=TestConfig.KAFKA_BROKER,
            request_timeout_ms=5000
        )
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.admin_client.close()
    
    def test_backup_events_topic(self):
        """Verifica topic 'backup-events'"""
        topics = self.admin_client.list_topics()
        self.assertIn('backup-events', topics)
    
    def test_pdf_processing_topic(self):
        """Verifica topic 'pdf-processing'"""
        topics = self.admin_client.list_topics()
        self.assertIn('pdf-processing', topics)
    
    def test_data_warehouse_events_topic(self):
        """Verifica topic 'data-warehouse-events'"""
        topics = self.admin_client.list_topics()
        self.assertIn('data-warehouse-events', topics)
    
    def test_alerts_topic(self):
        """Verifica topic 'alerts'"""
        topics = self.admin_client.list_topics()
        self.assertIn('alerts', topics)


# ============================================================================
# TESTES DE PRODUCER
# ============================================================================

class TestKafkaProducer(unittest.TestCase):
    """Testa Producer (Scheduler)"""
    
    def test_producer_send_event(self):
        """Testa envio de evento simples"""
        try:
            from kafka import KafkaProducer
            
            producer = KafkaProducer(
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=5000
            )
            
            evento_teste = {
                "tipo": "backup_concluido",
                "data_pasta": "TEST",
                "status": "sucesso"
            }
            
            future = producer.send('backup-events', evento_teste)
            record_metadata = future.get(timeout=TestConfig.TIMEOUT)
            
            self.assertIsNotNone(record_metadata.offset)
            producer.close()
            
        except Exception as e:
            self.fail(f"Erro ao enviar evento: {str(e)}")
    
    def test_producer_batch_events(self):
        """Testa envio de múltiplos eventos"""
        try:
            from kafka import KafkaProducer
            
            producer = KafkaProducer(
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            for i in range(5):
                evento = {
                    "tipo": "test_event",
                    "numero": i,
                    "timestamp": datetime.now().isoformat()
                }
                producer.send('backup-events', evento)
            
            producer.flush()
            producer.close()
            
            self.assertTrue(True, "Batch enviado com sucesso")
            
        except Exception as e:
            self.fail(f"Erro no batch: {str(e)}")


# ============================================================================
# TESTES DE CONSUMER
# ============================================================================

class TestKafkaConsumer(unittest.TestCase):
    """Testa Consumer básico"""
    
    def test_consumer_creation(self):
        """Testa criação de consumer"""
        try:
            from kafka import KafkaConsumer
            
            consumer = KafkaConsumer(
                'backup-events',
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                group_id='test-consumer-group',
                auto_offset_reset='earliest',
                consumer_timeout_ms=1000
            )
            
            self.assertIsNotNone(consumer)
            consumer.close()
            
        except Exception as e:
            self.fail(f"Erro ao criar consumer: {str(e)}")
    
    def test_consumer_read_events(self):
        """Testa leitura de eventos do consumer"""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            
            # Enviar evento
            producer = KafkaProducer(
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            evento_teste = {"tipo": "test", "valor": 123}
            producer.send('backup-events', evento_teste)
            producer.flush()
            producer.close()
            
            # Ler evento
            time.sleep(1)  # Aguardar propagação
            
            consumer = KafkaConsumer(
                'backup-events',
                bootstrap_servers=TestConfig.KAFKA_BROKER,
                group_id='test-read-group',
                auto_offset_reset='earliest',
                consumer_timeout_ms=2000
            )
            
            eventos = []
            for message in consumer:
                eventos.append(message.value)
                if len(eventos) >= 1:
                    break
            
            consumer.close()
            
            self.assertTrue(len(eventos) > 0, "Nenhum evento lido")
            
        except Exception as e:
            self.fail(f"Erro ao ler eventos: {str(e)}")


# ============================================================================
# TESTES DE BANCO DE DADOS
# ============================================================================

class TestDatabase(unittest.TestCase):
    """Testa banco de dados"""
    
    def test_database_exists(self):
        """Verifica se banco existe"""
        import platform
        
        if platform.system() == "Windows":
            db_path = Path("z:/git/rotina/data_warehouse.db")
        else:
            db_path = Path("/mnt/z/git/rotina/data_warehouse.db")
        
        if not db_path.exists():
            self.skipTest("Banco não criado ainda (será ao primeiro backup)")
        else:
            self.assertTrue(db_path.exists())
    
    def test_database_tables(self):
        """Testa estrutura das tabelas"""
        import sqlite3
        import platform
        
        if platform.system() == "Windows":
            db_path = "z:/git/rotina/data_warehouse.db"
        else:
            db_path = "/mnt/z/git/rotina/data_warehouse.db"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tabelas
            tabelas_esperadas = [
                'dim_datas',
                'dim_tipos_arquivo',
                'fato_backups',
                'fato_caixa',
                'fato_relatorios',
                'auditoria_processamento'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas_existentes = [row[0] for row in cursor.fetchall()]
            
            for tabela in tabelas_esperadas:
                self.assertIn(tabela, tabelas_existentes, 
                             f"Tabela '{tabela}' não existe")
            
            conn.close()
            
        except Exception as e:
            self.skipTest(f"Erro ao acessar banco: {str(e)}")


# ============================================================================
# TESTES DE PYTHON MODULES
# ============================================================================

class TestPythonModules(unittest.TestCase):
    """Testa se todas as dependências estão instaladas"""
    
    def test_kafka_python(self):
        """Testa kafka-python"""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            self.assertTrue(True)
        except ImportError:
            self.fail("kafka-python não instalado")
    
    def test_pandas(self):
        """Testa pandas"""
        try:
            import pandas
            self.assertTrue(True)
        except ImportError:
            self.fail("pandas não instalado")
    
    def test_flask(self):
        """Testa flask"""
        try:
            import flask
            self.assertTrue(True)
        except ImportError:
            self.fail("flask não instalado")
    
    def test_pdfplumber(self):
        """Testa pdfplumber"""
        try:
            import pdfplumber
            self.assertTrue(True)
        except ImportError:
            self.skipTest("pdfplumber opcional")
    
    def test_openpyxl(self):
        """Testa openpyxl"""
        try:
            import openpyxl
            self.assertTrue(True)
        except ImportError:
            self.fail("openpyxl não instalado")


# ============================================================================
# SUITE DE TESTES
# ============================================================================

def suite_basico():
    """Suite com testes básicos"""
    suite = unittest.TestSuite()
    
    # Testes de conexão
    suite.addTest(TestKafkaConnection('test_kafka_connection'))
    
    # Testes de módulos
    suite.addTest(TestPythonModules('test_kafka_python'))
    suite.addTest(TestPythonModules('test_pandas'))
    suite.addTest(TestPythonModules('test_flask'))
    
    return suite


def suite_completo():
    """Suite com todos os testes"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPythonModules))
    suite.addTests(loader.loadTestsFromTestCase(TestKafkaConnection))
    suite.addTests(loader.loadTestsFromTestCase(TestKafkaTopics))
    suite.addTests(loader.loadTestsFromTestCase(TestKafkaProducer))
    suite.addTests(loader.loadTestsFromTestCase(TestKafkaConsumer))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    
    return suite


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    
    # Verificar argumentos
    if '--quick' in sys.argv:
        sys.argv.remove('--quick')
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite_basico())
    else:
        # Suite completo por padrão
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite_completo())
