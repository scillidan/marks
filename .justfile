# == Default options
# size: 8(pt)
# font: MonaspiceNe NFM, Sarasa Mono SC

set dotenv-load

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

# == mark (A6)
a6 path size="" font="":
    uv run scripts/gen_a6.py "{{path}}" \
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

# == favorite-image (polario frame)
polario mode image text-first text-second text-third start resize size:
    uv run scripts/gen_polario.py {{mode}} "{{image}}" "{{text-first}}" "{{text-second}}" "{{text-third}}" "{{start}}" "{{resize}}" "{{size}}"