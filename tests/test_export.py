from __future__ import annotations

from pathlib import Path

from ukdbtool.pack.export import export_repo_pack
from ukdbtool.pack.validate import validate_pack
from ukdbtool.io.yamlio import read_yaml


def _write(dummy_root: Path, rel: str, content: str) -> None:
    path = dummy_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_export_repo_pack_includes_allowlisted_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Allowlisted dirs
    _write(repo, "docs/spec.md", "doc")
    _write(repo, "schemas/ukdb-0.2/manifest.schema.json", "{}")
    _write(repo, "examples/example.ukdb/ukdb.yaml", "ukdb_version: 0.2")

    # Allowlisted root files
    _write(repo, "README.md", "readme")
    _write(repo, "LICENSE", "license")

    # Excluded paths
    _write(repo, ".git/config", "ignore me")
    _write(repo, ".venv/site.py", "ignore me")
    _write(repo, "dist/old-pack/ukdb.yaml", "ignore me")
    _write(repo, "__pycache__/foo.pyc", "ignore me")

    out = tmp_path / "exported"
    summary = export_repo_pack(repo, out)

    pack_dir = summary.pack_path
    assert pack_dir.exists()
    assert (pack_dir / "blobs").is_dir()

    # We should have sources for at least the allowlisted files (5 above).
    sources_lines = (pack_dir / "sources.ndjson").read_text(encoding="utf-8").splitlines()
    assert len(sources_lines) >= 5

    # Manifest title updated and integrity present
    manifest = read_yaml(pack_dir / "ukdb.yaml")
    assert manifest["title"] == "UKDB Repo Export"
    assert "integrity" in manifest
    assert "files" in manifest["integrity"]

    # Exported pack validates (export_repo_pack already validates, but this guards against regressions)
    assert validate_pack(pack_dir)

