#let mode = sys.inputs.at("mode", default: "portrait")
#let theme = sys.inputs.at("theme", default: "dark")
#let image-path = sys.inputs.at("image", default: "")
#let commands = sys.inputs.at("commands", default: "")

#let bg = if theme == "light" { white } else { black }
#let fg = if theme == "light" { black } else { white }

// Layout: fixed page width, equal border on all sides, image fills content
// width. The image is pre-sized in Python so Typst does not have to resample.
#let page-width = if mode == "landscape" { 210mm } else { 148mm }
#let border = 5pt

#set page(
  width: page-width,
  height: auto,
  fill: bg,
  margin: border,
)

#let annotation = if commands != "" {
  box(
    width: 100%,
    fill: bg,
    inset: 5pt,
    text(
      font: "Sarasa Mono SC",
      size: 11pt,
      fill: fg,
    )[
      #commands.split("\n").join(parbreak())
    ],
  )
}

#stack(
  spacing: 2.5pt,
  if image-path != "" { image(image-path, width: 100%) },
  annotation,
)
