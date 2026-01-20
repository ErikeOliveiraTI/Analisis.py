#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador de Backup SEM Privilégios de Administrador - VERSÃO BACKGROUND SILENCIOSA
====================================================================================

Monitora a hora e executa backup_producao.py às 18:00 todos os dias.
Funciona 100% em background SEM NENHUMA INTERAÇÃO COM USUÁRIO.

Características:
  ✓ Roda silenciosamente em background
  ✓ Sem janelas pop-up ou solicitações
  ✓ Sem print durante monitoramento
  ✓ Apenas logs em arquivo
  ✓ Executa automaticamente ao iniciar Windows

Uso:
  python agendador_sem_admin.py

Para deixar rodando 24/7:
  - Coloque iniciar_agendador_sem_admin.bat na pasta Startup do Windows
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
import sys

# Configuração
SCRIPT_BACKUP = Path("z:/git/init_/analise_py/backup_producao.py")
LOG_DIR = Path("z:/git/rotina/log")
LOG_FILE = LOG_DIR / f"agendador_{datetime.now().strftime('%Y-%m-%d')}.log"
HORARIO_BACKUP = 18  # 18h00
SILENCIOSO = True  # Se False, exibe prints

# Criar pasta de log
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

def log_mensagem(mensagem, forcar_print=False):
    """Registra mensagem no log (silenciosamente)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {mensagem}"
    
    # Apenas print se não está em modo silencioso
    if not SILENCIOSO or forcar_print:
        print(msg, flush=True)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()
    except Exception:
        pass

def verificar_script():
    """Verifica se o script de backup existe"""
    if not SCRIPT_BACKUP.exists():
        log_mensagem(f"❌ ERRO: Script não encontrado: {SCRIPT_BACKUP}", forcar_print=True)
        return False
    log_mensagem(f"✓ Script encontrado: {SCRIPT_BACKUP}")
    return True

def executar_backup():
    """Executa o script de backup_producao.py"""
    try:
        log_mensagem("➤ Iniciando backup...")
        log_mensagem(f"   Executando: {SCRIPT_BACKUP}")
        
        resultado = subprocess.run(
            ["python", str(SCRIPT_BACKUP)],
            capture_output=True,
            text=True,
            timeout=3600,
            creationflags=0x08000000  # CREATE_NO_WINDOW no Windows
        )
        
        # Registrar saída do backup nos logs
        if resultado.stdout:
            for linha in resultado.stdout.split('\n'):
                if linha.strip():
                    log_mensagem(f"   {linha}")
        
        if resultado.returncode == 0:
            log_mensagem("✓ Backup concluído com sucesso!")
            return True
        else:
            log_mensagem(f"⚠ Backup terminou com erro")
            if resultado.stderr:
                log_mensagem(f"   Erro: {resultado.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        log_mensagem("❌ ERRO: Backup excedeu timeout de 1 hora")
        return False
    except Exception as e:
        log_mensagem(f"❌ ERRO ao executar backup: {str(e)}")
        return False

def main():
    """Loop principal do agendador - COMPLETAMENTE SILENCIOSO"""
    
    # Primeira mensagem no log (sem print)
    log_mensagem("="*60)
    log_mensagem("AGENDADOR DE BACKUP INICIADO (SEM ADMIN - BACKGROUND SILENCIOSO)")
    log_mensagem("="*60)
    log_mensagem(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_mensagem(f"Script: {SCRIPT_BACKUP}")
    log_mensagem(f"Log: {LOG_FILE}")
    log_mensagem(f"Execução diária: {HORARIO_BACKUP}:00")
    log_mensagem(f"Modo silencioso: {'SIM (nenhuma interação)' if SILENCIOSO else 'NÃO (mostra prints)'}")
    log_mensagem("="*60)
    
    # Verificar script
    if not verificar_script():
        log_mensagem("❌ Script de backup não encontrado. Encerrando...")
        return
    
    ultima_execucao = None
    
    try:
        while True:
            try:
                now = datetime.now()
                
                # Se for 18:00 a 18:02
                if now.hour == HORARIO_BACKUP and now.minute >= 0 and now.minute <= 2:
                    # Verifica se já não executou hoje
                    data_hoje = now.strftime("%Y-%m-%d")
                    if ultima_execucao != data_hoje:
                        log_mensagem("\n" + "="*60)
                        log_mensagem(f"🕕 HORÁRIO DE BACKUP ACIONADO: {now.strftime('%H:%M:%S')}")
                        log_mensagem("="*60)
                        
                        # EXECUTA O BACKUP
                        executar_backup()
                        
                        ultima_execucao = data_hoje
                        
                        # Aguarda 3 minutos para não executar de novo
                        log_mensagem("⏸️  Agendador em repouso até amanhã...")
                        log_mensagem("="*60 + "\n")
                        time.sleep(180)
                
                # Verifica a hora a cada 30 segundos
                time.sleep(30)
                
            except Exception as e:
                log_mensagem(f"⚠ Erro no loop: {str(e)}")
                time.sleep(60)
    
    except KeyboardInterrupt:
        log_mensagem("\n⚠ Agendador interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        log_mensagem(f"❌ ERRO CRÍTICO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()