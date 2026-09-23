"Teste para as migrações, com o pytest"

import sqlite3
import os
from exlibris.infrastructure.persistence.sqlite_catalog import SQLiteCatalogRepository
from exlibris.infrastructure.persistence import migrations

def test_banco_novo_ja_nasce_na_versao_atual(tmp_path):
    db_path = tmp_path / "teste.db"
    repo = SQLiteCatalogRepository(db_path=str(db_path))

    repo.iniciar_banco()

    con = sqlite3.connect(db_path)
    versao = con.execute("PRAGMA user_version;").fetchone()[0]
    assert versao == migrations.SCHEMA_VERSION

def test_schema_version_bate_com_ultima_migration():
    if migrations.MIGRATIONS:
        assert migrations.SCHEMA_VERSION == max(v for v, _ in migrations.MIGRATIONS)

def test_reexecucao_iniciar_base(tmp_path):
    db_path = tmp_path / "teste.db"
    repo = SQLiteCatalogRepository(db_path=str(db_path))

    repo.iniciar_banco()
    repo.iniciar_banco()

    con = sqlite3.connect(db_path)
    versao = con.execute("PRAGMA user_version;").fetchone()[0]
    assert versao == migrations.SCHEMA_VERSION

def test_backup(tmp_path):
    db_path = tmp_path / "teste.db"
    repo = SQLiteCatalogRepository(db_path=str(db_path))
    repo.iniciar_banco()

    con = sqlite3.connect(db_path)
    versao_atual = con.execute("PRAGMA user_version;").fetchone()[0]
    con.close()

    repo.update_schema(db_ver=versao_atual)

    assert os.path.exists(f'{db_path}.bak')


r"""
Exemplo do ultimo teste com sucesso:

===================================================================== test session starts ======================================================================
platform win32 -- Python 3.13.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\ projeto_ex-libris
configfile: pyproject.toml
collected 2 items                                                                                                                                               

src\exlibris\infrastructure\ persistence\test_migration.py ..                                                                                              [100%]

====================================================================== 2 passed in 0.45s =======================================================================

Exemplo do teste falho anterior:

    
        con = sqlite3.connect(db_path)
        versao = con.execute("PRAGMA user_version;").fetchone()[0]
>       assert versao == migrations.SCHEMA_VERSION
E       assert 0 == 1
E        +  where 1 = migrations.SCHEMA_VERSION

src\exlibris\infrastructure\persistence\test_migration.py:15: AssertionError
=================================================================== short test summary info ====================================================================
FAILED src/exlibris/infrastructure/persistence/test_migration.py::test_banco_novo_ja_nasce_na_versao_atual - assert 0 == 1
================================================================= 1 failed, 1 passed in 0.75s ==================================================================
"""