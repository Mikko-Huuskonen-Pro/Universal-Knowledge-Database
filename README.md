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

## CLI
- `ukdb init <path>` – create an empty pack skeleton at `<path>.ukdb/`
- `ukdb build <input_dir> <out_pack>` – build a pack from a directory of files into `<out_pack>.ukdb/`
- `ukdb validate <pack>` – validate pack against JSON Schemas
- `ukdb hash <pack>` – compute and write manifest integrity hashes into `ukdb.yaml`

Docs: `docs/CLI.md`

## Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ukdb --help
```

On Windows from this repo you can also use:

```powershell
.\ukdb.cmd --help
```

Non-goals
No prompt instructions inside UKDB core files.
No model-specific bindings.
Tooling should remain usable without any AI.
License
MIT (see LICENSE)

---

# 2) ROADMAP.md

```md
# Roadmap

## v0.1 (MVP)
- [ ] Define schemas for: manifest, entity, source, claim, note, link
- [ ] Implement `ukdb init`
- [ ] Implement `ukdb validate` (jsonschema)
- [ ] Implement `ukdb hash` (sha256, write to ukdb.yaml integrity section)
- [ ] Implement `ukdb build`:
  - [ ] Crawl input dir
  - [ ] Create `sources` entries for files
  - [ ] Copy attachments into `blobs/` with sha256 filenames
  - [ ] Emit minimal `entities/notes` (optional)
  - [ ] Write pack to output folder
- [ ] Provide example pack in `examples/`

## v0.2
- [ ] Extract entities/claims from Markdown headings & frontmatter (rule-based)
- [ ] Optional “export conversation to pack” adapter (still AI-agnostic)
- [ ] Merge tools: `ukdb merge A B -> C` (dedupe by IDs and hashes)

## v0.3
- [ ] Pluggable extractors (pdf text, md, docx)
- [ ] Provenance graph improvements (supports/contradicts linking)

## v1.0
- [ ] Stable spec + compatibility guarantees
- [ ] Language bindings (Node/Go)