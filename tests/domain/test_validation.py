"""Testes puros das validações de entrada dos casos de uso."""

import numpy as np
import pytest

from exlibris.domain.errors import (
    EmbeddingInvalido,
    TipoMarcaInvalido,
    TituloInvalido,
    TopKInvalido,
    VinculoInvalido,
)
from exlibris.domain.validation import (
    validar_embedding,
    validar_tipo_marca,
    validar_titulo,
    validar_top_k,
    validar_vinculo_confirmado,
)


# --- título -------------------------------------------------------------------

def test_validar_titulo_aceita_titulo_valido_e_remove_espacos():
    assert validar_titulo("  Os Lusíadas  ") == "Os Lusíadas"


@pytest.mark.parametrize("titulo", ["", "   ", None])
def test_validar_titulo_rejeita_titulo_vazio_ou_ausente(titulo):
    with pytest.raises(TituloInvalido):
        validar_titulo(titulo)


# --- tipo de marca --------------------------------------------------------------

@pytest.mark.parametrize("tipo", ["ex_libris", "proveniencia", "outro"])
def test_validar_tipo_marca_aceita_vocabulario_conhecido(tipo):
    assert validar_tipo_marca(tipo) == tipo


@pytest.mark.parametrize("tipo", ["ex-libris", "ExLibris", "", None, "outro "])
def test_validar_tipo_marca_rejeita_valores_fora_do_vocabulario(tipo):
    with pytest.raises(TipoMarcaInvalido):
        validar_tipo_marca(tipo)


# --- top_k ------------------------------------------------------------------------

def test_validar_top_k_aceita_inteiro_positivo_dentro_do_limite():
    assert validar_top_k(5, maximo=50) == 5


@pytest.mark.parametrize("top_k", [0, -1, -100])
def test_validar_top_k_rejeita_nao_positivo(top_k):
    with pytest.raises(TopKInvalido):
        validar_top_k(top_k, maximo=50)


def test_validar_top_k_rejeita_acima_do_limite():
    with pytest.raises(TopKInvalido):
        validar_top_k(51, maximo=50)


@pytest.mark.parametrize("top_k", [5.0, "5", True, None])
def test_validar_top_k_rejeita_tipos_nao_inteiros(top_k):
    with pytest.raises(TopKInvalido):
        validar_top_k(top_k, maximo=50)


# --- embedding -----------------------------------------------------------------

def test_validar_embedding_aceita_vetor_finito_com_norma_e_dimensao_corretas():
    vetor = validar_embedding([1.0, 0.0, 0.0], dimensao=3)

    assert vetor.dtype == np.float32
    assert vetor.shape == (3,)


def test_validar_embedding_rejeita_dimensao_incompativel():
    with pytest.raises(EmbeddingInvalido):
        validar_embedding([1.0, 0.0], dimensao=3)


def test_validar_embedding_rejeita_matriz_em_vez_de_vetor():
    with pytest.raises(EmbeddingInvalido):
        validar_embedding([[1.0, 0.0, 0.0]], dimensao=3)


@pytest.mark.parametrize("valor_invalido", [float("nan"), float("inf"), float("-inf")])
def test_validar_embedding_rejeita_valores_nao_finitos(valor_invalido):
    with pytest.raises(EmbeddingInvalido):
        validar_embedding([valor_invalido, 0.0, 0.0], dimensao=3)


def test_validar_embedding_rejeita_vetor_nulo():
    with pytest.raises(EmbeddingInvalido):
        validar_embedding([0.0, 0.0, 0.0], dimensao=3)


# --- vínculo confirmado -----------------------------------------------------------

def test_validar_vinculo_confirmado_aceita_confirmado_com_obra():
    validar_vinculo_confirmado(obra_id=1, confirmado=True)  # não levanta


def test_validar_vinculo_confirmado_aceita_pendente_sem_obra():
    validar_vinculo_confirmado(obra_id=None, confirmado=False)  # não levanta


def test_validar_vinculo_confirmado_rejeita_confirmado_sem_obra():
    with pytest.raises(VinculoInvalido):
        validar_vinculo_confirmado(obra_id=None, confirmado=True)
