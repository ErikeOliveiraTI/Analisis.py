#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes - Data Warehouse
=======================

Suite completa de testes para validar:
  ✓ Criação do banco de dados
  ✓ Extração de arquivos
  ✓ Normalização de dados
  ✓ Carga no DW
  ✓ Consultas com Pandas

Executar:
  python test_data_warehouse.py
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import sqlite3
import json

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from data_warehouse import DataWarehouse, ConfigDW
import pandas as pd

# ============================================================================
# CONFIGURAÇÃO DE TESTE
# ============================================================================

class TestConfig:
    """Configuração para testes"""
    
    # Usar banco de dados temporário para testes
    DB_TEST = Path(tempfile.gettempdir()) / "test_data_warehouse.db"
    
    @classmethod
    def limpar_banco_teste(cls):
        """Remove banco de teste anterior"""
        if cls.DB_TEST.exists():
            cls.DB_TEST.unlink()

# ============================================================================
# TESTES - BANCO DE DADOS
# ============================================================================

class TestBancoDados(unittest.TestCase):
    """Testes da criação e estrutura do banco de dados"""
    
    @classmethod
    def setUpClass(cls):
        """Setup uma vez antes de todos os testes"""
        TestConfig.limpar_banco_teste()
    
    def setUp(self):
        """Setup antes de cada teste"""
        # Sobrescrever ConfigDW temporariamente
        self.db_original = ConfigDW.DB_PATH
        ConfigDW.DB_PATH = TestConfig.DB_TEST
    
    def tearDown(self):
        """Cleanup após cada teste"""
        ConfigDW.DB_PATH = self.db_original
    
    def test_banco_criado(self):
        """Verifica se banco de dados é criado"""
        dw = DataWarehouse()
        self.assertTrue(TestConfig.DB_TEST.exists(), "Banco de dados não foi criado")
    
    def test_tabelas_existem(self):
        """Verifica se todas as tabelas foram criadas"""
        dw = DataWarehouse()
        
        conn = sqlite3.connect(str(TestConfig.DB_TEST))
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tabelas = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        
        tabelas_esperadas = {
            'dim_datas',
            'dim_tipos_arquivo',
            'fato_backups',
            'fato_caixa',
            'fato_relatorios',
            'auditoria_processamento'
        }
        
        self.assertEqual(
            tabelas_esperadas,
            tabelas,
            f"Tabelas esperadas: {tabelas_esperadas}, encontradas: {tabelas}"
        )
    
    def test_indices_criados(self):
        """Verifica se índices foram criados para performance"""
        dw = DataWarehouse()
        
        conn = sqlite3.connect(str(TestConfig.DB_TEST))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        indices = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        
        self.assertTrue(len(indices) > 0, "Nenhum índice foi criado")
        # Use safe character for Windows
        print(f"[OK] {len(indices)} indices criados: {indices}")

# ============================================================================
# TESTES - EXTRAÇÃO
# ============================================================================

class TestExtracao(unittest.TestCase):
    """Testes de extração de dados"""
    
    def setUp(self):
        """Setup antes de cada teste"""
        self.db_original = ConfigDW.DB_PATH
        ConfigDW.DB_PATH = TestConfig.DB_TEST
        TestConfig.limpar_banco_teste()
        self.dw = DataWarehouse()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        ConfigDW.DB_PATH = self.db_original
    
    def test_extrair_arquivo_inexistente(self):
        """Verifica comportamento com arquivo que não existe"""
        arquivo_fake = Path("/z/git/rotina/FAKE_XXX.xlsx")
        resultado = self.dw.extrair_arquivo_excel(arquivo_fake)
        self.assertIsNone(resultado, "Deve retornar None para arquivo inexistente")
    
    def test_extrair_cria_dataframe(self):
        """Verifica se extração cria DataFrame válido"""
        # Criar arquivo de teste temporário
        dados_teste = {
            'Descrição': ['Entrada 1', 'Entrada 2'],
            'Valor': [100.00, 200.00],
            'Status': ['OK', 'OK']
        }
        df_teste = pd.DataFrame(dados_teste)
        
        arquivo_teste = Path(tempfile.gettempdir()) / "teste_caixa.xlsx"
        df_teste.to_excel(arquivo_teste, index=False)
        
        try:
            resultado = self.dw.extrair_arquivo_excel(arquivo_teste)
            
            self.assertIsNotNone(resultado, "Deve retornar DataFrame")
            self.assertEqual(len(resultado), 2, "Deve ter 2 linhas")
            self.assertEqual(len(resultado.columns), 3, "Deve ter 3 colunas")
            
        finally:
            arquivo_teste.unlink()

