"""Testes de regressão do índice vetorial contra o contrato tipado de Marca."""

import importlib.util

import numpy as np
import pytest

from exlibris.domain.models import Marca
from exlibris.infrastructure.search import vector_index as vector_index_module
from exlibris.infrastructure.search.vector_index import IndiceVetorial

FAISS_DISPONIVEL = importlib.util.find_spec("faiss") is not None


def _marca_sintetica(marca_id: int, embedding: np.ndarray) -> Marca:
    return Marca(
        id=marca_id,
        obra_id=None,
        tipo="ex_libris",
        descricao=None,
        imagem_path=f"marca-{marca_id}.png",
        embedding=embedding,
        confirmado=False,
        criado_em="2026-01-01T00:00:00+00:00",
    )


def test_construir_a_partir_do_banco_com_lista_vazia():
    indice = IndiceVetorial.construir_a_partir_do_banco([], dimensao=4)

    assert len(indice) == 0
    assert indice.buscar(np.zeros(4, dtype=np.float32)) == []


def test_construir_a_partir_do_banco_usa_contrato_tipado_da_marca():
    marcas = [
        _marca_sintetica(1, np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)),
        _marca_sintetica(2, np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)),
    ]

    indice = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao=4)

    assert len(indice) == 2
    resultados = indice.buscar(np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32), top_k=1)
    assert resultados[0][0] == 2


def test_buscar_resultado_equivalente_entre_fallback_numpy_e_faiss(monkeypatch):
    marcas = [
        _marca_sintetica(10, np.array([1.0, 0.0, 0.0], dtype=np.float32)),
        _marca_sintetica(20, np.array([0.0, 1.0, 0.0], dtype=np.float32)),
        _marca_sintetica(30, np.array([0.0, 0.0, 1.0], dtype=np.float32)),
    ]
    consulta = np.array([0.1, 0.9, 0.05], dtype=np.float32)

    monkeypatch.setattr(vector_index_module, "_TEM_FAISS", False)
    indice_numpy = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao=3)
    resultado_numpy = indice_numpy.buscar(consulta, top_k=2)

    if not FAISS_DISPONIVEL:
        pytest.skip("faiss não instalado neste ambiente; backend FAISS não pôde ser comparado")

    monkeypatch.setattr(vector_index_module, "_TEM_FAISS", True)
    indice_faiss = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao=3)
    resultado_faiss = indice_faiss.buscar(consulta, top_k=2)

    ids_numpy = [marca_id for marca_id, _ in resultado_numpy]
    ids_faiss = [marca_id for marca_id, _ in resultado_faiss]
    assert ids_numpy == ids_faiss

    for (_, score_numpy), (_, score_faiss) in zip(resultado_numpy, resultado_faiss):
        assert score_numpy == pytest.approx(score_faiss, abs=1e-5)
