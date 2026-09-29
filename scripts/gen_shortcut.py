#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Generate shortcut cheatsheets.

For every .cht file in SHORTCUT_SOURCE/shortcut*/:
  1. Build a narrow per-software PDF (A4/4 width, auto height, receipt style).
  2. Build one final landscape-A4 PDF for the category, flowing all software
     content in 4 columns (top-to-bottom, left-to-right).

One final PDF is produced per category (shortcut, shortcut_dev, ...).
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from _common import check_dependencies, compile_typst, resolve_path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SOFTWARE_TEMPLATE = Path("/scripts/shortcut-software-template.typ").as_posix()
CATEGORY_TEMPLATE = Path("/scripts/shortcut-category-template.typ").as_posix()

CATEGORIES = ["shortcut", "shortcut_dev", "shortcut_windows", "shortcut_arch"]

# Characters that must be escaped inside Typst content brackets.
_TYPST_SPECIAL = {
    "\\": "\\\\",
    "[": "\\[",
    "]": "\\]",
    "#": "\\#",
    "*": "\\*",
    "_": "\\_",
    "`": "\\`",
    "$": "\\$",
    "<": "\\<",
    ">": "\\>",
    "/": "\\/",
    "-": "\\-",
    "+": "\\+",
}


@dataclass
class Entry:
    software: str
    plugin: str | None
    group: str | None
    description: str
    key: str


@dataclass
class Group:
    plugin: str | None
    group: str | None
    entries: list[Entry] = field(default_factory=list)


def load_env(path: Path) -> dict[str, str]:
    """Parse a simple .env file, expanding ${VAR} / %VAR% references."""
    env = dict(os.environ)
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = _strip_quotes(value)
        value = _expand_vars(value, {**env, **result})
        result[key] = value
    return result


def _strip_quotes(text: str) -> str:
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        return text[1:-1]
    return text


