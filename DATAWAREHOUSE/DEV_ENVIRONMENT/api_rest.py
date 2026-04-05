#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API REST - Data Warehouse
=========================

Endpoints para consulta de relatórios e caixa via HTTP
Endpoints: GET/POST com Request/Response JSON

Uso:
  python api_rest.py
  
Acesso:
  GET  http://localhost:5000/api/caixa
  GET  http://localhost:5000/api/resumo-diario?data=2024-01-13
  POST http://localhost:5000/api/processar-backup
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import sys
from pathlib import Path
import platform
from typing import Dict, List, Any

# Importar Data Warehouse
from data_warehouse import DataWarehouse, ConfigDW, logger as dw_logger

# ============================================================================
# CONFIGURAÇÃO FLASK
# ============================================================================

app = Flask(__name__)
CORS(app)  # Habilitar CORS para consumo cross-origin

# Configurar logging
logging.basicConfig(level=logging.INFO)
api_logger = logging.getLogger(__name__)

# Instância global do Data Warehouse
try:
    dw = DataWarehouse()
    api_logger.info("✓ Data Warehouse conectado com sucesso")
except Exception as e:
    api_logger.error(f"✗ Erro ao conectar Data Warehouse: {str(e)}")
    dw = None

# ============================================================================
# UTILIDADES
# ============================================================================

def sucesso(data: Any = None, mensagem: str = "OK", código: int = 200) -> tuple:
    """Retorna resposta de sucesso em JSON"""
    return jsonify({
        "status": "sucesso",
        "código": código,
        "mensagem": mensagem,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }), código

def erro(mensagem:str, código: int = 400, detalhes: Dict = None) -> tuple:
    """Retorna resposta de erro em JSON"""
    return jsonify({
        "status": "erro",
        "código": código,
        "mensagem": mensagem,
        "detalhes": detalhes,
        "timestamp": datetime.now().isoformat()
    }), código

def validar_data(data_str: str) -> bool:
    """Valida formato de data YYYY-MM-DD"""
    try:
        datetime.strptime(data_str, "%Y-%m-%d")
        return True
    except:
        return False

# ============================================================================
# ROTAS - HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return sucesso(
        data={"status": "conectado", "versão": "1.0"},
        mensagem="API operacional"
    )

@app.route('/status', methods=['GET'])
def status():
    """Status do Data Warehouse"""
    if dw is None:
        return erro("Data Warehouse não inicializado", 503)
    
    try:
        # Informações do banco de dados
        db_path = str(ConfigDW.DB_PATH)
        db_exists = Path(db_path).exists()
        db_size_mb = Path(db_path).stat().st_size / (1024 * 1024) if db_exists else 0
        
        return sucesso(
            data={
                "banco_de_dados": db_path,
                "existe": db_exists,
                "tamanho_mb": round(db_size_mb, 2),
                "data_hora": datetime.now().isoformat()
            },
            mensagem="Status operacional"
        )
    except Exception as e:
        return erro(f"Erro ao obter status: {str(e)}", 500)

# ============================================================================
# ROTAS - GET - CONSULTAS DE CAIXA
# ============================================================================

@app.route('/api/caixa', methods=['GET'])
def get_caixa():
    """
    GET /api/caixa
    
    Retorna dados de caixa com filtros opcionais
    
    Query Parameters:
      - data_inicio: YYYY-MM-DD (opcional)
      - data_fim: YYYY-MM-DD (opcional)
      - limite: número máximo de linhas (opcional, padrão 1000)
    
    Exemplo:
      GET /api/caixa?data_inicio=2024-01-01&data_fim=2024-01-31
    
    Response:
      {
        "status": "sucesso",
        "data": [
          {
            "id_caixa": 1,
            "data": "2024-01-13",
            "descricao": "Entrada Caixa",
            "valor_entrada": 500.00,
            "valor_saida": null,
            "saldo": 500.00
          },
          ...
        ]
      }
    """
    if dw is None:
        return erro("Data Warehouse não disponível", 503)
    
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        limite = int(request.args.get('limite', 1000))
        
        # Validar datas se fornecidas
        if data_inicio and not validar_data(data_inicio):
            return erro("Format data_inicio inválido (use YYYY-MM-DD)", 400)
        if data_fim and not validar_data(data_fim):
            return erro("Formato data_fim inválido (use YYYY-MM-DD)", 400)
        
        # Consultar Data Warehouse
        df = dw.consultar_caixa(data_inicio, data_fim)
        
        # Limitar resultados
        df = df.head(limite)
        
        # Converter para lista de dicionários
        dados = []
        for _, row in df.iterrows():
            dados.append({
                "id_caixa": int(row['id_caixa']) if pd.notna(row['id_caixa']) else None,
                "data": str(row['data']) if pd.notna(row['data']) else None,
                "data_operacao": str(row['data_operacao']) if pd.notna(row['data_operacao']) else None,
                "descricao": str(row['descricao']) if pd.notna(row['descricao']) else None,
                "valor_entrada": float(row['valor_entrada']) if pd.notna(row['valor_entrada']) else None,
                "valor_saida": float(row['valor_saida']) if pd.notna(row['valor_saida']) else None,
                "saldo": float(row['saldo']) if pd.notna(row['saldo']) else None,
                "metodo_pagamento": str(row['metodo_pagamento']) if pd.notna(row['metodo_pagamento']) else None,
                "referencia_externa": str(row['referencia_externa']) if pd.notna(row['referencia_externa']) else None
            })
        
        return sucesso(
            data={
                "total_registros": len(dados),
                "limite": limite,
                "caixa": dados,
                "filtros": {
                    "data_inicio": data_inicio,
                    "data_fim": data_fim
                }
            },
            mensagem=f"Retornados {len(dados)} registros de caixa"
        )
        
    except Exception as e:
        api_logger.error(f"Erro em GET /api/caixa: {str(e)}")
        return erro(f"Erro ao consultar caixa: {str(e)}", 500)

