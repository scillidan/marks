#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pikepdf", "pillow"]
# ///
# Process only the raster images embedded in a PDF, leaving vector text,
# fonts, and layout untouched. Unlike whole-page rasterisation, this keeps
# text sharp (still vector) while making dark screenshots readable in print.
#
# Two modes:
#   --brightness N [--grayscale]   simple multiply via PIL
#   --filter "magick $1 ... $2"    arbitrary ImageMagick chain per image
#
# Usage:
#   uv run scripts/pdf_brighten.py IN.pdf OUT.pdf --brightness 250
#   uv run scripts/pdf_brighten.py IN.pdf OUT.pdf --filter "magick $1 -colorspace Gray -evaluate multiply 3.5 $2"

import argparse
import io
import shutil
import subprocess
import sys
from pathlib import Path

import pikepdf
from PIL import Image, ImageEnhance

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import shell_quote

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def iter_image_xobjects(pdf):
    """Yield (page_index, name, xobject) for every image XObject."""
    for pageno, page in enumerate(pdf.pages):
        resources = page.get("/Resources")
        if resources is None:
            continue
        xobjects = resources.get("/XObject")
        if xobjects is None:
            continue
        for name, obj in xobjects.items():
            if obj.get("/Subtype") == "/Image":
                yield pageno, name, obj


def encode_jpeg(img: Image.Image) -> tuple[bytes, pikepdf.Name]:
    """Return JPEG bytes and the matching PDF colour space."""
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    cs = pikepdf.Name.DeviceGray if img.mode == "L" else pikepdf.Name.DeviceRGB
    return buf.getvalue(), cs


def replace_image(obj, jpeg_bytes: bytes, colorspace, width: int, height: int):
    obj.write(jpeg_bytes, filter=pikepdf.Name.DCTDecode)
    obj["/Width"] = width
    obj["/Height"] = height
    obj["/BitsPerComponent"] = 8
    obj["/ColorSpace"] = colorspace
    for key_to_drop in ("/DecodeParms", "/Decode"):
        if key_to_drop in obj:
            del obj[key_to_drop]


def process_pdf(
    input_pdf, output_pdf, brightness=None, grayscale=False, filter_cmd=None
):
    pdf = pikepdf.open(input_pdf)
    seen = set()
    done = 0
    skipped = 0
    work_dir = None

    if filter_cmd:
        if "$1" not in filter_cmd or "$2" not in filter_cmd:
            sys.exit("Error: --filter must contain $1 (input) and $2 (output)")
        work_dir = Path(output_pdf).parent / f"{Path(output_pdf).stem}_bright_work"
        work_dir.mkdir(parents=True, exist_ok=True)

    try:
        for idx, (_pageno, _name, obj) in enumerate(iter_image_xobjects(pdf)):
            key = obj.objgen
            if key in seen:
                continue
            seen.add(key)

            # Images with a soft mask (transparency) are left untouched:
            # replacing the base image while keeping a /Matte SMask can shift
            # edge colours.
            if "/SMask" in obj:
                skipped += 1
                continue

            try:
                img = pikepdf.PdfImage(obj).as_pil_image()
            except Exception as e:  # noqa: BLE001 - undecodable images are skipped, not fatal
                print(f"  skip image {obj.objgen}: {e}")
                skipped += 1
                continue

            if filter_cmd:
                tmp_in = work_dir / f"{idx:05d}.png"
                tmp_out = work_dir / f"{idx:05d}.jpg"
                img.save(tmp_in, format="PNG")
                cmd = filter_cmd.replace("$1", shell_quote(str(tmp_in))).replace(
                    "$2", shell_quote(str(tmp_out))
                )
                r = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                if r.returncode != 0 or not tmp_out.exists():
                    print(
                        f"  filter failed for image {obj.objgen}: {(r.stderr or r.stdout).strip()[:200]}"
                    )
                    skipped += 1
                    continue
                raw = tmp_out.read_bytes()
                with Image.open(io.BytesIO(raw)) as out:
                    w, h = out.size
                    mode = out.mode
                if raw[:2] == b"\xff\xd8":
                    # magick already produced JPEG; embed it as-is to avoid a
                    # second lossy re-encode.
                    jpeg_bytes = raw
                    colorspace = (
                        pikepdf.Name.DeviceGray
                        if mode == "L"
                        else pikepdf.Name.DeviceRGB
                    )
                else:
                    with Image.open(io.BytesIO(raw)) as out:
                        out.load()
                        jpeg_bytes, colorspace = encode_jpeg(out)
            else:
                if grayscale:
                    img = img.convert("L")
                elif img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                if brightness:
                    img = ImageEnhance.Brightness(img).enhance(1 + brightness / 100.0)
                jpeg_bytes, colorspace = encode_jpeg(img)
                w, h = img.size

            replace_image(obj, jpeg_bytes, colorspace, w, h)
            done += 1
    finally:
        if work_dir:
            shutil.rmtree(work_dir, ignore_errors=True)

    pdf.save(output_pdf)
    print(f"Processed {done} image(s), skipped {skipped}, unique {len(seen)}")
    print(f"Created: {output_pdf}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Process only the embedded raster images of a PDF (text stays vector)."
    )
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument(
        "--brightness",
        type=float,
        default=None,
        help="Brightness increase in percent, applied as a multiply (default: none).",
    )
    parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Convert images to grayscale (keeps text untouched).",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="ImageMagick command template with $1=input and $2=output, run once per image.",
    )
    args = parser.parse_args()
    if args.brightness is None and not args.filter:
        parser.error("provide --brightness or --filter")
    return process_pdf(
        args.input,
        args.output,
        brightness=args.brightness,
        grayscale=args.grayscale,
        filter_cmd=args.filter,
    )


if __name__ == "__main__":
    sys.exit(main())
