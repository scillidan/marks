#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse
import os
import shutil
import sys
from pathlib import Path

from _common import check_dependencies, compile_typst, convert_to_jpg, strip_quotes

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def escape_typst(text):
    for ch in ("\\", "#", "[", "]", "*", "_"):
        text = text.replace(ch, "\\" + ch)
    return text


def get_image_source():
    env = os.environ.get("IMAGE_COLLECT_SOURCE")
    if env:
        path = Path(os.path.expandvars(env))
        if path.is_dir():
            return path
        print(f"✗ IMAGE_COLLECT_SOURCE: {env} (not found)")

    local = Path(__file__).parent.parent / "image-collect" / "assets"
    if local.is_dir():
        print(f"✓ Image source (local): {local}")
        return local
    return None


def process_image(images_dir, image_name):
    source = get_image_source()
    if not source:
        sys.exit(
            "Error: No image source. Set IMAGE_COLLECT_SOURCE or place images in image-collect/assets/"
        )
    print(f"✓ Image source: {source}")

    base = Path(image_name).stem
    source_files = os.listdir(source)
    found = None
    for ext in ("jpg", "jpeg", "png", "gif", "svg", "webp"):
        f = f"{base}.{ext}"
        if f in source_files:
            found = f
            break
    if not found:
        sys.exit(f"✗ {base}.* (not found)")

    dest = images_dir / found
    if not dest.exists():
        shutil.copy2(Path(source) / found, dest)
    print(f"  ✓ {found}")
    return found


def generate_typ(
    image_name,
    text_first,
    text_second,
    text_third,
    mode,
    start,
    resize,
    size,
    output_dir,
):
    typs_dir = output_dir / "typs"
    typs_dir.mkdir(exist_ok=True)

    first, second, third = (
        escape_typst(t) for t in (text_first, text_second, text_third)
    )
    middle_ratio = "5%" if not text_second.strip() else "20%"

    content = f"""#import "@preview/polario-frame:1.0.0": *

#let render-polario(params) = {{
  set page(fill: black, margin: 2%, flipped: params.flipped)
  set text(font: ("MonaspiceNe NFM", "Sarasa Mono SC"))
  let img = crop(bytes(read(params.img-path, encoding: none)), start: params.start, resize: params.resize)
  render(params.size, theme: params.theme, img: img, ext-info: params.ext-info)
}}

#let ext-info = (
  "background": rgb("#00000000"),
  "extend-middle-ratio": {middle_ratio},
  "first": text(size: 11pt, fill: white)[
    #h(0.3em){first}#h(0.3em)
  ],
  "second": text(size: 11pt, fill: white)[
    #h(0.3em){second}#h(0.3em)
  ],
  "third": text(size: 11pt, fill: white)[
    #h(0.3em)_{third}_#h(0.3em)
  ],
)

#let params = (
  "ext-info": ext-info,
  "theme": "classic-bottom-three",
  "img-path": "../../_temp/images/{image_name}",
  "flipped": {"true" if mode == "landscape" else "false"},
  "start": {start},
  "resize": {resize},
  "size": {size},
)

#render-polario(params)
"""

    base_name = Path(image_name).stem
    typ_path = typs_dir / f"{base_name}.typ"
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")
    return typ_path, base_name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["landscape", "portrait"])
    parser.add_argument("image")
    parser.add_argument("text_first")
    parser.add_argument("text_second")
    parser.add_argument("text_third")
    parser.add_argument("start")
    parser.add_argument("resize")
    parser.add_argument("size")
    args = parser.parse_args()

    for attr in (
        "mode",
        "image",
        "text_first",
        "text_second",
        "text_third",
        "start",
        "resize",
        "size",
    ):
        setattr(args, attr, strip_quotes(getattr(args, attr)))

    check_dependencies()

    project_root = Path(__file__).parent.parent.resolve()
    output_dir = project_root / "image-collect" / "_output"
    images_dir = output_dir.parent / "_temp" / "images"
    pdfs_dir = output_dir / "pdfs"
    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    pdfs_dir.mkdir(exist_ok=True)

    image_name = process_image(images_dir, args.image)
    typ_path, base_name = generate_typ(
        image_name,
        args.text_first,
        args.text_second,
        args.text_third,
        args.mode,
        args.start,
        args.resize,
        args.size,
        output_dir,
    )

    pdf_path = pdfs_dir / f"{base_name}.pdf"
    compile_typst(typ_path, pdf_path, project_root)
    convert_to_jpg(pdf_path, str(output_dir / f"{base_name}.jpg"))
    print(f"Created: {output_dir / (base_name + '.jpg')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
