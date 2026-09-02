#import "polario-frame-template.typ": render-polario

#let ext-info = (
  "background": rgb("#00000000"),
  "first": text(size: 8pt, fill: white)[
    Text on the left \
    Text on the left
  ],
  "third": text(size: 12pt, fill: white)[
    Text on the right \
    Text on the right
  ],
)

#let params = (
  "theme": "classic-bottom-three",
  "flipped": true,
  "img-path": "/assets/Edward John Poynter_Pea Blossoms, 1890.jpg",
  "ext-info": ext-info,
)

#render-polario(params)
