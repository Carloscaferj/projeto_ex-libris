---
name: exlibris-migration
description: "Guide safe schema evolution of the Ex Libris SQLite catalog — versioning, additive changes, and reopening an existing database."
---

# Exlibris Migration

Use this skill when a change adds, renames, or restructures anything in the SQLite schema (`infrastructure/persistence/sqlite_catalog.py`).

Current state: the schema (`obras`, `marcas`, `identificacoes`) is created with `CREATE TABLE IF NOT EXISTS` and has no version tracking and no migration path. This is a known gap (project roadmap M0 goal: "banco existente reabre" — an existing database must still open cleanly after a schema change).

## Rules

- Prefer additive changes: a new nullable column or a new table over renaming/removing an existing one.
- If a column's meaning must change, add a new column, backfill it, and only remove the old one in a separate, later change — never rewrite meaning in place on a column other code may still read.
- Track schema version explicitly. SQLite's own `PRAGMA user_version` is the natural fit here — check and bump it in `infrastructure/persistence`, never in `application` or `domain`.
- Every migration must be idempotent and safe to run against both a brand-new database and one already populated from a previous version.
- A migration that is not purely additive (drops a column, changes a `CHECK` constraint, tightens a `NOT NULL`) needs a documented manual recovery step in the PR, and ideally a dry-run or backup path before it runs destructively.

Read [references/schema-notes.md](references/schema-notes.md) for the current tables, columns, and constraints before writing a migration.
