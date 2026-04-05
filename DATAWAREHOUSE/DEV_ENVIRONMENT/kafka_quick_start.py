#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Quick Start - Kafka + Data Warehouse
========================================

Este script verifica e prepara o ambiente para executar o pipeline completo.

Uso:
  python kafka_quick_start.py [comando]

Comandos:
  check        - Verificar ambiente (dependências, Kafka, DB)
  setup        - Setup completo (instalar deps, criar topics)
  run-all      - Iniciar todos os serviços (requires 4 terminals)
  cleanup      - Limpar dados e logs antigos
  status       - Status atual do sistema
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import platform

# ============================================================================
# CORES PARA TERMINAL
# ============================================================================

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ============================================================================
# VERIFICAÇÃO DO AMBIENTE
# ============================================================================

class EnvironmentChecker:
    """Verifica estado do ambiente"""
    
    @staticmethod
    def print_header(titulo):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{titulo:^80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")
    
    @staticmethod
    def print_ok(msg):
        print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")
    
    @staticmethod
    def print_error(msg):
        print(f"{Colors.RED}✗{Colors.RESET} {msg}")
    
    @staticmethod
    def print_warning(msg):
        print(f"{Colors.YELLOW}⚠ {Colors.RESET}{msg}")
    
    @staticmethod
    def print_info(msg):
        print(f"{Colors.BLUE}ℹ {Colors.RESET}{msg}")
    
    def check_python_version(self):
        """Verifica versão Python"""
        self.print_header("Python Version")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.print_ok(f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.print_error(f"Python {version.major}.{version.minor} - Requer Python 3.8+")
            return False
    
    def check_dependencies(self):
        """Verifica se bibliotecas estão instaladas"""
        self.print_header("Python Dependencies")
        
        dependencias = {
            "pandas": "Data processing",
            "kafka": "Kafka client",
            "flask": "Web framework",
            "openpyxl": "Excel files",
            "pdfplumber": "PDF extraction",
        }
        
        tudo_ok = True
        for lib, desc in dependencias.items():
            try:
                __import__(lib)
                self.print_ok(f"{lib:20} - {desc}")
            except ImportError:
                self.print_error(f"{lib:20} - {desc}")
                tudo_ok = False
        
        if not tudo_ok:
            self.print_warning("Execute: pip install -r requirements.txt")
        
        return tudo_ok
    
    def check_docker(self):
        """Verifica se Docker está instalado"""
        self.print_header("Docker & Docker Compose")
        
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_ok(result.stdout.strip())
            else:
                self.print_error("Docker não encontrado")
                return False
            
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_ok(result.stdout.strip())
            else:
                self.print_error("Docker Compose não encontrado")
                return False
            
            return True
        except FileNotFoundError:
            self.print_error("Docker não está instalado")
            self.print_info("Baixe em: https://www.docker.com/products/docker-desktop")
            return False
    
    def check_kafka_running(self):
        """Verifica se Kafka está rodando"""
        self.print_header("Kafka Status")
        
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers='localhost:9092',
                request_timeout_ms=5000
            )
            producer.close()
            self.print_ok("Kafka está respondendo em localhost:9092")
            return True
        except Exception as e:
            self.print_error("Kafka não está respondendo")
            self.print_info(f"Erro: {str(e)}")
            self.print_info("Inicie com: docker-compose up -d")
            return False
    
    def check_database(self):
        """Verifica banco de dados"""
        self.print_header("Data Warehouse Database")
        
        if platform.system() == "Windows":
            db_path = Path("z:/git/rotina/data_warehouse.db")
        else:
            db_path = Path("/mnt/z/git/rotina/data_warehouse.db")
        
        if db_path.exists():
            size = db_path.stat().st_size / (1024 * 1024)  # MB
            self.print_ok(f"Banco encontrado: {db_path}")
            self.print_ok(f"Tamanho: {size:.2f} MB")
            return True
        else:
            self.print_warning(f"Banco não encontrado: {db_path}")
            self.print_info("Será criado na primeira execução")
            return False
    
    def check_network(self):
        """Verifica conectividade"""
        self.print_header("Network Connectivity")
        
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.print_ok("Conexão internet OK")
            return True
        except:
            self.print_warning("Sem acesso à internet (não é crítico)")
            return True
    
    def run_all_checks(self):
        """Executa todos os checks"""
        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Docker", self.check_docker),
            ("Kafka", self.check_kafka_running),
            ("Database", self.check_database),
            ("Network", self.check_network),
        ]
        
        results = {}
        for name, func in checks:
            try:
                results[name] = func()
            except Exception as e:
                print(f"{Colors.RED}Erro em {name}: {str(e)}{Colors.RESET}")
                results[name] = False
        
        return results


