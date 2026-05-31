# Rotina Automation Project

Este projeto automatiza a captura e tratamento de relatórios em PDF, modela dados e alimenta um banco de dados SQLite para análise.

## Boas práticas de segurança

- Não commit arquivos de dados sensíveis como `data_warehouse.db`.
- Não commit arquivos de log ou arquivos de credenciais.
- Utilize `.env` para definir caminhos e credenciais locais.
- Mantenha o arquivo `.env.example` versionado como modelo, mas ignore o `.env` real.

## Configuração local

1. Copie `.env.example` para `.env`.
2. Ajuste `DATAWAREHOUSE_DB_PATH` para o caminho local do seu banco de dados.
3. Execute o script com Python.
