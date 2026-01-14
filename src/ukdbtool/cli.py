from __future__ import annotations

import argparse
from pathlib import Path
from rich.console import Console

from ukdbtool.pack.build import build_pack, init_pack_skeleton
from ukdbtool.pack.validate import validate_pack
from ukdbtool.pack.hash import write_integrity_hashes
from ukdbtool.pack.export import export_repo_pack

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(prog="ukdb", description="UKDB Pack tooling")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create an empty UKDB pack skeleton")
    p_init.add_argument("path", type=Path)

    p_build = sub.add_parser("build", help="Build a UKDB pack from an input directory")
    p_build.add_argument("input_dir", type=Path)
    p_build.add_argument("out_pack", type=Path)

    p_validate = sub.add_parser("validate", help="Validate a UKDB pack against schemas")
    p_validate.add_argument("pack", type=Path)

    p_hash = sub.add_parser("hash", help="Compute integrity hashes and write to manifest")
    p_hash.add_argument("pack", type=Path)

    p_export = sub.add_parser(
        "export",
        help="Export a UKDB pack containing repo docs/schemas/examples and related files",
    )
    p_export.add_argument("repo_root", type=Path)
    p_export.add_argument("out_pack", type=Path)

    args = parser.parse_args()

    if args.cmd == "init":
        init_pack_skeleton(args.path)
        console.print(f"[green]Created pack skeleton:[/green] {args.path}")
        return

    if args.cmd == "build":
        build_pack(args.input_dir, args.out_pack)
        console.print(f"[green]Built pack:[/green] {args.out_pack}")
        return

    if args.cmd == "validate":
        ok = validate_pack(args.pack)
        raise SystemExit(0 if ok else 2)

    if args.cmd == "hash":
        write_integrity_hashes(args.pack)
        console.print(f"[green]Wrote integrity hashes to manifest:[/green] {args.pack / 'ukdb.yaml'}")
        return

    if args.cmd == "export":
        summary = export_repo_pack(args.repo_root, args.out_pack)
        size_mb = summary.size_bytes / (1024 * 1024)
        console.print(
            "[green]Exported repo pack:[/green] "
            f"{summary.pack_path} (files={summary.file_count}, size={size_mb:.2f} MiB)"
        )
        return


if __name__ == "__main__":
    main()