"""Fakes usados pelos testes de orquestração de `CatalogRecognitionService`.

Nunca tocam um SQLite real em disco nem carregam um modelo Torch de verdade,
como pede a estratégia de testes de `application` (embeddings sintéticos).
"""

from dataclasses import replace

import numpy as np
import pytest

from exlibris.application.recognition_service import CatalogRecognitionService
from exlibris.domain.models import Marca, Obra


class FakeRepository:
    """Repositório em memória com a mesma interface pública de
    `SQLiteCatalogRepository`, usado para isolar os testes de aplicação do
    SQLite real."""

    def __init__(self):
        self._obras: dict[int, Obra] = {}
        self._marcas: dict[int, Marca] = {}
        self.identificacoes: list[dict] = []
        self._next_obra_id = 1
        self._next_marca_id = 1
        self._next_identificacao_id = 1

    def iniciar_banco(self) -> None:
        pass

    def inserir_obra(self, titulo, autor=None, local=None, editora=None, data=None) -> int:
        obra_id = self._next_obra_id
        self._next_obra_id += 1
        self._obras[obra_id] = Obra(
            id=obra_id, titulo=titulo, autor=autor, local=local,
            editora=editora, data=data, criado_em="2024-01-01T00:00:00+00:00",
        )
        return obra_id

    def buscar_obra(self, obra_id):
        return self._obras.get(obra_id)

    def listar_obras(self):
        return [self._obras[i] for i in sorted(self._obras)]

    def inserir_marca(self, imagem_path, embedding, tipo, obra_id=None,
                       descricao=None, confirmado=False) -> int:
        marca_id = self._next_marca_id
        self._next_marca_id += 1
        self._marcas[marca_id] = Marca(
            id=marca_id, obra_id=obra_id, tipo=tipo, descricao=descricao,
            imagem_path=imagem_path, embedding=np.asarray(embedding, dtype=np.float32),
            confirmado=bool(confirmado), criado_em="2024-01-01T00:00:00+00:00",
        )
        return marca_id

    def atualizar_vinculo_marca(self, marca_id, obra_id, confirmado=True) -> None:
        marca = self._marcas[marca_id]
        self._marcas[marca_id] = replace(marca, obra_id=obra_id, confirmado=bool(confirmado))

    def buscar_marca(self, marca_id):
        marca = self._marcas.get(marca_id)
        return replace(marca) if marca is not None else None

    def listar_marcas(self):
        return [replace(self._marcas[i]) for i in sorted(self._marcas)]

    def registrar_identificacao(self, imagem_path, marca_id_sugerida, obra_id_sugerida, confianca) -> int:
        identificacao_id = self._next_identificacao_id
        self._next_identificacao_id += 1
        self.identificacoes.append({
            "id": identificacao_id,
            "imagem_path": imagem_path,
            "marca_id_sugerida": marca_id_sugerida,
            "obra_id_sugerida": obra_id_sugerida,
            "confianca": confianca,
            "aceito": None,
        })
        return identificacao_id

    def registrar_feedback(self, identificacao_id, aceito) -> None:
        for registro in self.identificacoes:
            if registro["id"] == identificacao_id:
                registro["aceito"] = aceito
                return


class FakeExtrator:
    """Extrator de embeddings determinístico: devolve o vetor sintético
    registrado para cada caminho de imagem, sem tocar Torch/PIL."""

    def __init__(self):
        self._vetores: dict[str, np.ndarray] = {}

    def registrar(self, imagem_path: str, vetor) -> np.ndarray:
        embedding = np.asarray(vetor, dtype=np.float32)
        self._vetores[imagem_path] = embedding
        return embedding

    def __call__(self, imagem_path: str) -> np.ndarray:
        if imagem_path not in self._vetores:
            raise KeyError(f"Nenhum embedding sintético registrado para {imagem_path!r}")
        return self._vetores[imagem_path]


@pytest.fixture
def fake_repository():
    return FakeRepository()


@pytest.fixture
def fake_extrator():
    return FakeExtrator()


@pytest.fixture
def make_service(fake_repository, fake_extrator):
    def _make(dimensao=3, limiar_similaridade=0.75, repository=None):
        return CatalogRecognitionService(
            dimensao=dimensao,
            limiar_similaridade=limiar_similaridade,
            repository=repository if repository is not None else fake_repository,
            extrator_embedding=fake_extrator,
        )

    return _make
