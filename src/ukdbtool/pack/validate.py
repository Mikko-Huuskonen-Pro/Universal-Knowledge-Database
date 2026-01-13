from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator
from rich.console import Console

from ukdbtool.io.yamlio import read_yaml

console = Console()


def validate_pack(pack: Path) -> bool:
    pack = pack if pack.suffix == ".ukdb" else Path(str(pack) + ".ukdb")

    schema_dir = Path(__file__).resolve().parents[3] / "schemas" / "ukdb-0.1"
    ok = True

    # validate manifest
    manifest = read_yaml(pack / "ukdb.yaml")
    ok &= _validate_json(manifest, schema_dir / "manifest.schema.json", "ukdb.yaml")

    # validate ndjson lines
    ok &= _validate_ndjson(pack / "entities.ndjson", schema_dir / "entity.schema.json")
    ok &= _validate_ndjson(pack / "sources.ndjson", schema_dir / "source.schema.json")
    ok &= _validate_ndjson(pack / "claims.ndjson", schema_dir / "claim.schema.json")
    ok &= _validate_ndjson(pack / "notes.ndjson", schema_dir / "note.schema.json")
    ok &= _validate_ndjson(pack / "links.ndjson", schema_dir / "link.schema.json")

    if ok:
        console.print("[green]OK:[/green] Pack is valid")
    else:
        console.print("[red]FAIL:[/red] Pack has validation errors")
    return ok


def _validate_ndjson(path: Path, schema_path: Path) -> bool:
    if not path.exists():
        console.print(f"[red]Missing file:[/red] {path.name}")
        return False
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    ok = True
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            console.print(f"[red]{path.name}:{i} JSON error:[/red] {e}")
            ok = False
            continue
        for err in validator.iter_errors(obj):
            console.print(f"[red]{path.name}:{i}[/red] {err.message}")
            ok = False
    return ok


def _validate_json(obj: dict, schema_path: Path, label: str) -> bool:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    ok = True
    for err in validator.iter_errors(obj):
        console.print(f"[red]{label}[/red] {err.message}")
        ok = False
    return ok