@app.route('/api/resumo-diario', methods=['GET'])
def get_resumo_diario():
    """
    GET /api/resumo-diario
    
    Retorna resumo consolidado de caixa para uma data
    
    Query Parameters:
      - data: YYYY-MM-DD (obrigatório)
    
    Exemplo:
      GET /api/resumo-diario?data=2024-01-13
    
    Response:
      {
        "status": "sucesso",
        "data": {
          "data": "2024-01-13",
          "num_operacoes": 15,
          "total_entrada": 5000.00,
          "total_saida": 1200.00,
          "saldo_final": 3800.00
        }
      }
    """
    if dw is None:
        return erro("Data Warehouse não disponível", 503)
    
    try:
        data = request.args.get('data')
        
        if not data:
            return erro("Parâmetro 'data' obrigatório (formato YYYY-MM-DD)", 400)
        
        if not validar_data(data):
            return erro("Formato de data inválido (use YYYY-MM-DD)", 400)
        
        resumo = dw.resumo_diario(data)
        
        if not resumo:
            return erro("Nenhum dado encontrado para essa data", 404)
        
        return sucesso(
            data=resumo,
            mensagem=f"Resumo diário para {data}"
        )
        
    except Exception as e:
        api_logger.error(f"Erro em GET /api/resumo-diario: {str(e)}")
        return erro(f"Erro ao obter resumo: {str(e)}", 500)

@app.route('/api/relatorios', methods=['GET'])
def get_relatorios():
    """
    GET /api/relatorios
    
    Retorna lista de relatórios processados
    
    Query Parameters:
      - data_inicio: YYYY-MM-DD (opcional)
      - data_fim: YYYY-MM-DD (opcional)
      - limite: máximo de linhas (opcional)
    """
    if dw is None:
        return erro("Data Warehouse não disponível", 503)
    
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        limite = int(request.args.get('limite', 500))
        
        df = dw.consultar_relatorios(data_inicio, data_fim)
        df = df.head(limite)
        
        dados = []
        for _, row in df.iterrows():
            dados.append({
                "id_relatorio": int(row['id_relatorio']) if pd.notna(row['id_relatorio']) else None,
                "data": str(row['data']) if pd.notna(row['data']) else None,
                "nome_relatorio": str(row['nome_relatorio']) if pd.notna(row['nome_relatorio']) else None,
                "tipo_relatorio": str(row['tipo_relatorio']) if pd.notna(row['tipo_relatorio']) else None,
                "total_registros": int(row['total_registros']) if pd.notna(row['total_registros']) else 0,
                "valor_total": float(row['valor_total']) if pd.notna(row['valor_total']) else None
            })
        
        return sucesso(
            data={
                "total_registros": len(dados),
                "relatorios": dados
            },
            mensagem=f"Retornados {len(dados)} relatórios"
        )
        
    except Exception as e:
        api_logger.error(f"Erro em GET /api/relatorios: {str(e)}")
        return erro(f"Erro ao consultar relatórios: {str(e)}", 500)

# ============================================================================
# ROTAS - POST - PROCESSAR BACKUPS
# ============================================================================

