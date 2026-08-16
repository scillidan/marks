#import "tooltip-template.typ": *
#show: tooltip-layout

// https://www.dota2.com/hero/zeus
= Zeus
#v(.1em)
*Intelligence* \
*Attack Type* Ranged \
*Complexity* 1/3 \
None can hide from Zeus, whether he's calling down a bolt to reveal the surroundings, sending an arc coursing through his nearest enemies, or summoning a terrifying volley of lightning upon all enemies. Wherever his foes are, Zeus will find them.

#parbreak
[Attributes]
#align(horizon, oasis-align(force-frac: 0.45,
  [#table(stroke: none, inset: 2pt, align: left, columns: 3, column-gutter: .35em,
    [*Health*], [582], [+2.4],
    [*Mana*], [351], [+1.1])],
  [#table(stroke: none, inset: 2pt, align: left, columns: 3, column-gutter: .35em,
    [*Strength*], [21], [+2.1],
    [*Agility*], [11], [+1.2],
    [*Intelligence*], [23], [+3.3])]
))

#parbreak
[Roles]
#let data-roles = from-csv(delimiter: "|", "
Carry    | 0.3 | Support | 0 | Nuker     | 1
Disabler | 0   | Jungler | 0 | Durable   | 0
Escape   | 0   | Pusher  | 0 | Initiator | 0
")
#tblr(stroke: none, inset: 2pt, row-gutter: 0em, column-gutter: .75em, align: horizon,
  ..data-roles
)

#parbreak
[Stats]
#align(center, oasis-align(
  [#figure(
    table(stroke: none, inset: 2pt, align: (left, right), columns: 2,
      [*Damage*], [53-63],
      [*Attact Time*], [1.7],
      [*Attact Range*], [380],
      [*Projectile Speed*], [1100]),
    caption: [\(Attack\)]
  )],
  [#figure(
    table(stroke: none, inset: 2pt, align: (left, right), columns: 2,
      [*Armor*], [2.8],
      [*Magic Resist*], [25%]),
    caption: [\(Defense\)]
  )
  #figure(
    table(stroke: none, inset: 2pt, align: (left, right), columns: 2,
      [*Movement Speed*], [305],
      [*Turn Rate*], [0.6],
      [*Vision*], [1800/800]),
    caption: [\(Mobility\)]
  )]
))

#parbreak
[Abilities] \
#align(center)[\(Talent Tree\)]
#table(stroke: none, inset: 2pt, align: (left, horizon + center), columns: (9fr, 1fr),
  [3 Heavenly Jump Charges], table.cell(rowspan: 2)[25],
  [#h(2em)325 AoE Lightning, Bolt],
  [+0.5s Lightning Bolt Ministun], table.cell(rowspan: 2)[20],
  [#h(2em)+60 Arc Lightning Damage],
  [-20% Arc lightning Mana Cost / Cooldown], table.cell(rowspan: 2)[15],
  [#h(2em)+75 Thundergod's Wrath Damage],
  [+200 Health], table.cell(rowspan: 2)[10],
  [#h(2em)+1 Heavenly Jump Target],
)

#v(.1em)
#align(center)[\(Innate\)]
*Static Field* \
#indent[Zeus shocks any enemy that he attacks or is hit by his abilities, causing damage equal to a percentage of their current health.] \
#align(horizon, oasis-align(force-frac: 0.6,
  text(size: 0.85em)[Ability: Passive \
  Damage Type: Magical \
  Pierces Spell Immunity: No],
  text(size: 0.85em)[DAMAGE: 3.45]
))
#custom-quote([The air crackles with static when the Thundergod walks the world.])

#parbreak
[Ability Details]
#v(.5em)
*Arc Lightning* \
#indent[Hurls a bolt of lightning that leaps through nearby enemy units that deal damage.]
#align(horizon, oasis-align(force-frac: 0.55,
  text(size: 0.85em)[Ability: Unit Target \
  Affects: Enemy Units \
  Damage Type: Magical \
  Pierces Spell Immunity: No],
  text(size: 0.85em)[DAMAGE: 105/130/155/180 \
  JUMP RADIUS: 450 \
  JUMPS: 5/7/9/11]
))
#v(.1em)
#text(size: 0.85em)[Cooldown: 1.6 \
Mana Cost: 85/90/95/100]
#custom-quote([Arc Lightning is Zeus' favorite spell to use against puny mortals.])

