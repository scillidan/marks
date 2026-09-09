#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Render a bilingual post pair (`<stem>.md` + `<stem>.zh-cn.md`) as a
two-column, paragraph-synchronized A4 PDF using XeLaTeX + paracol.

Pipeline:
  1. Reuse gen_a4_latex.process_markdown on each side to collect images and
     produce a cleaned per-side body markdown + metadata.
  2. Split each body into top-level blocks (blank-line separated, code fences
     kept intact).
  3. Convert every block to TeX with the markdown Lua module (same options the
     shared template uses), then strip the document/section/interblock wrappers.
  4. Write an interleaved TeX file that feeds paired English/Chinese blocks
     into a `paracol` environment with `\\switchcolumn` between them.
  5. Compile with xelatex and convert to JPGs.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from _common import convert_to_jpg, find_imagemagick_cli
from gen_a4_latex import process_markdown

_MARKDOWN_OPTS = (
    "eagerCache=false fencedCode=true notes=true underscores=true texMathDollars=false"
)

_FENCE_OPEN = re.compile(r"^(?P<fence>`{3,})[^`]*$")
_FENCE_CLOSE = re.compile(r"^(?P<fence>`{3,})[ \t]*$")


def split_blocks(text):
    """Split markdown into top-level blocks on blank lines.

    Fenced code blocks are kept whole even when they contain blank lines.
    """
    lines = text.split("\n")
    blocks = []
    cur = []
    infence = False
    fence_marker = None

    def flush():
        if cur:
            blocks.append("\n".join(cur))
            cur.clear()

    for ln in lines:
        if not infence:
            m = _FENCE_OPEN.match(ln)
            if m:
                infence = True
                fence_marker = m.group("fence")
                cur.append(ln)
                continue
            if ln.strip() == "":
                flush()
            else:
                cur.append(ln)
        else:
            cur.append(ln)
            if (
                fence_marker
                and _FENCE_CLOSE.match(ln)
                and len(ln.strip()) >= len(fence_marker)
            ):
                infence = False
                fence_marker = None
    flush()
    return blocks


