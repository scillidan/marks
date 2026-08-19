#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Compile committed CTAN card files under ctan/ into PDFs and JPGs."""

import argparse
import concurrent.futures
import os
import subprocess
import sys
from pathlib import Path

from _common import check_dependencies, convert_to_jpg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()

IMAGE_DIR_ENV = "CTAN_SOURCE"
IMAGE_DIR_FALLBACK = PROJECT_ROOT / "ctan" / "assets"


def resolve_image_dir():
    env = os.environ.get(IMAGE_DIR_ENV)
    if env:
        path = Path(os.path.expandvars(env).strip())
        if path.is_dir():
            print(f"✓ Image dir (env {IMAGE_DIR_ENV}): {path}")
            return path
        print(f"✗ {IMAGE_DIR_ENV}: {env} (not found)")
    if IMAGE_DIR_FALLBACK.is_dir():
        print(f"✓ Image dir (fallback): {IMAGE_DIR_FALLBACK}")
        return IMAGE_DIR_FALLBACK
    return None


def compile_tex(tex_path, fail_on_error=True):
    check_dependencies()
    tex_path = tex_path.resolve()
    ctan_dir = tex_path.parent
    out_dir = ctan_dir / "_output"
    pdfs_dir = out_dir / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    out_rel = pdfs_dir.relative_to(ctan_dir).as_posix()

    image_dir = resolve_image_dir()
    if not image_dir:
        sys.exit(
            f"✗ Cannot resolve image dir. Set {IMAGE_DIR_ENV} or place images in {IMAGE_DIR_FALLBACK}"
        )

    image_stem = tex_path.stem
    image_path = image_dir / f"{image_stem}.jpg"
    if not image_path.exists():
        print(f"✗ {image_path.name} not found in {image_dir}; skipping compile")
        return None

    imgdir_path = out_dir / "imgdir.tex"
    imgdir_content = f"\\providecommand{{\\CDNImageDir}}{{{image_dir.as_posix().rstrip('/') + '/'}}}\n"
    if (
        not imgdir_path.exists()
        or imgdir_path.read_text(encoding="utf-8") != imgdir_content
    ):
        imgdir_path.write_text(imgdir_content, encoding="utf-8")

    r = subprocess.run(
        [
            "xelatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={out_rel}",
            tex_path.name,
        ],
        cwd=str(ctan_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    pdf_path = pdfs_dir / f"{tex_path.stem}.pdf"
    if r.returncode != 0 or not pdf_path.exists():
        if fail_on_error:
            sys.exit(f"xelatex error:\n{r.stdout or r.stderr}")
        print(f"✗ {tex_path.name}: xelatex failed")
        return None
    print(f"Created: {pdf_path}")

    for stale in out_dir.glob(f"{tex_path.stem}_p*.jpg"):
        stale.unlink(missing_ok=True)
    convert_to_jpg(str(pdf_path), str(out_dir / f"{tex_path.stem}_p%02d.jpg"))
    print(f"Created: {out_dir}/{tex_path.stem}_p*.jpg")
    return pdf_path


def compile_all(out_dir, jobs=None):
    tex_files = sorted(out_dir.glob("*.tex"))
    if not tex_files:
        print("No .tex files to compile.")
        return
    image_dir = resolve_image_dir()
    if not image_dir:
        sys.exit(f"✗ Cannot resolve image dir. Set {IMAGE_DIR_ENV}")
    imgdir = out_dir / "_output" / "imgdir.tex"
    imgdir.parent.mkdir(parents=True, exist_ok=True)
    imgdir.write_text(
        f"\\providecommand{{\\CDNImageDir}}{{{image_dir.as_posix().rstrip('/') + '/'}}}\n",
        encoding="utf-8",
    )
    jobs = jobs or (os.cpu_count() or 4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        results = list(ex.map(lambda p: compile_tex(p, fail_on_error=False), tex_files))
    ok = sum(1 for r in results if r is not None)
    print(
        f"Compiled {ok}/{len(tex_files)} cards ({len(tex_files) - ok} skipped/failed)"
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--out",
        default=str(PROJECT_ROOT / "ctan"),
        help="Directory containing the .tex cards (default: %(default)s)",
    )
    parser.add_argument(
        "--compile",
        default=None,
        help="Compile the card for this stem or .tex path (writes ctan/_output/pdfs).",
    )
    parser.add_argument(
        "--compile-all",
        action="store_true",
        help="Compile every ctan/*.tex card (parallel).",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=None,
        help="Parallel jobs for --compile-all (default: CPU count).",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)

    if args.compile_all:
        compile_all(out_dir, args.jobs)
        return

    if args.compile:
        arg = args.compile
        if Path(arg).suffix.lower() == ".tex":
            compile_target = Path(arg)
        else:
            compile_target = out_dir / f"{arg}.tex"
        if not compile_target.exists():
            sys.exit(f"✗ {compile_target} not found")
        compile_tex(compile_target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
