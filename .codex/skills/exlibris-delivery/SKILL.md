---
name: exlibris-delivery
description: "Guide implementation workflow in Ex Libris for branches, commits, documentation, and pull request preparation."
---

# Exlibris Delivery

Use this skill when shipping a change, preparing commits, or organizing work into reviewable slices.

Prefer small, coherent changes:

- Keep one concern per branch or PR when possible.
- Update docs when behavior, CLI usage, architecture, or setup changes.
- Call out missing tests instead of pretending they exist.

Use these project conventions:

- Branch name: `codex/<area>-<intent>` such as `codex/cli-feedback-flow`.
- Commit style: Conventional Commit inspired prefixes like `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
- Commit scope is optional, but helpful when it clarifies the subsystem, for example `feat(cli):` or `refactor(application):`.

Before finalizing work, read [references/workflow.md](references/workflow.md).
When preparing or summarizing a PR, read [references/pr-template.md](references/pr-template.md).