def call_texlua(script, *args, cwd=None):
    texlua = shutil.which("texlua") or shutil.which("lualatex")
    if not texlua:
        sys.exit("✗ texlua not found; markdown2tex conversion requires LuaTeX")
    r = subprocess.run(
        [texlua, script, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=cwd,
    )
    if r.returncode != 0:
        sys.exit(f"✗ texlua error:\n{r.stderr or r.stdout}")


def convert_blocks(indir, outdir, cwd=None):
    """Run scripts/markdown_block_convert.lua over every *.md in indir.

    cwd must be the LaTeX staging dir so fenced-code temp files written by the
    markdown converter land where xelatex will look for them.
    """
    script = Path(__file__).resolve().parent / "markdown_block_convert.lua"
    call_texlua(str(script), str(indir), str(outdir), cwd=cwd)


def find_markdown_lua_script():
    """Locate the markdown package's convert-dir lua helper inside this repo."""
    p = Path(__file__).resolve().parent / "markdown_block_convert.lua"
    return p


def generate_wrapper(md_en_path, md_zh_path, latex_dir, project_root):
    en_stem = md_en_path.stem
    zh_stem = md_zh_path.stem
    # e.g. foo.md + foo.zh-cn.md -> foo_zh-cn
    zh_lang = zh_stem
    if en_stem and zh_stem.startswith(en_stem + "."):
        zh_lang = zh_stem[len(en_stem) + 1 :]
    out_stem = f"{en_stem}_{zh_lang}" if zh_lang else f"{en_stem}-dual"

    rel_root = os.path.relpath(project_root, latex_dir).replace("\\", "/")
    wrapper = rf"""% !TeX program = xelatex
% Auto-generated bilingual LaTeX wrapper for {md_en_path.name} / {md_zh_path.name}.
% Regenerate with: python scripts/gen_a4_dual_latex.py {md_en_path.as_posix()} {md_zh_path.as_posix()}

\documentclass{{article}}
\usepackage[a4paper, margin=1.2cm]{{geometry}}
\usepackage{{paracol}}

\def\poststem{{{out_stem}}}
\def\postlayout{{a4}}

\input{{{rel_root}/scripts/gen_a4_latex}}

\def\postimagedir{{images/}}

% The article class is single-column here (paracol makes the two columns), so
% teach `responsive` to measure against half the text width -- otherwise it
% picks a ~13pt face meant for a full-width page and list items overflow.
\ResponsiveSetup{{boxwidth=0.46\textwidth, characters=50}}

\begin{{document}}

\input{{meta.tex}}

\input{{body-interleaved.tex}}

\postprintendnotes

\end{{document}}
"""
    wrapper_path = latex_dir / f"{out_stem}.tex"
    wrapper_path.write_text(wrapper, encoding="utf-8")
    print(f"Created: {wrapper_path}")
    return wrapper_path, out_stem


def compile_xelatex(wrapper_path, pdf_dir, jpg_pattern):
    r = subprocess.run(
        [
            "xelatex",
            "-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            str(wrapper_path.name),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=str(wrapper_path.parent),
    )
    if r.returncode != 0:
        sys.exit(f"✗ xelatex compile error:\n{(r.stderr or r.stdout)[-4000:]}")
    staged_pdf = wrapper_path.with_suffix(".pdf")
    pdf_path = pdf_dir / f"{wrapper_path.stem}.pdf"
    shutil.move(str(staged_pdf), str(pdf_path))
    print(f"Created: {pdf_path}")
    convert_to_jpg(pdf_path, jpg_pattern)


def main():
    parser = argparse.ArgumentParser(
        description="Render a bilingual post pair to a synchronized two-column A4 PDF."
    )
    parser.add_argument("en_path", help="English (source) markdown file")
    parser.add_argument("zh_path", help="Simplified-Chinese translation markdown file")
    args = parser.parse_args()

    md_en = Path(args.en_path).resolve()
    md_zh = Path(args.zh_path).resolve()
    if not md_en.exists():
        sys.exit(f"Error: File not found: {md_en}")
    if not md_zh.exists():
        sys.exit(f"Error: File not found: {md_zh}")

    content_dir = md_en.parent
    project_root = Path(__file__).resolve().parent.parent
    latex_dir = content_dir / "_output" / "latex" / f"{md_en.stem}-dual"
    latex_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run each side through the standard per-post markdown pipeline.
    #    Images from both sides land in the same images/ dir; each side's body
    #    is kept under a distinct name so they can be aligned later.
    body_en, meta_en, images_dir = process_markdown(md_en, latex_dir)
    body_en.replace(latex_dir / "body-en.md")
    meta_en.replace(latex_dir / "meta-en.tex")
    body_zh, meta_zh, _ = process_markdown(md_zh, latex_dir)
    body_zh.replace(latex_dir / "body-zh.md")
    meta_zh.replace(latex_dir / "meta.tex")

    # 2. Split both bodies into top-level blocks and align them pairwise.
    en_text = (latex_dir / "body-en.md").read_text(encoding="utf-8")
    zh_text = (latex_dir / "body-zh.md").read_text(encoding="utf-8")
    en_blocks = split_blocks(en_text)
    zh_blocks = split_blocks(zh_text)
    n = min(len(en_blocks), len(zh_blocks))
    if len(en_blocks) != len(zh_blocks):
        print(
            f"⚠ Block count mismatch: en={len(en_blocks)}, zh={len(zh_blocks)}; "
            f"aligning first {n} pairs"
        )

    # 3. Convert each block to a self-contained TeX fragment.
    staged = latex_dir / "blocks"
    en_md_dir = staged / "en"
    zh_md_dir = staged / "zh"
    en_tex_dir = staged / "en-tex"
    zh_tex_dir = staged / "zh-tex"
    for d in (en_md_dir, zh_md_dir, en_tex_dir, zh_tex_dir):
        d.mkdir(parents=True, exist_ok=True)

    for i, (en_blk, zh_blk) in enumerate(zip(en_blocks[:n], zh_blocks[:n]), 1):
        (en_md_dir / f"b{i:03d}.md").write_text(en_blk + "\n", encoding="utf-8")
        (zh_md_dir / f"b{i:03d}.md").write_text(zh_blk + "\n", encoding="utf-8")

    convert_blocks(en_md_dir, en_tex_dir, cwd=latex_dir)
    convert_blocks(zh_md_dir, zh_tex_dir, cwd=latex_dir)

    # 4. Interleave into paired paracol environments.
    # One paracol per pair: ending it re-synchronises the column tops, so every
    # English block starts at the same height as its Chinese counterpart.
    lines = []
    for i in range(1, n + 1):
        en_tex = (en_tex_dir / f"b{i:03d}.tex").read_text(encoding="utf-8").strip()
        zh_tex = (zh_tex_dir / f"b{i:03d}.tex").read_text(encoding="utf-8").strip()
        # NB: no `%` comment lines here. The metadata raw block is included
        # via \markdownEscape, which leaves `%` at catcode 12 afterwards, so
        # any later `%` would print as literal text instead of a comment.
        lines.append("\\begin{paracol}{2}")
        lines.append(en_tex)
        lines.append("\\par\\switchcolumn")
        lines.append(zh_tex)
        lines.append("\\par")
        lines.append("\\end{paracol}")
    (latex_dir / "body-interleaved.tex").write_text("\n".join(lines), encoding="utf-8")

    # 5. Wrapper + compile.
    wrapper_path, out_stem = generate_wrapper(md_en, md_zh, latex_dir, project_root)
    pdfs_dir = content_dir / "_output" / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    jpg_pattern = str(content_dir / "_output" / f"{out_stem}_p%02d.jpg")
    compile_xelatex(wrapper_path, pdfs_dir, jpg_pattern)


if __name__ == "__main__":
    main()
