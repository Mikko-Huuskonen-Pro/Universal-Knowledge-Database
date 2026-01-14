from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import shutil
import time

from ukdbtool.pack.build import init_pack_skeleton, _guess_mime, _now_iso  # type: ignore[attr-defined]
from ukdbtool.pack.hash import sha256_file, write_integrity_hashes
from ukdbtool.pack.validate import validate_pack
from ukdbtool.io.yamlio import read_yaml, write_yaml


_ALLOWLIST_ROOT_FILES = {
    "README.md",
    "ROADMAP.md",
    "LICENSE",
    "CONTRIBUTING.md",
}

_ALLOWLIST_DIRS = {
    "docs",
    "schemas",
    "examples",
}

_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}


@dataclass
class ExportSummary:
    pack_path: Path
    file_count: int
    size_bytes: int


def export_repo_pack(repo_root: Path, out_pack: Path) -> ExportSummary:
    """Export a UKDB pack containing UKDB-related content from a repo.

    The pack will contain:
    - docs/**
    - schemas/**
    - examples/**
    - top-level README.md, ROADMAP.md, LICENSE, CONTRIBUTING.md (if present)
    """
    repo_root = repo_root.resolve()
    # Normalize output to .ukdb directory via init_pack_skeleton
    init_pack_skeleton(out_pack)
    pack = (out_pack if out_pack.suffix == ".ukdb" else Path(str(out_pack) + ".ukdb")).resolve()

    sources_path = pack / "sources.ndjson"
    blobs_dir = pack / "blobs"

    # clear sources written by init
    sources_path.write_text("", encoding="utf-8")

    included_files = _collect_repo_files(repo_root)

    idx = 0
    for p in included_files:
        idx += 1
        h = sha256_file(p)
        ext = p.suffix.lower().lstrip(".") or "bin"
        blob_name = f"{h}.{ext}"
        dest = blobs_dir / blob_name
        if not dest.exists():
            shutil.copy2(p, dest)

        rel = p.relative_to(repo_root)
        src_obj = {
            "id": f"src_{idx:06d}",
            "type": "file",
            "title": p.name,
            "path": str(rel).replace("\\", "/"),
            "retrieved_at": _now_iso(),
            "license": "unknown",
            "reliability": "uncited",
            "blob": {
                "sha256": h,
                "mime": _guess_mime(p),
                "path": f"blobs/{blob_name}",
            },
        }
        _append_ndjson(sources_path, src_obj)

    # Update manifest title and updated_at
    manifest_path = pack / "ukdb.yaml"
    manifest = read_yaml(manifest_path)
    manifest["title"] = "UKDB Repo Export"
    manifest["updated_at"] = _now_iso()
    write_yaml(manifest_path, manifest)

    # Validate and hash, failing loudly if validation fails
    ok = validate_pack(pack)
    if not ok:
        raise RuntimeError(f"Validation failed for exported pack: {pack}")
    write_integrity_hashes(pack)
    # Validate again after hashing
    ok_after = validate_pack(pack)
    if not ok_after:
        raise RuntimeError(f"Validation failed after hashing for exported pack: {pack}")

    size_bytes = sum(p.stat().st_size for p in pack.rglob("*") if p.is_file())
    return ExportSummary(pack_path=pack, file_count=len(included_files), size_bytes=size_bytes)


def _collect_repo_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for p in repo_root.rglob("*"):
        if p.is_dir():
            # Skip excluded directories early
            if p.name in _EXCLUDED_DIRS:
                # rglob will still traverse them, so rely on path checks below as well
                continue
            continue

        rel = p.relative_to(repo_root)
        parts = rel.parts

        # Exclusions by path
        if any(part in _EXCLUDED_DIRS for part in parts):
            continue
        if rel.suffix == ".pyc":
            continue

        # Allowlisted top-level files
        if len(parts) == 1 and parts[0] in _ALLOWLIST_ROOT_FILES:
            files.append(p)
            continue

        # Allowlisted directories
        if parts[0] in _ALLOWLIST_DIRS:
            files.append(p)
            continue

    return sorted(files)


def _append_ndjson(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

