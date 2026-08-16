// https://typst.app/universe/package/baler
#import "@preview/baler:0.1.0": *

= 饮品
// menu
理查德·伊文斯·舒尔兹, 艾伯特·霍夫曼, 克里斯汀·拉，《众神的植物：神圣、具疗效和致幻力量的植物》
#divider()
#let table-content = (
	[jica], [希卡], [Ayahuasca], [阿亚瓦斯卡], [\-],
	[asca], [阿斯卡], [\-], [\-], [\-],
	[ayas], [亚斯卡], [\-], [\-], [\-],
	[huasca], [瓦斯卡], [\-], [\-], [\-],
	[ia], [伊阿], [Euphorbia sp.], [大戟], [润喉],
	[sacia], [萨西阿], [Erythrina spp.], [刺桐], [通便],
	[jia], [希阿], [Capsicum frutescens], [灌木辣椒], [强身],
	[huyaa], [乌亚阿], [Couroupita guianensis], [炮弹树], [健体],
	[longa], [隆加], [Thevetia sp.], [黄花夹竹桃], [护身],
	[yusa], [尤萨], [Ilex guayusa], [瓜尤萨冬青], [净化],
	[sheto], [塞托], [Panaeolus sphinctrinus], [蕾丝斑褶菇], [占卜],
	[riri], [莉莉], [Cyperus sp.], [莎草], [镇静],
	[raka], [拉卡], [Malouetia tamaquarina], [鱼鳃木], [安神],
	[bakawa], [巴卡瓦], [Psychotria], [九节], [强安神],
	[lama], [拉马], [Virola spp.], [油楠], [视力],
	[eto], [埃托], [Ipomoea carnea], [树牵牛], [视力],
	[lma], [尔马], [Calathea veitchiana], [维奇肖竹芋], [视力],
	[gonansa], [戈南萨], [Tabernaemontana sananho], [奥南萨山辣椒], [炎症],
	[ruru], [鲁鲁], [Alchornea castanaefolia], [栗叶山麻秆], [痢疾],
	[napulu], [纳普卢], [Chorisia insignis], [百花异木棉], [肠疾],
	[rapa], [拉帕], [Rapadou], [小圆木], [骨骼],
	[naka], [纳卡], [Sabicea amazonensis], [亚马逊木藤], [甜味剂],
	[mira], [米拉], [Lygodium venustum], [海金沙], [调剂],
	[more], [莫雷], [Pithecellobium laetum], [猴耳环], [调剂],
	[suba], [苏瓦], [Himatanthus sucuuba], [白花夹竹桃], [萃取箭草],
)
#baled-table(stroke: none, inset: (1.5pt, 3pt), align: left,
	columns: (26pt, 26pt, 36pt, 36pt, 28pt),
	..table-content)