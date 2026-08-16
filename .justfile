# == Default options
# size: 8(pt)
# font: MonaspiceNe NFM, Sarasa Mono SC

set dotenv-load

# == entry,part (A6)
a6 path size="" font="":
    uv run scripts/gen_a6.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == post (A4, 2-column)
a4 path size="" font="":
    uv run scripts/gen_a4.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == post (A4, 2-column) (file1 left, file2 right)
a42 path1 path2 size="" font="":
    uv run scripts/gen_a4.py "{{path1}}" --two-column "{{path2}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

# == BYYA-nineveh (from .md)
nineveh-md subdir source="":
    uv run scripts/gen_byya_nineveh_md.py "{{subdir}}" \
        {{ if source != "" { "--source \"" + source + "\"" } else { "" } }}

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

# == favorite-image (polario frame)
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

# == latex (LaTeX cards; add latex/<stem>.tex + matching <stem>.jpg to compile)
latex path:
    uv run scripts/gen_latex.py --compile "{{path}}"

# == latex-annex (A6 dynamic height)
latex-annex path size="" font="":
    uv run scripts/gen_latex_annex.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}