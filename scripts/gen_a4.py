# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "Pillow==12.2.0"
# ]
# ///
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _common import check_dependencies, compile_typst, convert_to_jpg, resolve_path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_UPSCAYL_WARNED = False

MEDIA_EXTS = {".gif", ".mp4", ".mov", ".webm"}
AVIF_EXTS = {".avif"}


def get_UPSCAYL_MODEL():
    global _UPSCAYL_WARNED
    env_path = os.environ.get("UPSCAYL_MODEL", "").strip()
    if not env_path:
        if not _UPSCAYL_WARNED:
            _UPSCAYL_WARNED = True
            print(
                "UPSCAYL_MODEL is not set. Set it to the directory containing 4xLSDIR.param and 4xLSDIR.bin."
            )
        return None

    path = Path(os.path.expandvars(env_path))
    if path.exists():
        return path
    print(f"✗ UPSCAYL_MODEL: {env_path} (not found)")
    return None


def upscale_image_if_needed(source_path, dest_path):
    if source_path.suffix.lower() in (".svg", ".gif"):
        return False

    try:
        with Image.open(source_path) as img:
            width = img.size[0]
            if width >= 800:
                return False

            print(f"Image {source_path.name} width ({width}px) < 800px, upscaling...")
            model_path = get_UPSCAYL_MODEL()
            if model_path is None:
                print(f"Copying original {source_path.name}.")
                shutil.copy(source_path, dest_path)
                return False

            if (
                not (model_path / "4xLSDIR.param").exists()
                or not (model_path / "4xLSDIR.bin").exists()
            ):
                print(
                    f"Upscaling model not found under {model_path} "
                    f"(expected 4xLSDIR.param and 4xLSDIR.bin). "
                    f"Set UPSCAYL_MODEL to the correct model directory. "
                    f"Copying original {source_path.name}."
                )
                shutil.copy(source_path, dest_path)
                return False

            cmd = [
                "upscayl-bin" if platform.system() == "Windows" else "upscayl",
                "-m",
                str(model_path),
                "-n",
                "4xLSDIR",
                "-w",
                "800",
                "-i",
                str(source_path),
                "-o",
                str(dest_path),
            ]
            r = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", check=False
            )
            if r.returncode != 0:
                print(f"Error upscaling {source_path.name}: {r.stderr}")
                shutil.copy(source_path, dest_path)
                return False

            print(f"Upscaled {source_path.name} to {dest_path}")
            return True
    except Exception as e:
        print(f"Error checking image dimensions for {source_path}: {e}")
        return False


def get_image_source(content_dir):
    env_path = os.environ.get("POST_SOURCE")
    if env_path:
        path = Path(os.path.expandvars(env_path))
        if path.exists():
            return path
        print(f"✗ POST_SOURCE: {env_path} (not found)")

    local_assets = content_dir / "assets"
    if local_assets.exists():
        print(f"✓ Image source (local): {local_assets}")
        return local_assets
    return None


def _ffmpeg_to_jpg(src, dest, frames=1):
    if shutil.which("ffmpeg") is None:
        print(f"  ✗ ffmpeg not found; cannot convert {src.name} to jpg")
        return None
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if frames:
        cmd += ["-frames:v", str(frames)]
    cmd.append(str(dest))
    r = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if r.returncode != 0:
        print(f"  ✗ ffmpeg failed for {src.name}: {r.stderr}")
        return None
    return dest if dest.exists() else None


def convert_media_to_jpg(src, images_dir):
    ext = src.suffix.lower()
    dest = images_dir / f"{src.stem}.jpg"
    if dest.exists():
        return dest
    try:
        if ext == ".gif":
            with Image.open(src) as im:
                im.seek(0)
                im.convert("RGB").save(dest, "JPEG", quality=90)
        elif ext in (".mp4", ".mov", ".webm"):
            _ffmpeg_to_jpg(src, dest, frames=1)
        else:
            return None
    except Exception as e:
        print(f"  ✗ conversion failed for {src.name}: {e}")
        return None
    return dest if dest.exists() else None


def convert_avif_to_jpg(src, images_dir):
    dest = images_dir / f"{src.stem}.jpg"
    if dest.exists():
        return dest
    return _ffmpeg_to_jpg(src, dest, frames=0)


