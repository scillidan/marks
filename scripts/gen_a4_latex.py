#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from _common import convert_to_jpg, find_imagemagick_cli

MEDIA_EXTS = {".gif", ".mp4", ".mov", ".webm"}
AVIF_EXTS = {".avif"}
WEBP_EXTS = {".webp"}
SVG_EXTS = {".svg"}
CONVERT_EXTS = MEDIA_EXTS | AVIF_EXTS | WEBP_EXTS
# xelatex cannot include SVG directly, so rasterise it alongside other formats.
LATEX_CONVERT_EXTS = CONVERT_EXTS | SVG_EXTS
SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".avif"]


def resolve_path(p):
    path = Path(p)
    return path if path.is_absolute() else Path.cwd() / path


def get_image_source(content_dir):
    env_path = os.environ.get("POST_SOURCE")
    if env_path:
        path = Path(os.path.expandvars(env_path))
        if path.exists():
            return path
        print(f"✗ POST_SOURCE: {env_path} (not found)")
    local_assets = content_dir / "assets"
    if local_assets.exists():
        return local_assets
    return None


def extract_metadata(md_content):
    lines = md_content.splitlines()
    meta = {}
    if lines and lines[0].strip().startswith("```"):
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "```":
                end = i
                break
        if end is not None:
            for line in lines[1:end]:
                m = re.match(r"^([A-Za-z][A-Za-z0-9_ ]*)\s*:\s*(.*)$", line)
                if m:
                    key = m.group(1).strip().lower().replace(" ", "")
                    meta[key] = m.group(2).strip()
            md_content = "\n".join(lines[end + 1 :])
    return meta, md_content


def clean_markdown(md_content):
    # Remove cmarker raw-typst comments.
    md_content = re.sub(r"<!--raw-typst.*?-->", "", md_content, flags=re.S)

    # Convert broken image lines (alt text without a path) to italic text.
    def fix_broken_image(m):
        alt = m.group(1)
        return f"*{alt}*" if alt else ""

    md_content = re.sub(
        r"^!\[([^\]]*)\]$",
        fix_broken_image,
        md_content,
        flags=re.M,
    )

    # Collapse runs of blank lines.
    md_content = re.sub(r"\n{3,}", "\n\n", md_content)
    return md_content


