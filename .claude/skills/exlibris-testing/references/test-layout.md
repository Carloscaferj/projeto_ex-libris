# Ex Libris test layout

## Directory convention

```
tests/
  domain/
    test_models.py
  application/
    test_recognition_service.py
  infrastructure/
    persistence/
      test_sqlite_catalog.py
    search/
      test_vector_index.py
    ml/
      test_feature_extractor.py
  interface/
    test_cli.py
```

This mirrors `src/exlibris/<layer>/...` one level at a time, so a reviewer can find the test for a module by substituting `src` for `tests`.

## Fixtures

- Prefer `tmp_path` (pytest built-in) over hand-rolled temp-file cleanup for anything touching SQLite or the filesystem.
- Put fakes/stubs used by more than one `application` test in a local `conftest.py` under `tests/application/`, not in a shared top-level utils module, unless a third layer needs the same fake.
- Keep fixtures free of real Torch/FAISS calls unless the test is explicitly marked as exercising the real model.

## Markers

Add to `pyproject.toml` under `[tool.pytest.ini_options]` when the first marker is introduced:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: loads a real ML model or does real vector search at scale",
]
```

Mark any test that loads the real ResNet model or runs FAISS against a non-trivial index as `slow`, so a fast local/CI run can do `pytest -m "not slow"`.

## Running

- Full suite: `pytest`
- Fast subset only: `pytest -m "not slow"`
- Single layer: `pytest tests/application`