#v(.5em)
*Lightning Bolt* \
#indent[Calls down a bolt of lightning to strike an enemy unit, causing damage and a mini-stun. When cast, Lightning Bolt briefly provides unobstructed vision and True Sight around the target in a 600 radius. Can be cast on the ground, affecting the closest enemy hero in 325 range.] \
#align(horizon, oasis-align(force-frac: 0.55,
  text(size: 0.85em)[Ability: Unit Target \
  Affects: Enemy Units \
  Damage Type: Magical \
  Pierces Spell Immunity: No],
  text(size: 0.85em)[DAMAGE: 140/220/330/380 \
  SIGHT RADIUS: 600 \
  SIGHT DURATION: 5 \
  MINISTUN DURATION: 0.35]
))
#v(.1em)
#text(size: 0.85em)[Cooldown: 6/6/6/6 \
Mana Cost: 120/125/130/135]
#custom-quote([A shocking punishment for rebellious heathen.])

#v(.5em)
*Heavenly Jump* \
#indent[Zeus performs a Heavenly Jump, leaping forward and shocking the closest visible nearby enemy (prioritizing heroes), dealing damage as well as reducing their movement and attack speed. Zeus gets 900 unobstructed vision around him for 3 seconds.] \
#align(horizon, oasis-align(force-frac: 0.5,
  text(size: 0.85em)[Ability: No Target \
  Damage Type: Magical \
  Pierces Spell Immunity: No \
  Dispellable: Yes],
  text(size: 0.85em)[DAMAGE: 25/50/75/100 \
  LEAP DISTANCE: 375/450/525/600 \
  SHOCK RANGE: 700/800/900/1000 \
  VISION RADIUS: 900 \
  DURATION: 1.4 \
  MOVE SPEED SLOW: 80 \
  ATTACK SPEED SLOW: 100 \
  TARGETS: 1]
))
#v(.1em)
#text(size: 0.85em)[Cooldown: 26/22/18/14 \
Mana Cost: 50/60/70/80]
#custom-quote([Though temporarily barred from the heavens, Zeus can still manage a measure of godly flight.])

#v(.5em)
*Thundergod's Wrath* \
#indent[Strikes all enemy heroes with a bolt of lightning, dealing damage no matter where they may be. Provides True Sight around each hero before they are struck.] \
#align(horizon, oasis-align(force-frac: 0.55,
  text(size: 0.85em)[Ability: No Target \
  Damage Type: Magical \
  Pierces Spell Immunity: No],
  text(size: 0.85em)[TRUE SIGHT RADIUS: 600 \
  DURATION: 3 \
  DAMAGE: 300/475/650]
))
#v(.1em)
#text(size: 0.85em)[Cooldown: 130 \
Mana Cost: 250/375/500]
#custom-quote([The Lord of Heaven smites all who oppose him, near or far.])

#v(.5em)
#align(center)[\(Shard Grants New Ability\)]
*Lightning Hands* \
#indent[Zeus gains bonus attack speed and his attacks create Arc Lightnings that deal a percentage of its damage. Can be toggled off to stop this effect.]
#align(horizon, oasis-align(force-frac: 0.55,
  text(size: 0.85em)[Ability: Toggle \
  Affects: Enemy Units \
  Damage Type: Magical \
  Pierces Spell Immunity: No \
  Dispellable: Yes],
  text(size: 0.85em)[BONUS ATTACK SPEED: 30 \
  ARC LIGHTNING DAMAGE: 50]
))
#custom-quote([A helping hand from Aghanim lets the fallen Lord of Heaven tap into some of his old strengths.])

#v(.5em)
#align(center)[\(Scepter Grants New Ability\)]
*Nimbus* \
#indent[Creates a storm cloud anywhere on the map that automatically casts Lightning Bolt on nearby enemies.]
#align(horizon, oasis-align(force-frac: 0.45,
  text(size: 0.85em)[Ability: Point Target \
  Damage Type: Magical \
  Pierces Spell Immunity: No],
  text(size: 0.85em)[DURATION: 30 \
  LIGHTNING BOLT BASE COOLDOWN: 2.5 \
  RADIUS: 450 \
  HITS TO DESTROY: 8 \
  CREEP HITS TO DESTROY: 16]
))
#v(.1em)
#text(size: 0.85em)[Cooldown: 45 \
Mana Cost: 275]
#custom-quote([Where the thunder god's ire grows, storm clouds quickly gather.])

#parbreak
[Full History] \
Lord of Heaven, father of gods, Zeus treats all the Heroes as if they are his rambunctious, rebellious children. After being caught unnumbered times in the midst of trysts with countless mortal women, his divine wife finally gave him an ultimatum: 'If you love mortals so much, go and become one. If you can prove yourself faithful, then return to me as my immortal husband. Otherwise, go and die among your creatures.' Zeus found her logic (and her magic) irrefutable, and agreed to her plan. He has been on his best behavior ever since, being somewhat fonder of immortality than he is of mortals. But to prove himself worthy of his eternal spouse, he must continue to pursue victory on the field of battle.