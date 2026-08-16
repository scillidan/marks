// https://typst.app/universe/package/baler
#import "@preview/baler:0.1.0": *

= 芳香提取物
// manual
多米尼克·洛克斯，《采香者：世界香水之源》
#divider()
#let table-content = (
	[Exsudat], [渗出物], [从树木创口中流出的一切物质],
	[Baume], [香脂], [有气味的液体渗出物],
	[Gomme|Résine], [树胶、树脂], [树木的渗出物，遇空气后会硬化。树胶溶于水，树脂溶于酒精],
	[Larmes], [固化浆液], [凝固的树胶块或树脂块],
	[Essence|Huile essentielle], [精油], [植物经过水蒸气蒸馏后的产物。精油不溶于水且比水轻，经澄清后与水分离],
	[Concrète], [浸膏], [利用溶剂对植物进行萃取后得到的有气味的软膏],
	[Absolue], [净油], [浸膏中可溶于酒精的部分，可被香水制造商使用],
	[Extrait|Résinoïde], [萃取物、类树脂], [植物经酒精萃取后的产物],
	[Eau florale|Eau de rose], [花水、蔷薇水], [有香气的水，花朵经水蒸馏后的产物],
	[Gemmage], [采脂], [割开树木的树皮以收集树胶或树脂],
	[Enfleurage], [脂吸法], [一种古老的工艺，通过将花瓣铺在一层油脂上来提取花香],
	[Distillation], [蒸馏], [让水蒸气循环通过植物或植物与水的混合物以得到精油],
	[Extraction], [萃取], [让溶剂流过植物以得到浸膏或净油],
	[Alambic], [蒸馏器], [生产花水或精油的装置],
	[Condensat], [冷凝液], [蒸馏冷却后得到的水和精油的混合物],
	[Florentin], [分液器], [用于收集从冷凝水中析出的精油的器皿],
	[Extracteur], [萃取器], [生产浸膏或香脂的装置]
)
#baled-table(stroke: none, inset: (1.5pt, 3pt), align: left, columns: 3,
	..table-content)