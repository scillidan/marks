#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Generate shortcut cheatsheets.

Discovers .cht files under SHORTCUT_SOURCE and builds landscape-A4 aggregate
PDFs, flowing all content in N columns (top-to-bottom, left-to-right). A narrow
per-software PDF (receipt style) is also produced for every selected file.

Selection
---------
* No --include/--exclude: every .cht found recursively under SHORTCUT_SOURCE is
  selected. One aggregate PDF is produced per top-level directory, named
  ``<directory>.pdf``.
* --include SPEC ...: the default "print all" output is replaced by a single
  aggregate PDF built only from the matched files, named after the include
  specs (e.g. ``--include neovim`` -> ``neovim.pdf``; multiple specs are joined
  with ``_``).
* --exclude SPEC ...: removes matched files from the selection (applied on top
  of --include when both are given, otherwise on the full recursive set).

SPEC is either a .cht stem / relative path (e.g. ``neovim``, ``shortcut/vim``)
or a directory with a trailing slash (e.g. ``shortcut/``, ``shortcut_dev/``).

Dialects
--------
``--style default`` (the default) parses the common ``Software: description | key``
and ``Software:: plugin: description | key`` format, treats ``(<Text>)`` as a group
name, and defaults to **5 columns**.

``--style neovim`` parses the heading-grouped format: ``## <Group>`` headings
(not URLs) define groups, the software prefix is stripped, ``(<Text>)`` is *not*
treated as a group, and the layout defaults to **4 columns**.

Use ``--columns N`` to override the default column count for either style.
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


@dataclass(frozen=True)
class Style:
    """A .cht dialect.

    Keeping each behavioural difference as a field (rather than branching on a
    filename) lets ``--style`` presets be added or granularized later without
    touching the parser.
    """

    name: str
    columns: int
    heading_groups: bool  # "## <Group>" headings define groups
    paren_group: bool  # "(<Text>)" at the start of a field is a group name
    group_by_group_only: bool  # group rows by group alone (not plugin+group)
    initial_group: str | None


DEFAULT = Style(
    name="default",
    columns=5,
    heading_groups=False,
    paren_group=True,
    group_by_group_only=False,
    initial_group=None,
)
NEOVIM = Style(
    name="neovim",
    columns=4,
    heading_groups=True,
    paren_group=False,
    group_by_group_only=True,
    initial_group="General",
)
STYLES: dict[str, Style] = {"default": DEFAULT, "neovim": NEOVIM}
STYLE_CHOICES = [*STYLES]


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


def parse_line(line: str, current_group: str | None, style: Style) -> Entry | None:
    """Parse a single non-comment .cht line into an Entry."""
    split = _split_desc_key(line)
    if split is None:
        return None

    desc_part, key_part = split
    key = key_part.replace(r"\|", "|").replace(r"\\", "\\")

    software = ""
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
        if style.paren_group and rest.startswith("(") and ")" in rest:
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
        # Lines with no colon: either "Software (Group) description | key"
        # (e.g. envx) or just "description | key" (e.g. cxt, gh-notify).
        match = re.match(r"^(\S+)\s+\(([^)]*)\)\s+(.+)$", desc_part)
        if match:
            software = match.group(1)
            group = match.group(2).strip()
            description = match.group(3).strip()
        else:
            description = desc_part.strip()

    software = software.strip()
    plugin = plugin.strip() if plugin else None
    # A trailing colon is usually a separator left over from the source syntax,
    # not part of the plugin name (e.g. "save-playlist:").
    plugin = plugin.removesuffix(":") if plugin else None
    description = description.strip()

    if style.heading_groups:
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


def parse_cht(path: Path, style: Style) -> list[Entry]:
    """Parse a .cht file, returning entries in file order."""
    entries: list[Entry] = []
    current_group = style.initial_group

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.startswith("#"):
            if style.heading_groups and line.startswith("## "):
                body = line[3:].strip()
                if "/" not in body and "\\" not in body:
                    current_group = body
            continue

        entry = parse_line(line, current_group, style)
        if entry:
            entries.append(entry)

    return entries


def group_entries(entries: list[Entry], style: Style) -> list[Group]:
    """Group entries preserving first-seen order."""
    groups: list[Group] = []
    index: dict[tuple[str | None, str | None], int] = {}

    for entry in entries:
        key = (
            (None, entry.group)
            if style.group_by_group_only
            else (entry.plugin, entry.group)
        )
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


def emit_software_content(name: str, groups: list[Group], style: Style) -> str:
    lines: list[str] = []
    lines.append(f"= {typst_escape(name)}")
    lines.append("#divider()")

    for g in groups:
        if style.group_by_group_only:
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

        if style.group_by_group_only:
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
    name: str, groups: list[Group], style: Style, typ_path: Path
) -> Path:
    typ_path.parent.mkdir(parents=True, exist_ok=True)
    content = emit_software_content(name, groups, style)
    text = f'''#import "{SOFTWARE_TEMPLATE}": *
#show: shortcut-software-layout

{content}
'''
    typ_path.write_text(text, encoding="utf-8")
    return typ_path


def generate_category_typ(
    category: str,
    software_groups: list[tuple[str, list[Group], Style]],
    columns: int,
    typ_path: Path,
) -> Path:
    typ_path.parent.mkdir(parents=True, exist_ok=True)
    parts: list[str] = [
        f'#import "{CATEGORY_TEMPLATE}": *',
        f"#show: shortcut-category-layout.with(columns: {columns})",
        "",
    ]
    for name, groups, style in software_groups:
        parts.append(emit_software_content(name, groups, style))
        parts.append("")

    typ_path.write_text("\n".join(parts), encoding="utf-8")
    return typ_path


