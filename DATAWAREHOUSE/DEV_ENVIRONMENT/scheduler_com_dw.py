#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler Integrado com Data Warehouse
======================================

Combinação do scheduler de backup com processamento automático 
no Data Warehouse.

Fluxo:
  1. Aguarda 17:00
  2. Executa backup_rede.bash
  3. Processa dados no Data Warehouse (ETL)
  4. Registra na auditoria

Uso:
  python scheduler_com_dw.py

Agendamento (Windows Startup):
  Adicionar iniciar_agendador.bat à pasta Startup
"""

import subprocess
import time
from datetime import datetime
import os
import sys
import platform
import json
from pathlib import Path
from typing import Dict, Optional

# Importar Data Warehouse
from data_warehouse import DataWarehouse, logger as dw_logger

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class ConfigScheduler:
    """Configuração do Scheduler Integrado"""
    
    # Detectar SO e ajustar caminhos
    sistema = platform.system()
    if "Windows" in sistema or "MINGW" in sistema or "mingw" in sistema.lower():
        BACKUP_SCRIPT = "/z/git/init_/analise_py/backup_rede.bash"
        LOG_PATH = "/z/git/rotina/log/scheduler_com_dw.log"
        SHELL = "bash"
    else:
        BACKUP_SCRIPT = "/mnt/z/git/init_/analise_py/backup_rede.bash"
        LOG_PATH = "/mnt/z/git/rotina/log/scheduler_com_dw.log"
        SHELL = "bash"
    
    # Horário de execução (17:00 = 5 PM)
    HORA_BACKUP = 17
    MINUTO_INICIO = 0
    MINUTO_FIM = 2  # Executar entre 17:00 e 17:02
    
    # Intervalo de verificação (segundos)
    INTERVALO_VERIFICACAO = 30
    
    # Timeout para backup (1 hora)
    TIMEOUT_BACKUP = 3600


# ============================================================================
# LOGGER INTEGRADO
# ============================================================================

import logging

def configurar_logger_scheduler():
    """Configura logging do scheduler"""
    log_dir = Path(ConfigScheduler.LOG_PATH).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("SchedulerDW")
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(ConfigScheduler.LOG_PATH, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(fh)
    
    return logger

scheduler_logger = configurar_logger_scheduler()

# ============================================================================
# CLASSE PRINCIPAL: SCHEDULER COM DW
# ============================================================================

class SchedulerComDataWarehouse:
    """
    Gerenciador de scheduling integrado com ETL automático
    """
    
    def __init__(self):
        """Inicializa scheduler e Data Warehouse"""
        self.data_warehouse = DataWarehouse()
        self.ultima_execucao = None
        self.backup_executado_hoje = False
        self.erros_hoje = []
        
        scheduler_logger.info("=" * 70)
        scheduler_logger.info("SCHEDULER COM DATA WAREHOUSE INICIALIZADO")
        scheduler_logger.info("=" * 70)
        scheduler_logger.info(f"Horário de backup: {ConfigScheduler.HORA_BACKUP}:00")
        scheduler_logger.info(f"Intervalo de verificação: {ConfigScheduler.INTERVALO_VERIFICACAO}s")
        scheduler_logger.info(f"Data Warehouse: {self.data_warehouse.db_path}")
        scheduler_logger.info("=" * 70)
    
    # ========================================================================
    # EXECUÇÃO DE BACKUP
    # ========================================================================
    
    def executar_backup(self) -> Dict[str, any]:
        """
        Executa script de backup via bash
        
        Returns:
            Dict com resultado da execução
        """
        init_time = datetime.now()
        resultado = {
            "sucesso": False,
            "tempo_ms": 0,
            "stdout": "",
            "stderr": "",
            "exit_code": -1
        }
        
        try:
            scheduler_logger.info("\n" + "=" * 70)
            scheduler_logger.info("INICIANDO BACKUP")
            scheduler_logger.info("=" * 70)
            
            # Executar script de backup
            proc = subprocess.Popen(
                [ConfigScheduler.SHELL, ConfigScheduler.BACKUP_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar com timeout
            try:
                stdout, stderr = proc.communicate(timeout=ConfigScheduler.TIMEOUT_BACKUP)
                resultado['exit_code'] = proc.returncode
                resultado['stdout'] = stdout
                resultado['stderr'] = stderr
                
                if proc.returncode == 0:
                    resultado['sucesso'] = True
                    scheduler_logger.info("✓ BACKUP EXECUTADO COM SUCESSO")
                    if stdout:
                        for linha in stdout.split('\n')[:10]:  # Primeiras 10 linhas
                            if linha.strip():
                                scheduler_logger.info(f"  {linha}")
                else:
                    scheduler_logger.error(f"✗ BACKUP FALHOU COM EXIT CODE {proc.returncode}")
                    if stderr:
                        for linha in stderr.split('\n')[:5]:
                            if linha.strip():
                                scheduler_logger.error(f"  {linha}")
                        
            except subprocess.TimeoutExpired:
                proc.kill()
                resultado['sucesso'] = False
                stderr_msg = "TIMEOUT: Backup excedeu tempo máximo permitido"
                scheduler_logger.error(f"✗ {stderr_msg}")
                
        except Exception as e:
            resultado['sucesso'] = False
            resultado['stderr'] = str(e)
            scheduler_logger.error(f"✗ Erro ao executar backup: {str(e)}")
        
        finally:
            resultado['tempo_ms'] = int((datetime.now() - init_time).total_seconds() * 1000)
        
        return resultado
    
    # ========================================================================
    # PROCESSAMENTO NO DATA WAREHOUSE
    # ========================================================================
    
    def processar_backup_no_dw(self, data_pasta: str) -> Dict[str, any]:
        """
        Processa backup no Data Warehouse após execução com sucesso
        
        Args:
            data_pasta: String no formato "DD MMM" (ex: "13 JAN")
            
        Returns:
            Dict com resultado do processamento
        """
        try:
            scheduler_logger.info("\n" + "=" * 70)
            scheduler_logger.info("PROCESSANDO BACKUP NO DATA WAREHOUSE")
            scheduler_logger.info("=" * 70)
            
            resultado = self.data_warehouse.processar_backup_diario(data_pasta)
            
            if resultado['status'] == 'sucesso':
                scheduler_logger.info("✓ DADOS CARREGADOS NO DATA WAREHOUSE COM SUCESSO")
                scheduler_logger.info(f"  Arquivos processados: {resultado['arquivos_processados']}")
                scheduler_logger.info(f"  Total de registros: {resultado['total_registros']}")
                scheduler_logger.info(f"  Tempo: {resultado['tempo_ms']}ms")
            else:
                scheduler_logger.error("✗ ERRO AO PROCESSAR DADOS NO DATA WAREHOUSE")
                for erro in resultado['erros']:
                    scheduler_logger.error(f"  - {erro}")
            
            return resultado
            
        except Exception as e:
            scheduler_logger.error(f"✗ Erro ao processar backup no DW: {str(e)}")
            return {
                "status": "falha",
                "erro": str(e)
            }
    
    # ========================================================================
    # CICLO PRINCIPAL
    # ========================================================================
    
    def verificar_hora_backup(self, now: datetime) -> bool:
        """Verifica se é hora de executar backup"""
        return (
            now.hour == ConfigScheduler.HORA_BACKUP and
            ConfigScheduler.MINUTO_INICIO <= now.minute <= ConfigScheduler.MINUTO_FIM
        )
    
    def resetar_flag_diaria(self, now: datetime):
        """Reseta flag diária à meia-noite"""
        if now.hour == 0 and now.minute == 0:
            self.backup_executado_hoje = False
            self.erros_hoje = []
            scheduler_logger.info("✓ Flag diária resetada (meia-noite)")
    
    def executar_ciclo(self):
        """
        Executa um ciclo de verificação
        Retorna True se backup foi executado
        """
        now = datetime.now()
        
        # Resetar flag à meia-noite
        self.resetar_flag_diaria(now)
        
        # Verificar se é hora de backup
        if not self.verificar_hora_backup(now):
            scheduler_logger.debug(f"[{now.strftime('%H:%M:%S')}] Aguardando horário de backup...")
            return False
        
        # Evitar execução duplicada
        if self.backup_executado_hoje:
            scheduler_logger.info(f"[{now.strftime('%H:%M:%S')}] Backup já executado hoje. Aguardando próximo dia...")
            return False
        
        scheduler_logger.info(f"[{now.strftime('%H:%M:%S')}] ► HORA DE BACKUP! Iniciando rotina...")
        
        # Gerar nome da pasta (DD MMM)
        data_pasta = now.strftime("%d %b").upper()  # Ex: "13 JAN"
        
        try:
            # 1. Executar backup
            resultado_backup = self.executar_backup()
            
            if not resultado_backup['sucesso']:
                self.erros_hoje.append(f"Backup falhou: {resultado_backup['stderr']}")
                scheduler_logger.error("✗ Abortando processamento: backup falhou")
                return False
            
            # 2. Processar no Data Warehouse
            resultado_dw = self.processar_backup_no_dw(data_pasta)
            
            # 3. Marcar como executado
            self.backup_executado_hoje = True
            self.ultima_execucao = now
            
            # 4. Log final
            scheduler_logger.info("\n" + "=" * 70)
            scheduler_logger.info("✓ CICLO COMPLETO EXECUTADO COM SUCESSO")
            scheduler_logger.info("=" * 70)
            scheduler_logger.info(f"Data/Hora: {now.isoformat()}")
            scheduler_logger.info(f"Próximo backup: Amanhã às {ConfigScheduler.HORA_BACKUP}:00")
            scheduler_logger.info("=" * 70 + "\n")
            
            return True
            
        except Exception as e:
            erro_msg = f"Erro crítico no ciclo: {str(e)}"
            self.erros_hoje.append(erro_msg)
            scheduler_logger.error(f"✗ {erro_msg}")
            return False
    
    # ========================================================================
    # LOOP PRINCIPAL
    # ========================================================================
    
    def executar_indefinidamente(self):
        """
        Loop infinito de monitoramento
        Executa indefinidamente até ser interrompido (Ctrl+C)
        """
        scheduler_logger.info(f"\n✓ Iniciando monitoramento...")
        scheduler_logger.info(f"✓ Sistema aguardando horário: {ConfigScheduler.HORA_BACKUP}:00")
        scheduler_logger.info(f"✓ Intervalo de verificação: {ConfigScheduler.INTERVALO_VERIFICACAO}s")
        scheduler_logger.info(f"✓ Pressione Ctrl+C para parar\n")
        
        contador_ciclos = 0
        
        try:
            while True:
                contador_ciclos += 1
                
                # Executar ciclo
                self.executar_ciclo()
                
                # Aguardar próxima verificação
                time.sleep(ConfigScheduler.INTERVALO_VERIFICACAO)
                
        except KeyboardInterrupt:
            scheduler_logger.info("\n\n" + "=" * 70)
            scheduler_logger.info("SCHEDULER INTERROMPIDO PELO USUÁRIO")
            scheduler_logger.info("=" * 70)
            scheduler_logger.info(f"Ciclos executados: {contador_ciclos}")
            if self.ultima_execucao:
                scheduler_logger.info(f"Última execução: {self.ultima_execucao.isoformat()}")
            if self.erros_hoje:
                scheduler_logger.info(f"Erros: {len(self.erros_hoje)}")
                for erro in self.erros_hoje:
                    scheduler_logger.error(f"  - {erro}")
            scheduler_logger.info("=" * 70 + "\n")
            
        except Exception as e:
            scheduler_logger.error(f"\n✗ ERRO CRÍTICO NO SCHEDULER: {str(e)}")
            scheduler_logger.error("Encerrando...")


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def teste_rapido():
    """Teste rápido: processa backup de hoje (útil para debugging)"""
    scheduler_logger.info("MODO TESTE: Processando backup de hoje...")
    
    try:
        dw = DataWarehouse()
        data_pasta = datetime.now().strftime("%d %b").upper()
        scheduler_logger.info(f"Data de teste: {data_pasta}")
        
        resultado = dw.processar_backup_diario(data_pasta)
        scheduler_logger.info(f"Resultado: {json.dumps(resultado, indent=2)}")
        
    except Exception as e:
        scheduler_logger.error(f"Erro no teste: {str(e)}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Suportar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--teste":
            teste_rapido()
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            print(f"Argumento desconhecido: {sys.argv[1]}")
            print("Use: --teste ou --help")
    else:
        # Modo normal: executar scheduler
        scheduler = SchedulerComDataWarehouse()
        scheduler.executar_indefinidamente()
