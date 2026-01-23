from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator
from rich.console import Console

from ukdbtool.io.yamlio import read_yaml

console = Console()


def validate_pack(pack: Path) -> bool:
    pack = pack if pack.suffix == ".ukdb" else Path(str(pack) + ".ukdb")

    ok = True

    # validate manifest
    manifest = read_yaml(pack / "ukdb.yaml")
    schema_dir = _schema_dir_for_version(manifest.get("ukdb_version"))
    if schema_dir is None:
        console.print("[red]FAIL:[/red] Unknown or missing ukdb_version in ukdb.yaml")
        return False

    ok &= _validate_json(manifest, schema_dir / "manifest.schema.json", "ukdb.yaml")
    ok &= _validate_no_floats(manifest, "ukdb.yaml")
    _warn_ambiguous_numeric_fields(manifest, "ukdb.yaml")

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
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
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
        ok &= _validate_no_floats(obj, f"{path.name}:{i}")
        _warn_ambiguous_numeric_fields(obj, f"{path.name}:{i}")
    return ok


def _validate_json(obj: dict, schema_path: Path, label: str) -> bool:
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    validator = Draft202012Validator(schema)
    ok = True
    for err in validator.iter_errors(obj):
        console.print(f"[red]{label}[/red] {err.message}")
        ok = False
    return ok


def _schema_dir_for_version(version: str | None) -> Path | None:
    if version not in {"0.1", "0.2"}:
        return None
    return Path(__file__).resolve().parents[3] / "schemas" / f"ukdb-{version}"


def _validate_no_floats(obj: object, label: str) -> bool:
    ok = True
    for path in _find_floats(obj):
        console.print(f"[red]{label}[/red] float value not allowed at {path}")
        ok = False
    return ok


def _find_floats(obj: object, path: str = "$") -> list[str]:
    if isinstance(obj, bool):
        return []
    if isinstance(obj, float):
        return [path]
    if isinstance(obj, dict):
        found: list[str] = []
        for key, value in obj.items():
            found.extend(_find_floats(value, f"{path}.{key}"))
        return found
    if isinstance(obj, list):
        found = []
        for idx, value in enumerate(obj):
            found.extend(_find_floats(value, f"{path}[{idx}]"))
        return found
    return []


def _warn_ambiguous_numeric_fields(obj: object, label: str) -> None:
    for path, key in _find_ambiguous_numeric_fields(obj):
        console.print(f"[yellow]WARN:[/yellow] {label} ambiguous numeric field {path}.{key}")


def _find_ambiguous_numeric_fields(obj: object, path: str = "$") -> list[tuple[str, str]]:
    if isinstance(obj, list):
        found: list[tuple[str, str]] = []
        for idx, value in enumerate(obj):
            found.extend(_find_ambiguous_numeric_fields(value, f"{path}[{idx}]"))
        return found
    if not isinstance(obj, dict):
        return []

    allowed_suffixes = (
        "_cents",
        "_bp",
        "_count",
        "_days",
        "_hours",
        "_minutes",
        "_year",
        "_month",
    )
    keyword_hints = (
        "amount",
        "price",
        "cost",
        "salary",
        "wage",
        "income",
        "tax",
        "rate",
        "percent",
        "percentage",
        "allowance",
        "pension",
        "fee",
        "budget",
        "balance",
        "total",
        "revenue",
        "expense",
        "vat",
        "rent",
        "interest",
        "discount",
    )

    found = []
    for key, value in obj.items():
        if isinstance(value, dict):
            found.extend(_find_ambiguous_numeric_fields(value, f"{path}.{key}"))
            continue
        if isinstance(value, list):
            found.extend(_find_ambiguous_numeric_fields(value, f"{path}.{key}"))
            continue
        if isinstance(value, bool):
            continue
        if not isinstance(value, (int, float)):
            continue
        key_lower = key.lower()
        if key_lower.endswith(allowed_suffixes):
            continue
        if any(hint in key_lower for hint in keyword_hints):
            found.append((path, key))
    return found
