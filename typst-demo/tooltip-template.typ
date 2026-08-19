// https://typst.app/universe/package/oasis-align
#import "@preview/oasis-align:0.3.3": *
// https://typst.app/universe/package/tblr
#import "@preview/tblr:0.5.0": *

#let tooltip-layout(doc) = {
  set page(paper: "a7", height: auto, margin: (x: 4pt, y: 8pt))
  set text(font: "Sarasa Mono SC", size: 8pt)
  set par(spacing: .6em, justify: true)
  set figure(numbering: none)
  set figure.caption(position: top)
  doc
}

#let parbreak = {
  v(.1em)
  line(stroke: 1pt, length: 100%)
  v(.1em)
}

#let indent(content) = {
  h(2em)
  content
}

#let custom-quote(content) = {
  pad(x: 1em, y: 0.1em)[
    #content
  ]
}