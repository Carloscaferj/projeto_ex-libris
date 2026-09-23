"""Testes de persistência: schema e CRUD contra um SQLite temporário."""

import numpy as np
import pytest

from exlibris.infrastructure.persistence.sqlite_catalog import SQLiteCatalogRepository


@pytest.fixture
def repo(tmp_path):
    repository = SQLiteCatalogRepository(str(tmp_path / "catalogo.db"))
    repository.iniciar_banco()
    return repository


def test_iniciar_banco_e_idempotente(repo):
    repo.iniciar_banco()
    repo.iniciar_banco()

    assert repo.listar_obras() == []


def test_inserir_e_buscar_obra(repo):
    obra_id = repo.inserir_obra("Os Lusíadas", "Luís de Camões", "Lisboa", "Antônio Gonçalves", "1572")

    obra = repo.buscar_obra(obra_id)

    assert obra.id == obra_id
    assert obra.titulo == "Os Lusíadas"
    assert obra.autor == "Luís de Camões"


def test_buscar_obra_inexistente_retorna_none(repo):
    assert repo.buscar_obra(999) is None


def test_listar_obras_retorna_em_ordem_de_insercao(repo):
    id1 = repo.inserir_obra("Primeira")
    id2 = repo.inserir_obra("Segunda")

    obras = repo.listar_obras()

    assert [o.id for o in obras] == [id1, id2]


def test_inserir_marca_preserva_embedding_como_float32(repo):
    embedding = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    marca_id = repo.inserir_marca("marca.jpg", embedding, "ex_libris")

    marca = repo.buscar_marca(marca_id)

    assert marca.embedding.dtype == np.float32
    np.testing.assert_allclose(marca.embedding, embedding, atol=1e-6)


def test_inserir_marca_default_nao_confirmado_e_sem_obra(repo):
    marca_id = repo.inserir_marca("marca.jpg", np.zeros(3, dtype=np.float32), "outro")

    marca = repo.buscar_marca(marca_id)

    assert marca.confirmado is False
    assert marca.obra_id is None


def test_inserir_marca_com_tipo_invalido_e_rejeitada_pelo_schema(repo):
    with pytest.raises(Exception):
        repo.inserir_marca("marca.jpg", np.zeros(3, dtype=np.float32), "tipo_invalido")


def test_atualizar_vinculo_marca_confirma_e_associa_obra(repo):
    obra_id = repo.inserir_obra("Obra")
    marca_id = repo.inserir_marca("marca.jpg", np.zeros(3, dtype=np.float32), "ex_libris")

    repo.atualizar_vinculo_marca(marca_id, obra_id, confirmado=True)

    marca = repo.buscar_marca(marca_id)
    assert marca.obra_id == obra_id
    assert marca.confirmado is True


def test_listar_marcas_inclui_pendentes_e_confirmadas(repo):
    repo.inserir_marca("a.jpg", np.zeros(3, dtype=np.float32), "ex_libris", confirmado=False)
    repo.inserir_marca("b.jpg", np.zeros(3, dtype=np.float32), "ex_libris", confirmado=True)

    marcas = repo.listar_marcas()

    assert len(marcas) == 2
    assert {m.confirmado for m in marcas} == {False, True}


def test_registrar_identificacao_e_buscar_feedback(repo):
    identificacao_id = repo.registrar_identificacao("foto.jpg", None, None, 0.5)

    repo.registrar_feedback(identificacao_id, aceito=True)

    with repo.conectar() as con:
        row = con.execute(
            "SELECT aceito FROM identificacoes WHERE id = ?", (identificacao_id,)
        ).fetchone()
    assert bool(row["aceito"]) is True


def test_remover_obra_desvincula_marca_sem_apagar_a_marca(repo):
    obra_id = repo.inserir_obra("Obra")
    marca_id = repo.inserir_marca("marca.jpg", np.zeros(3, dtype=np.float32), "ex_libris", obra_id=obra_id)

    with repo.conectar() as con:
        con.execute("DELETE FROM obras WHERE id = ?", (obra_id,))

    marca = repo.buscar_marca(marca_id)
    assert marca is not None
    assert marca.obra_id is None
