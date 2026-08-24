# Ex Libris delivery workflow

## Branching

- Use short-lived branches.
- Prefer `codex/<area>-<intent>`.
- Avoid mixing refactor, dependency changes, and product behavior unless the task requires it.

## Commits

Recommended format:

`<type>(<optional-scope>): <summary>`

Examples:

- `feat(cli): support manual confirmation notes`
- `fix(search): handle empty index on first run`
- `refactor(application): isolate catalog matching flow`
- `docs: document bootstrap workflow`

## Change hygiene

Before closing a task:

1. Verify the main path affected by the change.
2. Check whether README, CLI help text, or project docs should change.
3. Note risks, tradeoffs, or untested areas explicitly.

## Testing expectation

This repo does not yet expose a strong automated test harness. Until that changes:

- Run the most relevant local verification available.
- Prefer lightweight verification through CLI commands for touched flows.
- If no automated check exists, say so and describe what was validated manually.
