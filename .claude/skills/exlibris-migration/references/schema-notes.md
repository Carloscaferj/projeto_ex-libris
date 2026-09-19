# Ex Libris — current schema (as of `infrastructure/persistence/sqlite_catalog.py`)

No version tracking exists yet. Everything below is created with `CREATE TABLE IF NOT EXISTS`, so re-running it against an existing database is safe as long as column definitions don't change.

## `obras`

| column      | type    | notes                        |
|-------------|---------|-------------------------------|
| `id`        | INTEGER | primary key, autoincrement    |
| `titulo`    | TEXT    | not null                      |
| `autor`     | TEXT    |                                |
| `local`     | TEXT    |                                |
| `editora`   | TEXT    |                                |
| `data`      | TEXT    |                                |
| `criado_em` | TEXT    | not null                      |

## `marcas`

| column        | type    | notes                                                              |
|---------------|---------|---------------------------------------------------------------------|
| `id`          | INTEGER | primary key, autoincrement                                          |
| `obra_id`     | INTEGER | references `obras(id)`, `ON DELETE SET NULL`                        |
| `tipo`        | TEXT    | not null, `CHECK (tipo IN ('ex_libris', 'proveniencia', 'outro'))`   |
| `descricao`   | TEXT    |                                                                       |
| `imagem_path` | TEXT    | not null                                                             |
| `embedding`   | BLOB    | not null                                                             |
| `confirmado`  | INTEGER | not null, default `0`                                                |
| `criado_em`   | TEXT    | not null                                                             |

Index: `idx_marcas_obra` on `marcas(obra_id)`.

## `identificacoes`

| column               | type    | notes                                          |
|----------------------|---------|-------------------------------------------------|
| `id`                 | INTEGER | primary key, autoincrement                      |
| `imagem_path`        | TEXT    | not null                                        |
| `marca_id_sugerida`  | INTEGER | references `marcas(id)`, `ON DELETE SET NULL`   |
| `obra_id_sugerida`   | INTEGER | references `obras(id)`, `ON DELETE SET NULL`    |
| `confianca`          | REAL    |                                                  |
| `aceito`             | INTEGER |                                                  |
| `criado_em`          | TEXT    | not null                                        |

`PRAGMA foreign_keys = ON;` is set per connection in `SQLiteCatalogRepository.conectar`.

## Gaps to close before the schema can evolve safely

- No `PRAGMA user_version` (or equivalent) is read or written anywhere — there is currently no way to detect "this database predates change X."
- No migration runner exists; adding one is a prerequisite for any non-additive schema change.
