#!/usr/bin/env bash
# Build all PDFs for _site and generate manifest.json.
# Authors: Kimi-K2.7-Code🧙‍♂️, DeepSeek-V4-Flash🧙‍♂️, scillidan🤡
#
# Common commands:
#   ./_site/gen.sh                          build everything
#   ./_site/gen.sh --only entry              build only entry/
#   ./_site/gen.sh --only post --jobs 4     build post/ with 4 parallel jobs
#   ./_site/gen.sh --incremental            rebuild files changed in working tree
#   ./_site/gen.sh --incremental --dry-run  preview what would build without running

set -euo pipefail
# set -x  # uncomment for debugging

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Load optional .env for local overrides (e.g., GEN_EXCLUDE).
# Temporarily relax -u so variables like ${USERPROFILE} in .env don't error
# when sourced under bash.
if [[ -f ".env" ]]; then
	set +u
	set -a
	# shellcheck source=/dev/null
	source ".env"
	set +a
	set -u
fi

# Options
BUILD=1
ONLY=""
SKIP=""
JOBS=""
STRICT=0
INCREMENTAL=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
	case "$1" in
	--no-build)
		BUILD=0
		shift
		;;
	--only)
		ONLY="$2"
		shift 2
		;;
	--skip)
		SKIP="$2"
		shift 2
		;;
	--jobs | -j)
		JOBS="$2"
		shift 2
		;;
	--strict)
		STRICT=1
		shift
		;;
	--incremental)
		INCREMENTAL=1
		shift
		;;
	--dry-run)
		DRY_RUN=1
		shift
		;;
	*)
		echo "Unknown option: $1"
		exit 1
		;;
	esac
done

if [[ -n "$JOBS" ]]; then
	JUST_JOBS="--jobs $JOBS"
else
	JUST_JOBS=""
fi

# Detect Python
if command -v python3 >/dev/null 2>&1; then
	PYTHON=python3
elif command -v python >/dev/null 2>&1; then
	PYTHON=python
else
	echo "Error: python3 or python is required."
	exit 1
fi

# Build rules
#
# Format: "directory:maxdepth:glob:command_template:dependencies"
# maxdepth: 1 = top-level files only, 99 = recursive
# glob: filename pattern passed to find -name (e.g. *.md, *.typ)
# {path} in the template is replaced with the matched file path.
# {dir} is replaced with the directory name.
# dependencies: comma-separated list of paths; if any changed file matches one
#   of these prefixes, every file in this rule's directory is rebuilt.
# NOTE: byya-nineveh is handled separately below (its .typ files live under
# _output/typs/, which the main BUILD_RULES find loop prunes via -name _output).
BUILD_RULES=(
	"typst-demo:1:*-demo.typ:mkdir -p \$(dirname {path})/_output/pdfs && typst compile --root {dir} {path} \$(dirname {path})/_output/pdfs/\$(basename {path} .typ).pdf:typst-demo/assets,typst-demo/codly-template.typ,typst-demo/nineveh-template.typ,typst-demo/polario-frame-template.typ,typst-demo/receipt-template.typ,typst-demo/tooltip-template.typ"
	"latex-demo:1:*-demo.tex:just latex-demo {path}:scripts/gen_latex_demo.py,latex-demo/data"
	"post:99:*.md:just a4 {path}:scripts/gen_a4.py"
	"post_zh-cn:99:*.md:just a4 {path}:scripts/gen_a4.py"
	"chat:1:*.md:just a6 {path}:scripts/gen_a6.py"
	"entry:1:*.md:just a6 {path}:scripts/gen_a6.py"
	"part:1:*.md:just a6 {path}:scripts/gen_a6.py"
	"byya-nineveh-annex:1:*.md:just nineveh-annex {path}:scripts/gen_byya_nineveh_annex.py,scripts/byya-nineveh-annex-template.typ"
	"byya-lyra-annex:1:*.md:just lyra-annex {path}:scripts/gen_byya_lyra_annex.py,scripts/byya-lyra-annex-template.typ"
	"ctan-annex:1:*.md:just ctan-annex {path}:scripts/gen_ctan_annex.py,scripts/ctan-annex-template.typ"
	"receipt:1:*.typ:just receipt {path}:scripts/gen_a7_receipt.py,scripts/receipt-template.typ"
	"ctan:1:*.tex:just ctan {path}:scripts/gen_ctan.py"
)

