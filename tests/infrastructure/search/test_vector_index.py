"""Testes do índice vetorial com vetores pequenos e distâncias conhecidas.

Não fazemos nenhuma asserção contra saída real de ResNet aqui — apenas
vetores construídos à mão onde a ordenação por similaridade é óbvia.
"""

import numpy as np
import pytest

from exlibris.domain.models import Marca
from exlibris.infrastructure.search.vector_index import IndiceVetorial


def _marca(id_, embedding, obra_id=None, confirmado=True):
    return Marca(
        id=id_, obra_id=obra_id, tipo="ex_libris", descricao=None,
        imagem_path=f"marca-{id_}.jpg", embedding=np.asarray(embedding, dtype=np.float32),
        confirmado=confirmado, criado_em="2024-01-01T00:00:00+00:00",
    )


def test_indice_vazio_nao_retorna_vizinhos():
    indice = IndiceVetorial(dimensao=3)

    assert len(indice) == 0
    assert indice.buscar(np.array([1.0, 0.0, 0.0], dtype=np.float32)) == []


def test_adicionar_incrementa_tamanho_do_indice():
    indice = IndiceVetorial(dimensao=3)

    indice.adicionar(1, np.array([1.0, 0.0, 0.0], dtype=np.float32))
    indice.adicionar(2, np.array([0.0, 1.0, 0.0], dtype=np.float32))

    assert len(indice) == 2


def test_buscar_retorna_vizinho_mais_proximo_primeiro():
    indice = IndiceVetorial(dimensao=3)
    indice.adicionar(1, np.array([1.0, 0.0, 0.0], dtype=np.float32))
    indice.adicionar(2, np.array([0.0, 1.0, 0.0], dtype=np.float32))
    indice.adicionar(3, np.array([0.9, 0.1, 0.0], dtype=np.float32))

    resultados = indice.buscar(np.array([1.0, 0.0, 0.0], dtype=np.float32), top_k=3)

    ids_em_ordem = [marca_id for marca_id, _ in resultados]
    assert ids_em_ordem[0] == 1
    assert ids_em_ordem[-1] == 2


def test_buscar_respeita_top_k_mesmo_maior_que_o_indice():
    indice = IndiceVetorial(dimensao=3)
    indice.adicionar(1, np.array([1.0, 0.0, 0.0], dtype=np.float32))

    resultados = indice.buscar(np.array([1.0, 0.0, 0.0], dtype=np.float32), top_k=10)

    assert len(resultados) == 1


def test_buscar_scores_sao_produto_interno_esperado():
    indice = IndiceVetorial(dimensao=2)
    indice.adicionar(1, np.array([1.0, 0.0], dtype=np.float32))

    (marca_id, score), = indice.buscar(np.array([1.0, 0.0], dtype=np.float32), top_k=1)

    assert marca_id == 1
    assert score == pytest.approx(1.0)


def test_construir_a_partir_do_banco_com_lista_vazia():
    indice = IndiceVetorial.construir_a_partir_do_banco([], dimensao=3)

    assert len(indice) == 0


def test_construir_a_partir_do_banco_com_registros_de_marca_existentes():
    # Regressão: `construir_a_partir_do_banco` já quebrou com TypeError ao
    # tentar indexar objetos `Marca` como se fossem dicts/rows (`marca["id"]`).
    # `listar_marcas()` sempre retorna instâncias de `Marca`, então a
    # reconstrução do índice a partir de um catálogo populado precisa
    # funcionar com esse tipo concreto.
    marcas = [
        _marca(1, [1.0, 0.0, 0.0]),
        _marca(2, [0.0, 1.0, 0.0]),
    ]

    indice = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao=3)

    assert len(indice) == 2
    (melhor_id, _), *_ = indice.buscar(np.array([1.0, 0.0, 0.0], dtype=np.float32), top_k=1)
    assert melhor_id == 1


def test_construir_a_partir_do_banco_inclui_marcas_nao_confirmadas():
    marcas = [_marca(1, [1.0, 0.0, 0.0], confirmado=False)]

    indice = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao=3)

    assert len(indice) == 1
