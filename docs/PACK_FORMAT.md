# UKDB Pack Format (v0.1)

A UKDB Pack is either:
1) a directory ending with `.ukdb/`, or
2) a zip archive `.ukdb.zip` containing the same structure.

## Required files
- `ukdb.yaml` (manifest)
- `entities.ndjson`
- `sources.ndjson`
- `claims.ndjson`
- `notes.ndjson`
- `links.ndjson`

## Optional
- `blobs/` directory for attachments referenced by SHA256.

## NDJSON rules
Each line is a JSON object, UTF-8.
No trailing commas, no arrays at top-level.

## IDs
IDs MUST be stable strings. Recommended:
- ULID or UUIDv4
- prefix by kind: `ent_`, `src_`, `clm_`, `note_`, `lnk_`, `pack_`

## Integrity
Manifest may include hashes for each file and blob (sha256).
