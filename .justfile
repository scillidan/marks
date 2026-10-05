set dotenv-load

# == entry,part (A6)
a6 path size="" font="":
    uv run scripts/gen_a6.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == post (A4, 2-column) (engine: latex)
a4 path:
    uv run scripts/gen_a4_latex.py "{{path}}"

# == copy (A5 pages 2-up on landscape A4, reading order) (engine: latex)
copy path:
    uv run scripts/gen_copy.py "{{path}}"

# == copy-a5 (single A5 pages, reading order)
copy-a5 path:
    uv run scripts/gen_copy.py "{{path}}" --a5

# == copy-booklet (saddle-stitch imposition; print duplex flip-short-edge, stack, fold, staple spine)
# Accepts .md (compiled to A5 first) or .pdf (imposed directly).
# signature: number of pages per folded signature, must be a multiple of 4; default 4 keeps the first sheet full.
# Any trailing flags (e.g. --pages 1-16) are forwarded to the script.
copy-booklet path signature="4" pages="" *flags:
    uv run scripts/gen_copy.py "{{path}}" --booklet --signature "{{signature}}" \
        {{ if pages != "" { "--pages \"" + pages + "\"" } else { "" } }} \
        {{ flags }}

# == copy-grid (grid imposition, e.g. 2x2 cards on A4 landscape)
# Accepts .md or .pdf. Pages='1-8' limits the range (use "" for all pages).
# Trailing flags are forwarded, e.g. --frame, --divider, --divider-horizontal,
# --fit fill, --margin 5mm, --frame-color gray50, --frame-width 0.2pt.
# Image processing (text stays vector), e.g.
#   --brighten 250            multiply-brighten embedded images only
#   --image-filter 'magick $1 -colorspace Gray -gamma 2.2 $2'
#                             arbitrary per-image magick chain ($1=in $2=out)
#   --dither 'magick $1 -ordered-dither h8x8a -type Bilevel $2'
#                             whole-page rasterise + dither (PDF input)
#   --grayscale, --dither-dpi 300, --suffix .v2
copy-grid path grid="2x2" pages="" *flags:
    uv run scripts/gen_copy.py "{{path}}" \
        --grid "{{grid}}" \
        {{ if pages != "" { "--pages \"" + pages + "\"" } else { "" } }} \
        {{ flags }}

# == post bilingual pair (A4, synchronized two-column paracol)
# First file: source (e.g. post/foo.md), second file: translation (e.g. post/foo.zh-cn.md)
a4dual en zh:
    uv run scripts/gen_a4_dual_latex.py "{{en}}" "{{zh}}"

# == BYYA-nineveh (from .md)
nineveh-md subdir source="" force="":
    uv run scripts/gen_byya_nineveh_md.py "{{subdir}}" \
        {{ if source != "" { "--source \"" + source + "\"" } else { "" } }} \
        {{ if force != "" { "--force" } else { "" } }}

# == BYYA-nineveh (from .typ)
nineveh-typ path:
    uv run scripts/gen_byya_nineveh_typ.py "{{path}}"

# == BYYA-nineveh-annex (A6 dynamic height)
nineveh-annex path size="" font="":
    uv run scripts/gen_byya_nineveh_annex.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == BYYA-lyra (A6, from .md)
lyra subdir size="" font="":
    uv run scripts/gen_byya_lyra.py "{{subdir}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == BYYA-lyra-annex (A6 dynamic height)
lyra-annex path size="" font="":
    uv run scripts/gen_byya_lyra_annex.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == receipt (A7)
receipt path size="" font="":
    uv run scripts/gen_a7_receipt.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == receipt (A7, rotated 90 degrees, height locked to 74mm)
receipt-rotate path size="" font="" width="":
    uv run scripts/gen_a7_receipt.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }} \
        {{ if width != "" { "--width " + width } else { "" } }} \
        --rotate

# == image-collect (polario frame)
polario mode image text-first text-second text-third start resize size:
    uv run scripts/gen_polario.py {{mode}} "{{image}}" "{{text-first}}" "{{text-second}}" "{{text-third}}" "{{start}}" "{{resize}}" "{{size}}"

# == image-convert (image + command processing, outputs to image-convert/_output/)
# Positional args: mode (portrait/landscape), theme (dark/light), output
# (required, bare filename only), image (required), commands (empty = no
# command, image is used as-is).
# output is used as the shared base name: jpg -> image-convert/_output/,
# typ -> image-convert/_output/typs/, pdf -> image-convert/_output/pdfs/.
# Single quotes keep $1/$2 placeholders from being expanded by the shell.
# Windows cmd quoting: use "" (not \") for a literal quote inside commands,
# and keep && / & inside quotes — cmd does not use backslash escapes.
image-convert mode theme output image="" commands="":
    uv run scripts/image-convert.py '{{mode}}' '{{theme}}' \
        {{ if image != "" { "--image '" + image + "'" } else { "" } }} \
        {{ if commands != "" { "--commands '" + commands + "'" } else { "" } }} \
        --output '{{output}}'

# == image-convert (no-run: use a pre-prepared image, show commands text only)
image-convert-norun mode theme output image="" commands="":
    uv run scripts/image-convert.py '{{mode}}' '{{theme}}' --no-run \
        {{ if image != "" { "--image '" + image + "'" } else { "" } }} \
        {{ if commands != "" { "--commands '" + commands + "'" } else { "" } }} \
        --output '{{output}}'

# == ctan (engine: latex)
ctan path:
    uv run scripts/gen_ctan.py --compile "{{path}}"

# == shortcut cheatsheets (A4, generated from .cht files)
# Usage:
#   just shortcut                                      # all .cht, one PDF per dir
#   just shortcut --include neovim --style neovim      # only neovim -> neovim.pdf
#   just shortcut --include neovim --include vim       # merged -> neovim_vim.pdf
#   just shortcut --exclude neovim                     # everything except neovim
#   just shortcut --include shortcut/                  # one dir recursively
#   just shortcut --include neovim --columns 4         # override column count
shortcut *args:
    uv run scripts/gen_shortcut.py {{ args }}

