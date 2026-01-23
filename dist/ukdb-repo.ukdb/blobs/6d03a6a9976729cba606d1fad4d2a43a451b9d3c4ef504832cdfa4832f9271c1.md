## UKDB CLI

The `ukdb` command provides a small set of subcommands for working with UKDB packs.

When installed (or from this repo on Windows via `ukdb.cmd`), you can run:

```bash
ukdb --help
```

Subcommands:

- `ukdb init <path>` – create an empty pack skeleton at `<path>.ukdb/`
  - Creates:
    - `ukdb.yaml` manifest
    - empty `entities.ndjson`, `sources.ndjson`, `claims.ndjson`, `notes.ndjson`, `links.ndjson`
    - `blobs/` directory
- `ukdb build <input_dir> <out_pack>` – build a pack from an input directory
  - Accepts any directory of files.
  - Writes/overwrites `<out_pack>.ukdb/` (creating a fresh skeleton).
  - For each file under `input_dir`:
    - copies the file into `blobs/<sha256>.<ext>`
    - appends a `Source` line to `sources.ndjson` with:
      - `id`: `src_000001`, `src_000002`, …
      - `type`: `"file"`
      - `title`: original filename
      - `path`: relative path within `input_dir`
      - `retrieved_at`: build timestamp
      - `license`: `"unknown"`
      - `reliability`: `"uncited"`
      - `blob`: `{ sha256, mime, path: "blobs/<sha256>.<ext>" }`
  - Other NDJSON files remain empty in this MVP.
  - Updates `ukdb.yaml.updated_at` to the build time.
- `ukdb validate <pack>` – validate a pack against the JSON Schemas for its `ukdb_version`
  - `<pack>` can be `name` or `name.ukdb`; the tool normalizes the suffix.
  - Locates schemas from the repository’s `schemas/ukdb-<version>/*.schema.json`.
  - Exits with code `0` and prints `OK: Pack is valid` if everything passes.
- `ukdb hash <pack>` – compute integrity hashes and write them into `ukdb.yaml`
  - Normalizes `<pack>` similarly to `validate`.
  - Computes `sha256` for:
    - `entities.ndjson`, `sources.ndjson`, `claims.ndjson`, `notes.ndjson`, `links.ndjson`
    - all files under `blobs/` (if present)
  - Writes/updates the `integrity` section in `ukdb.yaml`:
    - `integrity.hash_alg = "sha256"`
    - `integrity.files` mapping of relative paths → hex digests
  - Does **not** change the pack contents otherwise.

- `ukdb export <repo_root> <out_dir_or_packname>` – export a pack containing UKDB-related repo content
  - Example: `ukdb export . dist/ukdb-repo` creates `dist/ukdb-repo.ukdb/`.
  - Creates a fresh pack skeleton, then:
    - includes files under `docs/**`, `schemas/**`, and `examples/**`
    - includes top-level `README.md`, `ROADMAP.md`, `LICENSE`, `CONTRIBUTING.md` if present
    - excludes `.git/**`, `.venv/**`, `__pycache__/**`, `dist/**`, `build/**`, `*.pyc`
  - For each included file:
    - copies the file into `blobs/<sha256>.<ext>`
    - appends a `Source` entry to `sources.ndjson` with the file’s path relative to `<repo_root>` and a blob reference
  - Updates the manifest title to `"UKDB Repo Export"` and `updated_at` to the export time.
  - Runs validation and integrity hashing as part of the command:
    - fails (non-zero exit) if validation fails before or after hashing.

### Local usage from this repo (Windows)

This repo includes a small helper script `ukdb.cmd` so you can run the CLI
without adding Python’s Scripts directory to `PATH`:

```powershell
.\ukdb.cmd init tmp-pack
.\ukdb.cmd validate tmp-pack.ukdb
.\ukdb.cmd build tmp-input tmp-built
.\ukdb.cmd hash tmp-built.ukdb
```

