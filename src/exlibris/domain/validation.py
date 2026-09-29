"""Validação de entrada dos casos de uso, independente de infraestrutura.

Cada função recebe um valor bruto, rejeita formatos inválidos com um erro de
`exlibris.domain.errors` e devolve o valor já normalizado. Chamadas diretas
ao serviço de aplicação passam por aqui tanto quanto as vindas da CLI.
"""

from typing import get_args

import numpy as np

from exlibris.domain.errors import (
    EmbeddingInvalido,
    TipoMarcaInvalido,
    TituloInvalido,
    TopKInvalido,
    VinculoInvalido,
)
from exlibris.domain.models import MarcaTipo

TIPOS_DE_MARCA: tuple[str, ...] = get_args(MarcaTipo)


def validar_titulo(titulo: str | None) -> str:
    if titulo is None or not titulo.strip():
        raise TituloInvalido("O título da obra não pode ser vazio.")
    return titulo.strip()


def validar_tipo_marca(tipo: str) -> str:
    if tipo not in TIPOS_DE_MARCA:
        raise TipoMarcaInvalido(
            f"Tipo de marca inválido: {tipo!r}. Use um de {TIPOS_DE_MARCA}."
        )
    return tipo


def validar_top_k(top_k: int, maximo: int) -> int:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
        raise TopKInvalido(f"top_k deve ser um inteiro positivo, recebido {top_k!r}.")
    if top_k > maximo:
        raise TopKInvalido(f"top_k não pode exceder {maximo}, recebido {top_k}.")
    return top_k


def validar_embedding(embedding, dimensao: int) -> np.ndarray:
    vetor = np.asarray(embedding, dtype=np.float32)
    if vetor.ndim != 1 or vetor.shape[0] != dimensao:
        raise EmbeddingInvalido(
            f"Embedding deve ser um vetor de dimensão {dimensao}, "
            f"recebido formato {tuple(vetor.shape)}."
        )
    if not np.all(np.isfinite(vetor)):
        raise EmbeddingInvalido("Embedding contém valores não finitos (NaN ou infinito).")
    norma = float(np.linalg.norm(vetor))
    if norma <= 0:
        raise EmbeddingInvalido("Embedding tem norma nula e não pode ser usado para busca.")
    return vetor


def validar_vinculo_confirmado(obra_id: int | None, confirmado: bool) -> None:
    if confirmado and not obra_id:
        raise VinculoInvalido(
            "Uma marca não pode ser confirmada sem um vínculo válido com uma obra."
        )
