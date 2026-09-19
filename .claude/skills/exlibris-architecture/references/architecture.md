# Ex Libris architecture notes

## Current structure

The repository already contains a workable layered split:

- `domain`: `Obra`, `Marca`, and identification result types.
- `application`: `CatalogRecognitionService`, the main orchestration entrypoint.
- `infrastructure/persistence`: SQLite repository and schema-facing code.
- `infrastructure/ml`: embedding extraction.
- `infrastructure/search`: vector index and similarity lookup.
- `interface`: argparse commands and terminal output.

## Architectural rules

1. Keep the domain dependency-light.
   Domain files should avoid persistence, CLI, and framework-specific behavior.

2. Let application coordinate.
   Multi-step flows such as identify, register, confirm, and retrain-by-feedback should stay in application services.

3. Treat infrastructure as replaceable.
   SQLite, FAISS, NumPy fallback, and future HTTP or model providers should be adapters around the use case layer.

4. Treat interface as translation.
   CLI code should parse arguments, call application services, and format responses. It should not become the business layer.

## Preferred evolution path

- New ingestion sources: add adapters under `infrastructure` and orchestrate them from `application`.
- API/server support: add a new interface layer, not business logic duplicated outside `application`.
- Better recognition models: swap or extend `infrastructure/ml` behind stable application behavior.
- New storage backends: add a repository implementation and keep service contracts stable.

## Smells to avoid

- Business rules spread between CLI and repository classes.
- Public imports pointing to legacy root files instead of `src/exlibris/...`.
- Cross-layer imports from `domain` into infrastructure-specific utilities.
- Refactors that bypass the service layer and make tests or future interfaces harder.
