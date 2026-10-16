set dotenv-load

a6 path size="" font="":
    uv run scripts/gen_a6.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

## 2-columns
a4 path:
    uv run scripts/gen_a4_latex.py "{{path}}"
a4dual en zh:
    uv run scripts/gen_a4_dual_latex.py "{{en}}" "{{zh}}"
# just a4dual post/file.en.md post/file.zh-cn.md

## a6 / a6, dynamic height
nineveh path *flags:
    {{ if path =~ '[.]typ$' { "uv run scripts/gen_byya_nineveh_typ.py" } else { "uv run scripts/gen_byya_nineveh_md.py" } }} "{{path}}" {{ flags }}
# just nineveh <subdir> [--source <dir>] [--force] [--no-compile]  (.md, via BYYA_SITE_DOCS)
# just nineveh path/to/file.typ  (.typ)
nineveh-annex path size="" font="":
    uv run scripts/gen_byya_nineveh_annex.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}
lyra subdir size="" font="":
    uv run scripts/gen_byya_lyra.py "{{subdir}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}
lyra-annex path size="" font="":
    uv run scripts/gen_byya_lyra_annex.py "{{path}}" \
        {{ if size != "" { "--size " + size } else { "" } }} \
        {{ if font != "" { "--font \"" + font + "\"" } else { "" } }}

## a7
receipt *args:
    uv run scripts/gen_a7_receipt.py {{ args }}
# just receipt receipt/file.typ [--size 9pt] [--font ".."]
# just receipt receipt/file.typ --rotate [--width ..]
# just receipt --include receipt/file1.typ receipt/file2.typ ... [--a5]

polario mode image text-first text-second text-third start resize size:
    uv run scripts/gen_polario.py {{mode}} "{{image}}" "{{text-first}}" "{{text-second}}" "{{text-third}}" "{{start}}" "{{resize}}" "{{size}}"

image-convert mode theme output image="" commands="" *flags:
    uv run scripts/image-convert.py '{{mode}}' '{{theme}}' \
        {{ if image != "" { "--image '" + image + "'" } else { "" } }} \
        {{ if commands != "" { "--commands '" + commands + "'" } else { "" } }} \
        --output '{{output}}' {{ flags }}
# just image-convert portrait light "name" "assets/img.jpg" "magick $1 ... $2" [--no-run]

ctan path:
    uv run scripts/gen_ctan.py --compile "{{path}}"

shortcut *args:
    uv run scripts/gen_shortcut.py {{ args }}