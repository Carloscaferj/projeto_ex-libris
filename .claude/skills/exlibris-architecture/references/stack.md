# Ex Libris stack notes

## Current stack

- Python `>=3.10`
- Packaging with `setuptools`
- Numeric and ML dependencies: `numpy`, `torch`, `torchvision`
- Image handling: `Pillow`
- Storage: SQLite
- Similarity search: FAISS when available, NumPy fallback per project README

## Stack decisions

- Prefer the Python standard library unless a new dependency clearly simplifies an important capability.
- Preserve CPU-friendly workflows when possible; avoid introducing infrastructure that assumes GPU-only execution.
- Favor incremental improvements that fit the current CLI-first product shape.
- If a dependency changes installation complexity, document the tradeoff and any setup step clearly.

## When proposing new tools

- Explain whether the tool belongs in `application`, `infrastructure`, or only in development workflow.
- Avoid adding web frameworks, background workers, or orchestration tooling unless the task genuinely needs them.
- Keep contributor ergonomics in mind; this repo is still at a stage where simplicity is a feature.
