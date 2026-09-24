#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# copy/: A5 sequential pages -> 2-up landscape A4. --print also makes a
# saddle-stitch booklet via pdfpages signature (duplex short-edge flip,
# stack, fold, staple 2-3 times on the spine).

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

from _common import convert_to_jpg, safe_staging_dir
from gen_a4_latex import process_markdown, resolve_path


def compile_tex(tex_path, engine):
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


def generate_impose_wrapper(tex_stem, latex_dir, signature=None):
    opts = "pages=-, nup=2x1"
    kind = "reader"
    if signature:
        # delta adds a binding gutter at the fold
        opts += f", signature={signature}, delta=6mm 0"
        kind = "booklet"
    # pax only supports pdfTeX; pdftexcmds must precede pax or links are
    # silently dropped
    wrapper = f"""% !TeX program = pdflatex
% Auto-generated {kind} imposition wrapper -- do not edit.

\\documentclass{{article}}
\\usepackage[a4paper, landscape, margin=0pt]{{geometry}}
\\usepackage{{pdfpages}}
\\usepackage{{pdftexcmds}}
\\makeatletter
\\ifx\\pdfstrcmp\\undefined\\let\\pdfstrcmp\\pdf@strcmp\\fi
\\makeatother
\\usepackage{{pax}}

\\begin{{document}}

\\includepdf[{opts}]{{{tex_stem}.pdf}}

\\end{{document}}
"""
    wrapper_path = latex_dir / f"{tex_stem}.{kind}.tex"
    wrapper_path.write_text(wrapper, encoding="utf-8")
    print(f"Created: {wrapper_path}")
    return wrapper_path


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
    """Locate the markdown file and decide where its outputs should live.

    Returns (md_path, output_base). The output base is the directory under
    which ``_output/latex`` and ``_output/pdfs`` will be created. Local files
    inside the repo's ``copy/`` tree keep their existing behaviour (outputs
    live next to the source). Files resolved via ``COPY_SOURCE`` are built
    into the repo's ``copy/_output`` tree so generated artefacts stay inside
    the project and remain gitignored.
    """
    project_root = Path(__file__).resolve().parent.parent

    # 1) Respect an explicit absolute/relative path if it exists.
    candidate = resolve_path(str(raw_path))
    if candidate.exists():
        md_path = candidate.resolve()
        copy_root = (project_root / "copy").resolve()
        if str(md_path).startswith(str(copy_root) + os.sep):
            return md_path, md_path.parent
        return md_path, project_root / "copy"

    # 2) Fall back to COPY_SOURCE for bare filenames or subpaths.
    base = _copy_source_base()
    if base:
        candidate = (base / raw_path).resolve()
        if candidate.exists():
            md_path = candidate
            try:
                rel = md_path.relative_to(base)
                output_base = project_root / "copy" / rel.parent
            except ValueError:
                output_base = project_root / "copy"
            return md_path, output_base

    sys.exit(f"Error: File not found: {raw_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Render a copy/ markdown file to landscape A4 2-up PDF."
    )
    parser.add_argument("path", help="Path to the markdown file")
    parser.add_argument(
        "--print",
        action="store_true",
        dest="booklet",
        help="Also produce the saddle-stitch booklet (imposition order).",
    )
    args = parser.parse_args()

    raw_path = Path(args.path)
    md_path, output_base = resolve_copy_input(raw_path)
    project_root = Path(__file__).resolve().parent.parent

    latex_dir = safe_staging_dir(output_base / "_output" / "latex", md_path.stem)
    latex_dir.mkdir(parents=True, exist_ok=True)
    pdfs_dir = output_base / "_output" / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    process_markdown(md_path, latex_dir, hard_breaks=True)

    # Dotted filenames break the markdown package's texlua bridge
    # ("Script file .texlua: not found"); sanitize the \jobname.
    tex_stem = md_path.stem.replace(".", "-")

    seq_path = generate_seq_wrapper(md_path, latex_dir, project_root, tex_stem)
    npages = compile_tex(seq_path, "xelatex")
    print(f"Sequential A5 document: {npages} pages")

    extract_pax(tex_stem, latex_dir)

    reader_path = generate_impose_wrapper(tex_stem, latex_dir)
    compile_tex(reader_path, "pdflatex")
    reader_pdf = pdfs_dir / f"{md_path.stem}.pdf"
    shutil.move(str(reader_path.with_suffix(".pdf")), str(reader_pdf))
    print(f"Created: {reader_pdf}")
    jpg_pattern = str(output_base / "_output" / f"{md_path.stem}_p%02d.jpg")
    convert_to_jpg(reader_pdf, jpg_pattern)

    if args.booklet:
        signature = max(4, math.ceil(npages / 4) * 4)
        booklet_path = generate_impose_wrapper(tex_stem, latex_dir, signature=signature)
        compile_tex(booklet_path, "pdflatex")
        booklet_pdf = pdfs_dir / f"{md_path.stem}.booklet.pdf"
        shutil.move(str(booklet_path.with_suffix(".pdf")), str(booklet_pdf))
        print(f"Created: {booklet_pdf} (signature={signature})")
        print("Print duplex (flip on short edge), stack, fold, staple the spine.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
