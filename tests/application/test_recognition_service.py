"""Testes de orquestração de `CatalogRecognitionService`.

Usam apenas fakes (ver `conftest.py`): nunca tocam um SQLite real em disco
nem carregam um modelo Torch — os embeddings são vetores sintéticos
pequenos com distâncias conhecidas.
"""

import numpy as np
import pytest


# --- cadastro básico de obras -------------------------------------------------

def test_cadastrar_e_listar_obras(make_service):
    service = make_service()

    obra_id = service.cadastrar_obra("Os Lusíadas", autor="Luís de Camões")

    obras = service.listar_obras()
    assert len(obras) == 1
    assert obras[0].id == obra_id
    assert obras[0].titulo == "Os Lusíadas"


# --- reconstrução do índice a partir do catálogo -------------------------------

def test_indice_e_construido_do_zero_quando_catalogo_esta_vazio(make_service):
    service = make_service()

    assert len(service._indice) == 0


def test_indice_e_reconstruido_a_partir_de_marcas_ja_persistidas(
    fake_repository, fake_extrator, make_service
):
    # Popula o "banco" diretamente, simulando um catálogo já existente antes
    # do serviço ser instanciado (é exatamente o caminho que já quebrou com
    # TypeError ao reconstruir o índice a partir de objetos `Marca`).
    obra_id = fake_repository.inserir_obra("Obra existente")
    fake_repository.inserir_marca(
        "marca-antiga.jpg", np.array([1.0, 0.0, 0.0], dtype=np.float32),
        "ex_libris", obra_id=obra_id, confirmado=True,
    )

    service = make_service(repository=fake_repository)
    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])

    resultado = service.identificar("consulta.jpg", top_k=5)

    assert len(resultado.vizinhos) == 1
    assert resultado.vizinhos[0].score == pytest.approx(1.0)
    assert resultado.novidade is False


# --- marcas pendentes não devem virar candidatas de obra -----------------------

def test_marca_pendente_nao_vira_candidata_de_obra(fake_extrator, make_service):
    service = make_service(limiar_similaridade=0.5)
    obra_id = service.cadastrar_obra("Obra pendente")

    # obra_id setado mas confirmado=False: só é alcançável via API direta do
    # serviço (a CLI sempre confirma quando um --obra-id é passado), mas é
    # exatamente o estado que uma marca "novidade" ainda não curada assume.
    fake_extrator.registrar("pendente.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca(
        "pendente.jpg", "ex_libris", embedding=fake_extrator("pendente.jpg"),
        obra_id=obra_id, confirmado=False,
    )

    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])
    resultado = service.identificar("consulta.jpg", top_k=5)

    obras_ids = [c.obra.id for c in resultado.obras_candidatas]
    assert obra_id not in obras_ids
    # A marca pendente ainda aparece como vizinho similar (útil para
    # curadoria), só não deve contar como candidata de obra confirmada.
    assert len(resultado.vizinhos) == 1


def test_marca_confirmada_vira_candidata_de_obra(fake_extrator, make_service):
    service = make_service(limiar_similaridade=0.5)
    obra_id = service.cadastrar_obra("Obra confirmada")

    fake_extrator.registrar("confirmada.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca(
        "confirmada.jpg", "ex_libris", embedding=fake_extrator("confirmada.jpg"),
        obra_id=obra_id, confirmado=True,
    )

    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])
    resultado = service.identificar("consulta.jpg", top_k=5)

    obras_ids = [c.obra.id for c in resultado.obras_candidatas]
    assert obra_id in obras_ids


# --- idempotência de feedback ---------------------------------------------------

def test_confirmar_vinculo_repetido_nao_desloca_o_prototipo_de_novo(
    fake_extrator, make_service
):
    service = make_service(limiar_similaridade=0.5)
    obra_id = service.cadastrar_obra("Obra")

    fake_extrator.registrar("m1.jpg", [1.0, 0.0, 0.0])
    marca1_id = service.registrar_marca(
        "m1.jpg", "ex_libris", embedding=fake_extrator("m1.jpg"),
        obra_id=obra_id, confirmado=True,
    )

    fake_extrator.registrar("m2.jpg", [0.0, 1.0, 0.0])
    marca2_id = service.registrar_marca(
        "m2.jpg", "ex_libris", embedding=fake_extrator("m2.jpg"),
    )

    service.confirmar_vinculo(marca2_id, obra_id)
    prototipo_apos_primeira_confirmacao = service._prototipos[obra_id].copy()
    contagem_apos_primeira_confirmacao = service._contagem_prototipo[obra_id]

    # Reenviar o mesmo feedback (mesma marca, mesma obra) não pode contar a
    # marca2 uma segunda vez na média do protótipo.
    service.confirmar_vinculo(marca2_id, obra_id)

    assert service._contagem_prototipo[obra_id] == contagem_apos_primeira_confirmacao
    np.testing.assert_array_equal(
        service._prototipos[obra_id], prototipo_apos_primeira_confirmacao
    )
    assert marca1_id != marca2_id  # sanity: duas marcas distintas contribuíram


