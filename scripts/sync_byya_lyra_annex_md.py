#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Sync BYYA-site lyra-a/annex.md into individual byya-lyra-annex .md files.

The generated .md files are intermediate build inputs: they are not committed
and are regenerated on each CI run from the upstream BYYA-site source.
"""

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Windows reserved filename characters.
_RESERVED = r'<>:"/\|?*'


def sanitize_filename(name: str) -> str:
    # Collapse spaces around &.
    name = re.sub(r"\s*&\s*", "&", name)
    # Replace characters that are illegal in Windows filenames.
    for ch in _RESERVED:
        name = name.replace(ch, "-")
    # Also map fullwidth colon just in case.
    name = name.replace("：", "-")
    # Drop trailing spaces / dots which Windows rejects.
    return name.rstrip(" .")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        help="Path to the BYYA-site content.zh/docs/lyra-a/annex.md file",
    )
    parser.add_argument(
        "--target",
        help="Directory to write the generated .md files (default: byya-lyra-annex)",
    )
    args = parser.parse_args()

    source = Path(args.source) if args.source else None
    if not source:
        # Default: assume BYYA-site is a sibling of the marks repo root.
        repo_root = Path(__file__).resolve().parent.parent
        default = (
            repo_root.parent
            / "BYYA-site"
            / "content.zh"
            / "docs"
            / "lyra-a"
            / "annex.md"
        )
        if default.exists():
            source = default
    if not source or not source.exists():
        sys.exit(f"Error: source not found: {source}")

    target = (
        Path(args.target)
        if args.target
        else Path(__file__).resolve().parent.parent / "byya-lyra-annex"
    )
    target.mkdir(parents=True, exist_ok=True)

    text = source.read_text(encoding="utf-8")
    order_stems = []
    # Strip YAML frontmatter.
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].lstrip("\r\n")

    # Entries are separated by blank lines; each entry ends with `**Author**`.
    blocks = [blk.strip("\r\n") for blk in re.split(r"\n\s*\n", text) if blk.strip()]

    count = 0
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        last = lines[-1].strip()
        m = re.fullmatch(r"\*\*(.+)\*\*", last)
        if not m:
            print(
                f"Skipping block without bold author line: {last!r}",
                file=sys.stderr,
            )
            continue
        author = m.group(1).strip()
        quote_lines = [ln.rstrip() for ln in lines[:-1]]
        if quote_lines:
            quote_lines[-1] = f"{quote_lines[-1]} [{author}]"
        content = "\n".join(quote_lines)
        filename = sanitize_filename(author) + ".md"
        (target / filename).write_text(content + "\n", encoding="utf-8")
        order_stems.append(Path(filename).stem)
        count += 1

    (target / "annex-order.txt").write_text(
        "\n".join(order_stems) + "\n", encoding="utf-8"
    )
    print(f"Synced {count} lyra annex markdown files to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
