"""Camada de persistência: catálogo de obras e marcas (ex-libris / proveniência).

Usa SQLite puro (sem ORM) para manter o sistema fácil de inspecionar e migrar.
Os embeddings são guardados como BLOB (bytes de um array numpy float32), o que
permite reconstruir o índice vetorial de busca a qualquer momento a partir do
banco de dados.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import numpy as np

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS obras (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo      TEXT NOT NULL,
    autor       TEXT,
    local       TEXT,
    editora     TEXT,
    data        TEXT,
    criado_em   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS marcas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    obra_id       INTEGER REFERENCES obras(id) ON DELETE SET NULL,
    tipo          TEXT NOT NULL CHECK (tipo IN ('ex_libris', 'proveniencia', 'outro')),
    descricao     TEXT,
    imagem_path   TEXT NOT NULL,
    embedding     BLOB NOT NULL,
    confirmado    INTEGER NOT NULL DEFAULT 0,
    criado_em     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS identificacoes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    imagem_path         TEXT NOT NULL,
    marca_id_sugerida   INTEGER REFERENCES marcas(id) ON DELETE SET NULL,
    obra_id_sugerida    INTEGER REFERENCES obras(id) ON DELETE SET NULL,
    confianca           REAL,
    aceito              INTEGER,
    criado_em           TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_marcas_obra ON marcas(obra_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def conectar(db_path: str = config.DB_PATH):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def iniciar_banco(db_path: str = config.DB_PATH) -> None:
    with conectar(db_path) as con:
        con.executescript(SCHEMA)


# ---------------------------------------------------------------- obras ----

def inserir_obra(titulo, autor=None, local=None, editora=None, data=None,
                  db_path: str = config.DB_PATH) -> int:
    with conectar(db_path) as con:
        cur = con.execute(
            "INSERT INTO obras (titulo, autor, local, editora, data, criado_em) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (titulo, autor, local, editora, data, _now()),
        )
        return cur.lastrowid


def buscar_obra(obra_id: int, db_path: str = config.DB_PATH):
    with conectar(db_path) as con:
        row = con.execute("SELECT * FROM obras WHERE id = ?", (obra_id,)).fetchone()
        return dict(row) if row else None


def listar_obras(db_path: str = config.DB_PATH):
    with conectar(db_path) as con:
        rows = con.execute("SELECT * FROM obras ORDER BY id").fetchall()
        return [dict(r) for r in rows]


# --------------------------------------------------------------- marcas ----

def inserir_marca(imagem_path, embedding: np.ndarray, tipo: str, obra_id=None,
                   descricao=None, confirmado: bool = False,
                   db_path: str = config.DB_PATH) -> int:
    vetor = np.asarray(embedding, dtype=np.float32).tobytes()
    with conectar(db_path) as con:
        cur = con.execute(
            "INSERT INTO marcas (obra_id, tipo, descricao, imagem_path, embedding, "
            "confirmado, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (obra_id, tipo, descricao, imagem_path, vetor, int(confirmado), _now()),
        )
        return cur.lastrowid


def atualizar_vinculo_marca(marca_id: int, obra_id: int, confirmado: bool = True,
                             db_path: str = config.DB_PATH) -> None:
    with conectar(db_path) as con:
        con.execute(
            "UPDATE marcas SET obra_id = ?, confirmado = ? WHERE id = ?",
            (obra_id, int(confirmado), marca_id),
        )


def buscar_marca(marca_id: int, db_path: str = config.DB_PATH):
    with conectar(db_path) as con:
        row = con.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
        return dict(row) if row else None


def listar_marcas(db_path: str = config.DB_PATH):
    """Retorna todas as marcas já com o embedding decodificado em numpy."""
    with conectar(db_path) as con:
        rows = con.execute("SELECT * FROM marcas").fetchall()
    marcas = []
    for r in rows:
        d = dict(r)
        d["embedding"] = np.frombuffer(d["embedding"], dtype=np.float32)
        marcas.append(d)
    return marcas


# ------------------------------------------------------- identificacoes ----

def registrar_identificacao(imagem_path, marca_id_sugerida, obra_id_sugerida,
                             confianca, db_path: str = config.DB_PATH) -> int:
    with conectar(db_path) as con:
        cur = con.execute(
            "INSERT INTO identificacoes (imagem_path, marca_id_sugerida, "
            "obra_id_sugerida, confianca, aceito, criado_em) VALUES (?, ?, ?, ?, ?, ?)",
            (imagem_path, marca_id_sugerida, obra_id_sugerida, confianca, None, _now()),
        )
        return cur.lastrowid


def registrar_feedback(identificacao_id: int, aceito: bool,
                        db_path: str = config.DB_PATH) -> None:
    with conectar(db_path) as con:
        con.execute(
            "UPDATE identificacoes SET aceito = ? WHERE id = ?",
            (int(aceito), identificacao_id),
        )
