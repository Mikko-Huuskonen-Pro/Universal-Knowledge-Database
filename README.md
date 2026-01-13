# Universal-Knowledge-Database
UKDB (Universal Knowledge Database) is an open, AI-agnostic format and toolchain for packaging knowledge. It turns folders of documents, notes, and files into a structured, portable knowledge pack with explicit sources, claims, and metadata, designed to be shared across conversations, tools, and AI systems without vendor lock-in.


# UKDB (Universal Knowledge Database)

UKDB is an open, AI-agnostic knowledge pack format and tooling.

## Goal
Build a program that turns a pile of files (docs, notes, markdown, PDFs, etc.) into a valid **UKDB Pack**
that can be shared across AI chats and tools, without vendor lock-in.

## UKDB Pack (v0.1)
A pack is a folder (or zip) containing:
- `ukdb.yaml` (manifest)
- `entities.ndjson`
- `sources.ndjson`
- `claims.ndjson`
- `notes.ndjson`
- `links.ndjson`
- optional `blobs/` for attachments referenced by SHA256

See: `docs/SPEC_UKDB_0_1.md` and `docs/PACK_FORMAT.md`.

## CLI (planned MVP)
- `ukdb init <path>` – create an empty pack skeleton
- `ukdb build <input_dir> <out_pack>` – build a pack from a directory of files
- `ukdb validate <pack>` – validate pack against JSON Schemas
- `ukdb hash <pack>` – compute and write manifest integrity hashes

Docs: `docs/CLI.md`

## Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ukdb --help