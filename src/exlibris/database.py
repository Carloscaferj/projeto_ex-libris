"""Compatibilidade para imports antigos do módulo de banco."""

from exlibris import config
from exlibris.infrastructure.persistence.sqlite_catalog import SQLiteCatalogRepository


def iniciar_banco(db_path):
    SQLiteCatalogRepository(db_path or config.DB_PATH).iniciar_banco()


def inserir_obra(titulo, autor=None, local=None, editora=None, data=None, db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).inserir_obra(
        titulo, autor, local, editora, data
    )


def buscar_obra(obra_id, db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).buscar_obra(obra_id)


def listar_obras(db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).listar_obras()


def inserir_marca(imagem_path, embedding, tipo, obra_id=None, descricao=None,
                  confirmado=False, db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).inserir_marca(
        imagem_path, embedding, tipo, obra_id, descricao, confirmado
    )


def atualizar_vinculo_marca(marca_id, obra_id, confirmado=True, db_path=None):
    SQLiteCatalogRepository(db_path or config.DB_PATH).atualizar_vinculo_marca(
        marca_id, obra_id, confirmado
    )


def buscar_marca(marca_id, db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).buscar_marca(marca_id)


def listar_marcas(db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).listar_marcas()


def registrar_identificacao(imagem_path, marca_id_sugerida, obra_id_sugerida,
                            confianca, db_path=None):
    return SQLiteCatalogRepository(db_path or config.DB_PATH).registrar_identificacao(
        imagem_path, marca_id_sugerida, obra_id_sugerida, confianca
    )


def registrar_feedback(identificacao_id, aceito, db_path=None):
    SQLiteCatalogRepository(db_path or config.DB_PATH).registrar_feedback(identificacao_id, aceito)
