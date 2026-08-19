#import "codly-template.typ": *
#show: codly-init.with()

#let code = read("tooltip-template.typ")

#raw(lang: "typst", block: true, code)