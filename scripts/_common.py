import shutil
import subprocess
import sys
from pathlib import Path


def _has_ghostscript():
    if sys.platform == "win32":
        return (
            shutil.which("gswin64c") is not None or shutil.which("gswin32c") is not None
        )
    return shutil.which("gs") is not None


def find_imagemagick_cli() -> str | None:
    """Return the ImageMagick CLI binary name/path, or None if not found.

    Prefers ``magick`` (ImageMagick 7). On non-Windows systems, falls back to
    ``convert`` (ImageMagick 6) because some distributions package IM6 only.
    """
    if shutil.which("magick"):
        return "magick"
    if sys.platform != "win32" and shutil.which("convert"):
        return "convert"
    return None


def check_dependencies():
    missing = []
    if not shutil.which("typst"):
        missing.append("typst")
    if not find_imagemagick_cli() and not _has_ghostscript():
        missing.append("ImageMagick (magick/convert) or Ghostscript (gs/gswin64c)")
    if missing:
        sys.exit("Missing dependencies:\n  - " + "\n  - ".join(missing))


def resolve_path(p):
    path = Path(p)
    return path if path.is_absolute() else Path.cwd() / path


def add_pt(size):
    return size + "pt" if not any(c.isalpha() for c in size) else size


def font_tuple(font_str):
    fonts = [f.strip() for f in font_str.split(",") if f.strip()]
    return "(" + ", ".join(f'"{f}"' for f in fonts) + ",)"


def strip_quotes(text):
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        return text[1:-1]
    return text


def compile_typst(typ_path, pdf_path, project_root, fail_on_error=True):
    r = subprocess.run(
        ["typst", "compile", "--root", str(project_root), str(typ_path), str(pdf_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if r.returncode != 0:
        if fail_on_error:
            sys.exit(f"✗ Typst compile error:\n{r.stderr}")
        print(f"✗ Typst compile error: {typ_path.name}", file=sys.stderr)
        return False
    print(f"Created: {pdf_path}")
    return True


def convert_to_jpg(pdf_path, pattern, density=150, quality=90, fail_on_error=True):
    from pdf_to_jpg import convert_pdf_to_jpg

    r = convert_pdf_to_jpg(pdf_path, pattern, density=density, quality=quality)
    if not r.success:
        if fail_on_error:
            sys.exit(f"✗ {r.tool or 'Converter'} error:\n{r.stderr}")
        print(
            f"✗ {r.tool or 'Converter'} error (JPG skipped): {r.stderr}",
            file=sys.stderr,
        )
        return False
    return True