# ============================================================================
# TESTES - TRANSFORMAÇÃO
# ============================================================================

class TestTransformacao(unittest.TestCase):
    """Testes de normalização e transformação"""
    
    def setUp(self):
        """Setup antes de cada teste"""
        self.db_original = ConfigDW.DB_PATH
        ConfigDW.DB_PATH = TestConfig.DB_TEST
        TestConfig.limpar_banco_teste()
        self.dw = DataWarehouse()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        ConfigDW.DB_PATH = self.db_original
    
    def test_normalizar_remove_duplicatas(self):
        """Verifica se normalização remove linhas duplicadas"""
        df = pd.DataFrame({
            'Descrição': ['Entrada', 'Entrada'],
            'Valor_Entrada': [100, 100],
            'Valor_Saída': [None, None]
        })
        
        resultado = self.dw.normalizar_caixa(df)
        
        # Deve ter apenas 1 linha (sem duplicata)
        self.assertEqual(len(resultado), 1, "Deve remover duplicatas")
    
    def test_normalizar_padroniza_colunas(self):
        """Verifica se nomes de colunas são padronizados"""
        df = pd.DataFrame({
            'Descrição': ['Teste'],
            'Valor Entrada': [100],
            'VALOR SAÍDA': [50]
        })
        
        resultado = self.dw.normalizar_caixa(df)
        
        # Colunas devem estar em lowercase
        self.assertIn('descricao', resultado.columns)
        self.assertIn('valor_entrada', resultado.columns)
        self.assertIn('valor_saida', resultado.columns)
    
    def test_normalizar_converte_tipos(self):
        """Verifica se tipos de dados são convertidos"""
        df = pd.DataFrame({
            'Descrição': ['Teste'],
            'Valor Entrada': ['100.50'],  # String
            'Valor Saída': ['50.25']       # String
        })
        
        resultado = self.dw.normalizar_caixa(df)
        
        # Devem ser numéricos
        self.assertTrue(
            pd.api.types.is_numeric_dtype(resultado['valor_entrada']),
            "Valor entrada deve ser numérico"
        )

# ============================================================================
# TESTES - CARGA
# ============================================================================

class TestCarga(unittest.TestCase):
    """Testes de carga de dados no DW"""
    
    def setUp(self):
        """Setup antes de cada teste"""
        self.db_original = ConfigDW.DB_PATH
        ConfigDW.DB_PATH = TestConfig.DB_TEST
        TestConfig.limpar_banco_teste()
        self.dw = DataWarehouse()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        ConfigDW.DB_PATH = self.db_original
    
    def test_carregar_caixa_insere_registros(self):
        """Verifica se dados são inseridos em fato_caixa"""
        # Criar DataFrame de teste
        df = pd.DataFrame({
            'descricao': ['Entrada Caixa'],
            'valor_entrada': [500.00],
            'valor_saida': [None],
            'saldo': [500.00],
            'metodo_pagamento': ['Dinheiro'],
            'referencia_externa': ['REF-001']
        })
        
        # Obter ID da data
        id_data = self.dw._obter_ou_criar_data(datetime.now())
        
        # Registrar backup
        id_backup = self.dw._registrar_backup(
            "Teste.xlsx", "teste", Path("teste.xlsx"),
            "abc123", len(df), len(df.columns), id_data
        )
        
        # Carregar dados
        self.dw.carregar_caixa(df, id_backup, id_data)
        
        # Verificar se foi inserido
        conn = sqlite3.connect(str(TestConfig.DB_TEST))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fato_caixa")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1, "Deve ter inserido 1 registro")

# ============================================================================
# TESTES - CONSULTAS
# ============================================================================

