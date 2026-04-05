#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executar backup de hoje"""

import sys
from datetime import datetime
from data_warehouse import DataWarehouse
import json

print("=" * 70)
print(f"BACKUP DE HOJE: {datetime.now().strftime('%d %b %Y').upper()}")
print("=" * 70)
print()

# Inicializar DW
print("[1/3] Inicializando Data Warehouse...")
try:
    dw = DataWarehouse()
    print("      OK - DW inicializado")
except Exception as e:
    print(f"      ERRO: {e}")
    sys.exit(1)

# Obter data de hoje
today = datetime.now().strftime("%d %b").upper()
print()
print(f"[2/3] Processando backup de: {today}")

try:
    resultado = dw.processar_backup_diario(today)
    
    print()
    print("      Resultado do processamento:")
    print("      " + "-" * 60)
    for chave, valor in resultado.items():
        if chave != "erros":
            print(f"      {chave:.<40} {valor}")
    
    if resultado.get("erros"):
        print()
        print("      Erros encontrados:")
        for erro in resultado["erros"]:
            print(f"      - {erro}")
    
except Exception as e:
    print(f"      ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("[3/3] Verificando dados no banco...")
print("=" * 70)

# Verificar dados
try:
    df = dw.consultar_caixa()
    print(f"Total de registros no DW: {len(df)}")
    
    if len(df) > 0:
        print(f"Colunas: {list(df.columns)}")
        print()
        print("Estrutura do DataFrame:")
        print(df.info())
    else:
        print("Nenhum registro no banco ainda")
        
except Exception as e:
    print(f"Erro ao consultar: {e}")

print()
print("=" * 70)
