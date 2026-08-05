#let lyra-layout(size: 8pt, font: ("MonaspiceNe NFM", "Sarasa Mono SC"), doc) = {
  set page(paper: "a6", margin: 5%)
  set text(font: font, size: size)
  set par(justify: true)
  show raw.where(block: false): set text(font: font, size: size)
  show raw.where(block: true): set text(font: font, size: 0.9em)
  // Level-2 headings (##) render only slightly larger than the A6 body text.
  show heading.where(level: 2): set text(size: size + 1pt)
  doc
}
