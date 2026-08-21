# LaTeX demo recipes.
# Run these from inside latex-demo/ or via `just -f latex-demo/.justfile ...`.

# Compile a single demo. Accepts a stem or a .tex path.
compile path:
    uv run "{{ justfile_directory() }}/../scripts/gen_latex_demo.py" --compile "{{path}}"

# Compile every *-demo.tex file in this directory.
all:
    uv run "{{ justfile_directory() }}/../scripts/gen_latex_demo.py" --compile-all
