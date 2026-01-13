from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import json
import time

from ukdbtool.pack.hash import sha256_file
from ukdbtool.io.yamlio import read_yaml, write_yaml


EMPTY_NDJSON_FILES = [
    "entities.ndjson",
    "sources.ndjson",
    "claims.ndjson",
    "notes.ndjson",
    "links.ndjson",
]


def init_pack_skeleton(path: Path) -> None:
    path = path if path.suffix == ".ukdb" else Path(str(path) + ".ukdb")
    path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "ukdb_version": "0.1",
        "pack_id": f"pack_{int(time.time())}",
        "title": path.stem,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "license": {"pack": "MIT", "blobs_default": "unknown"},
        "provenance": {"created_by": "human|tool", "generators": []},
        "languages": [],
        "tags": [],
        "integrity": {"hash_alg": "sha256", "files": {}},
        "defaults": {"claim_confidence": 0.6, "source_preference_order": ["official", "reputable", "community", "uncited"]},
    }
    write_yaml(path / "ukdb.yaml", manifest)

    for fn in EMPTY_NDJSON_FILES:
        (path / fn).write_text("", encoding="utf-8")

    (path / "blobs").mkdir(exist_ok=True)


def build_pack(input_dir: Path, out_pack: Path) -> None:
    """
    MVP build strategy:
    - create pack skeleton
    - add each file in input_dir as a Source (type=file) with blob sha256
    - copy blobs to blobs/<sha256>.<ext>
    - write sources.ndjson
    """
    input_dir = input_dir.resolve()
    init_pack_skeleton(out_pack)
    pack = (out_pack if out_pack.suffix == ".ukdb" else Path(str(out_pack) + ".ukdb")).resolve()

    sources_path = pack / "sources.ndjson"
    blobs_dir = pack / "blobs"

    # clear sources
    sources_path.write_text("", encoding="utf-8")

    idx = 0
    for p in input_dir.rglob("*"):
        if p.is_dir():
            continue
        idx += 1
        h = sha256_file(p)
        ext = p.suffix.lower().lstrip(".") or "bin"
        blob_name = f"{h}.{ext}"
        dest = blobs_dir / blob_name
        if not dest.exists():
            shutil.copy2(p, dest)

        src_obj = {
            "id": f"src_{idx:06d}",
            "type": "file",
            "title": p.name,
            "path": str(p.relative_to(input_dir)),
            "retrieved_at": _now_iso(),
            "license": "unknown",
            "reliability": "uncited",
            "blob": {"sha256": h, "mime": _guess_mime(p), "path": f"blobs/{blob_name}"},
        }
        _append_ndjson(sources_path, src_obj)

    # update manifest timestamps
    manifest_path = pack / "ukdb.yaml"
    manifest = read_yaml(manifest_path)
    manifest["updated_at"] = _now_iso()
    write_yaml(manifest_path, manifest)


def _append_ndjson(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _guess_mime(p: Path) -> str:
    # keep simple for MVP
    ext = p.suffix.lower()
    return {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
    }.get(ext, "application/octet-stream")


def _now_iso() -> str:
    # naive ISO local; good enough for MVP
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")