def test_confirmar_vinculo_com_obra_diferente_atualiza_o_prototipo(
    fake_extrator, make_service
):
    service = make_service(limiar_similaridade=0.5)
    obra_a = service.cadastrar_obra("Obra A")
    obra_b = service.cadastrar_obra("Obra B")

    fake_extrator.registrar("m.jpg", [1.0, 0.0, 0.0])
    marca_id = service.registrar_marca("m.jpg", "ex_libris", embedding=fake_extrator("m.jpg"))

    service.confirmar_vinculo(marca_id, obra_a)
    assert service._contagem_prototipo[obra_a] == 1

    # Corrigir o vínculo para outra obra é uma mudança real, não um replay.
    service.confirmar_vinculo(marca_id, obra_b)
    assert service._contagem_prototipo[obra_b] == 1


# --- filtragem por tipo ----------------------------------------------------------

def test_identificar_filtra_por_tipo_quando_solicitado(fake_extrator, make_service):
    service = make_service(limiar_similaridade=0.5)

    fake_extrator.registrar("ex_libris.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca("ex_libris.jpg", "ex_libris", embedding=fake_extrator("ex_libris.jpg"))

    fake_extrator.registrar("proveniencia.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca(
        "proveniencia.jpg", "proveniencia", embedding=fake_extrator("proveniencia.jpg")
    )

    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])
    resultado = service.identificar("consulta.jpg", tipo="ex_libris", top_k=5)

    assert len(resultado.vizinhos) == 1
    assert resultado.vizinhos[0].tipo == "ex_libris"


def test_identificar_sem_tipo_nao_filtra(fake_extrator, make_service):
    service = make_service(limiar_similaridade=0.5)

    fake_extrator.registrar("ex_libris.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca("ex_libris.jpg", "ex_libris", embedding=fake_extrator("ex_libris.jpg"))

    fake_extrator.registrar("proveniencia.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca(
        "proveniencia.jpg", "proveniencia", embedding=fake_extrator("proveniencia.jpg")
    )

    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])
    resultado = service.identificar("consulta.jpg", top_k=5)

    assert len(resultado.vizinhos) == 2


# --- consistência entre o resultado retornado e o histórico persistido ---------

def test_identificacao_persistida_nao_diverge_do_resultado_retornado(
    fake_repository, fake_extrator, make_service
):
    service = make_service(repository=fake_repository, limiar_similaridade=0.5)
    obra_id = service.cadastrar_obra("Obra")

    fake_extrator.registrar("m.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca(
        "m.jpg", "ex_libris", embedding=fake_extrator("m.jpg"), obra_id=obra_id, confirmado=True,
    )

    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])
    resultado = service.identificar("consulta.jpg", top_k=5)

    registro = fake_repository.identificacoes[-1]
    assert registro["imagem_path"] == "consulta.jpg"
    assert registro["marca_id_sugerida"] == resultado.vizinhos[0].marca_id
    assert registro["confianca"] == pytest.approx(resultado.vizinhos[0].score)
    assert registro["obra_id_sugerida"] == resultado.obras_candidatas[0].obra.id


def test_identificacao_sem_correspondencia_registra_sugestoes_vazias(
    fake_repository, fake_extrator, make_service
):
    service = make_service(repository=fake_repository)
    fake_extrator.registrar("consulta.jpg", [1.0, 0.0, 0.0])

    resultado = service.identificar("consulta.jpg")

    assert resultado.novidade is True
    registro = fake_repository.identificacoes[-1]
    assert registro["marca_id_sugerida"] is None
    assert registro["obra_id_sugerida"] is None
    assert registro["confianca"] == 0.0


# --- registrar_marca: uso do extrator só quando necessário ----------------------

def test_registrar_marca_usa_embedding_informado_sem_chamar_extrator(make_service):
    service = make_service()

    marca_id = service.registrar_marca(
        "sem-extrator.jpg", "outro", embedding=np.array([0.0, 0.0, 1.0], dtype=np.float32),
    )

    assert marca_id is not None


def test_registrar_marca_sem_embedding_chama_o_extrator(fake_extrator, make_service):
    service = make_service()
    fake_extrator.registrar("com-extrator.jpg", [0.0, 0.0, 1.0])

    marca_id = service.registrar_marca("com-extrator.jpg", "outro")

    assert marca_id is not None


def test_registrar_marca_sem_embedding_e_sem_registro_no_extrator_propaga_erro(make_service):
    service = make_service()

    with pytest.raises(KeyError):
        service.registrar_marca("desconhecida.jpg", "outro")


# --- limiar de novidade -----------------------------------------------------------

def test_novidade_e_true_abaixo_do_limiar(fake_extrator, make_service):
    service = make_service(limiar_similaridade=0.9)
    fake_extrator.registrar("base.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca("base.jpg", "ex_libris", embedding=fake_extrator("base.jpg"))

    fake_extrator.registrar("parecido.jpg", [0.7, 0.7, 0.0])  # cos ~0.7 < 0.9
    resultado = service.identificar("parecido.jpg")

    assert resultado.novidade is True


def test_novidade_e_false_acima_do_limiar(fake_extrator, make_service):
    service = make_service(limiar_similaridade=0.5)
    fake_extrator.registrar("base.jpg", [1.0, 0.0, 0.0])
    service.registrar_marca("base.jpg", "ex_libris", embedding=fake_extrator("base.jpg"))

    fake_extrator.registrar("igual.jpg", [1.0, 0.0, 0.0])
    resultado = service.identificar("igual.jpg")

    assert resultado.novidade is False
