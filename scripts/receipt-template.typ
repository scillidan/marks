// https://typst.app/universe/package/glossy
#import "@preview/glossy:0.9.1": *
// https://typst.app/universe/package/itemize
#import "@preview/itemize:0.2.0" as el

#let short-long-term(mode, short-form, long-form) = {
    // Force short mode by default, ignoring the first-use "both" behavior
    let m = if mode == none or mode == "" or mode == "both" { "short" } else { mode }
    if m == "short" { short-form }
    else if m == "long" { long-form }
    else {
      short-form + " (" + long-form + ")"
    }
  }

#let resume-enum(doc) = el.default-enum-list(auto-resuming: auto)[
  #el.auto-resume-enum(auto-resuming: true, doc)
]

#let divider() = {{
  v(.1em)
  line(stroke: 1pt, length: 100%)
  v(.1em)
}}

#let indent(content) = {
  h(2em)
  content
}

#let receipt-layout(doc, size: 8pt, font: ("Sarasa Mono SC",), rotate: false, width: none) = {
  let page-width = if rotate {
    if width == none { 105mm } else { width }
  } else { 74mm }
  set page(
    width: page-width,
    height: if rotate { 74mm } else { auto },
    margin: if rotate { (x: 8pt, y: 4pt) } else { (x: 4pt, y: 8pt) },
  )
  set text(font: font, size: size)
  set par(spacing: .6em, justify: true)
  show terms.item: it => {
    pad(left: 1.5em)[
      #par[
        #text(weight: "regular")[#it.term]
        #it.description
      ]
    ]
  }
  show: init-glossary.with(yaml("receipt-measure.yaml"), term-links: true, format-term: short-long-term)
  doc
}