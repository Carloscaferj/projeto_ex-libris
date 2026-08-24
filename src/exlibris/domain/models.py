"""Modelos tipados do domínio."""

from dataclasses import dataclass
from typing import Literal

import numpy as np

MarcaTipo = Literal["ex_libris", "proveniencia", "outro"]


@dataclass(slots=True)
class Obra:
    id: int
    titulo: str
    autor: str | None
    local: str | None
    editora: str | None
    data: str | None
    criado_em: str


@dataclass(slots=True)
class Marca:
    id: int
    obra_id: int | None
    tipo: MarcaTipo
    descricao: str | None
    imagem_path: str
    embedding: np.ndarray
    confirmado: bool
    criado_em: str


@dataclass(slots=True)
class IdentificacaoRegistrada:
    id: int
    imagem_path: str
    marca_id_sugerida: int | None
    obra_id_sugerida: int | None
    confianca: float | None
    aceito: bool | None
    criado_em: str


@dataclass(slots=True)
class MarcaVizinha:
    marca_id: int
    tipo: MarcaTipo
    obra: Obra | None
    score: float


@dataclass(slots=True)
class ObraCandidata:
    obra: Obra
    score: float


@dataclass(slots=True)
class ResultadoIdentificacao:
    embedding: np.ndarray
    vizinhos: list[MarcaVizinha]
    obras_candidatas: list[ObraCandidata]
    novidade: bool
    tipo_consultado: MarcaTipo | None
