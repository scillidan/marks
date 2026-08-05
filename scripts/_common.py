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


def check_dependencies():
    missing = []
    if not shutil.which("typst"):
        missing.append("typst")
    if not shutil.which("magick") and not _has_ghostscript():
        missing.append("ImageMagick (magick) or Ghostscript (gs/gswin64c)")
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


def compile_typst(typ_path, pdf_path, project_root):
    r = subprocess.run(
        ["typst", "compile", "--root", str(project_root), str(typ_path), str(pdf_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if r.returncode != 0:
        sys.exit(f"Typst compile error:\n{r.stderr}")
    print(f"Created: {pdf_path}")


def convert_to_jpg(pdf_path, pattern, density=150, quality=90):
    from pdf_to_jpg import convert_pdf_to_jpg

    r = convert_pdf_to_jpg(pdf_path, pattern, density=density, quality=quality)
    if not r.success:
        sys.exit(f"{r.tool or 'Converter'} error:\n{r.stderr}")