def discover_cht(source_dir: Path) -> list[Path]:
    """All .cht files under source_dir, recursive, sorted."""
    return sorted(p for p in source_dir.rglob("*.cht") if p.is_file())


def spec_matches(spec: str, rel: Path) -> bool:
    """Match a --include/--exclude SPEC against a source-relative .cht path."""
    s = spec.replace("\\", "/").strip()
    if not s:
        return False
    posix = rel.as_posix()
    if s.endswith("/"):
        prefix = s.rstrip("/")
        return posix.startswith(prefix + "/")
    if "/" in s:
        stem = s.removesuffix(".cht")
        return posix == f"{stem}.cht"
    stem = s.removesuffix(".cht")
    return rel.stem == stem


def select_files(
    source_dir: Path, includes: list[str], excludes: list[str]
) -> list[Path]:
    """Resolve the selected .cht files (include order preserved)."""
    all_files = discover_cht(source_dir)
    if includes:
        selected: list[Path] = []
        seen: set[Path] = set()
        for spec in includes:
            for path in all_files:
                if path in seen:
                    continue
                if spec_matches(spec, path.relative_to(source_dir)):
                    selected.append(path)
                    seen.add(path)
    else:
        selected = list(all_files)

    if excludes:
        selected = [
            path
            for path in selected
            if not any(
                spec_matches(spec, path.relative_to(source_dir)) for spec in excludes
            )
        ]
    return selected


def _sanitize_name(spec: str) -> str:
    s = spec.replace("\\", "/").strip().rstrip("/")
    return s.replace("/", "-") or "shortcut"


def output_groups(
    selected: list[Path], source_dir: Path, includes: list[str]
) -> list[tuple[str, list[Path]]]:
    """Split the selection into (output-name, files) aggregate groups."""
    if includes:
        name = "_".join(_sanitize_name(spec) for spec in includes)
        return [(name, selected)]

    grouped: dict[str, list[Path]] = {}
    for path in selected:
        rel = path.relative_to(source_dir)
        top = rel.parts[0] if len(rel.parts) > 1 else source_dir.name
        grouped.setdefault(top, []).append(path)
    return [(name, grouped[name]) for name in sorted(grouped)]


def resolve_columns(style_arg: str, override: int | None) -> int:
    if override is not None:
        return override
    return STYLES[style_arg].columns


def confirm_overwrite(path: Path) -> bool:
    try:
        answer = input(f"Output exists: {path}\nOverwrite? (y/N) ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer.startswith("y")


def process_group(
    name: str,
    files: list[Path],
    source_dir: Path,
    project_root: Path,
    style_arg: str,
    columns_override: int | None,
    force: bool,
) -> None:
    output_dir = project_root / "shortcut" / "_output"
    typs_dir = output_dir / "typs"
    per_software_dir = output_dir / "_temp"

    style = STYLES[style_arg]
    software_groups: list[tuple[str, list[Group], Style]] = []
    for cht in files:
        entries = parse_cht(cht, style)
        if not entries:
            continue
        groups = group_entries(entries, style)
        software_groups.append((cht.stem, groups, style))

        # Per-software narrow PDF (receipt style).
        rel = cht.relative_to(source_dir)
        sw_typ = typs_dir / rel.parent / f"{cht.stem}.typ"
        generate_software_typ(cht.stem, groups, style, sw_typ)
        sw_pdf = per_software_dir / rel.parent / f"{cht.stem}.pdf"
        sw_pdf.parent.mkdir(parents=True, exist_ok=True)
        compile_typst(sw_typ, sw_pdf, project_root)

    if not software_groups:
        print(f"Warning: no entries parsed for {name}", file=sys.stderr)
        return

    columns = resolve_columns(style_arg, columns_override)
    cat_typ = typs_dir / f"{name}.typ"
    generate_category_typ(name, software_groups, columns, cat_typ)
    print(f"Created: {cat_typ}")
    cat_pdf = output_dir / "pdfs" / f"{name}.pdf"
    cat_pdf.parent.mkdir(parents=True, exist_ok=True)
    if cat_pdf.exists() and not force and not confirm_overwrite(cat_pdf):
        print(f"Skipped: {cat_pdf}")
        return
    compile_typst(cat_typ, cat_pdf, project_root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate shortcut cheatsheets from .cht files."
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="SPEC",
        help="Only build these .cht files (stem/path) or directories ('dir/'). "
        "Repeatable; merges into one PDF named after the specs.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="SPEC",
        help="Remove .cht files/directories from the selection. Repeatable.",
    )
    parser.add_argument(
        "--style",
        choices=STYLE_CHOICES,
        default="default",
        help=".cht dialect to use: 'default' (plain, 5 cols) or 'neovim' (4 cols).",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=None,
        help="Column count for aggregate PDFs (default: from --style).",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing aggregate PDFs without prompting.",
    )
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        metavar="NAME",
        help="Deprecated alias for '--include NAME/'.",
    )
    args = parser.parse_args()

    includes = list(args.include)
    for category in args.category:
        includes.append(f"{category}/")

    check_dependencies()

    project_root = Path(__file__).resolve().parent.parent
    env = load_env(project_root / ".env")
    source_str = env.get("SHORTCUT_SOURCE")
    if not source_str:
        sys.exit("Error: SHORTCUT_SOURCE is not set in .env")

    source_dir = resolve_path(source_str)
    if not source_dir.exists():
        sys.exit(f"Error: SHORTCUT_SOURCE directory not found: {source_dir}")

    selected = select_files(source_dir, includes, args.exclude)
    if not selected:
        sys.exit("Error: no .cht files matched the given --include/--exclude filters")

    for name, files in output_groups(selected, source_dir, includes):
        process_group(
            name,
            files,
            source_dir,
            project_root,
            args.style,
            args.columns,
            args.force,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