def wrap_image_figures(md_content):
    parts = re.split(r"(\n[ \t]*\n)", md_content)
    out = []
    for part in parts:
        if re.fullmatch(r"\n[ \t]*\n", part):
            out.append(part)
            continue
        m = re.match(r"^(!\[[^\]]*\]\([^\s\)\\]+\))[ \t]*\n(.*)$", part, re.S)
        if m:
            image, caption = m.group(1), m.group(2)
            caption = caption.rstrip()
            if caption:
                out.append(
                    "<figure>\n\n"
                    + image
                    + "\n\n<figcaption>"
                    + caption
                    + "</figcaption>\n</figure>"
                )
                continue
        out.append(part)
    return "".join(out)


def process_markdown(md_path, content_dir, output_dir, filename_suffix=""):
    if not md_path.exists():
        sys.exit(f"Error: Markdown file not found: {md_path}")

    md_content = md_path.read_text(encoding="utf-8")

    supported_formats = ["jpg", "jpeg", "png", "gif", "svg", "webp", "avif"]
    images_dir = content_dir / "_temp" / "images"
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

    found_count = 0
    missing = []
    conv_map = {}
    media_note = {}

    def copy_src(src, dest_name):
        nonlocal found_count
        dest = images_dir / dest_name
        if not dest.exists():
            upscaled = upscale_image_if_needed(src, dest)
            if not upscaled:
                shutil.copy(src, dest)
        print(f"  ✓ {dest_name}")
        found_count += 1

    cdn_map = {}
    if cdn_names:
        image_source = get_image_source(content_dir)
        if not image_source:
            sys.exit("\nSet POST_SOURCE in .env or place images in post/assets/\n")
        for base in cdn_names:
            resolved = None
            for ext in supported_formats:
                src = image_source / f"{base}.{ext}"
                if src.exists():
                    resolved = src
                    break
            if resolved:
                if resolved.suffix.lower() in AVIF_EXTS:
                    jpg = convert_avif_to_jpg(resolved, images_dir)
                    if jpg is None:
                        missing.append(f"{base}.avif")
                        print(f"  ✗ {base}.avif (conversion failed)")
                        continue
                    cdn_map[base] = jpg.name
                    print(f"  ✓ {jpg.name} (from {resolved.name})")
                    found_count += 1
                else:
                    copy_src(resolved, resolved.name)
                    cdn_map[base] = resolved.name
            else:
                missing.append(f"{base}.*")
                print(f"  ✗ {base}.* (not found)")

    for name in sorted(local_names):
        src = assets_dir / name
        if not src.exists():
            missing.append(name)
            print(f"  ✗ {name} (not found)")
            continue

        ext = Path(name).suffix.lower()
        if ext in MEDIA_EXTS or ext in AVIF_EXTS:
            jpg = (
                convert_media_to_jpg(src, images_dir)
                if ext in MEDIA_EXTS
                else convert_avif_to_jpg(src, images_dir)
            )
            if jpg is None:
                missing.append(name)
                print(f"  ✗ {name} (conversion failed)")
                continue
            jpg_name = jpg.name
            for full, fname in local_map.items():
                if fname == name:
                    conv_map[full] = jpg_name
                    if ext in MEDIA_EXTS:
                        media_note[full] = ext.lstrip(".")
            print(f"  ✓ {jpg_name} (from {name})")
            found_count += 1
        else:
            copy_src(src, name)

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
        return f"{m.group(1)}images/{jpg}{m.group(3)}{sep}{caption}"

    md_content_local = media_img_re.sub(rewrite_media, md_content)

    def rewrite_cdn(m):
        base = m.group(2)
        if base in cdn_map:
            return f"{m.group(1)}images/{cdn_map[base]}{m.group(3)}"
        return m.group(0)

    md_content_local = cdn_re.sub(rewrite_cdn, md_content_local)

    def rewrite_local(m):
        full = m.group(2)
        if full in local_map:
            return f"{m.group(1)}images/{local_map[full]}{m.group(3)}"
        return m.group(0)

    md_content_local = any_img_re.sub(rewrite_local, md_content_local)

    md_content_local = wrap_image_figures(md_content_local)

    md_content_local = re.sub(r"\n{3,}", "\n\n", md_content_local)

    suffix = f"-{filename_suffix}" if filename_suffix else ""
    md_processed_path = output_dir / f"{md_path.stem}{suffix}-processed.md"
    md_processed_path.write_text(md_content_local, encoding="utf-8")

    return md_processed_path, images_dir


