#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "beautifulsoup4>=4.12",
# ]
# ///
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from _common import check_dependencies, compile_typst, convert_to_jpg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def html_to_typst(html):
    soup = BeautifulSoup(html, "html.parser")
    for cls in ("und1", "und2"):
        for span in soup.find_all("span", class_=cls):
            span.replace_with(f"#{cls}[{span.get_text()}]")
    for a in soup.find_all("a"):
        a.replace_with(f'#link("{a.get("href", "")}")[{a.get_text()}]')

    text = soup.get_text().replace("\xa0", " ").strip()
    marker, ph = "\x00", []

    def save(m):
        ph.append(m.group(0))
        return f"{marker}{len(ph) - 1}{marker}"

    text = re.sub(r"#(?:und[12]\[[^\]]*\]|link\(\"[^\"]*\"\)\[[^\]]*\])", save, text)
    text = text.replace("(", "\\(").replace(")", "\\)")
    for i, s in enumerate(ph):
        text = text.replace(f"{marker}{i}{marker}", s)
    return text


def parse_slides(md_path):
    content = Path(md_path).read_text(encoding="utf-8")
    pat = re.compile(
        r'<a\s+href="([^"]*?)"[^>]*?data-sub-html="(.*?)"[^>]*?>\s*'
        r"<img\s[^>]*?/>\s*"
        r"</a>",
        re.DOTALL,
    )
    slides = []
    for href, cap in pat.findall(content):
        cap = cap.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        h4 = re.search(r"<h4>(.*?)</h4>", cap, re.DOTALL)
        p = re.search(r"<p>(.*?)</p>", cap, re.DOTALL)
        slides.append(
            {
                "href": href,
                "img": Path(href).name,
                "h4": html_to_typst(h4.group(1)) if h4 else "",
                "p": html_to_typst(p.group(1)) if p else "",
            }
        )
    return slides


def load_layout_overrides(output_dir):
    path = output_dir.parent / "layout.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"Error: cannot read layout.json: {e}")
    if not isinstance(data, dict):
        sys.exit("Error: layout.json must be a JSON object")
    return data


def generate_typ_files(slides, output_dir, force=False):
    typs_dir = output_dir / "_output" / "typs"
    typs_dir.mkdir(parents=True, exist_ok=True)

    overrides = load_layout_overrides(output_dir)
    subdir = output_dir.name

    created = skipped = updated = 0
    typ_paths = []
    for i, s in enumerate(slides):
        cap = f", caption: [{s['p']}]" if s["p"] else ""
        ov = overrides.get(f"{subdir}/{Path(s['img']).stem}", {})
        force_frac = ov.get("force-frac", 0.5)
        top = ov.get("top", 4)
        bottom = ov.get("bottom", 4)
        content = f"""#import "../../../../scripts/byya-nineveh-template.typ": *
#show: nineveh-layout.with(size: 8pt, top: {top}%, bottom: {bottom}%)

#align(center + horizon, oasis-align(
  force-frac: {force_frac},
  [#figure(image("../../assets/{s["img"]}"){cap})],
  [#figure(balance([{s["h4"] or s["p"]}]))],
))
"""
        typ_path = typs_dir / f"{i + 1:02d}_{Path(s['img']).stem}.typ"
        if typ_path.exists():
            if force and typ_path.read_text(encoding="utf-8") != content:
                typ_path.write_text(content, encoding="utf-8")
                updated += 1
            else:
                skipped += 1
        else:
            typ_path.write_text(content, encoding="utf-8")
            created += 1
        typ_paths.append(typ_path)

    print(
        f"  {created} created, {updated} updated, {skipped} skipped "
        f"({len(typ_paths)} total) in {typs_dir}"
    )
    return typ_paths


def copy_images(slides, output_dir, image_source):
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    found, missing = 0, []
    for s in slides:
        src = image_source / s["img"]
        if src.exists():
            dest = assets_dir / s["img"]
            if not dest.exists():
                shutil.copy2(src, dest)
            found += 1
        else:
            print(f"  ✗ [MISS] {s['img']}")
            missing.append(s["img"])

    if missing:
        print(f"✗ Images: {found} found, {len(missing)} missing")
    else:
        print(f"✓ Images: all {found} found")


def compile_all(typ_paths, output_dir):
    root = Path(__file__).resolve().parent.parent
    pdfs_dir = output_dir / "_output" / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    for typ_path in typ_paths:
        pdf_path = pdfs_dir / f"{typ_path.stem}.pdf"
        if not compile_typst(typ_path, pdf_path, root, fail_on_error=False):
            continue
        ok += 1
        if not convert_to_jpg(
            pdf_path,
            str(output_dir / "_output" / f"{typ_path.stem}_p%02d.jpg"),
            fail_on_error=False,
        ):
            print(f"  ✗ [JPG SKIP] {typ_path.name}")
    print(f"  {ok}/{len(typ_paths)} PDFs in {pdfs_dir}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("subdir")
    parser.add_argument("--source")
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing typ files when content differs",
    )
    args = parser.parse_args()

    check_dependencies()

    source = args.source or os.environ.get("BYYA_SITE_DOCS")
    if not source:
        sys.exit("Error: set BYYA_SITE_DOCS env, or use --source")
    source_dir = Path(os.path.expandvars(source))
    if not source_dir.exists():
        sys.exit(f"Error: source dir not found: {source_dir}")

    md_path = source_dir / args.subdir / "_index.md"
    if not md_path.exists():
        sys.exit(f"Error: _index.md not found: {md_path}")

    images_env = os.environ.get("BYYA_NINEVEH_IMAGES")
    image_source = (
        Path(os.path.expandvars(images_env))
        if images_env
        else source_dir / args.subdir / args.subdir
    )
    if not image_source.exists():
        sys.exit(f"Error: image dir not found: {image_source}")

    output_dir = Path(__file__).resolve().parent.parent / "byya-nineveh" / args.subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parsing: {md_path}")
    slides = parse_slides(md_path)
    print(f"  {len(slides)} slides found")

    print(f"\nCopying images from: {image_source}")
    copy_images(slides, output_dir, image_source)

    print("\nGenerating Typst files...")
    typ_paths = generate_typ_files(slides, output_dir, force=args.force)

    print("\nCompiling PDFs...")
    compile_all(typ_paths, output_dir)

    print(f"\nDone: {output_dir / '_output' / 'pdfs'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
