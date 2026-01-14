# Contributing

## Development rules (MVP)
- Keep UKDB core AI-agnostic (no prompt instructions inside packs)
- Prefer small, testable steps
- Schemas define the contract; tooling must follow them
- NDJSON is append-friendly and git-friendly

## What to work on first
1) Finish JSON Schemas (schemas/ukdb-0.1/)
2) Make `ukdb init` + `ukdb validate` rock solid
3) Implement `ukdb build` for "pile of files" -> pack
4) Add minimal tests for pack validity

## Commit hygiene
- One logical change per commit
- Update docs when behavior changes