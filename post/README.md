# post/ 排版说明

本目录下的 `.md` 文件通过 `scripts/gen_a4.py` 渲染成 A4 双栏 PDF。

## 图片默认行为

- 所有图片宽度固定为单栏的 **90%**，并居中显示。
- 带 caption 的图片（`<figure>`）会自动浮动，文字会绕排，以减少栏底留白。

## 手动分栏（减少留白）

如果某页双栏底部出现较大空白，可以在 Markdown 中手动插入分栏符：

```md
一些文字...

<!--raw-typst #colbreak(weak: true)-->

更多文字...
```

`weak: true` 表示如果当前已经在栏首，则不会强制空出一栏，比较安全。

**放在哪里？** 放在你希望“当前栏在此结束，后续内容从下一栏开始”的位置。

## 图片通栏（跨双栏）

对于特别高、单栏放不下的图，可以手动让它跨双栏显示：

```md
<!--raw-typst #place(top + center, scope: "parent", float: true)[
  #figure(image("images/xxx.jpg", width: 90%), caption: [图片描述])
]-->
```

这里的 `width: 90%` 是相对于整页宽度，因此图会按等比变矮。

## 注意事项

- `<!--raw-typst ...-->` 是 cmarker 的语法，只在通过 Typst 渲染时生效；普通 Markdown 预览会把它当成普通 HTML 注释忽略。
- 图片路径相对于最终生成的 `.typ` 文件。通常使用 `images/xxx.jpg`（gen_a4.py 会自动把 `post/assets/` 下的图片复制到 `_output/_temp/images/`）。
