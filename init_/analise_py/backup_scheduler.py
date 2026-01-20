#!/usr/bin/env python3
# Script de Agendamento de Backup
# Executa o backup automaticamente às 17:00 todos os dias
# Otimizado para funcionar em bash/Git Bash

import subprocess
import time
from datetime import datetime
import os
import sys
import platform

# Detectar SO e ajustar caminhos
if platform.system() == "Windows" or "MINGW" in platform.system():
    # Em Git Bash no Windows, usar caminhos Unix
    SCRIPT_PATH = "/z/git/init_/analise_py/backup_rede.bash"
    LOG_PATH = "/z/git/rotina/log/scheduler.log"
    SHELL = "bash"
else:
    # Em Linux/WSL, usar caminhos Unix
    SCRIPT_PATH = "/mnt/z/git/init_/analise_py/backup_rede.bash"
    LOG_PATH = "/mnt/z/git/rotina/log/scheduler.log"
    SHELL = "bash"

def criar_pasta_log():
    """Cria a pasta de log se não existir"""
    try:
        log_dir = os.path.dirname(LOG_PATH)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"AVISO: Não consegui criar pasta de log: {e}")

def registrar_log(mensagem):
    """Registra mensagens no arquivo de log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {mensagem}"
    print(msg)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"AVISO: Não consegui escrever no log: {e}")

def executar_backup():
    """Executa o script de backup via bash"""
    try:
        registrar_log("Iniciando backup...")
        
        # Executar via bash com shell=True para melhor compatibilidade
        comando = f'bash "{SCRIPT_PATH}"'
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=3600  # Máximo 1 hora
        )
        
        if resultado.returncode == 0:
            registrar_log("Backup concluído com sucesso!")
            return True
        else:
            registrar_log(f"AVISO: Backup terminou com código de erro: {resultado.returncode}")
            if resultado.stderr:
                registrar_log(f"Erro: {resultado.stderr}")
            return False
    except subprocess.TimeoutExpired:
        registrar_log("ERRO: Backup excedeu timeout de 1 hora")
        return False
    except FileNotFoundError:
        registrar_log(f"ERRO: Script não encontrado em: {SCRIPT_PATH}")
        return False
    except Exception as e:
        registrar_log(f"ERRO ao executar backup: {str(e)}")
        return False

def main():
    """Loop principal do agendador"""
    criar_pasta_log()
    
    registrar_log("========================================")
    registrar_log("Agendador de Backup iniciado")
    registrar_log(f"Sistema operacional: {platform.system()}")
    registrar_log(f"Shell: {SHELL}")
    registrar_log(f"Script: {SCRIPT_PATH}")
    registrar_log(f"Log: {LOG_PATH}")
    registrar_log("Execução diária: 17:00 (5 PM)")
    registrar_log("========================================")
    
    ultima_execucao = None
    
    try:
        while True:
            try:
                now = datetime.now()
                
                # Verifica se é 17:00 ou se passou
                if now.hour == 17 and now.minute >= 0 and now.minute <= 2:
                    # Verifica se já não executou hoje
                    data_hoje = now.strftime("%Y-%m-%d")
                    if ultima_execucao != data_hoje:
                        executar_backup()
                        ultima_execucao = data_hoje
                        # Aguarda 3 minutos para não executar de novo
                        registrar_log("Agendador em repouso até amanhã...")
                        time.sleep(180)
                
                # Verifica a hora a cada 30 segundos
                time.sleep(30)
                
            except KeyboardInterrupt:
                registrar_log("Agendador interrompido pelo usuário")
                sys.exit(0)
            except Exception as e:
                registrar_log(f"ERRO no loop principal: {str(e)}")
                time.sleep(60)
    except KeyboardInterrupt:
        registrar_log("Agendador finalizado")
        sys.exit(0)

if __name__ == "__main__":
    main()

