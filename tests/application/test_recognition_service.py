"""Testes de regressão da inicialização do serviço de reconhecimento a partir do banco."""

import numpy as np

from exlibris.application.recognition_service import CatalogRecognitionService
from exlibris.infrastructure.persistence.sqlite_catalog import SQLiteCatalogRepository

DIMENSAO = 4


def _vetor(valores):
    return np.array(valores, dtype=np.float32)


def test_inicializa_servico_com_banco_vazio(tmp_path):
    db_path = str(tmp_path / "catalogo.db")

    servico = CatalogRecognitionService(db_path=db_path, dimensao=DIMENSAO)

    assert len(servico._indice) == 0


def test_inicializa_servico_com_marcas_persistidas_sem_erro(tmp_path):
    db_path = str(tmp_path / "catalogo.db")
    repositorio = SQLiteCatalogRepository(db_path)
    repositorio.iniciar_banco()
    obra_id = repositorio.inserir_obra("Os Lusíadas", autor="Luís de Camões")
    marca_id = repositorio.inserir_marca(
        "marca-1.png",
        _vetor([1.0, 0.0, 0.0, 0.0]),
        "ex_libris",
        obra_id=obra_id,
        confirmado=True,
    )

    servico = CatalogRecognitionService(db_path=db_path, dimensao=DIMENSAO)

    assert len(servico._indice) == 1
    resultados = servico._indice.buscar(_vetor([1.0, 0.0, 0.0, 0.0]), top_k=1)
    assert resultados[0][0] == marca_id


def test_persistir_fechar_reabrir_e_buscar_com_embeddings_sinteticos(tmp_path):
    db_path = str(tmp_path / "catalogo.db")

    servico_inicial = CatalogRecognitionService(db_path=db_path, dimensao=DIMENSAO)
    obra_id = servico_inicial.cadastrar_obra("Os Lusíadas", autor="Luís de Camões")
    marca_id = servico_inicial.registrar_marca(
        "marca-1.png",
        tipo="ex_libris",
        embedding=_vetor([0.0, 1.0, 0.0, 0.0]),
        obra_id=obra_id,
        confirmado=True,
    )
    del servico_inicial  # cada operação do repositório abre e fecha sua própria conexão

    servico_reaberto = CatalogRecognitionService(db_path=db_path, dimensao=DIMENSAO)

    assert len(servico_reaberto._indice) == 1
    resultados = servico_reaberto._indice.buscar(_vetor([0.0, 0.9, 0.1, 0.0]), top_k=1)
    assert resultados[0][0] == marca_id
