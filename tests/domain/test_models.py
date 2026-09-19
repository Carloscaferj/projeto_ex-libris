"""Testes puros dos modelos de domínio (sem banco, filesystem ou ML)."""

import numpy as np
import pytest

from exlibris.domain.models import (
    IdentificacaoRegistrada,
    Marca,
    MarcaVizinha,
    Obra,
    ObraCandidata,
    ResultadoIdentificacao,
)


def test_obra_guarda_os_campos_informados():
    obra = Obra(
        id=1, titulo="Os Lusíadas", autor="Luís de Camões", local="Lisboa",
        editora="Antônio Gonçalves", data="1572", criado_em="2024-01-01T00:00:00+00:00",
    )

    assert obra.id == 1
    assert obra.titulo == "Os Lusíadas"
    assert obra.autor == "Luís de Camões"


def test_obra_aceita_campos_opcionais_ausentes():
    obra = Obra(
        id=2, titulo="Sem metadados", autor=None, local=None,
        editora=None, data=None, criado_em="2024-01-01T00:00:00+00:00",
    )

    assert obra.autor is None
    assert obra.local is None


def test_marca_guarda_embedding_e_tipo():
    embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    marca = Marca(
        id=1, obra_id=None, tipo="ex_libris", descricao=None,
        imagem_path="foto.jpg", embedding=embedding, confirmado=False,
        criado_em="2024-01-01T00:00:00+00:00",
    )

    assert marca.tipo == "ex_libris"
    assert marca.confirmado is False
    np.testing.assert_array_equal(marca.embedding, embedding)


def test_marca_tipo_invalido_nao_e_bloqueado_em_tempo_de_execucao():
    # `MarcaTipo` é um Literal, checado estaticamente; em runtime o dataclass
    # não valida o valor. Documentamos esse comportamento aqui para que uma
    # futura validação em runtime seja uma mudança deliberada, não acidental.
    marca = Marca(
        id=1, obra_id=None, tipo="qualquer-coisa", descricao=None,
        imagem_path="foto.jpg", embedding=np.zeros(3, dtype=np.float32),
        confirmado=False, criado_em="2024-01-01T00:00:00+00:00",
    )

    assert marca.tipo == "qualquer-coisa"


def test_dataclasses_de_dominio_sao_slots_e_nao_aceitam_atributos_extras():
    marca = Marca(
        id=1, obra_id=None, tipo="ex_libris", descricao=None,
        imagem_path="foto.jpg", embedding=np.zeros(3, dtype=np.float32),
        confirmado=False, criado_em="2024-01-01T00:00:00+00:00",
    )

    with pytest.raises(AttributeError):
        marca.campo_inexistente = "valor"


def test_resultado_identificacao_agrupa_vizinhos_e_candidatas():
    obra = Obra(id=1, titulo="Obra", autor=None, local=None, editora=None,
                data=None, criado_em="2024-01-01T00:00:00+00:00")
    vizinho = MarcaVizinha(marca_id=10, tipo="ex_libris", obra=obra, score=0.9)
    candidata = ObraCandidata(obra=obra, score=0.9)

    resultado = ResultadoIdentificacao(
        embedding=np.zeros(3, dtype=np.float32),
        vizinhos=[vizinho],
        obras_candidatas=[candidata],
        novidade=False,
        tipo_consultado="ex_libris",
    )

    assert resultado.vizinhos == [vizinho]
    assert resultado.obras_candidatas == [candidata]
    assert resultado.novidade is False


def test_identificacao_registrada_permite_confianca_e_aceite_ausentes():
    identificacao = IdentificacaoRegistrada(
        id=1, imagem_path="foto.jpg", marca_id_sugerida=None,
        obra_id_sugerida=None, confianca=None, aceito=None,
        criado_em="2024-01-01T00:00:00+00:00",
    )

    assert identificacao.marca_id_sugerida is None
    assert identificacao.aceito is None
