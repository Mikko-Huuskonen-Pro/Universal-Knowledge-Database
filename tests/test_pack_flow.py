from __future__ import annotations

from pathlib import Path

from ukdbtool.pack.build import init_pack_skeleton, build_pack
from ukdbtool.pack.validate import validate_pack
from ukdbtool.pack.hash import write_integrity_hashes


def test_init_and_validate(tmp_path: Path) -> None:
    pack = tmp_path / "tmp-pack"
    init_pack_skeleton(pack)

    pack_dir = pack if pack.suffix == ".ukdb" else Path(str(pack) + ".ukdb")
    # required files
    for name in [
        "ukdb.yaml",
        "entities.ndjson",
        "sources.ndjson",
        "claims.ndjson",
        "notes.ndjson",
        "links.ndjson",
        "blobs",
    ]:
        assert (pack_dir / name).exists()

    assert validate_pack(pack_dir)


def test_build_hash_and_validate(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "a.txt").write_text("hello txt", encoding="utf-8")
    (input_dir / "b.md").write_text("# hello md", encoding="utf-8")

    out_pack = tmp_path / "built"
    build_pack(input_dir, out_pack)

    pack_dir = out_pack if out_pack.suffix == ".ukdb" else Path(str(out_pack) + ".ukdb")

    # sources.ndjson should have one line per input file
    sources_lines = (pack_dir / "sources.ndjson").read_text(encoding="utf-8").splitlines()
    assert len(sources_lines) == 2

    # blobs should exist
    blobs = list((pack_dir / "blobs").iterdir())
    assert len(blobs) == 2

    assert validate_pack(pack_dir)

    # write hashes and ensure manifest now contains integrity info
    write_integrity_hashes(pack_dir)
    manifest_text = (pack_dir / "ukdb.yaml").read_text(encoding="utf-8")
    assert "integrity:" in manifest_text
    assert "files:" in manifest_text

    # still validates after hashing
    assert validate_pack(pack_dir)

