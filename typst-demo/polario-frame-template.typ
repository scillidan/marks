// https://typst.app/universe/package/polario-frame
#import "@preview/polario-frame:1.0.0": *

#let render-polario(params) = {
  set page(fill: black, margin: 2%, flipped: params.flipped)
  let img = crop(bytes(read(params.img-path, encoding: none)), start: (0%, 0%), resize: 100%)
  render((100%, 100%), theme: params.theme, img: img, ext-info: params.ext-info)
}