---
name: exlibris-architecture
description: "Guide architecture changes in Ex Libris when work affects module boundaries, new components, refactors, or stack decisions."
---

# Exlibris Architecture

Use this skill when the request changes where logic lives, introduces new modules, or touches cross-cutting decisions.

Start from the existing project shape instead of inventing a new one:

- `src/exlibris/domain` holds pure domain models and types.
- `src/exlibris/application` orchestrates use cases and business flow.
- `src/exlibris/infrastructure` contains SQLite, vector search, and ML integrations.
- `src/exlibris/interface` exposes the CLI and user-facing input/output flow.
- Root-level Python files are compatibility wrappers and should stay thin.

Keep these boundaries stable:

- Do not move persistence, ML, or FAISS/NumPy concerns into `domain`.
- Prefer orchestration in `application` instead of embedding workflow rules in CLI commands.
- Add new adapters under `infrastructure` before creating new top-level packages.
- Preserve backward compatibility in CLI entrypoints unless the task explicitly changes the interface.

When the task is architectural, read [references/architecture.md](references/architecture.md).
When the task may change tooling or dependencies, read [references/stack.md](references/stack.md).

If a change alters module responsibilities, public commands, or data flow, update project documentation in the same task.
