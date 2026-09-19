---
name: exlibris-ci
description: "Guide setting up or extending continuous integration in Ex Libris — what to run, on which branches, and what to leave out."
---

# Exlibris CI

Use this skill when asked to add or change automated CI for the project.

Current state: `.github/` only holds a PR template. There is no workflow file, no lint/type-check step, and no `dev`/`test` dependency group declared in `pyproject.toml`.

## What to add, in order

1. A `dev` optional-dependency group in `pyproject.toml` (start with `pytest`; do not add linters/type-checkers the project hasn't asked for — see the `exlibris-architecture` skill's stack notes on avoiding unrequested tooling).
2. A single GitHub Actions workflow (e.g. `.github/workflows/ci.yml`) that: checks out the repo, sets up a Python version satisfying `requires-python = ">=3.10"`, installs the project with the `dev` extra, and runs `pytest -m "not slow"` (see the `exlibris-testing` skill for the `slow` marker convention).
3. Triggers matching this repo's Gitflow branches: run on pull requests targeting `main` and `develop`, and on pushes to those two branches. Do not trigger on every feature branch push — PRs already cover that.

## What to leave out unless explicitly requested

- Coverage gates or coverage-percentage enforcement.
- A build/test matrix across multiple OSes — this project targets a CPU-friendly, single-platform CLI workflow today.
- GPU runners — Torch/torchvision should install as CPU wheels here, consistent with the project's CPU-first stance.
- Release/publish automation.

Keep the workflow file itself small enough to read in one sitting; this project treats simplicity as a feature, and CI should follow the same rule as code.

Read [references/workflow-template.md](references/workflow-template.md) for a starting-point YAML skeleton.