# Paths to exclude from both PDF builds and the generated manifest.
# Each entry is a path prefix relative to the repo root (e.g., "chat/ctan/").
# Set via .env or environment variable:
#   GEN_EXCLUDE="chat/ctan/;post/laws-of-software-engineering/"
# Entries may be separated by spaces and/or semicolons:
#   GEN_EXCLUDE="chat/ctan/;post/laws-of-software-engineering/"
EXCLUDE_PATHS=()

# Merge any extra exclusions from .env / environment.
if [[ -n "${GEN_EXCLUDE:-}" ]]; then
	_extra_excludes=()
	if [[ "$GEN_EXCLUDE" == *";"* ]]; then
		IFS=';' read -ra _extra_excludes <<<"$GEN_EXCLUDE"
	else
		read -ra _extra_excludes <<<"$GEN_EXCLUDE"
	fi
	for _ex in "${_extra_excludes[@]}"; do
		_ex="${_ex#"${_ex%%[![:space:]]*}"}"
		_ex="${_ex%"${_ex##*[![:space:]]}"}"
		[[ -n "$_ex" ]] && EXCLUDE_PATHS+=("$_ex")
	done
	unset _extra_excludes _ex
fi

# Serialize EXCLUDE_PATHS for the Python manifest assembly step.
export _SITE_EXCLUDE_PATHS_JSON="$($PYTHON -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "${EXCLUDE_PATHS[@]}")"

# Dependencies that force a full rebuild of all rules when they change.
GLOBAL_DEPS=(
	".justfile"
	"scripts/_common.py"
	"scripts/gen_a6.py"
	"scripts/pdf_to_jpg.py"
)

# Incremental build: detect changed files
REBUILD_ALL=0
declare -A CHANGED_MAP

if [[ "$INCREMENTAL" -eq 1 ]]; then
	echo "Incremental build: detecting uncommitted changes..."
	mapfile -t CHANGED_FILES < <(
		git diff --name-only HEAD 2>/dev/null | sort -u || true
	)

	if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
		echo "No uncommitted changes detected."
		if [[ "$BUILD" -eq 1 && "$DRY_RUN" -eq 0 ]]; then
			echo "Nothing to build. Use --no-build to skip manifest regeneration."
		fi
	else
		echo "Changed files:"
		for f in "${CHANGED_FILES[@]}"; do
			echo "  - $f"
			CHANGED_MAP["$f"]=1
		done

		for f in "${CHANGED_FILES[@]}"; do
			for dep in "${GLOBAL_DEPS[@]}"; do
				if [[ "$f" == "$dep" || "$f" == "$dep/"* ]]; then
					echo "  Global dependency changed: $f -> rebuilding all outputs"
					REBUILD_ALL=1
					break 2
				fi
			done
		done
	fi
fi

# Helpers
should_process_dir() {
	local dir="$1"
	if [[ -n "$ONLY" && "$dir" != "$ONLY" ]]; then
		return 1
	fi
	if [[ -n "$SKIP" && "$dir" == "$SKIP" ]]; then
		return 1
	fi
	return 0
}

sanitize_log_name() {
	local s="$1"
	s="${s#./}"
	printf '%s' "$s" | sed 's/[^a-zA-Z0-9._-]/_/g; s/_\+/_/g; s/^_//; s/_$//'
}

is_excluded_path() {
	local path="$1"
	local exclude
	for exclude in "${EXCLUDE_PATHS[@]}"; do
		[[ -z "$exclude" ]] && continue
		exclude="${exclude%/}"
		if [[ "$path" == "$exclude" || "$path" == "$exclude/"* || "$path" == "/$exclude" || "$path" == "/$exclude/"* ]]; then
			return 0
		fi
	done
	return 1
}

LOG_DIR="$REPO_ROOT/_temp/build-_site-logs"
mkdir -p "$LOG_DIR"

run_just() {
	local cmd="$1"
	local log_file="$2"
	if [[ "$DRY_RUN" -eq 1 ]]; then
		echo "  [dry-run] $cmd"
		return 2
	fi
	echo "  $cmd"
	if eval "$cmd" 2>&1 | tee "$log_file"; then
		return 0
	else
		return 1
	fi
}

file_is_changed() {
	local file="$1"
	[[ -n "${CHANGED_MAP[$file]+x}" ]] && return 0
	return 1
}

changed_file_matches_any() {
	local prefixes_spec="$1"
	if [[ -z "$prefixes_spec" ]]; then
		return 1
	fi
	local prefixes=()
	IFS=',' read -ra prefixes <<<"$prefixes_spec"
	local prefix
	for prefix in "${prefixes[@]}"; do
		[[ -z "$prefix" ]] && continue
		for f in "${!CHANGED_MAP[@]}"; do
			if [[ "$f" == "$prefix" || "$f" == "$prefix/"* ]]; then
				return 0
			fi
		done
	done
	return 1
}

any_changed_under() {
	local prefix="$1"
	[[ "$REBUILD_ALL" -eq 1 ]] && return 0
	for f in "${!CHANGED_MAP[@]}"; do
		if [[ "$f" == "$prefix"* ]]; then
			return 0
		fi
	done
	return 1
}

TOTAL_BUILT=0
TOTAL_FAILED=0
TOTAL_SKIPPED=0
FAILED_ITEMS=()
FAILED_CMDS=()
FAILED_LOGS=()

# Build PDFs
if [[ "$BUILD" -eq 1 ]]; then
	echo "Building PDFs..."
	for rule in "${BUILD_RULES[@]}"; do
		# The template may contain colons, so read the fixed leading fields
		# explicitly and leave the remainder as template+deps.
		IFS=':' read -r dir maxdepth glob rest <<<"$rule"
		template="${rest%%:*}"
		deps="${rest#*:}"
		if [[ "$deps" == "$template" ]]; then
			deps=""
		fi

		if ! should_process_dir "$dir"; then
			continue
		fi

		if [[ ! -d "$dir" ]]; then
			echo "Skipping missing directory: $dir"
			continue
		fi

		local_rule_rebuild=0
		if [[ "$INCREMENTAL" -eq 1 && "$REBUILD_ALL" -eq 0 && -n "$deps" ]] && changed_file_matches_any "$deps"; then
			echo "  Rule dependency changed -> rebuilding all [$dir] files"
			local_rule_rebuild=1
		fi

		echo "[$dir] maxdepth=$maxdepth $glob -> $template"

		# Find matching files, excluding generated dirs.
		mapfile -t files < <(
			find "$dir" -maxdepth "$maxdepth" \
				-type d \( -name _output -o -name _temp -o -name .git \) -prune -o \
				-type f -name "$glob" -print | sort
		)

		if [[ ${#files[@]} -eq 0 ]]; then
			echo "  No files matched."
			continue
		fi

		for file in "${files[@]}"; do
			if is_excluded_path "$file"; then
				echo "  EXCLUDE: $file"
				continue
			fi

			if [[ "$INCREMENTAL" -eq 1 && "$REBUILD_ALL" -eq 0 && "$local_rule_rebuild" -eq 0 ]] && ! file_is_changed "$file"; then
				echo "  SKIP (unchanged): $file"
				TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
				continue
			fi

			# Use Python for placeholder substitution so filenames containing '&'
			# are not misinterpreted by bash parameter expansion. Force UTF-8
			# output so non-ASCII paths survive on Windows consoles.
			cmd="$(PYTHONIOENCODING=utf-8 "$PYTHON" -c 'import sys; sys.stdout.reconfigure(encoding="utf-8"); t=sys.argv[1]; p=sys.argv[2]; print(t.replace("{path}", p))' "$template" "\"$file\"")"
			cmd="$(PYTHONIOENCODING=utf-8 "$PYTHON" -c 'import sys; sys.stdout.reconfigure(encoding="utf-8"); t=sys.argv[1]; d=sys.argv[2]; print(t.replace("{dir}", d))' "$cmd" "\"$dir\"")"
			log_file="$LOG_DIR/$(sanitize_log_name "$file").log"
			status=0
			run_just "$cmd $JUST_JOBS" "$log_file" || status=$?
			if [[ $status -eq 0 ]]; then
				TOTAL_BUILT=$((TOTAL_BUILT + 1))
				rm -f "$log_file"
			elif [[ $status -eq 2 ]]; then
				: # dry-run: do not count, no log created
			else
				TOTAL_FAILED=$((TOTAL_FAILED + 1))
				FAILED_ITEMS+=("$file")
				FAILED_CMDS+=("$cmd $JUST_JOBS")
				FAILED_LOGS+=("$log_file")
				echo "  FAILED: $file"
			fi
		done
	done

	# byya-nineveh: compile only per-item files under _output/typs/.
	# Top-level <subdir>/<subdir>.typ collection overviews are excluded.
	if should_process_dir "byya-nineveh" && [[ -d "byya-nineveh" ]]; then
		echo "[byya-nineveh] Compiling .typ files..."
		mapfile -t files < <(
			find byya-nineveh -type f -path "*/_output/typs/*.typ" \
				! -path "*/_temp/*" \
				! -path "*/.git/*" | sort
		)
		if [[ ${#files[@]} -eq 0 ]]; then
			echo "  No .typ files found under byya-nineveh/."
		else
			local_rule_rebuild=0
			if [[ "$INCREMENTAL" -eq 1 && "$REBUILD_ALL" -eq 0 ]] && changed_file_matches_any "scripts/gen_byya_nineveh_typ.py,scripts/byya-nineveh-template.typ"; then
				echo "  Dependency changed -> rebuilding all byya-nineveh .typ files"
				local_rule_rebuild=1
			fi
			for file in "${files[@]}"; do
				if is_excluded_path "$file"; then
					echo "  EXCLUDE: $file"
					continue
				fi
				if [[ "$INCREMENTAL" -eq 1 && "$REBUILD_ALL" -eq 0 && "$local_rule_rebuild" -eq 0 ]] && ! file_is_changed "$file"; then
					echo "  SKIP (unchanged): $file"
					TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
					continue
				fi
				cmd="just nineveh-typ \"$file\""
				log_file="$LOG_DIR/$(sanitize_log_name "$file").log"
				status=0
				run_just "$cmd" "$log_file" || status=$?
				if [[ $status -eq 0 ]]; then
					TOTAL_BUILT=$((TOTAL_BUILT + 1))
					rm -f "$log_file"
				elif [[ $status -eq 2 ]]; then
					: # dry-run: do not count, no log created
				else
					TOTAL_FAILED=$((TOTAL_FAILED + 1))
					FAILED_ITEMS+=("$file")
					FAILED_CMDS+=("$cmd")
					FAILED_LOGS+=("$log_file")
					echo "  FAILED: $file"
				fi
			done
		fi
	fi

	# byya-lyra: build each subdirectory (lyra-a, lyra-b, orion-a) via
	# `just lyra <subdir>`, which regenerates all .md files in that subdir.
	if should_process_dir "byya-lyra" && [[ -d "byya-lyra" ]]; then
		echo "[byya-lyra] Building .md files..."
		mapfile -t subdirs < <(
			find byya-lyra -mindepth 1 -maxdepth 1 -type d \
				! -name _output ! -name _temp ! -name .git | sort
		)
		if [[ ${#subdirs[@]} -eq 0 ]]; then
			echo "  No subdirectories found under byya-lyra/."
		else
			local_rule_rebuild=0
			if [[ "$INCREMENTAL" -eq 1 && "$REBUILD_ALL" -eq 0 ]] && changed_file_matches_any "scripts/gen_byya_lyra.py,scripts/byya-lyra-template.typ"; then
				echo "  Dependency changed -> rebuilding all byya-lyra subdirectories"
				local_rule_rebuild=1
			fi
			for subdir in "${subdirs[@]}"; do
				if is_excluded_path "$subdir"; then
					echo "  EXCLUDE: $subdir"
					continue
				fi
				if [[ "$INCREMENTAL" -eq 1 && "$REBUILD_ALL" -eq 0 && "$local_rule_rebuild" -eq 0 ]] && ! any_changed_under "$subdir/"; then
					echo "  SKIP (unchanged): $subdir"
					TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
					continue
				fi
				cmd="just lyra \"${subdir#byya-lyra/}\""
				log_file="$LOG_DIR/$(sanitize_log_name "$subdir").log"
				status=0
				run_just "$cmd" "$log_file" || status=$?
				if [[ $status -eq 0 ]]; then
					TOTAL_BUILT=$((TOTAL_BUILT + 1))
					rm -f "$log_file"
				elif [[ $status -eq 2 ]]; then
					: # dry-run: do not count, no log created
				else
					TOTAL_FAILED=$((TOTAL_FAILED + 1))
					FAILED_ITEMS+=("$subdir")
					FAILED_CMDS+=("$cmd")
					FAILED_LOGS+=("$log_file")
					echo "  FAILED: $subdir"
				fi
			done
		fi
	fi
else
	echo "Skipping PDF builds (--no-build)."
fi

# Assemble _site
if [[ "$DRY_RUN" -eq 1 ]]; then
	echo "Skipping _site assembly (--dry-run)."
else
	echo "Assembling _site ..."

	# Manifest assembly uses pypinyin for Post (ZH-CN) title sorting; run it
	# under uv so the dependency is available (uv is required by the build).
	uv run --with pypinyin python <<'PYEOF'
import json
import os
import re
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone

repo_root = Path('.').resolve()
_site_dir = repo_root / "_site"
pdfs_dir = _site_dir / "pdfs"
manifest_path = _site_dir / "manifest.json"

# Paths to exclude from the generated manifest and _site/pdfs copy.
# Each entry is a path prefix relative to the repo root (e.g., "chat/ctan/").
EXCLUDE_PATHS = json.loads(os.environ.get("_SITE_EXCLUDE_PATHS_JSON", "[]"))

# Optional per-item sidebar title overrides for byya-nineveh entries.
# Keys are "<collection>/<stem>" (e.g. "amphissa/00_Malta"); the value is the
# display name shown in the sidebar, overriding the auto-extracted title.
# This lets you rename entries without touching the BYYA-site HTML source.
BYYA_TITLE_OVERRIDES = {}
_byya_titles = repo_root / "byya-nineveh" / "titles.json"
if _byya_titles.exists():
    try:
        BYYA_TITLE_OVERRIDES = json.loads(_byya_titles.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(f"Warning: ignoring unparseable {_byya_titles}")

manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "groups": []
}

GROUP_ORDER = [
    ("entry", "Entry"),
    ("part", "Part"),
    ("post", "Post"),
    ("post_zh-cn", "Post (ZH-CN)"),
    ("chat", "Chat"),
    ("byya-lyra", "BYYA Lyra"),
    ("byya-lyra-annex", "BYYA Lyra Annex"),
    ("byya-nineveh", "BYYA Nineveh"),
    ("byya-nineveh-annex", "BYYA Nineveh Annex"),
    ("receipt", "Receipt"),
    ("favorite-image", "Favorite Image"),
    ("image-convert", "Image Convert"),
    ("typst-demo", "Typst Demo"),
    ("ctan", "CTAN"),
    ("ctan-annex", "CTAN Annex"),
]

DISPLAY_NAMES = dict(GROUP_ORDER)


@dataclass
class GroupNode:
    name: str
    dir: str
    items: list = field(default_factory=list)
    subgroups: dict = field(default_factory=dict)


def is_excluded(dir_parts):
    rel = "/".join(dir_parts)
    for prefix in EXCLUDE_PATHS:
        if not prefix:
            continue
        normalized = prefix.rstrip("/")
        if rel == normalized or rel.startswith(normalized + "/"):
            return True
    return False


def count_items(node):
    total = len(node.items)
    for subgroup in node.subgroups.values():
        total += count_items(subgroup)
    return total


# Per-group ordering of top-level subgroups. Any subgroup not listed here is
# appended after the listed ones in alphabetical order.
SUBGROUP_ORDER = {
    "byya-nineveh": ["nineveh", "amphissa", "laguna", "jaffa"],
}


def sorted_subgroup_names(node):
    names = list(node.subgroups.keys())
    order = SUBGROUP_ORDER.get(node.dir)
    if order:
        ordered = [name for name in order if name in node.subgroups]
        rest = sorted(name for name in names if name not in order)
        return ordered + rest
    return sorted(names)


def node_to_dict(node):
    result = {
        "name": node.name,
        "dir": node.dir,
        "items": node.items,
    }
    if node.subgroups:
        result["subgroups"] = [
            node_to_dict(node.subgroups[name])
            for name in sorted_subgroup_names(node)
        ]
    return result


_BALANCE_RE = re.compile(r'balance\(\[(.*?)\]\)', re.DOTALL)


def unescape_typst(text):
    """Undo common Typst markup escapes (e.g., \\( -> ()."""
    return re.sub(r'\\(.)', r'\1', text)


def strip_typst_wrappers(text):
    """Strip #und1[...]/#und2[...] styling wrappers, keeping the inner text."""
    return re.sub(r"#und[12]\[([^\]]*)\]", r"\1", text)


def extract_byya_nineveh_title(typ_path):
    """Extract the <h4>-equivalent title from a generated byya-nineveh .typ file.

    The generated file wraps the heading + body in balance([...]). The heading
    is the text before the first ' ⚪', ' ⚫', or double-space separator.
    """
    if not typ_path.exists():
        return None
    text = typ_path.read_text(encoding="utf-8")
    m = _BALANCE_RE.search(text)
    if not m:
        return None
    content = m.group(1)
    best_pos = len(content)
    for sep in (" ⚪", " ⚫", "  "):
        pos = content.find(sep)
        if pos != -1 and pos < best_pos:
            best_pos = pos
    if best_pos < len(content):
        title = content[:best_pos].strip()
    else:
        title = content.strip()
    title = unescape_typst(title)
    title = strip_typst_wrappers(title)
    return title if title else None


def extract_markdown_h1(md_path):
    """Return the first level-1 ATX heading (# Title) of a markdown file, or None.

    Lines inside fenced code blocks are skipped so code examples starting with
    '#' are not mistaken for a title. Common inline markup (links, emphasis,
    inline code) is stripped from the heading text.
    """
    if not md_path.exists():
        return None
    try:
        in_fence = False
        with open(md_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if stripped.startswith("# "):
                    title = stripped[2:].strip()
                    title = re.sub(r"`[^`]*`", "", title)
                    title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", title)
                    title = re.sub(r"[*_~]", "", title)
                    title = re.sub(r"\s+", " ", title).strip()
                    return title if title else None
    except OSError:
        return None
    return None


def extract_byya_lyra_annex_title(md_path):
    """Return the original title (author/source) from a lyra annex .md file.

    The generated files end with ' [Author]' where the bracketed text is the
    original, unsanitized title. This lets the sidebar show '&' and ':' that
    were removed from the filename.
    """
    if not md_path.exists():
        return None
    text = md_path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"\[([^\]]+)\]", text))
    if matches:
        return matches[-1].group(1).strip()
    return None


groups_by_dir = {}
manifest_paths = set()

# Remove any previously-copied PDFs that now fall under excluded paths.
for prefix in EXCLUDE_PATHS:
    if not prefix:
        continue
    excluded_pdfs_dir = pdfs_dir / prefix.strip("/")
    if excluded_pdfs_dir.exists():
        shutil.rmtree(excluded_pdfs_dir)
        print(f"Removed excluded directory: {excluded_pdfs_dir.relative_to(_site_dir)}")

copied = 0
for pdf_path in sorted(repo_root.rglob("_output/pdfs/*.pdf")):
    rel = pdf_path.relative_to(repo_root)
    parts = rel.parts
    if len(parts) < 4:
        continue

    # Find the _output/pdfs segment and strip it out.
    try:
        output_idx = parts.index("_output")
    except ValueError:
        continue
    if output_idx + 2 >= len(parts) or parts[output_idx + 1] != "pdfs":
        continue

    dir_parts = parts[:output_idx]
    filename = parts[-1]

    if not dir_parts or is_excluded(dir_parts):
        continue

    # Copy PDF into _site/pdfs/<dir>/... preserving subdirectories.
    dest_dir = pdfs_dir.joinpath(*dir_parts)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    shutil.copy2(pdf_path, dest_path)
    copied += 1

    # Path used by _site/index.html.
    manifest_path_str = (Path("pdfs").joinpath(*dir_parts) / filename).as_posix()
    manifest_paths.add(_site_dir / manifest_path_str)

    top_dir = dir_parts[0]
    original_top_dir = top_dir

    if top_dir not in groups_by_dir:
        groups_by_dir[top_dir] = GroupNode(
            name=DISPLAY_NAMES.get(top_dir, top_dir),
            dir=top_dir,
        )

    node = groups_by_dir[top_dir]
    for part in dir_parts[1:]:
        if part not in node.subgroups:
            node.subgroups[part] = GroupNode(
                name=part,
                dir=f"{node.dir}/{part}",
            )
        node = node.subgroups[part]

    title = Path(filename).stem
    source_guess = None
    for ext in (".md", ".typ"):
        candidate = repo_root.joinpath(*dir_parts) / f"{title}{ext}"
        if candidate.exists():
            source_guess = str(candidate.relative_to(repo_root))
            break

    # For favorite-image entries the PDF filename is already the image filename,
    # so the default title (filename stem) is the image name. No override needed.

    # For byya-nineveh entries, use the <h4>-equivalent title from the generated .typ file,
    # unless overridden by a per-item entry in byya-nineveh/titles.json.
    # Override keys are "<collection>/<stem>" where <stem> is the slide name WITHOUT the
    # numeric prefix (e.g. "amphissa/Diogenes"), so renumbering slides never invalidates keys.
    if dir_parts[0] == "byya-nineveh" and len(dir_parts) >= 2:
        stem = Path(filename).stem
        slide_stem = re.sub(r"^\d+_", "", stem)
        override_key = f"{dir_parts[1]}/{slide_stem}"
        override_title = BYYA_TITLE_OVERRIDES.get(override_key)
        if override_title:
            title = override_title
        else:
            typ_path = repo_root.joinpath(*dir_parts) / "_output" / "typs" / f"{stem}.typ"
            extracted_title = extract_byya_nineveh_title(typ_path)
            if extracted_title:
                title = extracted_title

    # For Post / Post (ZH-CN) entries, prefer the source markdown's first H1
    # heading over the file name as the sidebar label.
    if source_guess and source_guess.endswith(".md") and dir_parts[0] in ("post", "post_zh-cn"):
        extracted_title = extract_markdown_h1(repo_root / source_guess)
        if extracted_title:
            title = extracted_title

    # For byya-lyra entries, the numeric prefix (001_, 002_, ...) is only a
    # filename sort key; drop it from the sidebar label.
    if dir_parts[0] == "byya-lyra":
        title = re.sub(r"^\d+_", "", title)

    # For byya-lyra-annex entries, restore the original title from the .md body.
    if original_top_dir == "byya-lyra-annex":
        md_source = repo_root.joinpath(*dir_parts) / f"{title}.md"
        extracted_title = extract_byya_lyra_annex_title(md_source)
        if extracted_title:
            title = extracted_title

    node.items.append({
        "title": title,
        "path": manifest_path_str,
        "source": Path(source_guess).as_posix() if source_guess else None,
    })

# Place LaTeX Demo under CTAN Annex in the sidebar.
if "latex-demo" in groups_by_dir:
    latex_node = groups_by_dir.pop("latex-demo")
    latex_node.name = "LaTeX Demo"
    if "ctan-annex" not in groups_by_dir:
        groups_by_dir["ctan-annex"] = GroupNode(
            name=DISPLAY_NAMES.get("ctan-annex", "ctan-annex"),
            dir="ctan-annex",
        )
    groups_by_dir["ctan-annex"].subgroups["latex-demo"] = latex_node

# Post (ZH-CN) items are sorted by the pinyin of their title (ascending).
# Chinese titles are converted to pinyin with the pypinyin library; the mixed
# Latin/pinyin key is lowercased so English titles interleave naturally.
def _pinyin_key(text):
    try:
        from pypinyin import lazy_pinyin, Style

        return "".join(lazy_pinyin(text, style=Style.NORMAL)).lower()
    except ImportError:
        return text.lower()


_zh_cn = groups_by_dir.get("post_zh-cn")
if _zh_cn:
    _zh_cn.items.sort(key=lambda item: _pinyin_key(item["title"]))

# byya-lyra-annex items follow the original annex.md order when an order file
# is present (written by sync_byya_lyra_annex_md.py). Fall back to filename sort.
_lyra_annex = groups_by_dir.get("byya-lyra-annex")
if _lyra_annex:
    _order_file = repo_root / "byya-lyra-annex" / "annex-order.txt"
    if _order_file.exists():
        _order = {
            name.strip(): idx
            for idx, name in enumerate(_order_file.read_text(encoding="utf-8").splitlines())
            if name.strip()
        }
        _lyra_annex.items.sort(
            key=lambda item: _order.get(Path(item["path"]).stem, float("inf"))
        )

for dir_name, display_name in GROUP_ORDER:
    if dir_name in groups_by_dir:
        manifest["groups"].append(node_to_dict(groups_by_dir[dir_name]))

for dir_name in sorted(groups_by_dir.keys()):
    if dir_name not in DISPLAY_NAMES:
        manifest["groups"].append(node_to_dict(groups_by_dir[dir_name]))

# Remove stale PDFs in _site/pdfs/ that are no longer referenced by the manifest.
removed = 0
for pdf_path in pdfs_dir.rglob("*.pdf"):
    if pdf_path not in manifest_paths:
        pdf_path.unlink()
        removed += 1
        parent = pdf_path.parent
        while parent != pdfs_dir and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
if removed:
    print(f"Removed {removed} stale PDF(s) from {pdfs_dir}")

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

total_pdfs = sum(count_items(groups_by_dir[d]) for d in groups_by_dir)
print(f"Copied {copied} PDFs to {pdfs_dir}")
print(f"manifest.json written with {total_pdfs} PDFs to {manifest_path}")
PYEOF
fi

# Summary
echo ""
echo "========================================"
echo "Build complete: $TOTAL_BUILT built, $TOTAL_FAILED failed, $TOTAL_SKIPPED skipped."

if [[ ${#FAILED_ITEMS[@]} -gt 0 ]]; then
	echo ""
	echo "========== ERROR DETAILS =========="
	for i in "${!FAILED_ITEMS[@]}"; do
		echo ""
		echo "---- Failure $((i + 1))/${#FAILED_ITEMS[@]} ----"
		echo "File: ${FAILED_ITEMS[$i]}"
		echo "Command: ${FAILED_CMDS[$i]}"
		echo "Log:"
		if [[ -f "${FAILED_LOGS[$i]}" ]]; then
			sed 's/^/  /' "${FAILED_LOGS[$i]}"
		else
			echo "  (log file not found)"
		fi
	done
	echo ""
	echo "========== END OF ERRORS =========="
	echo ""
	echo "Log files are preserved under: $LOG_DIR"
	if [[ "$STRICT" -eq 1 ]]; then
		exit 1
	fi
fi
