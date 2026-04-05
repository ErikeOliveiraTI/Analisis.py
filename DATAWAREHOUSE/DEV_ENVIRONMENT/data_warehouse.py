#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Warehouse com ETL - Sistema de Relatórios
==============================================

Módulo responsável por:
  ✓ Extração de dados dos arquivos de backup
  ✓ Transformação e normalização
  ✓ Carga em banco de dados centralizado (SQLite)
  ✓ Consultas estruturadas via Pandas

Arquitetura:
  - Origem: /z/git/rotina/DD MMM/*.xlsx
  - Processamento: Normalização em 3ª forma normal (3NF)
  - Destino: /z/git/rotina/data_warehouse.db (SQLite)
  - Acesso: Pandas + SQL

Uso:
  from data_warehouse import DataWarehouse
  dw = DataWarehouse()
  dw.processar_backup_diario("13 JAN")
  dados = dw.consultar_caixa(data_inicio="2024-01-01")
"""

import os
import sqlite3
import pandas as pd
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import platform
from typing import List, Dict, Optional, Tuple
import hashlib

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class ConfigDW:
    """Configuração centralizada do Data Warehouse"""
    
    if platform.system() == "Windows":
        BASE_DIR = Path("z:/git/rotina")
        DB_PATH = Path("z:/git/rotina/data_warehouse.db")
        LOG_DIR = Path("z:/git/rotina/log")
    else:  # Linux/WSL
        BASE_DIR = Path("/mnt/z/git/rotina")
        DB_PATH = Path("/mnt/z/git/rotina/data_warehouse.db")
        LOG_DIR = Path("/mnt/z/git/rotina/log")
    
    LOG_FILE = LOG_DIR / "data_warehouse.log"
    CHARSET = 'utf-8'

# ============================================================================
# LOGGER
# ============================================================================

def configurar_logger():
    """Configura logging"""
    ConfigDW.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("DataWarehouse")
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(ConfigDW.LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(fh)
    
    return logger

logger = configurar_logger()

# ============================================================================
# CLASSE PRINCIPAL: DATA WAREHOUSE
# ============================================================================

class DataWarehouse:
    """
    Gerenciador central do Data Warehouse
    Responsável pelo ciclo completo: Extração → Transformação → Carga
    """
    
    def __init__(self):
        """Inicializa Data Warehouse e cria banco se necessário"""
        self.db_path = ConfigDW.DB_PATH
        logger.info(f"Inicializando Data Warehouse: {self.db_path}")
        self._criar_banco_dados()
    
    # ========================================================================
    # INICIALIZAÇÃO E SCHEMA
    # ========================================================================
    
    def _criar_banco_dados(self):
        """Cria tabelas normalizadas em 3NF se não existirem"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Tabela de Datas (Dimensão Temporal)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_datas (
                    id_data INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE UNIQUE NOT NULL,
                    dia INTEGER,
                    mes INTEGER,
                    ano INTEGER,
                    nome_dia_semana TEXT,
                    eh_fim_de_semana BOOLEAN,
                    semana_do_ano INTEGER,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de Tipos de Arquivo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_tipos_arquivo (
                    id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_tipo TEXT UNIQUE NOT NULL,
                    extensao TEXT,
                    descricao TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de Backup (Fato)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fato_backups (
                    id_backup INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_data INTEGER NOT NULL,
                    id_tipo INTEGER NOT NULL,
                    nome_arquivo TEXT NOT NULL,
                    caminho_relativo TEXT NOT NULL,
                    hash_arquivo TEXT UNIQUE,
                    tamanho_bytes INTEGER,
                    numero_linhas INTEGER,
                    numero_colunas INTEGER,
                    status TEXT DEFAULT 'processado',
                    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_data) REFERENCES dim_datas(id_data),
                    FOREIGN KEY (id_tipo) REFERENCES dim_tipos_arquivo(id_tipo)
                )
            """)
            
            # Tabela de Caixa (Fato Detalhado)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fato_caixa (
                    id_caixa INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_backup INTEGER,
                    id_data INTEGER NOT NULL,
                    data_operacao DATE,
                    descricao TEXT,
                    valor_entrada DECIMAL(12, 2),
                    valor_saida DECIMAL(12, 2),
                    saldo DECIMAL(12, 2),
                    metodo_pagamento TEXT,
                    referencia_externa TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_backup) REFERENCES fato_backups(id_backup),
                    FOREIGN KEY (id_data) REFERENCES dim_datas(id_data)
                )
            """)
            
            # Tabela de Relatórios (Fato Sumário)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fato_relatorios (
                    id_relatorio INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_backup INTEGER,
                    id_data INTEGER NOT NULL,
                    nome_relatorio TEXT,
                    tipo_relatorio TEXT,
                    total_registros INTEGER,
                    valor_total DECIMAL(15, 2),
                    periodo_inicio DATE,
                    periodo_fim DATE,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_backup) REFERENCES fato_backups(id_backup),
                    FOREIGN KEY (id_data) REFERENCES dim_datas(id_data)
                )
            """)
            
            # Tabela de Auditoria (Log de Processamento)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditoria_processamento (
                    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_backup INTEGER,
                    id_data INTEGER,
                    tipo_operacao TEXT,
                    descricao TEXT,
                    status TEXT,
                    tempo_processamento_ms INTEGER,
                    erro_mensagem TEXT,
                    data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_backup) REFERENCES fato_backups(id_backup),
                    FOREIGN KEY (id_data) REFERENCES dim_datas(id_data)
                )
            """)
            
            # Criar índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_datas_data ON dim_datas(data)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_backups_data ON fato_backups(id_data)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_caixa_data ON fato_caixa(id_data)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relatorios_data ON fato_relatorios(id_data)")
            
            conn.commit()
            conn.close()
            logger.info("✓ Banco de dados criado/verificado com sucesso")
            
        except Exception as e:
            logger.error(f"✗ Erro ao criar banco de dados: {str(e)}")
            raise
    
    # ========================================================================
    # EXTRAÇÃO: Leitura de Arquivos
    # ========================================================================
    
    def extrair_arquivo_excel(self, caminho_arquivo: Path) -> Optional[pd.DataFrame]:
        """
        Extrai dados de arquivo Excel
        
        Args:
            caminho_arquivo: Path do arquivo .xlsx
            
        Returns:
            DataFrame com dados, ou None se falha
        """
        try:
            if not caminho_arquivo.exists():
                logger.warning(f"Arquivo não encontrado: {caminho_arquivo}")
                return None
            
            df = pd.read_excel(caminho_arquivo)
            logger.info(f"✓ Extraído {len(df)} linhas de {caminho_arquivo.name}")
            return df
            
        except Exception as e:
            logger.error(f"✗ Erro ao extrair {caminho_arquivo.name}: {str(e)}")
            return None
    
    # ========================================================================
    # TRANSFORMAÇÃO: Normalização e Limpeza
    # ========================================================================
    
    def normalizar_caixa(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza dados de Caixa.xlsx
        Remove duplicatas, padroniza tipos, trata missing values
        """
        try:
            import unicodedata
            
            # Criar cópia
            df = df.copy()
            
            # Remover linhas completamente vazias
            df = df.dropna(how='all')
            
            # Normalizar nomes de colunas (lowercase, sem espaços, sem acentos)
            def remove_accents(text):
                nfd = unicodedata.normalize('NFD', str(text))
                return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
            
            df.columns = [remove_accents(col).strip().lower().replace(' ', '_') for col in df.columns]
            
            # Converter colunas numéricas
            numeric_cols = ['valor_entrada', 'valor_saida', 'saldo']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Converter colunas de data
            date_cols = ['data_operacao', 'data']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Remover duplicatas baseadas em colunas chave
            df = df.drop_duplicates(keep='first')
            
            logger.info(f"✓ Normalizado: {len(df)} linhas")
            return df
            
        except Exception as e:
            logger.error(f"✗ Erro ao normalizar Caixa: {str(e)}")
            return df
    
    def normalizar_relatorio(self, df: pd.DataFrame, nome_relatorio: str) -> pd.DataFrame:
        """
        Normaliza dados de Relatório
        """
        try:
            import unicodedata
            
            df = df.copy()
            df = df.dropna(how='all')
            
            # Normalizar nomes de colunas (remove acentos)
            def remove_accents(text):
                nfd = unicodedata.normalize('NFD', str(text))
                return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
            
            df.columns = [remove_accents(col).strip().lower().replace(' ', '_') for col in df.columns]
            
            # Normalizar valores monetários
            for col in df.columns:
                if 'valor' in col or 'total' in col:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.drop_duplicates(keep='first')
            logger.info(f"✓ Relatório '{nome_relatorio}' normalizado: {len(df)} linhas")
            return df
            
        except Exception as e:
            logger.error(f"✗ Erro ao normalizar relatório {nome_relatorio}: {str(e)}")
            return df
    
    # ========================================================================
    # CARGA: Inserção no Banco
    # ========================================================================
    
    def _obter_ou_criar_data(self, data: datetime) -> int:
        """Obtém ID da data ou cria se não existir"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            data_str = data.date()
            
            cursor.execute("SELECT id_data FROM dim_datas WHERE data = ?", (data_str,))
            resultado = cursor.fetchone()
            
            if resultado:
                conn.close()
                return resultado[0]
            
            # Criar nova data
            cursor.execute("""
                INSERT INTO dim_datas 
                (data, dia, mes, ano, nome_dia_semana, eh_fim_de_semana, semana_do_ano)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data_str,
                data.day,
                data.month,
                data.year,
                data.strftime("%A"),
                data.weekday() >= 5,
                data.isocalendar()[1]
            ))
            conn.commit()
            conn.close()
            
            # Reobter ID
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT id_data FROM dim_datas WHERE data = ?", (data_str,))
            id_data = cursor.fetchone()[0]
            conn.close()
            
            return id_data
            
        except Exception as e:
            logger.error(f"✗ Erro ao obter/criar data: {str(e)}")
            raise
    
    def _calcular_hash_arquivo(self, caminho: Path) -> str:
        """Calcula SHA256 do arquivo"""
        try:
            sha256_hash = hashlib.sha256()
            with open(caminho, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None
    
    def carregar_caixa(self, df: pd.DataFrame, id_backup: int, id_data: int):
        """Carrega dados normalizados de Caixa no banco"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            for idx, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO fato_caixa
                    (id_backup, id_data, data_operacao, descricao, 
                     valor_entrada, valor_saida, saldo, metodo_pagamento, referencia_externa)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_backup,
                    id_data,
                    row.get('data_operacao'),
                    row.get('descricao'),
                    row.get('valor_entrada'),
                    row.get('valor_saida'),
                    row.get('saldo'),
                    row.get('metodo_pagamento'),
                    row.get('referencia_externa')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"✓ Carregadas {len(df)} linhas de Caixa")
            
        except Exception as e:
            logger.error(f"✗ Erro ao carregar Caixa: {str(e)}")
    
    # ========================================================================
    # PROCESSAMENTO: ETL Completo
    # ========================================================================
    
    def processar_backup_diario(self, data_pasta: str) -> Dict:
        """
        Processa backup completo de um dia
        
        Args:
            data_pasta: String no formato "DD MMM" (ex: "13 JAN")
            
        Returns:
            Dict com status do processamento
        """
        init_time = datetime.now()
        resultado = {
            "data_pasta": data_pasta,
            "status": "falha",
            "arquivos_processados": 0,
            "total_registros": 0,
            "tempo_ms": 0,
            "erros": []
        }
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"PROCESSANDO BACKUP: {data_pasta}")
            logger.info(f"{'='*60}")
            
            pasta_dia = ConfigDW.BASE_DIR / data_pasta
            if not pasta_dia.exists():
                msg = f"Pasta não encontrada: {pasta_dia}"
                logger.error(f"✗ {msg}")
                resultado["erros"].append(msg)
                return resultado
            
            # Obter ID da data
            try:
                parts = data_pasta.split()
                dia = int(parts[0])
                mes_str = parts[1] if len(parts) > 1 else "JAN"
                meses = {
                    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
                    "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12
                }
                mes = meses.get(mes_str.upper(), 1)
                ano = datetime.now().year
                data_obj = datetime(ano, mes, dia)
                id_data = self._obter_ou_criar_data(data_obj)
                logger.info(f"✓ Data registrada: {data_obj.date()}")
            except Exception as e:
                msg = f"Erro ao processar data: {str(e)}"
                resultado["erros"].append(msg)
                logger.error(f"✗ {msg}")
                return resultado
            
            # Processar Caixa.xlsx
            caixa_path = pasta_dia / "Caixa.xlsx"
            if caixa_path.exists():
                try:
                    df_caixa = self.extrair_arquivo_excel(caixa_path)
                    if df_caixa is not None:
                        df_caixa = self.normalizar_caixa(df_caixa)
                        
                        # Registrar backup
                        hash_caixa = self._calcular_hash_arquivo(caixa_path)
                        id_backup = self._registrar_backup(
                            "Caixa.xlsx", "caixa", caixa_path, hash_caixa, 
                            len(df_caixa), len(df_caixa.columns), id_data
                        )
                        
                        # Carregar dados
                        self.carregar_caixa(df_caixa, id_backup, id_data)
                        resultado["arquivos_processados"] += 1
                        resultado["total_registros"] += len(df_caixa)
                except Exception as e:
                    msg = f"Erro ao processar Caixa.xlsx: {str(e)}"
                    resultado["erros"].append(msg)
                    logger.error(f"✗ {msg}")
            
            # Processar Relatórios
            relatorios_dir = pasta_dia / "relatorios"
            if relatorios_dir.exists():
                for arquivo in relatorios_dir.glob("*.xlsx"):
                    try:
                        df_rel = self.extrair_arquivo_excel(arquivo)
                        if df_rel is not None:
                            df_rel = self.normalizar_relatorio(df_rel, arquivo.stem)
                            
                            hash_rel = self._calcular_hash_arquivo(arquivo)
                            id_backup = self._registrar_backup(
                                arquivo.name, "relatorio", arquivo, hash_rel,
                                len(df_rel), len(df_rel.columns), id_data
                            )
                            
                            resultado["arquivos_processados"] += 1
                            resultado["total_registros"] += len(df_rel)
                    except Exception as e:
                        msg = f"Erro ao processar {arquivo.name}: {str(e)}"
                        resultado["erros"].append(msg)
                        logger.error(f"✗ {msg}")
            
            resultado["status"] = "sucesso"
            
        except Exception as e:
            msg = f"Erro crítico no processamento: {str(e)}"
            resultado["erros"].append(msg)
            logger.error(f"✗ {msg}")
        
        finally:
            tempo_ms = int((datetime.now() - init_time).total_seconds() * 1000)
            resultado["tempo_ms"] = tempo_ms
            logger.info(f"\n✓ RESUMO: {resultado['arquivos_processados']} arquivos, "
                       f"{resultado['total_registros']} registros em {tempo_ms}ms")
        
        return resultado
    
    def _registrar_backup(self, nome_arquivo, tipo, caminho_relativo, hash_arq, 
                         linhas, colunas, id_data) -> int:
        """Registra arquivo de backup na fato_backups"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fato_backups
                (id_data, id_tipo, nome_arquivo, caminho_relativo, hash_arquivo,
                 tamanho_bytes, numero_linhas, numero_colunas, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_data,
                self._obter_id_tipo(tipo),
                nome_arquivo,
                str(caminho_relativo),
                hash_arq,
                0,
                linhas,
                colunas,
                "processado"
            ))
            
            conn.commit()
            id_backup = cursor.lastrowid
            conn.close()
            
            return id_backup
            
        except Exception as e:
            logger.error(f"✗ Erro ao registrar backup: {str(e)}")
            raise
    
    def _obter_id_tipo(self, tipo: str) -> int:
        """Obtém ID do tipo de arquivo"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_tipo FROM dim_tipos_arquivo WHERE nome_tipo = ?", (tipo,))
            resultado = cursor.fetchone()
            
            if resultado:
                conn.close()
                return resultado[0]
            
            cursor.execute(
                "INSERT INTO dim_tipos_arquivo (nome_tipo, extensao) VALUES (?, ?)",
                (tipo, "xlsx")
            )
            conn.commit()
            id_tipo = cursor.lastrowid
            conn.close()
            
            return id_tipo
            
        except Exception as e:
            logger.error(f"✗ Erro ao obter ID tipo: {str(e)}")
            return 1
    
    # ========================================================================
    # CONSULTAS: Interface Pandas
    # ========================================================================
    
    def consultar_caixa(self, data_inicio: Optional[str] = None, 
                       data_fim: Optional[str] = None) -> pd.DataFrame:
        """
        Consulta dados de Caixa com filtros por data
        
        Args:
            data_inicio: String "YYYY-MM-DD" ou None
            data_fim: String "YYYY-MM-DD" ou None
            
        Returns:
            DataFrame com caixa filtrado
        """
        try:
            query = """
                SELECT 
                    c.id_caixa, d.data, c.data_operacao, c.descricao,
                    c.valor_entrada, c.valor_saida, c.saldo,
                    c.metodo_pagamento, c.referencia_externa,
                    c.criado_em
                FROM fato_caixa c
                JOIN dim_datas d ON c.id_data = d.id_data
                WHERE 1=1
            """
            
            params = []
            if data_inicio:
                query += " AND d.data >= ?"
                params.append(data_inicio)
            if data_fim:
                query += " AND d.data <= ?"
                params.append(data_fim)
            
            query += " ORDER BY d.data DESC"
            
            conn = sqlite3.connect(str(self.db_path))
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"✗ Erro ao consultar Caixa: {str(e)}")
            return pd.DataFrame()
    
    def consultar_relatorios(self, data_inicio: Optional[str] = None,
                            data_fim: Optional[str] = None) -> pd.DataFrame:
        """Consulta dados de Relatórios"""
        try:
            query = """
                SELECT 
                    r.id_relatorio, d.data, r.nome_relatorio, r.tipo_relatorio,
                    r.total_registros,r.valor_total, r.periodo_inicio, 
                    r.periodo_fim, r.criado_em
                FROM fato_relatorios r
                JOIN dim_datas d ON r.id_data = d.id_data
                WHERE 1=1
            """
            
            params = []
            if data_inicio:
                query += " AND d.data >= ?"
                params.append(data_inicio)
            if data_fim:
                query += " AND d.data <= ?"
                params.append(data_fim)
            
            query += " ORDER BY d.data DESC"
            
            conn = sqlite3.connect(str(self.db_path))
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"✗ Erro ao consultar Relatórios: {str(e)}")
            return pd.DataFrame()
    
    def resumo_diario(self, data: str) -> Dict:
        """Retorna resumo diário de caixa"""
        try:
            query = """
                SELECT 
                    COUNT(*) as num_operacoes,
                    SUM(valor_entrada) as total_entrada,
                    SUM(valor_saida) as total_saida
                FROM fato_caixa
                WHERE id_data IN (SELECT id_data FROM dim_datas WHERE data = ?)
            """
            
            conn = sqlite3.connect(str(self.db_path))
            df = pd.read_sql_query(query, conn, params=[data])
            conn.close()
            
            if not df.empty and len(df) > 0:
                row = df.iloc[0]
                total_entrada = float(row['total_entrada']) if row['total_entrada'] else 0.0
                total_saida = float(row['total_saida']) if row['total_saida'] else 0.0
                return {
                    "data": data,
                    "num_operacoes": int(row['num_operacoes']) if row['num_operacoes'] else 0,
                    "total_entrada": total_entrada,
                    "total_saida": total_saida,
                    "saldo_final": total_entrada - total_saida
                }
            
            return {
                "data": data,
                "num_operacoes": 0,
                "total_entrada": 0.0,
                "total_saida": 0.0,
                "saldo_final": 0.0
            }
            
        except Exception as e:
            logger.error(f"✗ Erro ao gerar resumo diário: {str(e)}")
            return {}


# ============================================================================
# FUNÇÃO DE TESTE
# ============================================================================

if __name__ == "__main__":
    # Teste básico
    dw = DataWarehouse()
    logger.info("Data Warehouse inicializado com sucesso")
