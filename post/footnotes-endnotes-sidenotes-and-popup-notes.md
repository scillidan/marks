```
Date: 2018.05.29
Author: Chris Jennings
Source: https://www.publisha.org/pages/footnotes/
```

# Footnotes, Endnotes, Sidenotes and Popup Notes

I start with a quote from Robert Bringhurst in his _The Elements of Typographic Style_[^1]

> …the academic habit of relegating notes to the foot of the page or the end of the book is a mirror of Victorian social and domestic practice, in which the kitchen was kept out of sight and the servants were kept below stairs. If the notes are permitted to move around in the margins as they were in Renaissance books they can be present where needed and at the same time enrich the life of the page.

In _The Elements of Typographic Style_, the notes are held in the side margins thus putting the information near and even alongside the reference in the text. Robert Bringhurst doesn’t need to bother with those little superscript numbers because the supplementary information is very much nearby for the reader.

Still, tradition dictates that in some books, there are footnotes and some there are endnotes (either at the end of the chapter or the end of the book). Putting notes in the side margins is nice if you can afford the space. Let’s face it, book design and usability does not often win-out over commercial considerations. Robert Bringhurst’s book is exceptional and it is a beautiful thing. Lots of space for the text to breath.

How I dislike some books that give me less than a centimetre of margin.

## Footnotes

These need to be separated from the main body of the text, and are best set with a smaller size and possibly event a different typeface and colour. The idea of any notes is that it is supplementary information and it is entirely optional that the reader even bothers to look, so setting in a style that does not distract from the flow of the reading experience is important.

![Here we see the example of the first footnote in the chapter and the reference number  in the text.](assets/footnotes-endnotes-sidenotes-and-popup-notes_01.png)  
Here we see the example of the first footnote in the chapter and the reference number in the text.

Footnotes are best numbered with an outdented figure, although (for technical reasons) the numbers are most often aligned to the main text block. These numbers refer to the superscript number within the text itself. Most publishers will favour the numbers to begin again for each chapter, otherwise the numbers could get unwieldy (superscript numbers of more than two digits could look ugly). If there are very few references in the text, symbols can be used instead of numbers (\* or †, ‡, §, ‖,¶).

The listed footnotes will look best when separated from the main body with a partial line; giving the reader a strong clue that these notes are not following on from the text above. Where footnotes are long, they can be split across more than one page, although this will compromise the usability somewhat.

## Endnotes

Notes are often placed at the end of the chapter or even at the end of the book (before the index). This approach means that the reader will need to ‘hunt down’ the note referred to in the text.

This usually means that the endnotes will be organised by chapter or section.

The advantage of endnotes over footnotes is that the page composition in the vertical plane is not compromised for the sake of the note space.

Where there are lots of references in the text, this must be the best approach.

Ridiculous as this seems, we have seen books with footnotes that take more page space than the main text itself!

## Sidenotes (sometimes called Margin Notes)

Clearly the page layout needs to provide the space in the margins for this to be an option. Unless this is a large-format book, the measure of the notes (width of the text), is likely to be narrow, so don’t design for this option if the notes are long or there are lots of them and, the book is small.[^2]

**Sidenotes** fall outside the text block unlike footnotes that will be inside the text block.

Sidenotes do not necessarily need superscript numbers within the text (and they themselves do not need to be numbered), if it is obvious what the sidenote refers to.

## Footnotes with InDesign

**InDesign** will help us build footnotes and the software will even import the footnotes from Microsoft Word. InDesign users get their very own configuration panel seen in the image alongside here. In this we can set the way the references are displayed in the text (superscript etc), and how the footnotes appear at the bottom of the page. We need a paragraph style set up for the display of the footnotes themselves and we can (optionally), use a character style for the reference figure in the text.

![InDesign dialogue for controlling the display of the footnotes](assets/footnotes-endnotes-sidenotes-and-popup-notes_02.png)  
InDesign dialogue for controlling the display of the footnotes

As you can see from the first example spread the footnote list figure is aligned to the left edge of the text box. You will often see this in the books on your shelves, however, a more attractive arrangement is to ‘outdent’ these listed figures so that the footnotes are are aligned to the text and the number figures are offset from this text box.

![The layout of the footnotes is controlled through the second tab](assets/footnotes-endnotes-sidenotes-and-popup-notes_03.png)  
The layout of the footnotes is controlled through the second tab

InDesign does **not** provide the means to set footnotes outside the text box, so we need to plan for this by indenting all of the text inside the text box by an amount that we then remove from the left margins. This way we can outdent the footnote numbers. You will see from the image provided here that we are using guides to make sure that these items align. My footnote style is using a 4mm offset for the numbers and my paragraph styles are using a 4mm indent.

![Here we see an enlargement of the page in InDesign. The numbers are now outdented from the left edge of the body text](assets/footnotes-endnotes-sidenotes-and-popup-notes_04.png)  
Here we see an enlargement of the page in InDesign. The numbers are now outdented from the left edge of the body text

You will notice that there is no option to change these footnotes into endnotes; for this we need a script.

## Endnotes with a Script

