---
name: marks-pipeline
description: Use when working with the marks Typst publishing pipeline — gen_*.py build scripts, .justfile recipes, .typ templates, or cmarker integration. Does not cover authoring content files (post/, receipt/, etc.).
---

# marks Publishing Pipeline Conventions

## Rules

- **Output dir:** `<content>/_output/` (gitignored). Contains `typs/`, `pdfs/`, `*.jpg`.
- **Build:** `uv run scripts/gen_*.py` via justfile. Recipes: `a4`, `a42` (two-column), `a6`.
- **Python pattern:** PEP 723 inline metadata. `check_dependencies()` → `generate_typ()` → `typst compile --root <root>` → `magick -density 150 -quality 90 ..._p%02d.jpg` → cleanup.
- **cmarker:** `@preview/cmarker:0.1.9`. `read()` path relative to `.typ`, `--root` to project root.
- **Defaults:** size=8pt, font="MonaspiceNe NFM, Sarasa Mono SC".
- **Deps:** typst, magick (ImageMagick), uv, upscayl-bin (optional, Windows only).

## Key Decisions

- `POST_IMAGES_SOURCE` env var for local image resolution. Falls back to `post/assets/` when not set.
- Image upscale via `upscayl-bin` (model `4xLSDIR`) when width < 800px. Pillow for dimension check.
- Two-column: `#grid(columns: (1fr, 1fr))`. Smart stem: `article.md` + `article.zh-cn.md` → `article_zh-cn`.
