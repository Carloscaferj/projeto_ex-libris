# Starting-point CI workflow

Adapt before wiring this up — it is a skeleton, not a ready-to-merge file. Confirm the actual Python version and dependency extra name against `pyproject.toml` at the time it's used.

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install project (dev extra)
        run: pip install -e ".[dev]"

      - name: Run fast test suite
        run: pytest -m "not slow"
```

Notes:

- Add the `dev` extra to `pyproject.toml` (`[project.optional-dependencies]`) before this workflow can install it.
- If the `exlibris-testing` skill's `slow` marker doesn't exist yet in `pyproject.toml`, either add it first or drop the `-m "not slow"` filter temporarily.
- Torch/torchvision installs as CPU wheels by default on `ubuntu-latest` runners; do not pin a CUDA index unless the project's stack notes change.
