from __future__ import annotations

import hashlib
from pathlib import Path
from ukdbtool.io.yamlio import read_yaml, write_yaml


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_integrity_hashes(pack: Path) -> None:
    pack = pack if pack.suffix == ".ukdb" else Path(str(pack) + ".ukdb")
    manifest_path = pack / "ukdb.yaml"
    manifest = read_yaml(manifest_path)

    files = {}
    for fn in ["entities.ndjson", "sources.ndjson", "claims.ndjson", "notes.ndjson", "links.ndjson"]:
        p = pack / fn
        files[fn] = sha256_file(p)

    # blobs optional
    blobs_dir = pack / "blobs"
    if blobs_dir.exists():
        for b in blobs_dir.iterdir():
            if b.is_file():
                files[f"blobs/{b.name}"] = sha256_file(b)

    manifest.setdefault("integrity", {})
    manifest["integrity"]["hash_alg"] = "sha256"
    manifest["integrity"]["files"] = files
    write_yaml(manifest_path, manifest)