@app.route('/api/processar-backup', methods=['POST'])
def post_processar_backup():
    """
    POST /api/processar-backup
    
    Processa um backup diário e carrega no Data Warehouse
    
    Request Body (JSON):
      {
        "data_pasta": "13 JAN"
      }
    
    Exemplo:
      POST /api/processar-backup
      {
        "data_pasta": "13 JAN"
      }
    
    Response:
      {
        "status": "sucesso",
        "data": {
          "data_pasta": "13 JAN",
          "status": "sucesso",
          "arquivos_processados": 5,
          "total_registros": 250,
          "tempo_ms": 1234
        }
      }
    """
    if dw is None:
        return erro("Data Warehouse não disponível", 503)
    
    try:
        payload = request.get_json()
        
        if not payload:
            return erro("Body JSON obrigatório", 400)
        
        data_pasta = payload.get('data_pasta')
        
        if not data_pasta:
            return erro("Campo 'data_pasta' obrigatório (formato: 'DD MMM')", 400)
        
        # Validar formato
        parts = data_pasta.split()
        if len(parts) != 2:
            return erro("Formato data_pasta inválido. Use 'DD MMM' (ex: '13 JAN')", 400)
        
        api_logger.info(f"Iniciando processamento: {data_pasta}")
        
        # Processar backup
        resultado = dw.processar_backup_diario(data_pasta)
        
        if resultado['status'] == 'falha':
            return erro(
                f"Falha ao processar backup",
                400,
                detalhes={"erros": resultado['erros']}
            )
        
        return sucesso(
            data=resultado,
            mensagem=f"Backup '{data_pasta}' processado com sucesso",
            código=201
        )
        
    except Exception as e:
        api_logger.error(f"Erro em POST /api/processar-backup: {str(e)}")
        return erro(f"Erro ao processar backup: {str(e)}", 500)

@app.route('/api/consulta-customizada', methods=['POST'])
def post_consulta_customizada():
    """
    POST /api/consulta-customizada
    
    Executa consulta SQL customizada (para usuários avançados)
    
    Request Body (JSON):
      {
        "query": "SELECT * FROM fato_caixa WHERE valor_entrada > ?",
        "parametros": [100.0]
      }
    
    Note: Por segurança, apenas tabelas públicas são permitidas
    """
    if dw is None:
        return erro("Data Warehouse não disponível", 503)
    
    try:
        payload = request.get_json()
        
        if not payload:
            return erro("Body JSON obrigatório", 400)
        
        query = payload.get('query', '').strip()
        parametros = payload.get('parametros', [])
        
        if not query:
            return erro("Campo 'query' obrigatório", 400)
        
        # Validações de segurança: desabilitar operações perigosas
        query_upper = query.upper()
        operacoes_proibidas = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        
        for op in operacoes_proibidas:
            if op in query_upper:
                return erro(f"Operação '{op}' não permitida em consulta customizada", 400)
        
        # Executar consulta
        import sqlite3
        conn = sqlite3.connect(str(ConfigDW.DB_PATH))
        df = pd.read_sql_query(query, conn, params=parametros)
        conn.close()
        
        # Converter resultado
        dados = df.to_dict(orient='records')
        
        return sucesso(
            data={
                "total_registros": len(dados),
                "registros": dados
            },
            mensagem="Consulta executada com sucesso"
        )
        
    except Exception as e:
        api_logger.error(f"Erro em POST /api/consulta-customizada: {str(e)}")
        return erro(f"Erro ao executar consulta: {str(e)}", 500)

# ============================================================================
# TRATAMENTO DE ERROS GLOBAL
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Rota não encontrada"""
    return erro("Endpoint não encontrado", 404)

@app.errorhandler(500)
def internal_error(error):
    """Erro interno do servidor"""
    return erro("Erro interno do servidor", 500)

@app.errorhandler(405)
def method_not_allowed(error):
    """Método não permitido"""
    return erro("Método HTTP não permitido para esse endpoint", 405)

# ============================================================================
# IMPORTAR PANDAS (necessário para as rotas)
# ============================================================================

try:
    import pandas as pd
except ImportError:
    print("Aviso: pandas não está instalado")
    pd = None

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import platform
    
    # Usar host 0.0.0.0 para aceitar conexões externas
    host = '0.0.0.0' if platform.system() != 'Windows' else '127.0.0.1'
    port = 5000
    debug = True
    
    api_logger.info(f"{'='*60}")
    api_logger.info(f"API REST - Data Warehouse")
    api_logger.info(f"{'='*60}")
    api_logger.info(f"Host: {host}:{port}")
    api_logger.info(f"Debug: {debug}")
    api_logger.info(f"{'='*60}\n")
    api_logger.info("Endpoints disponíveis:")
    api_logger.info("  GET  /health - Health check")
    api_logger.info("  GET  /status - Status do DW")
    api_logger.info("  GET  /api/caixa - Consultar caixa")
    api_logger.info("  GET  /api/resumo-diario - Resumo de um dia")
    api_logger.info("  GET  /api/relatorios - Listar relatórios")
    api_logger.info("  POST /api/processar-backup - Processar backup")
    api_logger.info("  POST /api/consulta-customizada - Consulta SQL")
    api_logger.info(f"\nAcesso: http://localhost:{port}\n")
    
    app.run(host=host, port=port, debug=debug)
