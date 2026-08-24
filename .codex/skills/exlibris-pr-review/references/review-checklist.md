# Ex Libris review checklist

## Correctness

- Does the change preserve the identify, add-marca, feedback, and list-obras flows?
- Could embeddings, similarity scores, or prototype updates become inconsistent?
- Are empty-state and first-run scenarios still safe?

## Architecture

- Is business flow still centered in `application`?
- Did CLI code remain thin?
- Were infra-specific details kept out of the domain?

## Delivery

- Were user-visible behavior changes documented?
- Is verification evidence credible for the touched paths?
- Is the change narrow enough for review?

## What to report

Lead with actionable findings. If no issues are found, say that explicitly and mention residual risks such as missing automated tests or partial manual verification.
