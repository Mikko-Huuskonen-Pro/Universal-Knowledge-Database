# UKDB Specification v0.1

## Design principles
- AI-agnostic and vendor-neutral
- Human-readable, git-friendly
- Provenance-first: sources and timestamps
- Uncertainty and conflicts are explicit

## Core object kinds
### Entity
Represents a concept/project/person/artifact.

Required:
- id, type, name

### Source
Represents provenance: web, file, conversation, repo, paper.

Required:
- id, type, title
Recommended:
- url OR blob reference OR occurred_at/retrieved_at
- reliability

### Claim
Atomic knowledge statement.

Required:
- id, subject, predicate, object
Recommended:
- confidence (0..1), status, supports[], contradicts[]

### Note
Freeform memo/decision/todo.

Required:
- id, type, body (or title+body)

### Link
Graph edge between objects.

Required:
- id, from, to, type
Recommended:
- weight (0..1)

## No prompt instructions
Core UKDB files MUST NOT contain “how the AI should answer”.
If needed, keep usage instructions outside the core pack (e.g. `usage/`).