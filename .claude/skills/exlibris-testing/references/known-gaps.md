# Ex Libris — areas most worth testing first

These are the parts of the recognition flow with the highest history of reported inconsistency and zero current coverage. When a task touches any of them, adding a regression test is not optional.

- **Index reconstruction from `Marca` records.** Rebuilding the in-memory/FAISS index from persisted `marcas` rows has previously failed with a `TypeError`. Cover both a fresh index build and a rebuild from an existing populated catalog.
- **Pending/unconfirmed marks leaking into search.** A `Marca` that hasn't been confirmed (`confirmado = 0` in `infrastructure/persistence/sqlite_catalog.py`) should not silently become a match candidate.
- **Feedback idempotency.** Submitting the same feedback/confirmation on the same identification more than once must not keep shifting the underlying prototype embedding each time it's replayed.
- **Type filtering.** `Marca.tipo` (`ex_libris`, `proveniencia`, `outro`) should constrain candidate matches when the caller asks for a specific type; verify it actually does.
- **`identify` vs. persisted history divergence.** The result returned by an identification call should not promise something that the persisted `identificacoes` history later disagrees with.

When fixing one of these, put the regression test in the layer where the bug actually lives (see the `exlibris-architecture` skill) — most of them belong in `application` (orchestration) or `infrastructure/search` (index), not in the CLI.
