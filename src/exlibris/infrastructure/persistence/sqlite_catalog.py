"""Persistência SQLite para catálogo de obras, marcas e identificações."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import numpy as np

from exlibris import config
from exlibris.domain.models import IdentificacaoRegistrada, Marca, Obra
from exlibris.infrastructure.persistence import migrations

SCHEMA = """
CREATE TABLE IF NOT EXISTS obras (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo      TEXT NOT NULL,
    autor       TEXT,
    local       TEXT,
    editora     TEXT,
    data        TEXT,
    criado_em   TEXT NOT NULL,
    teste       TEXT
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


class SQLiteCatalogRepository:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path

    @contextmanager
    def conectar(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON;")
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def iniciar_banco(self) -> None:
        with self.conectar() as con:
            db_test = con.execute(
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='obras';"
            )
            db_exists = db_test.fetchone() is not None

            if db_exists:
                db_ver_test = con.execute(
                    "PRAGMA user_version;"
                )
                db_ver = db_ver_test.fetchone()[0]
                if db_ver == migrations.SCHEMA_VERSION:
                    return
                else:
                    self.update_schema(db_ver)
                    return
            else:
                con.executescript(SCHEMA)
                con.execute(f"PRAGMA user_version = {migrations.SCHEMA_VERSION};")
                return

    def update_schema(self, db_ver: int) -> None:
        backup_path = f"{self.db_path}.bak"
        con_origem = sqlite3.connect(self.db_path)
        con_backup = sqlite3.connect(backup_path)
        con_origem.backup(con_backup)
        con_origem.close()
        con_backup.close()

        try:

            with self.conectar() as con:
                for versao, sql in migrations.MIGRATIONS:
                    if versao > db_ver:
                        con.executescript(sql)
                con.execute(f"PRAGMA user_version = {migrations.SCHEMA_VERSION};")

                integrity = con.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
                keys_ok = con.execute("PRAGMA foreign_key_check;").fetchall() == []

                if not integrity:
                    raise RuntimeError("Integridade comprometida, restaurando backup...")
                elif not keys_ok:
                    raise RuntimeError("Dados comprometidos, restaurando backup...")

        except Exception:
            con_backup = sqlite3.connect(backup_path)
            con_restaurado = sqlite3.connect(self.db_path)
            con_backup.backup(con_restaurado)
            con_backup.close()
            con_restaurado.close()
            raise


    def inserir_obra(self, titulo, autor=None, local=None, editora=None, data=None) -> int:
        with self.conectar() as con:
            cur = con.execute(
                "INSERT INTO obras (titulo, autor, local, editora, data, criado_em) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (titulo, autor, local, editora, data, _now()),
            )
            return cur.lastrowid

    def buscar_obra(self, obra_id: int):
        with self.conectar() as con:
            row = con.execute("SELECT * FROM obras WHERE id = ?", (obra_id,)).fetchone()
            return self._row_para_obra(row) if row else None

    def listar_obras(self):
        with self.conectar() as con:
            rows = con.execute("SELECT * FROM obras ORDER BY id").fetchall()
            return [self._row_para_obra(r) for r in rows]

    def inserir_marca(self, imagem_path, embedding: np.ndarray, tipo: str, obra_id=None,
                      descricao=None, confirmado: bool = False) -> int:
        vetor = np.asarray(embedding, dtype=np.float32).tobytes()
        with self.conectar() as con:
            cur = con.execute(
                "INSERT INTO marcas (obra_id, tipo, descricao, imagem_path, embedding, "
                "confirmado, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (obra_id, tipo, descricao, imagem_path, vetor, int(confirmado), _now()),
            )
            return cur.lastrowid

    def atualizar_vinculo_marca(self, marca_id: int, obra_id: int, confirmado: bool = True) -> None:
        with self.conectar() as con:
            con.execute(
                "UPDATE marcas SET obra_id = ?, confirmado = ? WHERE id = ?",
                (obra_id, int(confirmado), marca_id),
            )

    def buscar_marca(self, marca_id: int):
        with self.conectar() as con:
            row = con.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
            return self._row_para_marca(row) if row else None

    def listar_marcas(self):
        with self.conectar() as con:
            rows = con.execute("SELECT * FROM marcas").fetchall()
        return [self._row_para_marca(r) for r in rows]

    def registrar_identificacao(self, imagem_path, marca_id_sugerida, obra_id_sugerida,
                                confianca) -> int:
        with self.conectar() as con:
            cur = con.execute(
                "INSERT INTO identificacoes (imagem_path, marca_id_sugerida, "
                "obra_id_sugerida, confianca, aceito, criado_em) VALUES (?, ?, ?, ?, ?, ?)",
                (imagem_path, marca_id_sugerida, obra_id_sugerida, confianca, None, _now()),
            )
            return cur.lastrowid

    def registrar_feedback(self, identificacao_id: int, aceito: bool) -> None:
        with self.conectar() as con:
            con.execute(
                "UPDATE identificacoes SET aceito = ? WHERE id = ?",
                (int(aceito), identificacao_id),
            )

    @staticmethod
    def _row_para_obra(row: sqlite3.Row) -> Obra:
        return Obra(
            id=row["id"],
            titulo=row["titulo"],
            autor=row["autor"],
            local=row["local"],
            editora=row["editora"],
            data=row["data"],
            criado_em=row["criado_em"],
        )

    @staticmethod
    def _row_para_marca(row: sqlite3.Row) -> Marca:
        return Marca(
            id=row["id"],
            obra_id=row["obra_id"],
            tipo=row["tipo"],
            descricao=row["descricao"],
            imagem_path=row["imagem_path"],
            embedding=np.frombuffer(row["embedding"], dtype=np.float32),
            confirmado=bool(row["confirmado"]),
            criado_em=row["criado_em"],
        )
