// Single-software shortcut cheatsheet template.
// Width = 1/4 A4 portrait (52.5 mm); height grows with content (receipt style).

#let divider() = {
  v(.1em)
  line(stroke: 0.6pt, length: 100%)
  v(.1em)
}

#let shortcut-software-layout(doc, size: 6pt, font: ("Sarasa Mono SC",)) = {
  set page(
    width: 52.5mm,
    height: auto,
    margin: (x: 3pt, y: 4pt),
  )
  set text(font: font, size: size)
  set par(spacing: .35em, justify: false)
  set heading(outlined: false)
  show heading.where(level: 1): it => block(above: .5em, below: .25em)[
    #text(size: size * 1.4, weight: "bold", it.body)
  ]
  show table.cell: it => context {
    let indent = measure(text("  ")).width
    par(hanging-indent: indent, leading: 0.5em, it.body)
  }
  doc
}
