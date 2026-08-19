// https://typst.app/universe/package/its-scripted/
#import "@preview/its-scripted:0.1.0": *

#show: screenplay.with()

// creates the title page

#maketitle(
  title: "When John met Jane",
  authors: "John H. Doh",
  date: datetime.today(),
  draft: 1,
  info: [
    John Harrison Doh \
    john.doh\@email.com \
    2697 Blane Street, Saint Luis, Missouri
  ]
)

// scenes are divided by headings:

= INT. COFFEE SHOP - DAY

The coffee shop is bustling with people. A soft murmur of conversations fills the air. At a corner table, JANE, late 20s, sits alone, sipping her coffee while staring at her laptop screen. She seems lost in thought.

// dialog can be created using the `dialog` function:

#dialog[
  // use sub-headings for character names
  == JANE

  I just... I just need to finish this.

  She types a few words, hesitates, and deletes them. She sighs in frustration.
]

JOHN (30s), dressed casually, walks into the coffee shop. He scans the room for a place to sit. His eyes land on the empty seat across from Jane. He approaches her table.

#dialog[
  == JOHN

  // use the `parenthetical` for parentheticals
  #parenthetical[Hesitant]

  Can I seat here?
]

#dialog[
  == JANE

  Oh, um... sure.
]


Suddenly a PTERODACTYL flies through the coffee-shop window.

// pass multiple parameters to the `dialog` function for multiple pieces of dialog happening at once
#dialog[
  == JOHN

  Ahh! What's that!
][
  ==  JANE

  What the hell?
]

//  use the close functions for act/script endings

#close[TO BE CONTINUED]