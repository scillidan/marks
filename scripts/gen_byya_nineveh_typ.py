# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import argparse
import sys
from pathlib import Path

from _common import compile_typst
from pdf_to_jpg import convert_pdf_to_jpg

p = argparse.ArgumentParser()
p.add_argument("path")
args = p.parse_args()

typ_path = Path(args.path).resolve()
if not typ_path.exists():
    sys.exit(f"Error: File not found: {typ_path}")

root = Path(__file__).resolve().parent.parent

if typ_path.parts[-3:-1] == ("_output", "typs"):
    pdf_path = typ_path.parent.parent / "pdfs" / f"{typ_path.stem}.pdf"
    output_dir = typ_path.parent.parent
else:
    pdf_path = typ_path.parent / "_output" / "pdfs" / f"{typ_path.stem}.pdf"
    output_dir = typ_path.parent / "_output"
pdf_path.parent.mkdir(parents=True, exist_ok=True)

compile_typst(typ_path, pdf_path, root)

r = convert_pdf_to_jpg(
    pdf_path,
    str(output_dir / f"{typ_path.stem}_p%02d.jpg"),
    density=150,
    quality=90,
)
if not r.success:
    print(f"{r.tool or 'Converter'} error (JPG skipped): {r.stderr}", file=sys.stderr)
else:
    print(f"Created: {output_dir}/{typ_path.stem}_p*.jpg")
