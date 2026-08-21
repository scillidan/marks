#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Compile LaTeX demo files under latex-demo/ into PDFs."""

import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
DEMO_DIR = PROJECT_ROOT / "latex-demo"

_ENGINE_RE = re.compile(
    r"^\s*%+\s*!TeX\s+program\s*=\s*(\S+)", re.MULTILINE | re.IGNORECASE
)
_DEMO_RE = re.compile(r"^.*-demo(-\d+)?\.tex$", re.IGNORECASE)


def check_dependencies():
    missing = []
    for engine in ("xelatex", "lualatex"):
        if not shutil.which(engine):
            missing.append(engine)
    if missing:
        sys.exit("Missing dependencies:\n  - " + "\n  - ".join(missing))


def detect_engine(tex_path):
    """Return the engine declared by a % !TeX program = ... directive, if any."""
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    m = _ENGINE_RE.search(text)
    if m:
        engine = m.group(1).lower()
        if engine in ("xelatex", "lualatex", "pdflatex"):
            return engine
    return "xelatex"


def compile_tex(tex_path, engine=None, fail_on_error=True):
    check_dependencies()
    tex_path = Path(tex_path).resolve()
    demo_dir = tex_path.parent
    pdfs_dir = demo_dir / "_output" / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    out_rel = pdfs_dir.relative_to(demo_dir).as_posix()

    engine = engine or detect_engine(tex_path)
    if not shutil.which(engine):
        if fail_on_error:
            sys.exit(f"Missing engine: {engine}")
        print(f"✗ {tex_path.name}: missing engine {engine}")
        return None

    pdf_path = pdfs_dir / f"{tex_path.stem}.pdf"

    # Run twice so references and indexes can settle.
    r = None
    for run in range(1, 3):
        r = subprocess.run(
            [
                engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "--shell-escape",
                f"-output-directory={out_rel}",
                tex_path.name,
            ],
            cwd=str(demo_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if r.returncode != 0:
            if fail_on_error:
                sys.exit(f"{engine} error (run {run}):\n{r.stdout or r.stderr}")
            print(f"✗ {tex_path.name}: {engine} failed (run {run})")
            return None

    if not pdf_path.exists():
        if fail_on_error:
            sys.exit(
                f"{engine} produced no PDF for {tex_path.name}:\n{r.stdout or r.stderr}"
            )
        print(f"✗ {tex_path.name}: {engine} produced no PDF")
        return None

    print(f"Created: {pdf_path}")
    return pdf_path


def compile_all(jobs=None):
    tex_files = sorted(
        p for p in DEMO_DIR.glob("*-demo*.tex") if _DEMO_RE.match(p.name)
    )
    if not tex_files:
        print("No .tex files to compile.")
        return
    jobs = jobs or (os.cpu_count() or 4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        results = list(ex.map(lambda p: compile_tex(p, fail_on_error=False), tex_files))
    ok = sum(1 for r in results if r is not None)
    print(f"Compiled {ok}/{len(tex_files)} demos ({len(tex_files) - ok} failed)")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--compile",
        default=None,
        help="Compile the demo for this stem or .tex path (writes latex-demo/_output/pdfs).",
    )
    parser.add_argument(
        "--compile-all",
        action="store_true",
        help="Compile every latex-demo/*-demo*.tex file (parallel).",
    )
    parser.add_argument(
        "--engine",
        choices=["xelatex", "lualatex", "pdflatex"],
        default=None,
        help="Override the LaTeX engine (default: auto-detect, else xelatex).",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=None,
        help="Parallel jobs for --compile-all (default: CPU count).",
    )
    args = parser.parse_args()

    if args.compile_all:
        compile_all(args.jobs)
        return

    if args.compile:
        arg = args.compile
        if Path(arg).suffix.lower() == ".tex":
            compile_target = Path(arg)
        else:
            compile_target = DEMO_DIR / f"{arg}.tex"
        if not compile_target.exists():
            sys.exit(f"✗ {compile_target} not found")
        compile_tex(compile_target, engine=args.engine)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
