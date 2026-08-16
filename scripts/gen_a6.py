#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse
import sys

from _common import (
    add_pt,
    check_dependencies,
    compile_typst,
    convert_to_jpg,
    font_tuple,
    resolve_path,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def generate_typ(content_path, size, font, output_dir):
    typs_dir = output_dir / "typs"
    typs_dir.mkdir(exist_ok=True)

    size = add_pt(size)
    ft = font_tuple(font)
    content = f"""#import "@preview/cmarker:0.1.9"

#set page(paper: "a6", margin: 5%)
#set text(font: {ft}, size: {size})
#set par(justify: true)

#show raw.where(block: false): set text(font: {ft}, size: {size})
#show raw.where(block: true):  set text(font: {ft}, size: 0.9em)

#show heading.where(level: 2): set text(size: {size} + 1pt)

#cmarker.render(read("../../{content_path.name}"))"""

    typ_path = typs_dir / f"{content_path.stem}.typ"
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")
    return typ_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--size", default="8pt")
    parser.add_argument("--font", default="MonaspiceNe NFM, Sarasa Mono SC")
    args = parser.parse_args()

    check_dependencies()

    content_path = resolve_path(args.path)
    if not content_path.exists():
        sys.exit(f"Error: File not found: {content_path}")

    content_dir = content_path.parent
    project_root = content_dir.parent
    output_dir = content_dir / "_output"
    pdfs_dir = output_dir / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    typ_path = generate_typ(content_path, args.size, args.font, output_dir)
    pdf_path = pdfs_dir / f"{content_path.stem}.pdf"
    compile_typst(typ_path, pdf_path, project_root)
    convert_to_jpg(pdf_path, str(output_dir / f"{content_path.stem}_p%02d.jpg"))
    print(f"Created: {output_dir}/{content_path.stem}_p*.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