def convert_with_magick(src, dest):
    cli = find_imagemagick_cli()
    if not cli:
        print(
            f"  ✗ conversion failed for {src.name}: ImageMagick (magick/convert) not found"
        )
        return False

    src_ext = src.suffix.lower()

    # Animated / multi-frame sources: ensure we emit a single output file.
    # ImageMagick's default behaviour for GIF/video is to write a numbered
    # sequence (foo-0.jpg, foo-1.jpg, ...), so xelatex never finds foo.jpg.
    if src_ext == ".gif":
        # [0] selects the first frame and forces a single output file.
        magick_spec = f"{src}[0]"
    elif src_ext in MEDIA_EXTS:
        # Video formats convert more reliably with ffmpeg on CI images.
        if shutil.which("ffmpeg"):
            r = subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(src),
                    "-ss",
                    "00:00:00",
                    "-vframes",
                    "1",
                    str(dest),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            if r.returncode == 0 and dest.exists():
                return True
            print(f"  ✗ ffmpeg conversion failed for {src.name}: {r.stderr}")
            return False
        magick_spec = f"{src}[0]"
    else:
        magick_spec = str(src)

    try:
        r = subprocess.run(
            [cli, magick_spec, str(dest)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if r.returncode == 0:
            return True
        # ImageMagick's SVG delegate is sometimes missing on CI images.
        # Fall back to rsvg-convert (PNG) + ImageMagick (PNG -> JPG) when possible.
        if src_ext == ".svg" and shutil.which("rsvg-convert"):
            png = dest.with_suffix(".png")
            r2 = subprocess.run(
                ["rsvg-convert", "--format=png", "-o", str(png), str(src)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            if r2.returncode == 0 and png.exists():
                r3 = subprocess.run(
                    [cli, str(png), str(dest)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                png.unlink(missing_ok=True)
                if r3.returncode == 0:
                    return True
                print(f"  ✗ conversion failed for {src.name}: {r3.stderr}")
                return False
            print(f"  ✗ conversion failed for {src.name} (rsvg-convert): {r2.stderr}")
            return False
        print(f"  ✗ conversion failed for {src.name}: {r.stderr}")
        return False
    except Exception as e:
        print(f"  ✗ conversion error for {src.name}: {e}")
        return False


def protect_pipe_tables(md_content):
    """Convert markdown pipe-table rows into bulleted list items.

    The `markdown` package trips over the HTML entities (``&nbsp;`` etc.) that
    frequently appear inside such tables, and long fenced-code rows overflow.
    Emitting each row as a bullet list item keeps the text wrapping and lets
    the package handle the (already unescaped) entities normally.
    """
    lines = md_content.splitlines()
    out = []
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if not in_fence and line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            for row in rows:
                content = row.strip().strip("|")
                if re.fullmatch(r":?-+:?", content.strip()):
                    continue
                content = " — ".join(cell.strip() for cell in content.split("|"))
                if content:
                    out.append(f"- {content}")
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def unwrap_md_code_blocks(md_content):
    r"""Strip ````md` fenced code blocks and render their contents as markdown.

    Some articles use ````md` fences for styled callout blocks. The markdown
    package would otherwise typeset the inner content as a verbatim code block
    that does not wrap, causing overfull \\hbox lines that spill across columns.
    """
    fence_re = re.compile(r"^(```+)md[ \t]*\n(.*?)\n\1[ \t]*$", re.S | re.M)
    return fence_re.sub(lambda m: m.group(2), md_content)


def escape_underscores_in_urls(md_content):
    """Escape underscores in markdown image/link URLs.

    The markdown package is loaded with ``underscores=true`` so that ``_*_``
    emphasis works. That also makes underscores inside URLs emphasis markers,
    which breaks filenames such as ``image_01.jpg``. Escaping them keeps the
    URL intact while allowing emphasis syntax elsewhere.
    """

    def esc(url):
        return url.replace("_", r"\_")

    # Links that wrap an image: [![alt](inner)](outer)
    def link_with_image_repl(m):
        inner_alt, inner_url, outer_url = m.group(1), m.group(2), m.group(3)
        return f"[![{inner_alt}]({esc(inner_url)})]({esc(outer_url)})"

    md_content = re.sub(
        r"\[!\[([^\]]*)\]\(([^\s\)]+)\)\]\(([^\s\)]+)\)",
        link_with_image_repl,
        md_content,
    )

    # Standalone images and regular links. Skip URLs that already contain an
    # escaped underscore so that nested image/link combinations are not double
    # escaped.
    def repl(m):
        url = m.group(2)
        if r"\_" in url:
            return m.group(0)
        return m.group(1) + esc(url) + m.group(3)

    md_content = re.sub(r"(!?\[[^\]]*\]\()([^\s\)]+)(\))", repl, md_content)
    return md_content


def separate_footnote_definitions(md_content):
    """Ensure consecutive footnote definitions are separated by blank lines.

    The markdown package only recognises footnote definitions that are
    separated by at least one blank line. Many source files list them
    back-to-back, which causes "Undefined note reference" warnings.
    """
    return re.sub(
        r"(\[\^[^\]]+\]:.*)\n(?=\[\^[^\]]+\]:)",
        r"\1\n\n",
        md_content,
    )


def normalize_whitespace(md_content):
    """Clean up stray whitespace.

    * Remove trailing spaces that markdown interprets as hard line breaks.
    * Collapse runs of multiple spaces to a single space outside code fences.
    """
    # Preserve fenced code blocks while normalizing the rest.
    fence_re = re.compile(r"^(```+)[^\n]*\n.*?\n\1[ \t]*$", re.S | re.M)
    parts = []
    last = 0
    for m in fence_re.finditer(md_content):
        parts.append(md_content[last : m.start()])
        parts.append(m.group(0))
        last = m.end()
    parts.append(md_content[last:])

    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            part = re.sub(r"[ \t]+$", "", part, flags=re.M)
            part = re.sub(r"([^\s])  +", r"\1 ", part)
        out.append(part)
    return "".join(out)


def process_figures(md_content):
    """Normalise image blocks.

    * Image + caption in the same paragraph become an image whose alt text is
      the caption (the template renders it as a narrow caption block).
    * Standalone images get their alt cleared, so the template never prints
      descriptive alt text as a caption.
    * Consecutive standalone images stay as separate images: each is sized
      individually by ``fitbox`` against the true remaining column space.
      Wrapping them in an unbreakable ``postimagegroup`` minipage instead
      created all-or-nothing blocks that jumped to the next column when they
      did not fit the column remainder, leaving large blank bands.
    """
    img_re = re.compile(r"^!\[[^\]]*\]\(([^\s\)\\]+)\)[ \t]*$")

    blocks = re.split(r"\n{2,}", md_content)
    out = []
    pending = []

    def flush_images():
        if not pending:
            return
        for f in pending:
            out.append(f"![]({f})")
        pending.clear()

    for block in blocks:
        lines = block.splitlines()
        if not lines:
            flush_images()
            continue
        first = lines[0].rstrip()
        m = img_re.match(first)
        if m is None:
            flush_images()
            out.append(block)
            continue
        filename = m.group(1)
        caption = " ".join(ln.strip() for ln in lines[1:] if ln.strip())
        if caption:
            flush_images()
            out.append(f"![{caption}]({filename})")
        else:
            pending.append(filename)
    flush_images()
    return "\n\n".join(out)


def process_markdown(md_path, output_dir):
    content_dir = md_path.parent
    md_content = md_path.read_text(encoding="utf-8")

    meta, md_content = extract_metadata(md_content)
    md_content = clean_markdown(md_content)

    # Sanitize HTML leftovers so the markdown package + xelatex can handle them.
    md_content = protect_pipe_tables(md_content)
    md_content = re.sub(r"<br\s*/?>", " ", md_content, flags=re.IGNORECASE)
    md_content = html.unescape(md_content)

    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = content_dir / "assets"

    cdn_re = re.compile(
        r"(!\[[^\]]*\]\()https://scillidan\.github\.io/cdn_image_post/([^\s\)\\]+)(\))"
    )
    assets_re = re.compile(r"(!\[[^\]]*\]\()assets/([^\s\)\\]+)(\))")
    any_img_re = re.compile(r"(!\[[^\]]*\]\()([^\s\)\\]+)(\))")

    cdn_names = sorted({m.group(2) for m in cdn_re.finditer(md_content)})
    local_map = {}
    local_names = set()

    for m in assets_re.finditer(md_content):
        name = m.group(2)
        local_map[f"assets/{name}"] = name
        local_names.add(name)

    for m in any_img_re.finditer(md_content):
        ref = m.group(2)
        if ref.startswith(("http://", "https://", "assets/")):
            continue
        local_map[ref] = ref
        local_names.add(ref)

    conv_map = {}
    media_note = {}
    found_count = 0
    missing = []

    def record_conversion(full, jpg_name, ext):
        conv_map[full] = jpg_name
        if ext in MEDIA_EXTS:
            media_note[full] = ext.lstrip(".")

    cdn_map = {}
    if cdn_names:
        image_source = get_image_source(content_dir)
        if not image_source:
            sys.exit("\nSet POST_SOURCE in .env or place images in post/assets/\n")
        for base in cdn_names:
            resolved = None
            for ext in SUPPORTED_EXTS:
                src = image_source / f"{base}{ext}"
                if src.exists():
                    resolved = src
                    break
            if not resolved:
                missing.append(f"{base}.*")
                print(f"  ✗ {base}.* (not found)")
                continue

            src_ext = resolved.suffix.lower()
            if src_ext in LATEX_CONVERT_EXTS:
                jpg = images_dir / f"{resolved.stem}.jpg"
                if convert_with_magick(resolved, jpg):
                    cdn_map[base] = jpg.name
                    found_count += 1
                    print(f"  ✓ {jpg.name} (from {resolved.name})")
                else:
                    missing.append(f"{base}.*")
            else:
                dest_name = resolved.name
                dest = images_dir / dest_name
                if not dest.exists():
                    shutil.copy2(resolved, dest)
                cdn_map[base] = dest_name
                found_count += 1
                print(f"  ✓ {dest_name}")

    for name in sorted(local_names):
        src = assets_dir / name
        if not src.exists():
            missing.append(name)
            print(f"  ✗ {name} (not found)")
            continue

        src_ext = src.suffix.lower()
        if src_ext in LATEX_CONVERT_EXTS:
            jpg = images_dir / f"{src.stem}.jpg"
            if convert_with_magick(src, jpg):
                for full, fname in local_map.items():
                    if fname == name:
                        record_conversion(full, jpg.name, src_ext)
                found_count += 1
                print(f"  ✓ {jpg.name} (from {src.name})")
            else:
                missing.append(name)
        else:
            dest = images_dir / name
            if not dest.exists():
                shutil.copy2(src, dest)
            found_count += 1
            print(f"  ✓ {name}")

    if missing:
        print(f"\n✗ Images: {found_count} found, {len(missing)} missing")
        for m in missing:
            print(f"    - {m}")
        sys.exit(1)
    else:
        print(f"✓ Images: all {found_count} found")

    media_img_re = re.compile(r"(!\[[^\]]*\]\()([^\s\)\\]+)(\))([ \t]*\n)([^\n]*)")

    def rewrite_media(m):
        full = m.group(2)
        if full not in conv_map:
            return m.group(0)
        jpg = conv_map[full]
        sep = m.group(4)
        caption = m.group(5)
        if full in media_note and caption and not caption.lstrip().startswith("!["):
            caption = f"[Original Format: {media_note[full]}]{caption}"
        return f"{m.group(1)}{jpg}{m.group(3)}{sep}{caption}"

    md_content = media_img_re.sub(rewrite_media, md_content)

    def rewrite_cdn(m):
        base = m.group(2)
        if base in cdn_map:
            return f"{m.group(1)}{cdn_map[base]}{m.group(3)}"
        return m.group(0)

    md_content = cdn_re.sub(rewrite_cdn, md_content)

    def rewrite_local(m):
        full = m.group(2)
        if full in local_map:
            return f"{m.group(1)}{local_map[full]}{m.group(3)}"
        return m.group(0)

    md_content = any_img_re.sub(rewrite_local, md_content)

    md_content = unwrap_md_code_blocks(md_content)
    md_content = process_figures(md_content)
    md_content = escape_underscores_in_urls(md_content)
    md_content = separate_footnote_definitions(md_content)
    md_content = normalize_whitespace(md_content)
    md_content = re.sub(r"\n{3,}", "\n\n", md_content)

    meta_path = output_dir / "meta.tex"
    title_from_h1 = False
    if "title" not in meta:
        m = re.search(r"^#\s+(.+)$", md_content, re.M)
        if m:
            meta["title"] = m.group(1).strip()
            title_from_h1 = True

    # If the title came from the first H1, remove that H1 from the body
    # so the wrapper can print it once as the article header.
    if title_from_h1:
        md_content = re.sub(r"^#\s+.+$\n?", "", md_content, count=1, flags=re.M)

    body_path = output_dir / "body.md"
    body_path.write_text(md_content, encoding="utf-8")
    print(f"Created: {body_path}")

    def tex_escape(text):
        return (
            text.replace("\\", "\\textbackslash{}")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("$", "\\$")
            .replace("&", "\\&")
            .replace("#", "\\#")
            .replace("^", "\\^{}")
            .replace("_", "\\_")
            .replace("%", "\\%")
            .replace("~", "\\textasciitilde{}")
        )

    meta_lines = ["% Auto-generated post metadata"]
    for key, val in meta.items():
        cmd = "post" + key.capitalize()
        meta_lines.append(f"\\def\\{cmd}{{{tex_escape(val)}}}")
    meta_path.write_text("\n".join(meta_lines), encoding="utf-8")
    print(f"Created: {meta_path}")

    return body_path, meta_path, images_dir


def generate_wrapper(md_path, latex_dir, project_root):
    """Write the per-article LaTeX wrapper that pulls in the shared template."""
    stem = md_path.stem
    rel_root = os.path.relpath(project_root, latex_dir).replace("\\", "/")
    wrapper = f"""% !TeX program = xelatex
% Auto-generated LaTeX wrapper for {md_path.name} -- do not edit.
% Regenerate with: python scripts/gen_a4_latex.py {md_path.as_posix()}
% The wrapper is compiled from inside this directory (see generator).

\\documentclass[twocolumn]{{article}}
\\usepackage[a4paper, margin=1.2cm]{{geometry}}

\\def\\poststem{{{stem}}}
\\def\\postlayout{{a4}}
\\def\\posttwocolumn{{1}}

\\input{{{rel_root}/scripts/gen_a4_latex}}

\\def\\postimagedir{{images/}}

\\begin{{document}}

\\input{{meta.tex}}

\\ifdefined\\posttitle
  \\begin{{center}}
    {{\\LARGE\\posttitle}}\\par
    \\ifdefined\\postauthor
      {{\\small by \\postauthor\\par}}
    \\fi
    \\ifdefined\\postdate
      {{\\small\\postdate\\par}}
    \\fi
  \\end{{center}}
  \\vspace{{0.5em}}
\\fi

\\postmarkdowninput{{body.md}}

\\end{{document}}
"""
    wrapper_path = latex_dir / f"{stem}.tex"
    wrapper_path.write_text(wrapper, encoding="utf-8")
    print(f"Created: {wrapper_path}")
    return wrapper_path


def compile_xelatex(wrapper_path, pdf_dir, project_root, jpg_pattern):
    """Compile from the staging dir, then move the PDF and convert to JPGs.

    xelatex is run with cwd = the wrapper's directory: the markdown package's
    Lua bridge is written next to the PDF there and executed relative to it,
    which breaks if we redirect the output to another directory.
    """
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
        description="Render a post/ markdown file to A4 double-column LaTeX PDF."
    )
    parser.add_argument("path", help="Path to the markdown file")
    args = parser.parse_args()

    md_path = resolve_path(args.path)
    if not md_path.exists():
        sys.exit(f"Error: File not found: {md_path}")

    content_dir = md_path.parent
    project_root = Path(__file__).resolve().parent.parent
    latex_dir = content_dir / "_output" / "latex" / md_path.stem
    latex_dir.mkdir(parents=True, exist_ok=True)
    pdfs_dir = content_dir / "_output" / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    process_markdown(md_path, latex_dir)
    wrapper_path = generate_wrapper(md_path, latex_dir, project_root)
    jpg_pattern = str(content_dir / "_output" / f"{md_path.stem}_p%02d.jpg")
    compile_xelatex(wrapper_path, pdfs_dir, project_root, jpg_pattern)
    return 0


if __name__ == "__main__":
    sys.exit(main())
