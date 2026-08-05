# /// script
# requires-python = ">=3.12"
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
    resolve_path,
)

TEMPLATE = Path("../../../scripts/receipt-template.typ").as_posix()


def generate_typ(content_path, size, font, rotate, width, output_dir):
    typs_dir = output_dir / "typs"
    typs_dir.mkdir(exist_ok=True)

    layout = (
        f"size: {add_pt(size)}, font: {font_tuple(font)}, rotate: {str(rotate).lower()}"
    )
    if width:
        layout += f", width: {width}"

    content = f"""#import "{TEMPLATE}": *
#show: receipt-layout.with({layout})

{content_path.read_text(encoding="utf-8")}
"""
    generated = typs_dir / f"{content_path.stem}.typ"
    generated.write_text(content, encoding="utf-8")
    print(f"Created: {generated}")
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--size", default="8pt")
    parser.add_argument("--font", default="Sarasa Mono SC")
    parser.add_argument("--rotate", action="store_true")
    parser.add_argument("--width", default="")
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

    typ_path = generate_typ(
        content_path, args.size, args.font, args.rotate, args.width, output_dir
    )
    pdf_path = pdfs_dir / f"{content_path.stem}.pdf"
    compile_typst(typ_path, pdf_path, project_root)
    convert_to_jpg(pdf_path, str(output_dir / f"{content_path.stem}_p%02d.jpg"))
    print(f"Created: {output_dir}/{content_path.stem}_p*.jpg")
