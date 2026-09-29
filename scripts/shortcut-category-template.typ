// Final 4-up landscape A4 shortcut cheatsheet template.
// Content flows top-to-bottom within each column, columns ordered left-to-right.

#let divider() = {
  v(.1em)
  line(stroke: 0.6pt, length: 100%)
  v(.1em)
}

#let shortcut-category-layout(doc, size: 6pt, font: ("Sarasa Mono SC",)) = {
  set page(
    paper: "a4",
    flipped: true,
    margin: (x: 6pt, y: 10pt),
    columns: 5,
    numbering: "1",
    number-align: center,
  )
  set text(font: font, size: size)
  set par(spacing: .35em, justify: false)
  set heading(outlined: false)
  show heading.where(level: 1): it => block(
    above: .5em,
    below: .25em,
    breakable: false,
  )[
    #text(size: size * 1.4, weight: "bold", it.body)
  ]
  show table.cell: it => context {
    let indent = measure(text("  ")).width
    par(hanging-indent: indent, leading: 0.5em, it.body)
  }
  doc
}
