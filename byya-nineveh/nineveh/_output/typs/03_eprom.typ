#import "../../../../scripts/byya-nineveh-template.typ": *
#show: nineveh-layout.with(size: 8pt)

#align(center + horizon, oasis-align(
  int-dir: -1,
  [#figure(image("../../assets/eprom.jpg"), caption: [.img by #link("https://www.flickr.com/photos/sic66/")[Martijn Boer] on #link("https://www.flickr.com/photos/sic66/50786660562/")[flickr] / #link("https://creativecommons.org/publicdomain/mark/1.0/")[pmd]])],
  [#figure(balance([eprom ⚪#und2[可洗可烧写只读记忆体] ⚫烧一词最早用在一次性烧写\(otp\)芯片上 写入时所需的高电压会永久改变其中的物理组成 来实现逻辑 ⚫进行擦除时 需要透过外包装顶部的非结晶石英窗 将硅芯暴露在强紫外光下 ⚫在一篇论文里 数学家艾伦·图灵\(Alan Turing\)描述了一种假设的机器 现被称为通用图灵机 它有着一个无限的储存区 今天的术语是#und2[随机访问记忆体]\(ram\) ⚫随机访问指信息读写时无关读写顺序,物理位置 ⚫不同于只读记忆体\(rom\) 经断电后 指令,数据的载体将释放 ⚫这种储存器是线形编址的 映射该物理记忆体内散列的地址到虚拟化的连续的地址 也就是从栈\(frame\)到页 就是一个简单页表\(page table\) ⚪pages ⚪页]))],
))
