#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# copy/: A5 sequential pages -> 2-up landscape A4 reader, single A5 pages,
# or saddle-stitch booklet imposition. The reader is A5 pages 2-up on A4 in
# reading order; the booklet uses pdfpages signature imposition (duplex
# short-edge flip, stack, fold, staple 2-3 times on the spine).
#
# Starting 2026-10: existing PDF files are also accepted as input. They are
# imposed directly (no markdown compilation). Use --grid, --paper, --gutter,
# --margin, etc. to control the layout.

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from _common import convert_to_jpg, safe_staging_dir, shell_quote
from gen_a4_latex import process_markdown, resolve_path

DEFAULT_PAPER = "a4"
DEFAULT_GRID_MARGIN = "3mm"
DEFAULT_READER_MARGIN = "0pt"

# ISO / common paper sizes in mm (portrait width x height).
PAPER_SIZES_MM = {
    "a6": (105.0, 148.0),
    "a5": (148.0, 210.0),
    "a4": (210.0, 297.0),
    "a3": (297.0, 420.0),
    "letter": (215.9, 279.4),
    "legal": (215.9, 355.6),
    "executive": (184.15, 266.7),
}


def compile_tex(tex_path, engine, runs: int = 1):
    """Compile a LaTeX wrapper, optionally multiple times."""
    runs = max(1, runs)
    for _ in range(runs):
        r = subprocess.run(
            [
                engine,
                "-shell-escape",
                "-interaction=nonstopmode",
                "-halt-on-error",
                str(tex_path.name),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            cwd=str(tex_path.parent),
        )
        if r.returncode != 0:
            sys.exit(
                f"✗ {engine} compile error ({tex_path.name}):\n{(r.stderr or r.stdout)[-4000:]}"
            )
    m = re.search(r"Output written on .+ \((\d+) pages?", r.stdout)
    return int(m.group(1)) if m else 0


def extract_pax(tex_stem, latex_dir):
    # pdfpages drops embedded-page links; pax re-inserts them from <stem>.pax
    if not shutil.which("java"):
        print("  ⚠ java not found; endnote links will not survive imposition")
        return
    r = subprocess.run(
        ["kpsewhich", "pax.sty"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    jar = None
    if r.returncode == 0 and r.stdout.strip():
        # <texmf>/tex/latex/pax/pax.sty -> <texmf>/scripts/pax/pax.jar
        texmf = Path(r.stdout.strip().splitlines()[0]).parents[3]
        candidate = texmf / "scripts" / "pax" / "pax.jar"
        if candidate.exists():
            jar = str(candidate)
    if not jar:
        print("  ⚠ pax.jar not found (install the pax package); links skipped")
        return
    r = subprocess.run(
        ["java", "-jar", jar, f"{tex_stem}.pdf"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=str(latex_dir),
    )
    if r.returncode != 0 or not (latex_dir / f"{tex_stem}.pax").exists():
        print(f"  ⚠ pax extraction failed: {(r.stderr or r.stdout)[-500:]}")


def generate_seq_wrapper(md_path, latex_dir, project_root, tex_stem):
    stem = md_path.stem
    rel_root = os.path.relpath(project_root, latex_dir).replace("\\", "/")
    wrapper = rf"""% !TeX program = xelatex
% Auto-generated LaTeX wrapper for {md_path.name} -- do not edit.
% Regenerate with: python scripts/gen_copy.py {md_path.as_posix()}

\documentclass{{article}}
\usepackage[a5paper, margin=1.2cm]{{geometry}}

\def\poststem{{{stem}}}
\def\postlayout{{a5}}

\input{{{rel_root}/scripts/gen_a4_latex}}
\input{{{rel_root}/scripts/gen_copy}}

\def\postimagedir{{images/}}

\begin{{document}}

\input{{meta.tex}}

\postmarkdowninput{{body.md}}

\postprintendnotes

\end{{document}}
"""
    wrapper_path = latex_dir / f"{tex_stem}.tex"
    wrapper_path.write_text(wrapper, encoding="utf-8")
    print(f"Created: {wrapper_path}")
    return wrapper_path


def count_selected_pages(raw: str, total: int) -> int:
    """Count pages selected by a pdfpages-style page list."""
    raw = raw.strip()
    if raw == "-":
        return total
    count = 0
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str) if start_str.strip() else 1
            end = int(end_str) if end_str.strip() else total
            count += max(0, end - start + 1)
        else:
            count += 1
    return count


def get_paper_dimensions(paper: str, landscape: bool) -> tuple[float, float]:
    """Return paper width and height in mm."""
    p = paper.strip().lower().replace("paper", "")
    if p not in PAPER_SIZES_MM:
        sys.exit(
            f"Error: unknown paper size {paper!r}; "
            f"supported: {', '.join(PAPER_SIZES_MM)}"
        )
    w, h = PAPER_SIZES_MM[p]
    if landscape:
        w, h = h, w
    return w, h


def _bp(value: float) -> str:
    """Format a bp length with a reasonable number of decimals."""
    return f"{value:.2f}bp" if value != int(value) else f"{int(value)}bp"


def normalize_paper(paper: str) -> str:
    """Convert a user-friendly paper size to a geometry package option."""
    p = paper.strip().lower()
    if "paper" not in p:
        p += "paper"
    return p


def normalize_color(color: str) -> str:
    """Convert a shell-friendly color shorthand to xcolor syntax.

    xcolor uses 'gray!50', but '!' is often expanded by shells. Allow
    'gray50' to mean 'gray!50' so users can avoid quoting special chars.
    """
    color = color.strip()
    m = re.fullmatch(r"([a-zA-Z]+)(\d{1,3})", color)
    if m:
        return f"{m.group(1)}!{m.group(2)}"
    return color


def generate_pdfpages_wrapper(
    tex_stem,
    latex_dir,
    source_pdf: Path,
    signature=None,
    grid: tuple[int, int] | None = None,
    paper: str = DEFAULT_PAPER,
    landscape: bool = True,
    gutter: tuple[float, float] | None = None,
    margin: float = 0.0,
    frame: bool = False,
    frame_color: str = "gray!70",
    frame_width: str = "0.4pt",
    pages: str = "-",
):
    """Generate a pdfpages imposition wrapper (reader or booklet)."""
    if grid is None:
        nup = "2x1"
    else:
        nup = f"{grid[0]}x{grid[1]}"

    kind = "booklet" if signature else "reader"

    opts_parts = [f"pages={pages}", f"nup={nup}"]

    if signature:
        delta_x = gutter[0] if gutter else 6.0
        opts_parts.append(f"signature={signature}, delta={_bp(delta_x)} 0")
    elif gutter:
        opts_parts.append(f"delta={_bp(gutter[0])} {_bp(gutter[1])}")

    if frame:
        opts_parts.append("frame")

    opts = ", ".join(opts_parts)

    margin_str = _bp(margin)
    paper_opt = normalize_paper(paper)
    landscape_str = ", landscape" if landscape else ""
    color_opt = normalize_color(frame_color)
    xcolor_pkg = "\\usepackage{xcolor}\n" if frame else ""
    include_cmd = (
        f"{{\\setlength{{\\fboxrule}}{{{frame_width}}}\\color{{{color_opt}}}\\includepdf[{opts}]{{{source_pdf.name}}}}}"
        if frame
        else f"\\includepdf[{opts}]{{{source_pdf.name}}}"
    )

    wrapper = f"""% !TeX program = pdflatex
% Auto-generated {kind} imposition wrapper -- do not edit.

\\documentclass{{article}}
\\usepackage[{paper_opt}{landscape_str}, margin={margin_str}]{{geometry}}
{xcolor_pkg}\\usepackage{{pdfpages}}
\\usepackage{{pdftexcmds}}
\\makeatletter
\\ifx\\pdfstrcmp\\undefined\\let\\pdfstrcmp\\pdf@strcmp\\fi
\\makeatother
\\usepackage{{pax}}

\\begin{{document}}

{include_cmd}

\\end{{document}}
"""
    wrapper_path = latex_dir / f"{tex_stem}.{kind}.tex"
    wrapper_path.write_text(wrapper, encoding="utf-8")
    print(f"Created: {wrapper_path}")
    return wrapper_path


def generate_grid_wrapper(
    tex_stem,
    latex_dir,
    source_pdf: Path,
    npages: int,
    grid: tuple[int, int],
    paper: str = DEFAULT_PAPER,
    landscape: bool = True,
    gutter: tuple[float, float] = (0.0, 0.0),
    margin: float = 0.0,
    fit_mode: str = "fit",
    frame: bool = False,
    frame_color: str = "gray!70",
    frame_width: str = "0.4pt",
    divider_horizontal: bool = False,
    divider_vertical: bool = False,
    pages: str = "-",
):
    """Generate a TikZ-based grid imposition wrapper.

    Pages are placed left-to-right, top-to-bottom. The grid is centered on
    the output page with the requested margin around it.
    """
    cols, rows = grid
    page_w, page_h = get_paper_dimensions(paper, landscape)

    cell_w = (page_w - 2 * margin - (cols - 1) * gutter[0]) / cols
    cell_h = (page_h - 2 * margin - (rows - 1) * gutter[1]) / rows
    if cell_w <= 0 or cell_h <= 0:
        sys.exit(
            "Error: grid cells have zero or negative size; reduce --margin or --gutter"
        )

    color_opt = normalize_color(frame_color)

    # Build includegraphics options per fit mode.
    if fit_mode == "fit":
        img_opts = f"width={cell_w:.4f}mm, height={cell_h:.4f}mm, keepaspectratio"
    elif fit_mode == "fill":
        img_opts = f"width={cell_w:.4f}mm, height={cell_h:.4f}mm"
    elif fit_mode == "none":
        img_opts = ""
    else:
        sys.exit(f"Error: --fit must be 'fit', 'fill', or 'none', got {fit_mode!r}")

    # Build per-page placements. Page order is left-to-right, top-to-bottom.
    cells_per_sheet = cols * rows
    nsheets = math.ceil(npages / cells_per_sheet)

    # Common frame/divider lines (same on every page), drawn relative to the
    # lower-left corner via current page.south west.
    draw_cmds: list[str] = []
    if frame:
        for r in range(rows):
            for c in range(cols):
                x1 = margin + c * (cell_w + gutter[0])
                y1 = margin + r * (cell_h + gutter[1])
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                draw_cmds.append(
                    f"  \\draw[{color_opt}, line width={frame_width}] "
                    f"([xshift={x1:.4f}mm, yshift={y1:.4f}mm]current page.south west) "
                    f"rectangle "
                    f"([xshift={x2:.4f}mm, yshift={y2:.4f}mm]current page.south west);"
                )
    if divider_vertical and cols > 1:
        for i in range(cols - 1):
            x = margin + (i + 1) * cell_w + i * gutter[0]
            draw_cmds.append(
                f"  \\draw[{color_opt}, line width={frame_width}] "
                f"([xshift={x:.4f}mm, yshift={margin:.4f}mm]current page.south west) -- "
                f"([xshift={x:.4f}mm, yshift={page_h - margin:.4f}mm]current page.south west);"
            )
    if divider_horizontal and rows > 1:
        for j in range(rows - 1):
            y = margin + (j + 1) * cell_h + j * gutter[1]
            draw_cmds.append(
                f"  \\draw[{color_opt}, line width={frame_width}] "
                f"([xshift={margin:.4f}mm, yshift={y:.4f}mm]current page.south west) -- "
                f"([xshift={page_w - margin:.4f}mm, yshift={y:.4f}mm]current page.south west);"
            )

    overlay_code = "\n".join(draw_cmds)

    page_blocks = []
    for sheet in range(nsheets):
        nodes = []
        for pos in range(cells_per_sheet):
            src_page = sheet * cells_per_sheet + pos + 1
            if src_page > npages:
                break
            row_from_top = pos // cols
            row_from_bottom = (rows - 1) - row_from_top
            col = pos % cols
            center_x = margin + col * (cell_w + gutter[0]) + cell_w / 2
            center_y = margin + row_from_bottom * (cell_h + gutter[1]) + cell_h / 2
            img = f"\\includegraphics[{img_opts}, page={src_page}]{{{source_pdf.name}}}"
            nodes.append(
                f"  \\node[anchor=center, inner sep=0pt, outer sep=0pt] at "
                f"([xshift={center_x:.4f}mm, yshift={center_y:.4f}mm]current page.south west) {{{img}}};"
            )
        block = "\\begin{tikzpicture}[overlay, remember picture]\n" + "\n".join(nodes)
        if overlay_code:
            block += "\n" + overlay_code
        block += "\n\\end{tikzpicture}\n\\newpage\n"
        page_blocks.append(block)

    pages_code = "\n".join(page_blocks)
    pages_code = pages_code.removesuffix("\\newpage\n")

    paper_opt = normalize_paper(paper)
    landscape_str = ", landscape" if landscape else ""
    xcolor_pkg = (
        "\\usepackage{xcolor}\n"
        if (frame or divider_horizontal or divider_vertical)
        else ""
    )

    wrapper = f"""% !TeX program = pdflatex
% Auto-generated grid imposition wrapper -- do not edit.

\\documentclass{{article}}
\\usepackage[{paper_opt}{landscape_str}, margin=0pt]{{geometry}}
{xcolor_pkg}\\usepackage{{graphicx}}
\\usepackage{{tikz}}

\\begin{{document}}

{pages_code}

\\end{{document}}
"""
    wrapper_path = latex_dir / f"{tex_stem}.grid.tex"
    wrapper_path.write_text(wrapper, encoding="utf-8")
    print(f"Created: {wrapper_path}")
    # TikZ 'remember picture' needs two runs.
    return wrapper_path, 2


def _copy_source_base():
    """Return the expanded COPY_SOURCE directory, or None if unset/missing."""
    env = os.environ.get("COPY_SOURCE")
    if not env:
        return None
    base = Path(os.path.expandvars(env)).expanduser().resolve()
    if not base.exists():
        return None
    return base


def resolve_copy_input(raw_path: Path) -> tuple[Path, Path]:
    """Locate the input file and decide where its outputs should live.

    Returns (source_path, output_base). The output base is the directory under
    which ``_output/latex`` and ``_output/pdfs`` will be created. Local files
    inside the repo's ``copy/`` tree keep their existing behaviour (outputs
    live next to the source). Files resolved via ``COPY_SOURCE`` or absolute
    paths outside ``copy/`` are built into the repo's ``copy/_output`` tree so
    generated artefacts stay inside the project and remain gitignored.
    """
    project_root = Path(__file__).resolve().parent.parent

    # 1) Respect an explicit absolute/relative path if it exists.
    candidate = resolve_path(str(raw_path))
    if candidate.exists():
        source_path = candidate.resolve()
        copy_root = (project_root / "copy").resolve()
        if str(source_path).startswith(str(copy_root) + os.sep):
            return source_path, source_path.parent
        return source_path, project_root / "copy"

    # 2) Fall back to COPY_SOURCE for bare filenames or subpaths.
    base = _copy_source_base()
    if base:
        candidate = (base / raw_path).resolve()
        if candidate.exists():
            source_path = candidate
            try:
                rel = source_path.relative_to(base)
                output_base = project_root / "copy" / rel.parent
            except ValueError:
                output_base = project_root / "copy"
            return source_path, output_base

    sys.exit(f"Error: File not found: {raw_path}")


def _auto_signature(npages: int) -> int:
    """Pick a sensible saddle-stitch signature size."""
    if npages <= 16:
        return max(4, math.ceil(npages / 4) * 4)
    return 16


def _validate_signature(raw: str, npages: int) -> int:
    if raw == "auto":
        return _auto_signature(npages)
    try:
        value = int(raw)
    except ValueError:
        sys.exit(f"Error: --signature must be 'auto' or a multiple of 4, got {raw!r}")
    if value <= 0 or value % 4 != 0:
        sys.exit(f"Error: --signature must be a positive multiple of 4, got {value}")
    return value


def parse_grid(raw: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)x(\d+)", raw.strip().lower())
    if not m:
        sys.exit(f"Error: --grid must be COLSxROWS (e.g. 2x2), got {raw!r}")
    cols, rows = int(m.group(1)), int(m.group(2))
    if cols < 1 or rows < 1:
        sys.exit(f"Error: --grid rows and columns must be positive, got {raw!r}")
    return cols, rows


def _unit_factor(unit: str) -> float:
    """Return the number of mm per one unit."""
    unit = unit.lower()
    if unit in ("mm", ""):
        return 1.0
    if unit == "cm":
        return 10.0
    if unit == "pt":
        return 25.4 / 72.27
    if unit == "bp":
        return 25.4 / 72.0
    if unit == "in":
        return 25.4
    sys.exit(f"Error: unsupported length unit {unit!r}")


def parse_length(raw: str) -> float:
    """Parse a length string into millimetres."""
    raw = raw.strip()
    if not raw:
        sys.exit("Error: empty length value")
    m = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*(mm|cm|pt|bp|in)?", raw)
    if not m:
        sys.exit(f"Error: invalid length {raw!r}")
    value = float(m.group(1))
    unit = m.group(2) or "mm"
    return value * _unit_factor(unit)


def parse_gutter(raw: str) -> tuple[float, float]:
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 1:
        val = parse_length(parts[0])
        return val, val
    if len(parts) == 2:
        return parse_length(parts[0]), parse_length(parts[1])
    sys.exit(f"Error: --gutter must be one or two lengths, got {raw!r}")


def get_pdf_pages(pdf_path: Path) -> int:
    """Return the number of pages in a PDF, using pdfinfo or pdfcrop."""
    if shutil.which("pdfinfo"):
        r = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())

    if shutil.which("pdfcrop"):
        r = subprocess.run(
            ["pdfcrop", "--verbose", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        m = re.search(r"\*\*\* PDFcrop:.*?(\d+) pages?", r.stdout, re.DOTALL)
        if m:
            return int(m.group(1))

    sys.exit("Error: could not determine PDF page count (pdfinfo or pdfcrop required)")


def select_pdf_pages(input_pdf: Path, output_pdf: Path, pages: str):
    """Extract a page range from a PDF using qpdf."""
    if not shutil.which("qpdf"):
        sys.exit("Error: page selection requires qpdf")
    r = subprocess.run(
        [
            "qpdf",
            str(input_pdf),
            "--pages",
            str(input_pdf),
            pages,
            "--",
            str(output_pdf),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if r.returncode != 0 or not output_pdf.exists():
        sys.exit(f"✗ page extraction failed:\n{(r.stderr or r.stdout)[-2000:]}")
    print(f"Selected pages {pages}: {output_pdf}")


def run_pdf_brighten(
    source_pdf: Path,
    output_pdf: Path,
    brightness: float | None = None,
    grayscale=False,
    filter_cmd: str | None = None,
):
    """Process only the embedded images of a PDF via the pikepdf helper.

    Text, fonts, and layout stay untouched (still vector), unlike the
    whole-page rasterisation used for dithering.
    """
    script = Path(__file__).resolve().parent / "pdf_brighten.py"
    if not script.exists():
        sys.exit(f"✗ pdf_brighten.py not found: {script}")
    if filter_cmd is None and brightness is None:
        sys.exit("✗ run_pdf_brighten requires a filter command or a brightness value")

    cmd = ["uv", "run", str(script), str(source_pdf), str(output_pdf)]
    if filter_cmd:
        cmd += ["--filter", filter_cmd]
    else:
        cmd += ["--brightness", str(brightness)]
        if grayscale:
            cmd.append("--grayscale")

    print("  Processing embedded images (text stays vector)...")
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if r.returncode != 0 or not output_pdf.exists():
        sys.exit(f"✗ pdf_brighten failed:\n{(r.stderr or r.stdout)[-4000:]}")
    for line in (r.stdout or "").splitlines():
        print(f"  {line}")


def dither_pdf_pages(
    source_pdf: Path, output_pdf: Path, dither_cmd: str, dpi: int = 300
):
    """Rasterize a PDF to images, apply a dither command, and rebuild a PDF.

    This is used for PDF inputs where images are already embedded and cannot
    be re-processed at the markdown level. The result is a monochrome/dithered
    PDF whose pages can then be imposed normally.
    """
    if "$1" not in dither_cmd or "$2" not in dither_cmd:
        sys.exit(
            "Error: --dither command template must contain $1 (input) and $2 (output)"
        )

    if not shutil.which("pdftoppm"):
        sys.exit("✗ pdftoppm not found; PDF dithering requires it")
    if not shutil.which("img2pdf"):
        sys.exit("✗ img2pdf not found; PDF dithering requires it")

    work_dir = output_pdf.parent / f"{output_pdf.stem}_dither_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    prefix = work_dir / "page"
    print(f"  Rasterizing PDF at {dpi} dpi...")
    r = subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(source_pdf), str(prefix)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if r.returncode != 0:
        sys.exit(f"✗ pdftoppm failed:\n{(r.stderr or r.stdout)[-2000:]}")

    page_images = sorted(
        p
        for p in work_dir.glob("page-*.png")
        if re.fullmatch(r"page-\d+\.png", p.name, re.IGNORECASE)
    )
    if not page_images:
        sys.exit("✗ pdftoppm produced no page images")

    dithered_images = []
    for img_path in page_images:
        dithered_path = img_path.with_stem(f"{img_path.stem}_dither")
        cmd = dither_cmd.replace("$1", shell_quote(str(img_path))).replace(
            "$2", shell_quote(str(dithered_path))
        )
        print(f"  dither page: {img_path.name}")
        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if r.returncode != 0:
            print(f"    ✗ failed: {(r.stderr or r.stdout).strip()}")
            dithered_images.append(img_path)
            continue
        if not dithered_path.exists():
            print("    ✗ no output produced")
            dithered_images.append(img_path)
            continue
        dithered_images.append(dithered_path)
        print(f"    ✓ {dithered_path.name}")

    print(f"  Rebuilding PDF from {len(dithered_images)} dithered pages...")
    r = subprocess.run(
        ["img2pdf", "--output", str(output_pdf)] + [str(p) for p in dithered_images],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if r.returncode != 0 or not output_pdf.exists():
        sys.exit(f"✗ img2pdf failed:\n{(r.stderr or r.stdout)[-2000:]}")

    # Clean up intermediate raster files to save disk space.
    shutil.rmtree(work_dir, ignore_errors=True)

    print(f"Dithered PDF: {output_pdf}")


def main():
    parser = argparse.ArgumentParser(
        description="Render a copy/ markdown file to A4 2-up, A5 single-page, or saddle-stitch booklet PDF. "
        "Existing PDF files are also accepted and imposed directly."
    )
    parser.add_argument("path", help="Path to the markdown file or PDF")
    parser.add_argument(
        "--a5",
        action="store_true",
        dest="a5",
        help="Produce a single-page A5 PDF (reading order).",
    )
    parser.add_argument(
        "--booklet",
        action="store_true",
        dest="booklet",
        help="Produce a saddle-stitch booklet (imposition order).",
    )
    parser.add_argument(
        "--signature",
        default="auto",
        help="Signature size for --booklet; 'auto' or a multiple of 4 (default: auto).",
    )
    parser.add_argument(
        "--grid",
        default=None,
        help="Grid layout for imposition, e.g. 2x2, 3x2, 1x1 (default: 2x1).",
    )
    parser.add_argument(
        "--paper",
        default=DEFAULT_PAPER,
        help="Output paper size for imposition (default: a4).",
    )
    parser.add_argument(
        "--landscape",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Use landscape output paper (default: on for reader/booklet/grid, off for --a5).",
    )
    parser.add_argument(
        "--fit",
        default="fit",
        choices=["fit", "fill", "none"],
        help="How source pages are scaled inside grid cells (default: fit).",
    )
    parser.add_argument(
        "--gutter",
        default=None,
        help="Gutter between imposed pages: one or two lengths (default: 0).",
    )
    parser.add_argument(
        "--margin",
        default=None,
        help="Output page margin around the grid (grid default: 3mm, reader/booklet default: 0pt).",
    )
    parser.add_argument(
        "--frame",
        action="store_true",
        help="Draw a thin frame around each grid cell (useful as cut guide).",
    )
    parser.add_argument(
        "--frame-color",
        default="gray!70",
        help="Color of the frame/divider lines (default: gray!70). 'gray50' is accepted as shorthand for 'gray!50'.",
    )
    parser.add_argument(
        "--frame-width",
        default="0.4pt",
        help="Width of the frame/divider lines (default: 0.4pt).",
    )
    parser.add_argument(
        "--divider",
        action="store_true",
        help="Draw internal grid divider lines (no outer border).",
    )
    parser.add_argument(
        "--divider-horizontal",
        action="store_true",
        help="Draw only horizontal internal divider lines.",
    )
    parser.add_argument(
        "--divider-vertical",
        action="store_true",
        help="Draw only vertical internal divider lines.",
    )
    parser.add_argument(
        "--pages",
        default="-",
        help="Page range to impose, pdfpages syntax (default: '-', all pages).",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="booklet_legacy",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--dither",
        nargs="?",
        const="magick $1 -colorspace Gray -ordered-dither h8x8a -type Bilevel $2",
        default=None,
        help="Dither raster images or PDF pages before imposing. Provide a command template with $1=input and $2=output (default: 'magick $1 -colorspace Gray -ordered-dither h8x8a -type Bilevel $2').",
    )
    parser.add_argument(
        "--dither-dpi",
        default=300,
        type=int,
        help="DPI for rasterizing PDF pages before dithering (default: 300).",
    )
    parser.add_argument(
        "--brighten",
        type=float,
        default=None,
        help="Brighten only the embedded raster images by PERCENT (text stays vector). "
        "For PDFs this edits images in place; for markdown it brightens extracted images.",
    )
    parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Convert the processed images to grayscale (works alone or with --brighten).",
    )
    parser.add_argument(
        "--image-filter",
        default=None,
        help="Arbitrary ImageMagick command template with $1=input and $2=output, "
        "run once per embedded image (PDF) or extracted image (markdown). "
        'Text stays vector. Example: "magick $1 -colorspace Gray -gamma 2.2 $2".',
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Append a suffix to output PDF filenames before .pdf (e.g. --suffix .h8x8a).",
    )
    args = parser.parse_args()

    # --print is the old name for --booklet; keep it working.
    if args.booklet_legacy:
        args.booklet = True

    suffix = args.suffix

    # Build the image-only filter command. --brighten is a shortcut mapping to
    # a multiplicative brightness (same semantics as PIL), so markdown and PDF
    # behave identically. --image-filter takes precedence when given.
    image_filter = args.image_filter
    if image_filter is None and args.brighten is not None:
        factor = 1 + args.brighten / 100.0
        gray = " -colorspace Gray" if args.grayscale else ""
        image_filter = f"magick $1{gray} -evaluate multiply {factor:g} $2"
    elif image_filter is None and args.grayscale:
        image_filter = "magick $1 -colorspace Gray $2"

    raw_path = Path(args.path)
    source_path, output_base = resolve_copy_input(raw_path)
    project_root = Path(__file__).resolve().parent.parent

    is_pdf = source_path.suffix.lower() == ".pdf"

    # Decide landscape default.
    if args.landscape is None:
        landscape = not args.a5
    else:
        landscape = args.landscape

    latex_dir = safe_staging_dir(output_base / "_output" / "latex", source_path.stem)
    latex_dir.mkdir(parents=True, exist_ok=True)
    pdfs_dir = output_base / "_output" / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize the jobname: spaces and '%' confuse the TeX command line,
    # and dots break the markdown package's texlua bridge.
    tex_stem = re.sub(r"[^A-Za-z0-9_-]+", "-", source_path.stem).strip("-")

    if is_pdf:
        # Copy PDF into staging so the LaTeX wrapper can refer to it with a
        # simple, safe filename.
        staged_pdf = latex_dir / f"{tex_stem}-source.pdf"
        shutil.copy2(str(source_path), str(staged_pdf))
        source_pdf = staged_pdf

        # Extract a subset of pages first to keep huge PDFs manageable.
        if args.pages != "-":
            selected_pdf = latex_dir / f"{tex_stem}-selected.pdf"
            select_pdf_pages(source_pdf, selected_pdf, args.pages)
            source_pdf = selected_pdf

        if image_filter:
            brightened_pdf = latex_dir / f"{tex_stem}-bright.pdf"
            run_pdf_brighten(source_pdf, brightened_pdf, filter_cmd=image_filter)
            source_pdf = brightened_pdf

        if args.dither:
            dithered_pdf = latex_dir / f"{tex_stem}-dithered.pdf"
            dither_pdf_pages(source_pdf, dithered_pdf, args.dither, dpi=args.dither_dpi)
            source_pdf = dithered_pdf

        npages = get_pdf_pages(source_pdf)
        print(f"PDF source: {npages} pages")
    else:
        if image_filter and args.dither:
            print(
                "  note: --image-filter takes precedence over --dither for markdown; "
                "combine both operations in a single filter command if needed"
            )
        md_cmd = image_filter if image_filter else args.dither
        process_markdown(source_path, latex_dir, hard_breaks=True, dither=md_cmd)

        seq_path = generate_seq_wrapper(source_path, latex_dir, project_root, tex_stem)
        npages = compile_tex(seq_path, "xelatex")
        print(f"Sequential A5 document: {npages} pages")

        extract_pax(tex_stem, latex_dir)

        source_pdf = latex_dir / f"{tex_stem}.pdf"

    # Parse grid and gutter.
    grid = parse_grid(args.grid) if args.grid else None
    gutter = parse_gutter(args.gutter) if args.gutter else (0.0, 0.0)

    # Default margin depends on mode.
    if args.margin is not None:
        margin_mm = parse_length(args.margin)
    elif grid and grid != (2, 1):
        margin_mm = parse_length(DEFAULT_GRID_MARGIN)
    else:
        margin_mm = parse_length(DEFAULT_READER_MARGIN)

    # Divider flags: --divider enables both directions; the specific flags
    # can be combined with it or used alone.
    draw_h = args.divider or args.divider_horizontal
    draw_v = args.divider or args.divider_vertical

    if args.a5:
        a5_pdf = pdfs_dir / f"{source_path.stem}{suffix}.a5.pdf"
        if is_pdf:
            shutil.copy2(str(source_pdf), str(a5_pdf))
        else:
            shutil.copy2(str(latex_dir / f"{tex_stem}.pdf"), str(a5_pdf))
        print(f"Created: {a5_pdf}")

    if args.booklet:
        selected_pages = count_selected_pages(args.pages, npages)
        signature = _validate_signature(args.signature, selected_pages)
        if gutter == (0.0, 0.0):
            gutter = (parse_length("6mm"), 0.0)
        booklet_path = generate_pdfpages_wrapper(
            tex_stem,
            latex_dir,
            source_pdf,
            signature=signature,
            grid=grid,
            paper=args.paper,
            landscape=landscape,
            gutter=gutter,
            margin=margin_mm,
            frame=args.frame,
            frame_color=args.frame_color,
            frame_width=args.frame_width,
            pages=args.pages,
        )
        compile_tex(booklet_path, "pdflatex")
        booklet_pdf = pdfs_dir / f"{source_path.stem}{suffix}.booklet.pdf"
        shutil.move(str(booklet_path.with_suffix(".pdf")), str(booklet_pdf))
        print(f"Created: {booklet_pdf} (signature={signature})")
        print("Print duplex (flip on short edge), stack, fold, staple the spine.")

    if not args.a5 and not args.booklet:
        # Default mode: reader (2-up) or explicit grid.
        if grid is None:
            grid = (2, 1)

        if grid != (2, 1):
            # Manual TikZ grid layout with margins and scaling control.
            grid_path, runs = generate_grid_wrapper(
                tex_stem,
                latex_dir,
                source_pdf,
                npages,
                grid,
                paper=args.paper,
                landscape=landscape,
                gutter=gutter,
                margin=margin_mm,
                fit_mode=args.fit,
                frame=args.frame,
                frame_color=args.frame_color,
                frame_width=args.frame_width,
                divider_horizontal=draw_h,
                divider_vertical=draw_v,
                pages=args.pages,
            )
            compile_tex(grid_path, "pdflatex", runs=runs)
            grid_pdf = (
                pdfs_dir / f"{source_path.stem}{suffix}.grid-{grid[0]}x{grid[1]}.pdf"
            )
            shutil.move(str(grid_path.with_suffix(".pdf")), str(grid_pdf))
            print(f"Created: {grid_pdf}")
        else:
            # Classic 2-up reader uses pdfpages for speed and link preservation.
            reader_path = generate_pdfpages_wrapper(
                tex_stem,
                latex_dir,
                source_pdf,
                grid=grid,
                paper=args.paper,
                landscape=landscape,
                gutter=gutter,
                margin=margin_mm,
                frame=args.frame,
                frame_color=args.frame_color,
                frame_width=args.frame_width,
                pages=args.pages,
            )
            compile_tex(reader_path, "pdflatex")
            reader_pdf = pdfs_dir / f"{source_path.stem}{suffix}.pdf"
            shutil.move(str(reader_path.with_suffix(".pdf")), str(reader_pdf))
            print(f"Created: {reader_pdf}")

            jpg_pattern = str(output_base / "_output" / f"{source_path.stem}_p%02d.jpg")
            convert_to_jpg(reader_pdf, jpg_pattern)

    return 0


if __name__ == "__main__":
    sys.exit(main())
