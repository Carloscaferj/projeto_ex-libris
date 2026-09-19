---
name: exlibris-pr-review
description: "Review Ex Libris changes for regressions, architectural drift, missing tests, and weak pull request hygiene."
---

# Exlibris Pr Review

Use this skill for code review, pre-merge checks, and self-review before opening a PR.

Review with findings first. Prioritize:

- correctness regressions
- data integrity issues
- CLI or workflow breakage
- architecture boundary violations
- undocumented setup or behavior changes

Assume this project is still evolving quickly:

- favor concrete bug and risk detection over style commentary
- call out missing verification plainly
- check whether a change should have updated docs or CLI help

Read [references/review-checklist.md](references/review-checklist.md) when performing a review.
