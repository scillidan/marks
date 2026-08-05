#!/usr/bin/env python3
"""Install fonts from Scoop manifests.

Each manifest must contain:
  - url:    download URL
  - hash:   expected sha256 hex digest
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

FONT_DIR = Path.home() / ".local/share/fonts"
CACHE_DIR = Path(tempfile.gettempdir()) / "install-fonts-cache"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"Using cached {dest.name}")
        return
    print(f"Downloading {url} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def extract(archive: Path, dest: Path) -> None:
    suffix = archive.suffix.lower()
    if suffix == ".zip":
        shutil.unpack_archive(str(archive), str(dest), "zip")
    elif suffix in (".7z", ".7zip"):
        subprocess.run(["7z", "x", str(archive), f"-o{dest}", "-y"], check=True)
    else:
        raise RuntimeError(f"Unsupported archive format: {archive}")


def fetch_manifest(url: str) -> Path:
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as f:
        urllib.request.urlretrieve(url, f.name)
        return Path(f.name)


def install_from_manifest(manifest_path: Path) -> None:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    url = data["url"]
    expected_hash = data["hash"].lower()
    filename = Path(url).name

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    archive = CACHE_DIR / filename
    download(url, archive)

    actual_hash = sha256(archive)
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"Hash mismatch for {filename}: expected {expected_hash}, got {actual_hash}"
        )

    with tempfile.TemporaryDirectory() as tmp:
        extract_dir = Path(tmp) / "extracted"
        extract(archive, extract_dir)

        fonts = list(extract_dir.rglob("*.ttf")) + list(extract_dir.rglob("*.otf"))
        glob = data.get("install_glob")
        if glob:
            from fnmatch import fnmatch

            fonts = [f for f in fonts if fnmatch(f.name, glob)]
        if not fonts:
            raise RuntimeError(f"No font files found in {filename}")

        FONT_DIR.mkdir(parents=True, exist_ok=True)
        for font in fonts:
            dest = FONT_DIR / font.name
            shutil.copy2(font, dest)
            print(f"Installed {dest}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: install.py <manifest.json|url>...", file=sys.stderr)
        sys.exit(1)

    for arg in sys.argv[1:]:
        if arg.startswith(("http://", "https://")):
            manifest_path = fetch_manifest(arg)
        else:
            manifest_path = Path(arg)
        install_from_manifest(manifest_path)


if __name__ == "__main__":
    main()
