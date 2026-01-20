import os
import pandas as pd
from pymongo import MongoClient
from tqdm import tqdm


""""
O Excel, por si só, não possui suporte nativo para conexões diretas com APIs externas e bancos de dados, o que pode limitar a obtenção e o armazenamento de informações. Com Python, é possível integrar planilhas a fontes de dados externas, permitindo que informações sejam coletadas, atualizadas e sincronizadas automaticamente.

A integração com APIs possibilita importar dados financeiros, cotações de moedas, informações de sistemas internos e até mesmo dados climáticos diretamente para o Excel. Além disso, a conexão com bancos de dados SQL e NoSQL permite armazenar e recuperar grandes volumes de informações sem a necessidade de manipulação manual.

Outro benefício dessa integração é a automação de processos administrativos, como o envio de dados para servidores, a extração de relatórios de sistemas e a sincronização de informações entre diferentes plataformas.

📚 Bibliotecas para Integração com APIs e Banco de Dados
requests → Comunicação com APIs REST e consumo de dados externos
sqlalchemy → Conexão e manipulação de bancos de dados SQL
pymongo → Integração com bancos de dados NoSQL (MongoDB)
gspread → Acesso e edição de planilhas no Google Sheets via API
Com essas ferramentas, o Excel se torna uma plataforma dinâmica e conectada, eliminando a necessidade de atualizações manuais e garantindo que os dados estejam sempre atualizados e acessíveis.

📝Exemplo:
Este é outro exemplo de um programa que desenvolvi para utilizar no meu trabalho. Ele verifica a existência de uma lista de IDs armazenados em um arquivo Excel (.xlsx) dentro de uma coleção específica no MongoDB. O código realiza a busca com base no id_cliente, garantindo que apenas os registros pertencentes a um determinado cliente sejam considerados.

import os
"""
def verificar_ids_no_mongo(excel_path, sheet_name, column_name, collection_name, id_cliente, output_path_encontrados, output_path_nao_encontrados):

  # Obtém a URI de conexão ao MongoDB a partir das variáveis de ambiente
  mongo_uri = os.getenv('MONGO_DB_CONNECTION')
  client = MongoClient(mongo_uri)
  db = client['meuBanco']
  collection = db[collection_name]

  # Verifica se o arquivo Excel existe e não está vazio
  if not os.path.exists(excel_path) or os.path.getsize(excel_path) == 0:
      print(f"Erro: O arquivo {excel_path} não existe ou está vazio.")
      return

  try:
      # Carrega os dados do Excel para um DataFrame do pandas
      df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str)
  except Exception as e:
      print(f"Erro ao ler o arquivo Excel: {e}")
      return

  # Verifica se a coluna especificada existe no DataFrame
  if column_name not in df.columns:
      print(f"Erro: A coluna '{column_name}' não foi encontrada no arquivo Excel.")
      return

  # Obtém os IDs da coluna, removendo valores nulos e duplicados
  ids = df[column_name].dropna().astype(str).unique().tolist()

  if not ids:
      print("Erro: O arquivo Excel não contém nenhum `_id` válido.")
      return

  encontrados = []  # Lista para armazenar os IDs encontrados no MongoDB
  nao_encontrados = []  # Lista para armazenar os IDs não encontrados

  print(f"\nVerificando {len(ids)} IDs na coleção '{collection_name}' para id_cliente: {id_cliente}...\n")

  # Itera sobre os IDs e verifica se estão na coleção do MongoDB
  for item_id in tqdm(ids, desc="Processando", unit="item"):
      result = collection.find_one({"_id": item_id, "id_cliente": id_cliente})

      if result:
          encontrados.append({"_id": item_id, "id_cliente": id_cliente})
      else:
          nao_encontrados.append({"_id": item_id, "id_cliente": id_cliente})

  # Se houver IDs encontrados, salva em um arquivo Excel
  if encontrados:
      df_encontrados = pd.DataFrame(encontrados)
      df_encontrados.to_excel(output_path_encontrados, index=False)
      print(f"\nArquivo gerado: {output_path_encontrados}")

  # Se houver IDs não encontrados, salva em outro arquivo Excel
  if nao_encontrados:
      df_nao_encontrados = pd.DataFrame(nao_encontrados)
      df_nao_encontrados.to_excel(output_path_nao_encontrados, index=False)
      print(f"\nArquivo gerado: {output_path_nao_encontrados}")


# Definição dos parâmetros do programa
excel_path = "ids_para_verificacao.xlsx"  # Caminho do arquivo Excel contendo os IDs
sheet_name = "Planilha1"  # Nome da aba no Excel
column_name = "id_verificacao"  # Nome da coluna onde os IDs estão armazenados
collection_name = "colecao_dados"  # Nome da coleção do MongoDB
id_cliente = os.getenv("ID_CLIENTE")  # Obtém o ID do cliente das variáveis de ambiente
output_path_encontrados = "ids_encontrados.xlsx"  # Arquivo de saída para IDs encontrados
output_path_nao_encontrados = "ids_nao_encontrados.xlsx"  # Arquivo de saída para IDs não encontrados

# Chamada da função principal
verificar_ids_no_mongo(excel_path, sheet_name, column_name, collection_name, id_cliente, output_path_encontrados, output_path_nao_encontrados)