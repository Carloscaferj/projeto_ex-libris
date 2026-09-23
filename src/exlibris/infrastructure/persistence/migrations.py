"Atualizações entre cada uma das versões do schema. Serve para atualizar bases que estejam operando em uma versão mais antiga"

# Versão atual do Schema para atualizações:
SCHEMA_VERSION = 1

MIGRATIONS = [
    (1,"ALTER TABLE obras ADD COLUMN teste TEXT")
]

# Política de atualização:
"""
Bancos novos são criados diretamente através do esquema em sqlite_catalogue.py.

Bancos já existentes possuem sua PRAGMA verificada;
Se a PRAGMA for diferente da SCHEMA_VERSION, ela é atualizada de acordo com as instruções do MIGRATIONS;
Por exemplo, com 10 migrations, um esquema na versão 3 iria fazer todas as atualizações da versão 4 até a 10 em ordem.
"""