class TestConsultas(unittest.TestCase):
    """Testes de consultas com Pandas"""
    
    def setUp(self):
        """Setup antes de cada teste"""
        self.db_original = ConfigDW.DB_PATH
        ConfigDW.DB_PATH = TestConfig.DB_TEST
        TestConfig.limpar_banco_teste()
        self.dw = DataWarehouse()
        
        # Inserir dados de teste
        self._inserir_dados_teste()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        ConfigDW.DB_PATH = self.db_original
    
    def _inserir_dados_teste(self):
        """Insere dados de teste"""
        data_teste = datetime(2024, 1, 13)
        id_data = self.dw._obter_ou_criar_data(data_teste)
        
        df_teste = pd.DataFrame({
            'descricao': ['Entrada 1', 'Entrada 2', 'Saída 1'],
            'valor_entrada': [500.00, 300.00, None],
            'valor_saida': [None, None, 100.00],
            'saldo': [500.00, 800.00, 700.00],
            'metodo_pagamento': ['Dinheiro', 'Cartão', 'Dinheiro'],
            'referencia_externa': ['REF-001', 'REF-002', 'REF-003']
        })
        
        id_backup = self.dw._registrar_backup(
            "Caixa_Teste.xlsx", "caixa", Path("teste.xlsx"),
            "hash_teste", len(df_teste), len(df_teste.columns), id_data
        )
        
        self.dw.carregar_caixa(df_teste, id_backup, id_data)
    
    def test_consultar_caixa_retorna_dataframe(self):
        """Verifica se consulta retorna DataFrame"""
        resultado = self.dw.consultar_caixa()
        
        self.assertIsInstance(resultado, pd.DataFrame, "Deve retornar DataFrame")
        self.assertGreater(len(resultado), 0, "Deve ter dados")
    
    def test_consultar_caixa_com_filtro_data(self):
        """Verifica se filtro de data funciona"""
        # Inserir dados de outras datas
        data_outra = datetime(2024, 2, 1)
        id_data_outra = self.dw._obter_ou_criar_data(data_outra)
        
        df_outra = pd.DataFrame({
            'descricao': ['Entrada Fevereiro'],
            'valor_entrada': [1000.00],
            'valor_saida': [None],
            'saldo': [1000.00],
            'metodo_pagamento': ['Dinheiro'],
            'referencia_externa': ['REF-FEV']
        })
        
        id_backup = self.dw._registrar_backup(
            "Caixa_Fev.xlsx", "caixa", Path("fev.xlsx"),
            "hash_fev", len(df_outra), len(df_outra.columns), id_data_outra
        )
        self.dw.carregar_caixa(df_outra, id_backup, id_data_outra)
        
        # Consultar apenas janeiro
        resultado = self.dw.consultar_caixa("2024-01-01", "2024-01-31")
        
        self.assertEqual(len(resultado), 3, "Deve ter 3 registros de janeiro")
    
    def test_resumo_diario(self):
        """Verifica se resumo diário funciona"""
        resumo = self.dw.resumo_diario("2024-01-13")
        
        self.assertIsInstance(resumo, dict)
        self.assertEqual(resumo['num_operacoes'], 3)
        self.assertEqual(resumo['total_entrada'], 800.00)
        self.assertEqual(resumo['total_saida'], 100.00)
        self.assertEqual(resumo['saldo_final'], 700.00)

# ============================================================================
# SUITE DE TESTES
# ============================================================================

def criar_suite_testes():
    """Cria suite com todos os testes"""
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBancoDados))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExtracao))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTransformacao))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCarga))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConsultas))
    
    return suite

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SUITE DE TESTES - DATA WAREHOUSE")
    print("=" * 70 + "\n")
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    suite = criar_suite_testes()
    resultado = runner.run(suite)
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Testes executados: {resultado.testsRun}")
    print(f"Sucessos: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"Falhas: {len(resultado.failures)}")
    print(f"Erros: {len(resultado.errors)}")
    
    if resultado.wasSuccessful():
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
        exit(0)
    else:
        print("\n[FALHA] ALGUNS TESTES FALHARAM")
        exit(1)
