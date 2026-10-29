// Shortcut cheatsheet templates (mirror scripts/receipt-template.typ).
//
// Two layouts sharing one body style:
// - shortcut-layout:      single-software narrow strip (width = 1/4 A4
//                         portrait, 52.5 mm); height grows with content
//                         (receipt style).
// - shortcut-a4-layout:   aggregate landscape A4, content flowing
//                         top-to-bottom within each column, columns ordered
//                         left-to-right.

#let divider() = {
  v(.1em)
  line(stroke: 0.6pt, length: 100%)
  v(.1em)
}

// Shared body styling for both layouts (single strip and aggregate A4).
#let shortcut-style(doc, size: 6pt, font: ("Sarasa Mono SC",)) = {
  // Disable ligatures: shortcuts must show each key character exactly.
  // `ligatures: false` covers liga/clig; `calt: 0` covers contextual
  // alternates, which programming fonts (e.g. Sarasa Mono) use for ligatures.
  set text(font: font, size: size, ligatures: false, features: (calt: 0))
  set par(spacing: .35em, justify: false)
  set heading(outlined: false)
  show heading.where(level: 1): it => block(
    above: .5em,
    below: .25em,
    breakable: false,
  )[
    #text(size: size * 1.4, weight: "bold", it.body)
  ]
  // Keep the line pitch inside a wrapping cell equal to the pitch between
  // table rows. 0.2em let descenders (j/g/p/q/y) touch the next line's
  // ascenders; 0.275em is the largest value that still keeps the 245-entry
  // Neovim preview on one A4 page. row-gutter in gen_shortcut.py uses the
  // same 0.275em.
  show table.cell: it => context {
    let indent = measure(text("  ")).width
    par(hanging-indent: indent, leading: 0.275em, it.body)
  }
  doc
}

#let shortcut-layout(doc, size: 6pt, font: ("Sarasa Mono SC",)) = {
  set page(
    width: 52.5mm,
    height: auto,
    margin: (x: 3pt, y: 4pt),
  )
  show: shortcut-style.with(size: size, font: font)
  doc
}

// Aggregate layout: landscape A4 flowing into N columns.
#let shortcut-a4-layout(doc, size: 6pt, font: ("Sarasa Mono SC",), columns: 5) = {
  set page(
    paper: "a4",
    flipped: true,
    margin: (x: 6pt, y: 10pt),
    columns: columns,
    numbering: "1",
    number-align: center,
  )
  show: shortcut-style.with(size: size, font: font)
  doc
}
