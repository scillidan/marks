# /// script
# requires-python = ">=3.12"
# ///
import argparse
import sys

from _common import add_pt, check_dependencies, compile_typst, font_tuple, resolve_path
from pdf_to_jpg import convert_pdf_to_jpg


def generate_typ(content_path, size, font, output_dir):
    typs_dir = output_dir / "typs"
    typs_dir.mkdir(exist_ok=True)

    content = f"""#import "../../../scripts/byya-lyra-annex-template.typ": *

#show: lyra-annex-layout.with(size: {add_pt(size)}, font: {font_tuple(font)})

#let _lines = read("../../{content_path.name}").split("\\n")
#_lines.filter(l => l != "").join(linebreak())"""

    typ_path = typs_dir / f"{content_path.stem}.typ"
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")
    return typ_path


if __name__ == "__main__":
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

    r = convert_pdf_to_jpg(
        pdf_path,
        str(output_dir / f"{content_path.stem}_p%02d.jpg"),
        density=150,
        quality=90,
    )
    if not r.success:
        print(
            f"{r.tool or 'Converter'} error (JPG skipped): {r.stderr}", file=sys.stderr
        )
    else:
        print(f"Created: {output_dir}/{content_path.stem}_p*.jpg")
