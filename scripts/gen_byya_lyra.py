#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse
import sys
from pathlib import Path

from _common import (
    add_pt,
    check_dependencies,
    compile_typst,
    convert_to_jpg,
    font_tuple,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def generate_typ(md_path, size, font, output_dir):
    typs_dir = output_dir / "typs"
    typs_dir.mkdir(parents=True, exist_ok=True)

    content = f"""#import "@preview/cmarker:0.1.9"
#import "../../../../scripts/byya-lyra-template.typ": *

#show: lyra-layout.with(size: {add_pt(size)}, font: {font_tuple(font)})

#cmarker.render(read("../../{md_path.name}"))"""

    typ_path = typs_dir / f"{md_path.stem}.typ"
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")
    return typ_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("subdir", choices=["lyra-a", "lyra-b", "orion-a"])
    parser.add_argument("--size", default="8pt")
    parser.add_argument("--font", default="MonaspiceNe NFM, Sarasa Mono SC")
    args = parser.parse_args()

    check_dependencies()

    root = Path(__file__).resolve().parent.parent
    content_dir = root / "byya-lyra" / args.subdir
    if not content_dir.exists():
        sys.exit(f"Error: subdir not found: {content_dir}")

    output_dir = content_dir / "_output"
    pdfs_dir = output_dir / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(content_dir.glob("*.md"))
    if not md_files:
        sys.exit(f"Error: no .md files in {content_dir}")

    ok = 0
    for md_path in md_files:
        typ_path = generate_typ(md_path, args.size, args.font, output_dir)
        pdf_path = pdfs_dir / f"{md_path.stem}.pdf"
        compile_typst(typ_path, pdf_path, root)
        if convert_to_jpg(
            pdf_path,
            str(output_dir / f"{md_path.stem}_p%02d.jpg"),
            fail_on_error=False,
        ):
            ok += 1
    print(f"\nDone: {ok}/{len(md_files)} JPGs in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
