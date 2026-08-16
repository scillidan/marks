#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Sync byya-lyra markdown sources from a BYYA-site checkout.

The .md files live in the upstream BYYA-site repo under
content.zh/docs/<subdir>/ and are treated as intermediate build inputs:
they are not committed to this repo. This script copies them into
byya-lyra/<subdir>/ with a zero-padded NNN_ prefix derived from each
file's frontmatter `weight` (ascending, renumbered contiguously from 1).

Usage:
    uv run scripts/sync_byya_lyra_md.py --source <BYYA-site>/content.zh/docs
"""

import argparse
import io
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SUBDIRS = ["lyra-a", "lyra-b", "orion-a"]
SKIP = {"_index.md", "annex.md"}

_WEIGHT_RE = re.compile(r"^weight:\s*(\d+)\s*$", re.MULTILINE)
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def read_weight(path: Path) -> int:
    """Return the frontmatter `weight` of a markdown file (0 if absent)."""
    try:
        text = io.open(path, encoding="utf-8").read()
    except OSError:
        return 0
    m = _FM_RE.search(text)
    if not m:
        return 0
    wm = _WEIGHT_RE.search(m.group(1))
    return int(wm.group(1)) if wm else 0


def strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block and its trailing blank line.

    Sorting is already encoded in the NNN_ filename prefix, so the frontmatter
    (e.g. `weight`) is dropped from the synced copies.
    """
    m = _FM_RE.match(text)
    if not m:
        return text
    return text[m.end() :].lstrip("\r\n")


def sync_subdir(source_root: Path, subdir: str, dest_root: Path) -> int:
    src_dir = source_root / subdir
    if not src_dir.is_dir():
        print(f"[{subdir}] SKIP: source not found: {src_dir}", file=sys.stderr)
        return 0

    entries = []
    for name in os.listdir(src_dir):
        if not name.endswith(".md") or name in SKIP:
            continue
        entries.append((read_weight(src_dir / name), name))
    entries.sort(key=lambda t: t[0])

    dest_dir = dest_root / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for i, (_, name) in enumerate(entries, 1):
        dest = dest_dir / f"{i:03d}_{name}"
        text = io.open(src_dir / name, encoding="utf-8").read()
        dest.write_text(strip_frontmatter(text), encoding="utf-8")
        copied += 1
    print(f"[{subdir}] copied {copied} markdown files to {dest_dir}")
    return copied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        help="Path to the BYYA-site content.zh/docs directory "
        "(env var may contain %VAR% expansion)",
    )
    args = parser.parse_args()

    source = args.source or os.environ.get("BYYA_SITE_DOCS")
    if not source:
        sys.exit("Error: set --source or BYYA_SITE_DOCS")
    source_root = Path(os.path.expandvars(source))
    if not source_root.is_dir():
        sys.exit(f"Error: source dir not found: {source_root}")

    dest_root = Path(__file__).resolve().parent.parent / "byya-lyra"
    total = 0
    for subdir in SUBDIRS:
        total += sync_subdir(source_root, subdir, dest_root)
    print(f"\nDone: {total} markdown files synced to {dest_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
