# /// script
# requires-python = ">=3.12"
# ///
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import find_imagemagick_cli


@dataclass(frozen=True)
class ConversionResult:
    success: bool
    stderr: str
    tool: str | None = None


def _find_ghostscript_cli() -> str | None:
    candidates = ["gswin64c", "gswin32c"] if sys.platform == "win32" else ["gs"]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p

    gs_dll = os.environ.get("GS_DLL")
    if gs_dll:
        exes = ["gswin64c.exe", "gswin32c.exe"] if sys.platform == "win32" else ["gs"]
        for exe in exes:
            cli = Path(gs_dll).with_name(exe)
            if cli.exists():
                return str(cli)
    return None


def convert_pdf_to_jpg(
    pdf_path: Path,
    output_pattern: str,
    density: int = 150,
    quality: int = 90,
) -> ConversionResult:
    gs = _find_ghostscript_cli()
    if gs:
        cmd = [
            gs,
            "-q",
            "-dQUIET",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-dNOPROMPT",
            "-dMaxBitmap=500000000",
            "-dAlignToPixels=0",
            "-dGridFitTT=2",
            "-sDEVICE=jpeg",
            f"-dJPEGQ={quality}",
            "-dTextAlphaBits=4",
            "-dGraphicsAlphaBits=4",
            f"-r{density}x{density}",
            "-dPrinted=false",
            f"-sOutputFile={output_pattern}",
            str(pdf_path),
        ]
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return ConversionResult(r.returncode == 0, r.stderr, "ghostscript")

    magick = find_imagemagick_cli()
    if not magick:
        return ConversionResult(
            False,
            "Neither Ghostscript (gs/gswin64c/gswin32c) nor ImageMagick (magick/convert) was found.",
        )

    cmd = [
        magick,
        "-density",
        str(density),
        str(pdf_path),
        "-background",
        "white",
        "-alpha",
        "remove",
        "-quality",
        str(quality),
        output_pattern,
    ]
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return ConversionResult(r.returncode == 0, r.stderr, "imagemagick")
