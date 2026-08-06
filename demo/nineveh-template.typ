// https://typst.app/universe/package/oasis-align
#import "@preview/oasis-align:0.3.3": *
// https://typst.app/universe/package/libra
#import "@preview/libra:0.1.0": balance

#let nineveh-layout(doc) = {
  set page(paper: "a6", flipped: true, margin: 2%)
  set text(font: "Sarasa Mono SC", size: 8pt)
  set grid(column-gutter: 1em)
  set figure(numbering: none)
  doc
}

#let und1(text) = underline(background: true, evade: false, offset:0.8pt , stroke: 0.6pt + black, text)
#let und2(text) = strike(background: false, stroke: 0.6pt + white, text)