To do this we need to turn to [Peter Kahrel](http://www.kahrel.plus.com/indesign/footnotes.html "see this web site for scripting InDesign") who provides many useful scripts. The one that I use here is called ‘convert footnotes to (dynamic) endnotes’ meaning that the numbering will change if further notes are added.

As always when using scripts to change content, save your work first! Scripts will often run through a long sequence of actions; you can always use ‘revert’ (from the file menu), to get back to the previous.

You will see from the image here that the endnotes have their own page(s) with a heading that matches other heading styles. You may need to tweak the paragraph styles for the notes and their listed numbers.

![Endnotes at the end of the chapter.](assets/footnotes-endnotes-sidenotes-and-popup-notes_05.png)  
Endnotes at the end of the chapter.

## Sidenotes with a Script

Once again,Peter Kahrel will help us (please make a donation on his site) with a set of scripts. Using these we can control the width and position as the footnotes are converted to side notes. Each note comes in it’s own text frame which is anchored at the reference point. You will see in the example spread given here that I have turned off the numbering. This is an option in the script dialogue. There may be the need to move text boxes vertically, where references are near to one another; some degree of hand crafting will be required.[^3]

![A spread with side notes. You see that the text alignment (left or right), is automatic depending on recto or verso achieved by the paragraph style using Towards the Spine.](assets/footnotes-endnotes-sidenotes-and-popup-notes_06.png)  
A spread with side notes. You see that the text alignment (left or right), is automatic depending on recto or verso achieved by the paragraph style using Towards the Spine.

## Notes in eBooks

Footnotes are no good for reflowable eBooks! You don’t actually have a page bottom. There are various choices for eBooks depending on the type, the proposed platform and the pBook to eBook workflow.

### For the reflowable eBook

When you export from InDesgn to ePub (reflowable), you have an option to convert your _footnotes_ to pop-up notes. This will take the notes from the foot of the page, wrap them in an HTML tag `<aside>` and add thenecessaryePub3 classes in the XHTML code. In fact you will get an attribute added to the hyperlinked number:

`epub:type="noteref"`

and then the footnote reference will be wrapped in the `<aside>` tag.

![Pop-up notes using Apple iBooks on the MAC](assets/footnotes-endnotes-sidenotes-and-popup-notes_07.png)  
Pop-up notes using Apple iBooks on the MAC

### Finger Friendly Hyperlinks

You may find that removing the superscripted reference number (traditional in book design) and making the whole line into a hyperlink, would improve usability.

So instead of this:

```
<p>To death, or to a vow of single life.<a href=""><span class="reference">1</span></a></p>
```

We do this:

```
<p><a class=reference epub:type="noteref" href="dream-116.xhtml#footnote-002">To death, or to a vow of single life. </a></p>
```

With some further adjustments to the `CSS` for the reference class of hyperlink, we can see the result.

![The hyperlink now comes from text not just a reference number](assets/footnotes-endnotes-sidenotes-and-popup-notes_08.png)  
The hyperlink now comes from text not just a reference number

This really is much better that our original superscript numbers. What we have done here could equally apply to the reflowable form of the ePUB3 format.

> **Note:** It is not possible currently to modify the style of the popup text in Apple iBooks.

In other eReaders such as Adobe Digital Editions the hyperlink works as expected, by taking the reader to the notes page.

The pop-up note reference is supported by Apple in their iBooks app for MACs and iOS on tablets etc. It is also [documented](https://github.com/kobolabs/epub-spec#footnotesendnotes-are-fully-supported-across-kobo-platforms) that later Kobo devices also support pop-up notes.

It is also supported on later models of the Kindle when an ePub is converted to the MOBI format.

Other devices and software that cannot support pop-up notes will simply function as hyperlinks to the list of notes at the end of the chapter or section.InDesign does not do us any favours though, because the list of notes loses it’s numbering and the backlink does not work.

What can we do about this?

### Fixing the ePUB footnotes for all systems

Solving the backlink problem can be done in 2 ways:

We can export from InDesign as for pop-up notes, and then post edit the ePub file by adding the numbers into the notes list. You will find XHTML markup that looks something like the following:

```
<aside id="footnote-003"class="_idFootnote" epub:type="footnote"> <p class="footnotes"><a class="_idFootnoteAnchor_idGenColorInherit" href="introduction.xhtml#footnote-003-backlink"></a>
  John Shakespeare's father, Richard Shakespeare, was a tenant farmer,who wasin1550 renting his little farm at Snitterfield, four miles north of Stratford,from another farmer, Robert Arden of Wilmcote.</p>
</aside>
```

If you look carefully, you will see that the link tag ends before any content. It should be wrapping around the number. We can add the number before the `</a>` however, this is not a bulleted list and so we need a space as well. This is a solution, although could be rather an onerous task is you have a lot of footnotes.

**Here is another way**

Rather than export from InDesign with the pop-up note option, choose the ‘End of Section (Endnotes)’ option. This will work properly for those systems that do not support pop-up notes. In iBooks (Apple systems), the hyperlinked number will take us to the notes section at the end of the chapter. If we want to get pop-up notes working on those systems that support it we will need to crack open the ePUB and make some changes.

#### Editing the ePUB from the Endnotes Version

Once you have unpacked the ePUB (actually I prefer to do this with BBedit no unpacking required), you can search for:

`<a class="_idFootnoteLink`

and replace with:

`<a epub:type="noteref"class="_idFootnoteLink`

If you do this then the pop-up will work BUT you will also see that the notes are still listed at the end of the chapter. Personally I actually prefer this, because we can get a second chance to read through the notes.

![Showing both pop-up and list of notes at the end of the chapter.](assets/footnotes-endnotes-sidenotes-and-popup-notes_09.png)  
Showing both pop-up and list of notes at the end of the chapter.

If you prefer **not** to see this list of notes, then you will need to wrap each note in the `<aside>` tag, and we can do this by search and replace but this time using GREP.

GREP Find this:

`<div( id="footnote-.+\s+.+\s+)</div>`

and replace with

`<aside\1</aside>`

You may also want to remove the horizontal line `<hr>` above the notes list.

## Notes for the Fixed Layout eBook

If you are an InDesign CC user planning to export a fixed-layout ePUB and you have footnotes in your document, you might be disappointed to notice that there is no option to make these footnotes become popup notes using the ePUB3 standard `epub:type`.

In the export to ePUB(reflowable) options we can select the popup type, but not for the fixed layout. Your footnotes will remain exactly where they are on the page. Disappointing no?

InDesign will expect the footnotes to be in the same XHTML file where they are referenced. There are some settings in InDesign, but nothing will help us convert them to invisible notes that are only seen in a popup.

Is there a solution while we wait for Adobe to release another version of InDesign?

### Move the Footnotes

We need our references to come off the bottom of the page and be on their own page at the end of the book.

![The notes are at th endo of the eBook under their own heading but they also work as popup notes.](assets/footnotes-endnotes-sidenotes-and-popup-notes_10.png)  
The notes are at th endo of the eBook under their own heading but they also work as popup notes.

InDesign does not have any configuration that provides this so we need to use a script. There is one available from Peter Kahrel. On his site he credits others too, but the one you need is called Footnotes to Endnotes. [You can grab it here](http://www.kahrel.plus.com/indesign/footnotes.html "Thanks to Peter Kahrel").

### Locate the References in the text

If you locate one of your references in the `HTML` markup you will find an empty hyperlink and no mention of the correct `epub:type` for the ePUB3 format.

We will need to go to the last page in the ePUB to add the correct ePUB3 signals for the eBook format to get the correct message!

So, in the final page we need to have a look at the destination references and where we find this:

```
<li class="footnotes-numbered"><a id="_idTextAnchor032"></a>
```

We need to add the `<aside>` block inside the list item like this:

```
<li class="footnotes-numbered"><a id="_idTextAnchor032"></a> <aside id="footnote-001" epub:type="footnote">
```

Not forgetting to close the `<aside>` tag before the `</li>`.

You will need to number all of your references footnote-001, footnote-002 etc. _I don’t know an easy way to do this yet._

The next step is to locate the hyperlinked references in the text. If you have correctly exported a reliable tag name from InDesign, then you can use your editor (I use Atom) to search for

`<span class="reference`

We now need to go through this markup in turn and add the following:

`<a epub:type="noteref" href=dream-116.xhtml#footnote-001">`

in the place of the empty `<a>` tag.

The footnote reference has a number; you need to increment this appropriately.

### Footnotes for the Kindle

Some Kindles (Paperwhite) now support poup notes (although this is not exactly a floating window), but as I write, if you use InDesign and opt for footnotes to become popup notes then you will NOT get popup notes on the Kindle. You will get a link to the references at the end of the chapter, and also the numbers are gone.

This is one of those situations where forking a slightly different version of the ePub for the Kindle may be necessary.

We can’t finish this article without mentioning _iBooks Author_.

iBooks Author is free software from Apple for iOS designed to create ‘multi-touch’ ebooks. You can read more about using this software [here](https://www.publisha.org/pages/iBooksAuthor/ "This page will help"), but regarding adding notes; you will need to familerise yourself with the Glossary feature, which allows the direct input of text (and images) to provide popup references.

![Here we see entry for glossary that becomes a popup](assets/footnotes-endnotes-sidenotes-and-popup-notes_11.png)  
Here we see entry for glossary that becomes a popup

The glossary term is provided in a popup box and the text can be styled. Once a glossary term has been created, other references can be made to the same glossary term.

![This glossary term is long so a scrollbar appears.](assets/footnotes-endnotes-sidenotes-and-popup-notes_12.png)  
This glossary term is long so a scrollbar appears.

[^1]: The Elements of Typographic Style, Bringhurst, Robert, Hartley & Marks, Publishers, 2012
[^2]: see Edward Tufte and [this thread on sidenotes](http://www.edwardtufte.com/bboard/q-and-a-fetch-msg?msg_id=0000ld)
[^3]: If you use the scripts mentioned here to put the notes in the margin or at the end of the book or chapter then your pop-up notes will not work in the reflowable eBook.