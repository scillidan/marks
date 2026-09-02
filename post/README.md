# post/ 排版说明

本目录下的 `.md` 文件通过 `scripts/gen_a4_latex.py` 渲染成 **A4 双栏 PDF**（xelatex + markdown 包），共用样式模板 `scripts/gen_a4_latex.tex`。

## 构建

```bash
just a4 latex post/a-history-of-microwave-ovens.md
# 或直接用 python：
python scripts/gen_a4_latex.py post/<文件>.md
```

输出：

- PDF：`_output/pdfs/<stem>.pdf`
- 预览图：`_output/<stem>_p*.jpg`
- 中间文件：`_output/latex/<stem>/`（body.md、images/、meta.tex、<stem>.tex wrapper）

## 图片默认行为

- 图片默认 **90% 栏宽、居中**（`maxwidth=0.9\linewidth`）。
- 超高竖图会被 fitbox 压缩或移到下一栏，尽量减少栏尾空白。
- webp / avif / gif 等格式会自动转成 jpg；`post/assets/` 是本地图片源（或用环境变量 `POST_SOURCE` 指定 CDN 图片目录）。

## Figure（带注释的图）

如果某张图**紧跟一段说明文字、且二者之间没有空行**（如 manual-spaces 文章），这段文字会被当作该图的注释，排版成：

- 图片正常显示；
- 注释收窄到约 80% 栏宽、整块居中，但注释文字本身左对齐（`\footnotesize`）。

```md
![](assets/xxx.png)
这里是图片注释，同一段落、紧跟图片。
```

## 连续图片

连续两、三张独立图片会两两成组、作为整体移动，避免“一张垫栏尾 + 大片空白 + 下一张在下一页开头”的断裂。

## 注意事项

- 图片路径在源 markdown 里写 `assets/xxx.jpg`，生成时会自动重写到中间目录。
- 样式（字体、标题大小、图片宽度、行距）都集中在 `scripts/gen_a4_latex.tex`，改它即可，不需要改 Python。
- 想手工微调某篇时，可改 `_output/latex/<stem>/<stem>.tex`（会被下次生成覆盖）。
