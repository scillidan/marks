// https://forum.typst.app/t/how-to-force-line-breaks-without-extra-spaces/4091

#set page("a6", flipped: false, margin: 5%)
#set text(font: "Monaspace Neon Frozen", size: 8pt)

#show raw.where(lang: "poem"): it => {
  set par(leading: 0.76em, spacing: 1.5em)
  set text(font: "Monaspace Neon Frozen", size: 1em * 1.25)
  set raw(theme: none)
  let space-width = 0.5em
  block(
    inset: (x: 2em, y: 1em),
    eval(
      it.text
        .replace(regex("\n\n+"), "#parbreak()")
        .replace(regex("\n( *)"), (i) => {
          "\ "
          if i.captures.at(0).len() > 0 { "#h(" + repr(i.captures.at(0).len() * space-width) + ")" }
        }),
      mode: "markup",
      scope: (
        :
        // add whatever you need here
      )
    )
  )
}
```poem
*Avalon (Sieren Remix) - Equador*

Somewhere there's an island
Our elusive remedy
Tip toe through the fire
Never come down
'Til we all fall down

Let's get back to where we're from
Brighter days of halcyon
Can we come back from where we've gone, gone
Back to Avalon

Somewhere there's a garden
Our mistaken fantasy
Everything's forgotten
Never come down
'Til we all fall down

Let's get back to where we're from
Brighter days of halcyon
Can we come back from where we've gone, gone
Back to Avalon
Back to Avalon

We're chasing footsteps where we begun
They take us back to, back to Avalon
We're chasing footsteps where we begun
They take us back to, back to Avalon
Back to Avalon
```
