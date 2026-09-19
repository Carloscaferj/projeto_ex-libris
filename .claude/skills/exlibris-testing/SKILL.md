---
name: exlibris-testing
description: "Guide writing and running automated tests in Ex Libris — layout, per-layer strategy, and how to handle non-deterministic ML/similarity code."
---

# Exlibris Testing

Use this skill whenever a task adds, changes, or should be backed by an automated test — including as the last step of a bug fix.

Current state: this project has no automated tests versioned in git (`tests/` may contain stale `__pycache__` files from a previous local run, but no tracked `.py` sources) and no CI. Treat any new test as a net gain; do not wait for a "full suite" before adding one.

## Tooling and layout

- Test runner: `pytest`.
- Mirror the `src/exlibris/<layer>/...` structure under `tests/`: `tests/domain/`, `tests/application/`, `tests/infrastructure/`, `tests/interface/`.
- One test file per module: `tests/<layer>/test_<module>.py`.

## Per-layer strategy

- `domain`: pure unit tests. No database, filesystem, or ML model involved.
- `application`: exercise orchestration (`CatalogRecognitionService`) against fakes/stubs for the repository, vector index, and feature extractor. Never load a real Torch model or touch a real on-disk SQLite file here.
- `infrastructure/persistence`: use a temporary file or `:memory:` SQLite connection per test. Assert schema and CRUD behavior, not application-level rules.
- `infrastructure/search`: use small, hand-crafted embedding vectors with known distances. Do not assert correctness against real ResNet output.
- `infrastructure/ml`: smoke-test shape/dtype of extracted features only; mark model-loading tests so they can be skipped in a fast run.
- `interface`: drive the CLI/argparse entrypoints against a faked application layer for unit coverage, plus a small number of true end-to-end smoke tests against a temp catalog for the golden path.

## Determinism

Recognition depends on floating-point similarity, which is not exactly reproducible across environments. Don't assert exact scores from real models — assert relative ordering, thresholds, or behavior against small deterministic fixtures instead.

Read [references/test-layout.md](references/test-layout.md) for directory/fixture/marker conventions and how to run the suite.
Read [references/known-gaps.md](references/known-gaps.md) for the areas most worth covering first.
