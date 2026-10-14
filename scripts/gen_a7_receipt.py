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
    resolve_path,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


def generate_merge_typ(content_paths, size, font, output_dir, a5=False):
    """Merge several .typ receipts into one aggregate document, flowing
    top-to-bottom, left-to-right, packed with no gap between receipts.
    Default: landscape A4 (4 columns at the native A7 width); a5=True uses
    portrait A5 with 2 columns instead."""
    typs_dir = output_dir / "typs"
    typs_dir.mkdir(exist_ok=True)

    layout = "receipt-a5-layout" if a5 else "receipt-a4-layout"
    parts = [
        f'#import "{TEMPLATE}": *',
        f"#show: {layout}.with(size: {add_pt(size)}, font: {font_tuple(font)})",
        "",
    ]
    for path in content_paths:
        parts.append(path.read_text(encoding="utf-8"))

    generated = typs_dir / f"{merge_name(content_paths)}.typ"
    generated.write_text("\n".join(parts), encoding="utf-8")
    print(f"Created: {generated}")
    return generated


def merge_name(content_paths):
    """Aggregate PDF name: stems joined with '_', hashed if too long."""
    import hashlib

    name = "_".join(p.stem for p in content_paths)
    if len(name) > 120:
        name = f"{content_paths[0].stem}_{hashlib.sha1(name.encode('utf-8')).hexdigest()[:8]}"
    return name


def run_merge(paths, size, font, a5=False):
    content_paths = [resolve_path(p) for p in paths]
    for path in content_paths:
        if not path.exists():
            sys.exit(f"Error: File not found: {path}")
        if path.suffix != ".typ":
            sys.exit(f"Error: Not a .typ file: {path}")
    content_dirs = {p.parent for p in content_paths}
    if len(content_dirs) > 1:
        sys.exit(
            "Error: --include files must all live in the same directory "
            f"(got: {', '.join(str(d) for d in sorted(content_dirs))})"
        )

    content_dir = content_paths[0].parent
    project_root = content_dir.parent
    output_dir = content_dir / "_output"
    pdfs_dir = output_dir / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    typ_path = generate_merge_typ(content_paths, size, font, output_dir, a5=a5)
    pdf_path = pdfs_dir / f"{typ_path.stem}.pdf"
    compile_typst(typ_path, pdf_path, project_root)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument(
        "--include",
        nargs="+",
        default=None,
        metavar="PATH",
        help="Merge these .typ receipts into one landscape-A4 PDF (4 columns).",
    )
    parser.add_argument(
        "--a5",
        action="store_true",
        help="With --include: emit portrait-A5 PDF (2 columns) instead of A4.",
    )
    parser.add_argument("--size", default="8pt")
    parser.add_argument("--font", default="Sarasa Mono SC")
    parser.add_argument("--rotate", action="store_true")
    parser.add_argument("--width", default="")
    args = parser.parse_args()

    check_dependencies()

    if args.include:
        return run_merge(args.include, args.size, args.font, a5=args.a5)

    if not args.paths:
        sys.exit("Error: missing path (or use --include to merge several .typ files)")
    if len(args.paths) > 1:
        sys.exit(
            "Error: too many positional arguments "
            "(did you mean: --include " + " ".join(args.paths) + ")"
        )

    content_path = resolve_path(args.paths[0])
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