def _typst_package_cache_dir():
    env_path = os.environ.get("TYPST_PACKAGE_CACHE_PATH", "").strip()
    if env_path:
        return Path(os.path.expandvars(env_path))

    try:
        r = subprocess.run(
            ["typst", "info"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        for line in (r.stdout + r.stderr).splitlines():
            stripped = line.strip()
            if stripped.startswith("Package cache path"):
                _, _, path = stripped.partition("Package cache path")
                path = path.strip()
                if path:
                    return Path(path)
    except Exception:
        pass

    system = platform.system()
    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "typst" / "packages"
    if system == "Darwin":
        return Path.home() / "Library" / "Caches" / "typst" / "packages"
    cache_home = os.environ.get("XDG_CACHE_HOME", "")
    if cache_home:
        return Path(cache_home) / "typst" / "packages"
    return Path.home() / ".cache" / "typst" / "packages"


def _cmarker_package_dir():
    return _typst_package_cache_dir() / "preview" / "cmarker" / "0.1.9"


def _ensure_cmarker_installed():
    cmarker_dir = _cmarker_package_dir()
    if cmarker_dir.exists() and (cmarker_dir / "typst.toml").exists():
        return True

    with tempfile.TemporaryDirectory() as tmp:
        dummy_typ = Path(tmp) / "dummy.typ"
        dummy_typ.write_text('#import "@preview/cmarker:0.1.9"\n', encoding="utf-8")
        r = subprocess.run(
            ["typst", "compile", str(dummy_typ), str(Path(tmp) / "dummy.pdf")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    if not (cmarker_dir.exists() and (cmarker_dir / "typst.toml").exists()):
        print(
            f"Warning: cmarker package not installed. "
            f"Dummy compile exit={r.returncode} stderr={r.stderr.strip()!r}",
            file=sys.stderr,
        )
        return False
    return True


def copy_to_cmarker(images_dir):
    if not images_dir.exists():
        return
    try:
        if not _ensure_cmarker_installed():
            print("Warning: skipping cmarker image copy (package not installed)")
            return

        cmarker_images_dir = _cmarker_package_dir() / "images"
        cmarker_images_dir.mkdir(parents=True, exist_ok=True)

        for image_path in images_dir.glob("*"):
            if image_path.suffix.lower() in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".svg",
                ".webp",
            ]:
                shutil.copy2(image_path, cmarker_images_dir / image_path.name)

        print("Copied images to cmarker directory")
    except Exception as copy_error:
        print(f"Error copying images: {copy_error}")


def generate_typ_single(content_path, size_str, fonts, output_dir):
    md_processed_path, images_dir = process_markdown(
        content_path, content_path.parent, output_dir
    )
    copy_to_cmarker(images_dir)

    if not any(c.isalpha() for c in size_str):
        size_str = size_str + "pt"

    font_str = ", ".join(f'"{f}"' for f in fonts)
    content = f"""#import "@preview/cmarker:0.1.9"

#set page(paper: "a4", margin: 2%, columns: 2)
#set text(font: ({font_str}), size: {size_str})
#set par(justify: true)

#show raw.where(block: false): set text(font: ({font_str}), size: {size_str})
#show raw.where(block: true):  set text(font: ({font_str}), size: {size_str})

#show image: set align(center)
#set image(width: 100%)

#set figure(numbering: none, supplement: none, gap: 0.25em)
#show figure.caption: set text(style: "italic")

#cmarker.render(read("../{md_processed_path.name}"))"""

    typ_path = output_dir / "typs" / f"{content_path.stem}.typ"
    typ_path.parent.mkdir(exist_ok=True)
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")

    return typ_path, md_processed_path, images_dir


def generate_typ_dual_two_files(
    content_path_left, content_path_right, size_str, fonts, output_dir
):
    content_dir = content_path_left.parent

    md_left_processed, images_dir = process_markdown(
        content_path_left, content_dir, output_dir, "left"
    )
    md_right_processed, _ = process_markdown(
        content_path_right, content_dir, output_dir, "right"
    )
    copy_to_cmarker(images_dir)

    if not any(c.isalpha() for c in size_str):
        size_str = size_str + "pt"

    font_str = ", ".join(f'"{f}"' for f in fonts)
    output_name = f"{content_path_left.stem}-{content_path_right.stem}"
    content = f"""#import "@preview/cmarker:0.1.9"

#set page(paper: "a4", margin: 2%)
#set text(font: ({font_str}), size: {size_str})
#set par(justify: true)

#show image: set align(center)
#set image(width: 100%)

#set figure(numbering: none, supplement: none, gap: 0.25em)
#show figure.caption: set text(style: "italic")

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  [#cmarker.render(read("../{md_left_processed.name}"))],
  [#cmarker.render(read("../{md_right_processed.name}"))],
)"""

    typ_path = output_dir / "typs" / f"{output_name}.typ"
    typ_path.parent.mkdir(exist_ok=True)
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")

    return typ_path, md_left_processed, md_right_processed, images_dir


def generate_output_stem(stem1, stem2):
    if stem1 == stem2:
        return f"{stem1}-dual"

    if stem1 in stem2:
        idx = len(stem1)
        diff = stem2[idx:].lstrip("._-")
        if diff:
            return f"{stem1}_{diff}"
        return stem2
    elif stem2 in stem1:
        idx = len(stem2)
        diff = stem1[idx:].lstrip("._-")
        if diff:
            return f"{stem2}_{diff}"
        return stem1

    common_len = 0
    for c1, c2 in zip(stem1, stem2):
        if c1 == c2:
            common_len += 1
        else:
            break

    if common_len > 0:
        common = stem1[:common_len].rstrip("._-")
        diff1 = stem1[common_len:].lstrip("._-")
        diff2 = stem2[common_len:].lstrip("._-")

        if diff1 and diff2:
            return f"{common}_{diff1}_{diff2}"
        elif diff1:
            return f"{common}_{diff1}"
        elif diff2:
            return f"{common}_{diff2}"

    return f"{stem1}-{stem2}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--size", default="8pt")
    parser.add_argument("--font", dest="fonts")
    parser.add_argument("--two-column", dest="two_column", default=None)
    args = parser.parse_args()

    check_dependencies()

    fonts = (
        [f.strip() for f in args.fonts.split(",")]
        if args.fonts
        else ["MonaspiceNe NFM", "Sarasa Mono SC"]
    )

    content_path = resolve_path(args.path)
    if not content_path.exists():
        sys.exit(f"Error: File not found: {content_path}")

    content_dir = content_path.parent
    project_root = content_dir.parent
    output_dir = content_dir / "_output"
    output_dir.mkdir(exist_ok=True)
    pdfs_dir = output_dir / "pdfs"
    pdfs_dir.mkdir(exist_ok=True)

    if args.two_column:
        right = Path(args.two_column)
        if not right.is_absolute():
            right = (
                content_dir / args.two_column
                if right.parent == Path(".")
                else Path.cwd() / args.two_column
            )
        if not right.exists():
            sys.exit(f"Error: File not found: {right}")

        typ_path, md_left, md_right, images_dir = generate_typ_dual_two_files(
            content_path, right, args.size, fonts, output_dir
        )
        md_processed = [md_left, md_right]
        output_stem = generate_output_stem(content_path.stem, right.stem)
    else:
        typ_path, md_processed, images_dir = generate_typ_single(
            content_path, args.size, fonts, output_dir
        )
        output_stem = content_path.stem

    for md in md_processed if isinstance(md_processed, list) else [md_processed]:
        print(f"Generated: {md}")

    pdf_path = pdfs_dir / f"{output_stem}.pdf"
    compile_typst(typ_path, pdf_path, project_root)
    convert_to_jpg(pdf_path, str(output_dir / f"{output_stem}_p%02d.jpg"))
    print(f"Created: {output_dir}/{output_stem}_p*.jpg")

    for md in md_processed if isinstance(md_processed, list) else [md_processed]:
        md.unlink()

    try:
        cmarker_images_dir = _cmarker_package_dir() / "images"
        if cmarker_images_dir.exists():
            shutil.rmtree(cmarker_images_dir)
    except Exception as e:
        print(f"Warning: Could not cleanup cmarker images: {e}")

    if images_dir and images_dir.exists():
        shutil.rmtree(images_dir)
