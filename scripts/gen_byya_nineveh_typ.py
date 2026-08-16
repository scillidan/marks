#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse
import sys
from pathlib import Path

from _common import check_dependencies, compile_typst, convert_to_jpg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    check_dependencies()

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
    if convert_to_jpg(
        pdf_path,
        str(output_dir / f"{typ_path.stem}_p%02d.jpg"),
        fail_on_error=False,
    ):
        print(f"Created: {output_dir}/{typ_path.stem}_p*.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
