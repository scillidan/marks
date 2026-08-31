#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from _common import check_dependencies, convert_to_jpg, strip_quotes

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
OUTPUT_DIR = Path.cwd().resolve() / "image-convert"
OUT_DIR = OUTPUT_DIR / "_output"
ASSETS_DIR = OUTPUT_DIR / "assets"
PDFS_DIR = OUT_DIR / "pdfs"
TYPS_DIR = OUT_DIR / "typs"


def resolve_image(image_arg):
    candidate = Path(image_arg)
    if candidate.is_absolute():
        if not candidate.exists():
            sys.exit(f"✗ Image not found: {candidate}")
        return candidate
    candidate = (Path.cwd() / candidate).resolve()
    if candidate.exists():
        return candidate
    sys.exit(f"✗ Image not found: {candidate}")


def compute_output_path(input_path):
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ext = input_path.suffix or ".jpg"
    stem = input_path.stem
    candidate = ASSETS_DIR / f"{stem}{ext}"
    if not candidate.exists():
        return candidate
    seq = 1
    while True:
        candidate = ASSETS_DIR / f"{stem}_{seq:03d}{ext}"
        if not candidate.exists():
            return candidate
        seq += 1


def compute_target_image_width_px(mode, margin_pt=5, dpi=150):
    """Return the exact content width in pixels at the target DPI.

    The image is pre-sized to this width so Typst does not have to resample it,
    avoiding the uneven left/right margins that come from sub-pixel scaling.
    """
    page_width_mm = 210 if mode == "landscape" else 148
    page_width_px = round(page_width_mm * dpi / 25.4)
    margin_px = round(margin_pt * dpi / 72)
    return max(1, page_width_px - 2 * margin_px)


def resize_to_width(input_path, output_path, width_px):
    """Resize `input_path` to `width_px` pixels wide, preserving aspect ratio."""
    r = subprocess.run(
        [
            "magick",
            str(input_path),
            "-resize",
            f"{width_px}x",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if r.returncode != 0:
        sys.exit(f"Resize failed:\n{r.stderr or r.stdout}")
    if not output_path.exists():
        sys.exit(f"✗ Resize did not produce: {output_path}")
    print(f"  ✓ resized to {width_px}px wide: {output_path}")
    return output_path


def run_commands(commands, input_path):
    output_path = compute_output_path(input_path)

    def quote(p):
        return '"' + p + '"' if os.name == "nt" else shlex.quote(p)

    shell_cmd = commands.replace("$1", quote(str(input_path))).replace(
        "$2", quote(str(output_path))
    )
    print(f"Running: {shell_cmd}")
    r = subprocess.run(
        shell_cmd,
        shell=True,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        sys.exit(f"Command failed ({r.returncode}):\n{(r.stderr or r.stdout).strip()}")
    if not output_path.exists():
        sys.exit(f"✗ Command did not produce: {output_path}\n{r.stdout}")
    print(f"  ✓ {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Render scripts/image-convert.typ as a PDF. "
        "commands placeholders: $1 = input image, $2 = output image."
    )
    parser.add_argument("mode", nargs="?", choices=["portrait", "landscape"])
    parser.add_argument("theme", nargs="?", choices=["dark", "light"])
    parser.add_argument("--image", required=True)
    parser.add_argument("--commands", default="")
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Do not run `commands`; use the image as-is and show `commands` text only.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Bare output filename (no path). Used as the shared base name: "
        "jpg -> <cwd>/image-convert/_output/<output>.jpg, "
        "typ -> _output/typs/<output>.typ, pdf -> _output/pdfs/<output>.pdf.",
    )
    args = parser.parse_args()

    args.image = strip_quotes(args.image)
    args.commands = strip_quotes(args.commands) if args.commands else ""
    args.output = strip_quotes(args.output)

    mode = args.mode or "portrait"
    theme = args.theme or "dark"
    image_arg = args.image
    commands = args.commands

    check_dependencies()
    if not args.no_run and commands.strip() and not shutil.which("magick"):
        print("Warning: 'magick' not found in PATH; command processing may fail.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PDFS_DIR.mkdir(parents=True, exist_ok=True)
    TYPS_DIR.mkdir(parents=True, exist_ok=True)

    input_path = resolve_image(image_arg)

    if args.no_run:
        print("  ✓ (no-run) using image as-is; commands text shown only")
        typ_image = input_path
    elif commands.strip():
        typ_image = run_commands(commands, input_path)
    else:
        typ_image = input_path

    # Pre-size the image to the exact content width at the target DPI so Typst
    # does not have to resample it, avoiding uneven left/right margins.
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    output_stem = Path(args.output).stem
    target_width_px = compute_target_image_width_px(mode)
    resized_path = ASSETS_DIR / f"{output_stem}_resized.png"
    typ_image = resize_to_width(typ_image, resized_path, target_width_px)

    typ_path = TYPS_DIR / f"{output_stem}.typ"
    shutil.copy2(SCRIPT_DIR / "image-convert.typ", typ_path)
    print(f"Created: {typ_path}")

    try:
        image_rel = typ_image.relative_to(TYPS_DIR).as_posix()
    except ValueError:
        image_rel = Path(os.path.relpath(typ_image, TYPS_DIR)).as_posix()

    pdf_path = PDFS_DIR / f"{output_stem}.pdf"
    jpg_path = OUT_DIR / f"{output_stem}.jpg"

    r = subprocess.run(
        [
            "typst",
            "compile",
            "--root",
            str(PROJECT_ROOT),
            "--input",
            f"mode={mode}",
            "--input",
            f"theme={theme}",
            "--input",
            f"image={image_rel}",
            "--input",
            f"commands={commands}",
            str(typ_path),
            str(pdf_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if r.returncode != 0:
        sys.exit(f"Typst compile error:\n{r.stderr}")
    print(f"Created: {pdf_path}")

    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    convert_to_jpg(pdf_path, str(jpg_path))
    print(f"Created: {jpg_path}")


if __name__ == "__main__":
    main()
