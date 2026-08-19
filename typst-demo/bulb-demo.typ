// https://typst.app/universe/package/bulb
#import "@preview/bulb:0.1.0": dither

#set page(paper: "a4", flipped: true, margin: 1%)
#set text(font: "Sarasa Mono SC", size: 8pt)
#set figure(numbering: none, gap: 6pt)

#let modes = (
  (mode: "rgb", method: "bayer2x2"),
  (mode: "rgb", method: "bayer4x4"),
  (mode: "rgb", method: "bayer8x8"),
  (mode: "rgb", method: "cluster4"),
  (mode: "rgb", method: "cluster6"),
  (mode: "rgb", method: "cluster8"),
)
#let img-data = read("assets/Edward John Poynter_Pea Blossoms, 1890.jpg", encoding: none)

// Fit an image (raw bytes) into an area while preserving its aspect ratio.
#let fit-image(data, width, height) = image(data, width: width, height: height, fit: "contain")

#let title-block = pad(top: 20pt, align(center, text(size: 10pt)[
  Typst Package: bulb \
  Version: 0.1.0 \
  Author: Edward John Poynter \
  Sample Image: Pea Blossoms (1890)
]))

// Page 1: 3x2 thumbnail grid + title, sized so everything fits the page.
#layout(size => {
  let col-gutter = 4pt
  let outer-gutter = 20pt
  let inner-gutter = 8pt
  let fig-gap = 6pt
  let pad-y = 10pt
  let col-w = (size.width - 2 * col-gutter) / 3

  let captions = modes.map(((mode, method)) => block(width: col-w, text([mode: #raw(mode),  method: #raw(method)])))
  let cap-h = measure(captions.first()).height

  let title-h = measure(title-block).height
  let grid-h = size.height - title-h - 2 * outer-gutter
  let row-h = (grid-h - inner-gutter) / 2
  let img-h = calc.max(row-h - pad-y - fig-gap - cap-h, 0pt)

  let thumbnails = modes.map(((mode, method)) => {
    figure(
      pad(top: 5pt, bottom: 5pt, fit-image(dither(img-data, mode: mode, method: method), col-w, img-h)),
      caption: [mode: #raw(mode),  method: #raw(method)],
    )
  })

  block(height: 100%, align(center + horizon,
    grid(
      columns: (1fr, 1fr, 1fr),
      column-gutter: col-gutter,
      row-gutter: outer-gutter,
      grid.cell(colspan: 3,
        grid(
          columns: (1fr, 1fr, 1fr),
          align: center,
          column-gutter: col-gutter,
          row-gutter: inner-gutter,
          ..thumbnails,
        )
      ),
      title-block,
      grid.cell(colspan: 2)[],
    )
  ))
})

// One page per dither mode: single figure, image fitted to the page height.
#for (mode, method) in modes [
  #pagebreak()
  #layout(size => {
    let cap = [mode: #raw(mode),  method: #raw(method)]
    let fig-gap = 20pt
    let cap-h = measure(block(width: size.width, text(size: 16pt, cap))).height
    let img-h = calc.max(size.height - cap-h - fig-gap, 0pt)
    block(height: 100%, align(center + horizon,
      text(size: 16pt,
        figure(
          fit-image(dither(img-data, mode: mode, method: method), size.width, img-h),
          caption: cap,
          gap: fig-gap,
        )
      )
    ))
  })
]