def _expand_vars(text: str, env: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        var = match.group(1) or match.group(2)
        return env.get(var, match.group(0))

    return re.sub(r"\$\{([^}]+)\}|%([^%]+)%", repl, text)


def typst_escape(text: str) -> str:
    return "".join(_TYPST_SPECIAL.get(ch, ch) for ch in text)


def _split_desc_key(line: str) -> tuple[str, str] | None:
    """Split a line on the last unescaped '|', returning (desc, key)."""
    for i in range(len(line) - 1, -1, -1):
        if line[i] == "|" and (i == 0 or line[i - 1] != "\\"):
            return line[:i].rstrip(), line[i + 1 :].lstrip()
    return None


def parse_line(line: str, current_group: str | None, is_neovim: bool) -> Entry | None:
    """Parse a single non-comment .cht line into an Entry."""
    split = _split_desc_key(line)
    if split is None:
        return None

    desc_part, key_part = split
    key = key_part.replace(r"\|", "|").replace(r"\\", "\\")

    plugin: str | None = None
    group: str | None = None
    description = ""
    if ":: " in desc_part:
        software, rest = desc_part.split(":: ", 1)
        rest = rest.strip()
        # Some files (e.g. mpv) put the group before the plugin:
        #   Software:: (<group>) Plugin: description
        #   Software:: (<group>) Plugin            (no description)
        #   Software:: (<group>)                   (group only)
        if rest.startswith("(") and ")" in rest:
            close = rest.find(")")
            group = rest[1:close].strip()
            rest = rest[close + 1 :].strip()

        if rest:
            if ": " in rest:
                plugin, description = rest.split(": ", 1)
            else:
                plugin = rest
                description = ""
        else:
            plugin = None
            description = ""
    elif ": " in desc_part:
        software, description = desc_part.split(": ", 1)
    else:
        return None

    software = software.strip()
    plugin = plugin.strip() if plugin else None
    # A trailing colon is usually a separator left over from the source syntax,
    # not part of the plugin name (e.g. "save-playlist:").
    plugin = plugin.removesuffix(":") if plugin else None
    description = description.strip()

    if is_neovim:
        group = current_group
    else:
        if group is None and description.startswith("(") and ")" in description:
            close = description.find(")")
            group = description[1:close].strip()
            description = description[close + 1 :].strip()

    # Fallback: if a row has a key but no description, use the most specific
    # label available (plugin first, then group) so the table cell is not blank.
    if not description:
        if plugin:
            description = plugin
        elif group:
            description = group

    if not key or (not description and not key):
        return None

    return Entry(software, plugin, group, description, key)


def parse_cht(path: Path) -> tuple[list[Entry], bool]:
    """Parse a .cht file, returning entries in file order and a neovim flag."""
    is_neovim = path.stem.lower() == "neovim"
    entries: list[Entry] = []
    current_group: str | None = "General" if is_neovim else None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue

        if is_neovim:
            if line.startswith("## "):
                body = line[3:].strip()
                if "/" not in body and "\\" not in body:
                    current_group = body
                continue
        else:
            if line.startswith("#"):
                continue

        entry = parse_line(line, current_group, is_neovim)
        if entry:
            entries.append(entry)

    return entries, is_neovim


def group_entries(entries: list[Entry], is_neovim: bool) -> list[Group]:
    """Group entries preserving first-seen order."""
    groups: list[Group] = []
    index: dict[tuple[str | None, str | None], int] = {}

    for entry in entries:
        key = (None, entry.group) if is_neovim else (entry.plugin, entry.group)
        if key not in index:
            groups.append(Group(plugin=entry.plugin, group=entry.group))
            index[key] = len(groups) - 1
        groups[index[key]].entries.append(entry)

    return groups


def emit_table(rows: list[tuple[str, str]]) -> str:
    lines = [
        "#table(stroke: none, inset: 2pt, row-gutter: 1.5pt, column-gutter: 4pt, align: left, columns: 2,"
    ]
    for i, (desc, key) in enumerate(rows):
        comma = "," if i < len(rows) - 1 else ""
        lines.append(f"\t[{typst_escape(desc)}], [{typst_escape(key)}]{comma}")
    lines.append(")")
    return "\n".join(lines)


def emit_software_content(name: str, groups: list[Group], is_neovim: bool) -> str:
    lines: list[str] = []
    lines.append(f"= {typst_escape(name)}")
    lines.append("#divider()")

    for g in groups:
        if is_neovim:
            header = f"[{typst_escape(g.group)}]" if g.group else ""
        else:
            header = ""
            if g.plugin and g.group:
                header = f"[{typst_escape(g.plugin)}][{typst_escape(g.group)}]"
            elif g.plugin:
                header = f"[{typst_escape(g.plugin)}]"
            elif g.group:
                header = f"[{typst_escape(g.group)}]"

        if header:
            lines.append("")
            lines.append("#v(.4em)")
            lines.append(header)

        if is_neovim:
            rows = [
                (
                    f"{e.plugin}: {e.description}" if e.plugin else e.description,
                    e.key,
                )
                for e in g.entries
            ]
        else:
            rows = [(e.description, e.key) for e in g.entries]
        lines.append(emit_table(rows))

    return "\n".join(lines)


def generate_software_typ(
    name: str, groups: list[Group], is_neovim: bool, typ_path: Path
) -> Path:
    typ_path.parent.mkdir(parents=True, exist_ok=True)
    content = emit_software_content(name, groups, is_neovim)
    text = f'''#import "{SOFTWARE_TEMPLATE}": *
#show: shortcut-software-layout

{content}
'''
    typ_path.write_text(text, encoding="utf-8")
    return typ_path


def generate_category_typ(
    category: str,
    software_groups: list[tuple[str, list[Group], bool]],
    typ_path: Path,
) -> Path:
    typ_path.parent.mkdir(parents=True, exist_ok=True)
    parts: list[str] = [
        f'#import "{CATEGORY_TEMPLATE}": *',
        "#show: shortcut-category-layout",
        "",
    ]
    for name, groups, is_neovim in software_groups:
        parts.append(emit_software_content(name, groups, is_neovim))
        parts.append("")

    typ_path.write_text("\n".join(parts), encoding="utf-8")
    return typ_path


def process_category(source_dir: Path, category: str, project_root: Path) -> None:
    cat_dir = source_dir / category
    if not cat_dir.exists():
        print(f"Warning: source directory not found: {cat_dir}", file=sys.stderr)
        return

    cht_files = sorted(p for p in cat_dir.iterdir() if p.suffix == ".cht")
    if not cht_files:
        print(f"Warning: no .cht files in {cat_dir}", file=sys.stderr)
        return

    output_dir = project_root / "shortcut" / "_output"
    typs_dir = output_dir / "typs" / category
    per_software_dir = output_dir / "per-software-pdfs" / category

    software_groups: list[tuple[str, list[Group], bool]] = []
    for cht in cht_files:
        entries, is_neovim = parse_cht(cht)
        if not entries:
            continue
        groups = group_entries(entries, is_neovim)
        software_groups.append((cht.stem, groups, is_neovim))

        # Per-software narrow PDF (receipt style).
        sw_typ = typs_dir / f"{cht.stem}.typ"
        generate_software_typ(cht.stem, groups, is_neovim, sw_typ)
        print(f"Created: {sw_typ}")
        sw_pdf = per_software_dir / f"{cht.stem}.pdf"
        sw_pdf.parent.mkdir(parents=True, exist_ok=True)
        compile_typst(sw_typ, sw_pdf, project_root)

    if not software_groups:
        print(f"Warning: no entries parsed for {category}", file=sys.stderr)
        return

    # Final landscape A4 4-column PDF.
    cat_typ = typs_dir / f"{category}.typ"
    generate_category_typ(category, software_groups, cat_typ)
    print(f"Created: {cat_typ}")
    cat_pdf = output_dir / "pdfs" / f"{category}.pdf"
    cat_pdf.parent.mkdir(parents=True, exist_ok=True)
    compile_typst(cat_typ, cat_pdf, project_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--category", choices=CATEGORIES, help="Generate only one category"
    )
    args = parser.parse_args()

    check_dependencies()

    project_root = Path(__file__).resolve().parent.parent
    env = load_env(project_root / ".env")
    source_str = env.get("SHORTCUT_SOURCE")
    if not source_str:
        sys.exit("Error: SHORTCUT_SOURCE is not set in .env")

    source_dir = resolve_path(source_str)
    if not source_dir.exists():
        sys.exit(f"Error: SHORTCUT_SOURCE directory not found: {source_dir}")

    categories = [args.category] if args.category else CATEGORIES
    for category in categories:
        process_category(source_dir, category, project_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
