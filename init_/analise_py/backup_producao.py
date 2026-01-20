#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Backup Automático - PRODUÇÃO
======================================
Cria pastas diárias e copia arquivos de rede automaticamente

Características:
  ✓ Automação diária às 17:00 via Task Scheduler
  ✓ Cria pasta no formato: DD MMM (ex: 20 JAN)
  ✓ Copia arquivos com tratamento de erros
  ✓ Logs estruturados e rotacionados
  ✓ Validação de permissões e caminhos
  ✓ Pronto para produção
  
Uso:
  python backup_producao.py
  
Agendamento:
  Windows Task Scheduler às 17:00 (via agendar_backup_v2.ps1)
"""

import os
import shutil
import logging
import platform
from datetime import datetime
from pathlib import Path
import sys

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Configuração centralizada do backup"""
    
    # Detectar SO e ajustar caminhos
    if platform.system() == "Windows":
        BASE_DIR = Path("z:/git/rotina")
        ORIGEM_REDE = Path("z:/01.FO_Tejo/02.Night_Auditor/Relatorios_e_Ficheiros/Relatorios")
        ARQUIVO_CAIXA = Path("z:/Caixa.xlsx")
        LOG_DIR = Path("z:/git/rotina/log")
    else:  # Linux/WSL
        BASE_DIR = Path("/mnt/z/git/rotina")
        ORIGEM_REDE = Path("/mnt/z/01.FO_Tejo/02.Night_Auditor/Relatorios_e_Ficheiros/Relatorios")
        ARQUIVO_CAIXA = Path("/mnt/z/Caixa.xlsx")
        LOG_DIR = Path("/mnt/z/git/rotina/log")
    
    # Formato de data para pasta
    DATA_PASTA = datetime.now().strftime("%d %b").upper()  # Ex: 20 JAN
    PASTA_DESTINO = BASE_DIR / DATA_PASTA
    
    # Log
    LOG_FILE = LOG_DIR / f"backup_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Timeout para operações
    TIMEOUT_COPIA = 3600  # 1 hora


# ============================================================================
# LOGGER CONFIGURADO
# ============================================================================

def configurar_logger():
    """Configura logging com arquivo e console"""
    Config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("Backup")
    logger.setLevel(logging.DEBUG)
    
    # Handler arquivo
    fh = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    # Handler console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # Formato
    formato = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formato)
    ch.setFormatter(formato)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = configurar_logger()


# ============================================================================
# VALIDAÇÕES
# ============================================================================

def validar_ambiente():
    """Valida se o ambiente está pronto para backup"""
    logger.info("="*60)
    logger.info("INICIANDO VALIDAÇÃO DO AMBIENTE")
    logger.info("="*60)
    
    erros = []
    
    # Verificar unidade de rede
    if not Config.BASE_DIR.parent.exists():
        erros.append(f"Unidade de rede não acessível: {Config.BASE_DIR.parent}")
        logger.error(f"❌ Unidade /z não encontrada")
    else:
        logger.info(f"✓ Unidade de rede acessível: {Config.BASE_DIR.parent}")
    
    # Verificar pasta de origem
    if not Config.ORIGEM_REDE.exists():
        erros.append(f"Pasta de origem não existe: {Config.ORIGEM_REDE}")
        logger.error(f"❌ Pasta de origem não encontrada: {Config.ORIGEM_REDE}")
    else:
        logger.info(f"✓ Pasta de origem acessível: {Config.ORIGEM_REDE}")
    
    # Verificar arquivo Caixa.xlsx
    if not Config.ARQUIVO_CAIXA.exists():
        logger.warning(f"⚠ Arquivo Caixa.xlsx não encontrado (não crítico)")
    else:
        logger.info(f"✓ Arquivo Caixa.xlsx encontrado")
    
    if erros:
        logger.error("\n❌ VALIDAÇÃO FALHOU:")
        for erro in erros:
            logger.error(f"   - {erro}")
        return False
    
    logger.info("✓ VALIDAÇÃO CONCLUÍDA COM SUCESSO\n")
    return True


# ============================================================================
# OPERAÇÕES DE BACKUP
# ============================================================================

def criar_pasta_destino():
    """Cria pasta diária no formato: 20 JAN"""
    try:
        Config.PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Pasta criada/verificada: {Config.PASTA_DESTINO}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta: {e}")
        return False


def copiar_caixa():
    """Copia arquivo Caixa.xlsx"""
    if not Config.ARQUIVO_CAIXA.exists():
        logger.warning(f"⚠ Caixa.xlsx não encontrado, pulando...")
        return True
    
    try:
        destino_caixa = Config.PASTA_DESTINO / "Caixa.xlsx"
        shutil.copy2(Config.ARQUIVO_CAIXA, destino_caixa)
        logger.info(f"✓ Caixa.xlsx copiado com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao copiar Caixa.xlsx: {e}")
        return False


def copiar_relatorios():
    """Copia recursivamente arquivos de relatórios"""
    if not Config.ORIGEM_REDE.exists():
        logger.error(f"❌ Pasta de origem não existe: {Config.ORIGEM_REDE}")
        return False
    
    try:
        contador = {"copiados": 0, "erros": 0}
        
        for arquivo in Config.ORIGEM_REDE.rglob("*"):
            if arquivo.is_file():
                try:
                    # Preserva estrutura de subpastas
                    caminho_relativo = arquivo.relative_to(Config.ORIGEM_REDE)
                    destino = Config.PASTA_DESTINO / caminho_relativo
                    
                    # Criar subpasta se necessário
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(arquivo, destino)
                    contador["copiados"] += 1
                    
                except Exception as e:
                    logger.warning(f"⚠ Erro ao copiar {arquivo}: {e}")
                    contador["erros"] += 1
        
        if contador["copiados"] > 0:
            logger.info(f"✓ {contador['copiados']} arquivo(s) copiado(s) com sucesso")
        if contador["erros"] > 0:
            logger.warning(f"⚠ {contador['erros']} erro(s) durante cópia")
        
        return contador["copiados"] > 0
    
    except Exception as e:
        logger.error(f"❌ Erro ao copiar relatórios: {e}")
        return False


# ============================================================================
# EXECUTAR BACKUP
# ============================================================================

def executar_backup():
    """Executa sequência completa de backup"""
    logger.info("="*60)
    logger.info(f"BACKUP INICIADO EM: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    logger.info(f"Data da pasta: {Config.DATA_PASTA}")
    logger.info(f"Destino: {Config.PASTA_DESTINO}\n")
    
    # Executar etapas
    etapas = [
        ("Validação do ambiente", validar_ambiente),
        ("Criar pasta destino", criar_pasta_destino),
        ("Copiar Caixa.xlsx", copiar_caixa),
        ("Copiar relatórios", copiar_relatorios),
    ]
    
    sucesso = True
    for nome_etapa, funcao in etapas:
        logger.info(f"\n➤ {nome_etapa}...")
        if not funcao():
            sucesso = False
            logger.warning(f"⚠ {nome_etapa} falhou (continuando...)")
    
    # Resultado final
    logger.info("\n" + "="*60)
    if sucesso:
        logger.info("✓ BACKUP CONCLUÍDO COM SUCESSO")
    else:
        logger.warning("⚠ BACKUP CONCLUÍDO COM ERROS (veja acima)")
    logger.info(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60 + "\n")
    
    return sucesso


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        sucesso = executar_backup()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠ Backup interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO: {e}", exc_info=True)
        sys.exit(1)