# ============================================================================
# SETUP ENVIRONMENT
# ============================================================================

class EnvironmentSetup:
    """Configura o ambiente"""
    
    def __init__(self, checker):
        self.checker = checker
    
    def install_dependencies(self):
        """Instala dependências Python"""
        self.checker.print_header("Installing Python Dependencies")
        
        req_file = Path("requirements.txt")
        if not req_file.exists():
            self.checker.print_error("requirements.txt não encontrado")
            return False
        
        try:
            self.checker.print_info(f"Instalando a partir de {req_file}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                capture_output=False
            )
            
            if result.returncode == 0:
                self.checker.print_ok("Dependências instaladas com sucesso")
                return True
            else:
                self.checker.print_error("Erro ao instalar dependências")
                return False
                
        except Exception as e:
            self.checker.print_error(f"Erro: {str(e)}")
            return False
    
    def start_docker_containers(self):
        """Inicia containers Docker"""
        self.checker.print_header("Starting Docker Containers")
        
        try:
            self.checker.print_info("Iniciando: zookeeper, kafka, kafka-ui...")
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.checker.print_ok("Containers iniciados com sucesso")
                self.checker.print_info("Aguardando Kafka ficar pronto...")
                
                # Aguardar Kafka estar pronto
                import time
                for i in range(30):
                    try:
                        from kafka import KafkaProducer
                        producer = KafkaProducer(bootstrap_servers='localhost:9092')
                        producer.close()
                        self.checker.print_ok("Kafka está pronto!")
                        return True
                    except:
                        time.sleep(1)
                        print(".", end="", flush=True)
                
                self.checker.print_error("Timeout aguardando Kafka")
                return False
            else:
                self.checker.print_error(f"Erro ao iniciar containers: {result.stderr}")
                return False
                
        except Exception as e:
            self.checker.print_error(f"Erro: {str(e)}")
            return False
    
    def create_kafka_topics(self):
        """Cria topics do Kafka"""
        self.checker.print_header("Creating Kafka Topics")
        
        topics = {
            "backup-events": {"partitions": 3},
            "pdf-processing": {"partitions": 2},
            "data-warehouse-events": {"partitions": 1},
            "alerts": {"partitions": 1},
        }
        
        tudo_ok = True
        
        for topic_name, config in topics.items():
            partitions = config.get("partitions", 1)
            
            try:
                cmd = [
                    "docker", "exec", "kafka",
                    "kafka-topics",
                    "--create",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", topic_name,
                    "--partitions", str(partitions),
                    "--replication-factor", "1",
                    "--if-not-exists"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 or "already exists" in result.stderr:
                    self.checker.print_ok(f"Topic '{topic_name}' ready ({partitions} partitions)")
                else:
                    self.checker.print_error(f"Erro ao criar topic '{topic_name}'")
                    tudo_ok = False
                    
            except Exception as e:
                self.checker.print_error(f"Erro: {str(e)}")
                tudo_ok = False
        
        return tudo_ok


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    comando = sys.argv[1].lower()
    checker = EnvironmentChecker()
    
    if comando == "check":
        checker.run_all_checks()
        
    elif comando == "setup":
        results = checker.run_all_checks()
        
        if not results.get("Dependencies", False):
            setup = EnvironmentSetup(checker)
            setup.install_dependencies()
        
        if results.get("Docker", False):
            setup = EnvironmentSetup(checker)
            setup.start_docker_containers()
            setup.create_kafka_topics()
        
        # Re-check
        checker.run_all_checks()
        
    elif comando == "status":
        checker.run_all_checks()
        
    elif comando == "run-all":
        checker.print_header("Instruções de Execução")
        print("""
        Abra 4 TERMINAIS DIFERENTES e execute em cada um:
        
        Terminal 1: KAFKA BROKER (se não usando Docker Compose)
        $ docker-compose up
        
        Terminal 2: SCHEDULER PRODUCER
        $ cd DEV_ENVIRONMENT
        $ python scheduler_kafka.py
        
        Terminal 3: DATA WAREHOUSE CONSUMER
        $ cd DEV_ENVIRONMENT
        $ python dw_consumer_kafka.py
        
        Terminal 4: PDF PROCESSOR CONSUMER
        $ cd DEV_ENVIRONMENT
        $ python pdf_processor_kafka.py
        
        Kafka UI: http://localhost:8080
        """)
        
    else:
        print(f"Comando desconhecido: {comando}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
