// References:
// Authors: MiniMax-M2.1🧙‍♂️, scillidan🤡

#let src = sys.inputs.at("path", default: "/assets/Avalon (Sieren Remix) - Equador.lrc")
#let title = sys.inputs.at("title", default: "Avalon (Sieren Remix)")
#let artist = sys.inputs.at("artist", default: "Equador")

#let rawContent = read(src)
#let processLines(text) = {
  text
    .split("\n")
    .map(line => {
      line.replace(regex("^\[.+?\]"), "").trim()
    })
    .join("\n")
}
#let content = processLines(rawContent)

#set text(font: ("MonaspiceNe NFM", "Sarasa Mono SC"), size: 9pt)

#if title != "" [
  #text(weight: "bold", size: 2.5em, title)
  #linebreak()
  #v(0.5em)
]
#if artist != "" [
  #text(weight: "bold", style: "italic", size: 2em, artist)
  #linebreak()
  #v(1em)
]

#set par(leading: 0.76em, spacing: 1.5em)
#set text(font: ("MonaspiceNe NFM", "Sarasa Mono SC"), size: 1.3em * 1.25)

#for line in content.split("\n") {
  line
  linebreak()
}
