```
Date: 2026.10.11
Creator: The Hack
Source: https://nonfunctional.substack.com/p/passkeys-are-a-trap-do-not-use-them
```

# Passkeys are a trap. Do not use them.

Seems like every website wants us to stop using passwords. There is a replacement we are being asked to use instead called *passkeys*. This should be a tad concerning if passwords are familiar to you and you don’t fully understand these nebulous passkeys.

Websites say that passkeys are *more secure* or *more convenient* or something similarly beneficial. While it is true that passkeys can be far more secure than passwords, and may indeed be more convenient, that’s not the whole story. Passkeys are not designed to prioritize your interests. Like the Trojan Horse, passkeys are legitimately elegant on the surface, but there is something troubling inside.

What’s important to know is that unlike with any other kind of login credential, **you do not have ultimate control over your passkeys**. With passwords, you can choose where to write them down; with authenticator apps, you can decide for yourself which ones to use (they’re pretty interchangeable); and with physical security keys you can hand them to your colleague if you really trust them. But with passkeys come a hidden dial that lets the websites you use them on gradually remove your ability to do as you please with them.

I will explain how that is possible further down, but let’s first take a look at who wants you to be using passkeys.

Passkeys are the invention of the [FIDO Alliance](https://en.wikipedia.org/wiki/FIDO_Alliance),[^1] which is a consortium of a number of different competing interests – Big Tech, little tech, national governments, intelligence agencies, banks, various public institutions, and even a handful of nonprofits like Mozilla – who are all able to agree that passkeys are a good and righteous cause.

The members of the FIDO Alliance all have their own interests. Big Tech wants to bring little inconveniences into our life so they can sell us more ads. Intelligence agencies want to track everyone in the world. Banks want to be free of indemnity. Little tech wants cheap solutions to reduce liability. Mozilla wants to avoid having to die on any particular hill.[^2] I make no particular claim that any of these are bad motivations. But it is notable that no consumer advocacy groups are members of the FIDO Alliance. (This stands in contrast to, for example, the [World Wide Web Consortium](https://en.wikipedia.org/wiki/World_Wide_Web_Consortium), the organization that decides the standards used on the web. Alongside the usual corporate members it has not only public interest groups but also universities and Tim Berners-Lee, the British computer scientist who invented the World Wide Web in 1989. Honestly, if Gandalf himself were to join the W3C he would not be out of place.) Regarding the FIDO Alliance, nobody is there to make a strong case for the user’s own interests.

The reason presented to the public for why everyone needs to use passkeys now is that passwords are insecure. On this point I agree. Consider that the servers behind the billion-dollar American IT company SolarWinds [were famously found](https://www.cnn.com/2021/02/26/politics/solarwinds123-password-intern/) to be using `solarwinds123`. Hawaii’s Emergency Management Agency (the same one that sent out that false missile alert) [accidentally revealed a password](https://www.businessinsider.com/hawaii-emergency-agency-password-discovered-in-photo-sparks-security-criticism-2018-1?op=1) due to a sticky note on someone’s desk in the background of a photograph. If your security relies on a password, you will always be anxious that somebody, somewhere, has somehow figured out what it is and already has access to your bank account.

On the other hand: what passwords have going for them is that they’re very intuitive, everyone knows how they work, people have been using them since time immemorial, and you can choose where you store them and who you share them with. Keep this in mind.

(Also keep this in mind: Netflix does not want you to share your passwords.)

But there already exist superior security mechanisms to passwords, and the FIDO Alliance seems to be giving the cold shoulder: first there was *Two-Factor Authentication* (in particular: receiving a text message or email with a one-time code), and later came the more robust system of *Time-Based One-Time Passwords* (TOTP) – in common parlance, “authenticator apps.*”*

What’s neat about TOTP is that it doesn’t rely on text messages or email or even the internet at all. Your authenticator software simply generates a random-looking number every 30 seconds based on the current time (and a random starting number called a “seed” or a “key” that is unique to you), and this is all that a website needs to verify you’re you. The term *authenticator app* is misleading, not in the least because websites tend to heavily imply you need to download a *specific* app, such as Google Authenticator. In reality, there is an open standard for TOTP (called [RFC 6238](https://en.wikipedia.org/wiki/Time-based_one-time_password)); that is to say, the formula used to generate these random-looking numbers is public knowledge, so you don’t need to use any one specific piece of software. In almost all cases you don’t need to use Google Authenticator just because the website suggests it. You don’t even need to use a smartphone; you can use your laptop or even a Game Boy[^3] from the 90s for this purpose. You can use any software and hardware you like, so long as it can tell time decently and can handle a few lines of code. You can even write the software yourself in Python if you want, or if you feel like burning a moticum of jet fuel you can get an LLM to write it for you.

TOTP is a great solution. If you accidentally leak your TOTP in a photograph of your desk, you’re only at risk for a couple of minutes until the code expires. TOTP is certainly less intuitive than passwords, but at least like passwords you can still choose how you want to store them. You can choose where you want them to live and what software you want to use to generate the codes. And you can’t easily shoot yourself in the foot with an easy-to-guess TOTP code like you can with a `password123`; as they are nothing more than random-looking numbers, all TOTP codes are equally hard to guess. Oh, what’s more, you can send a code to your friend to let them log into your Netflix account temporarily while you’re away on business. You can even share your TOTP seed itself if you really want to so that your friends can generate your TOTP codes themselves and then they can let *their* friends log into your Netflix account. You might get some strange looks if you write all your TOTP seeds down on a piece of paper like you do with your passwords, but at the end of the day this data is *yours* to handle how you like. Aren’t open standards wonderful?

(Netflix does not want you to share your TOTP keys either.)

So what makes *passkeys* so different? Well, they look very similar to TOTP on the surface. Both have an open standard (RFC 6238 for TOTP, WebAuthn for passkeys), so surely passkeys must have all these same nice properties as TOTP, right? At first glance it would seem so. Indeed, just now I generated a passkey using free and open source software, and then I emailed it to a friend, and now we can both access the same website using that passkey. At no point did I have to ask anyone for permission, not the website, not the FIDO Alliance; not even my friend, who kindly let me monopolize her time without objection. What’s more, I don’t have to type any numbers by hand to use a passkey; I don’t have to remember any magic words; passkeys just work. Judging from that alone, a passkey is indeed convenient. And it sure *seems* like I can do whatever I want with my passkeys.

(But Netflix does not want you to share your passkeys.)

So where’s the catch?

The catch is that there is something else that is also called a “passkey” and it’s nothing like the nice kind that I just described.

In fact there are many different things called “passkeys” and the FIDO Alliance has intentionally named all of them the same thing. I believe this was done in order to deliberately confuse users and encourage them not to look too closely at the fine text. Indeed, in the technical documentation, the WebAuthn standard that defines passkeys barely uses the term *passkey* at all. Instead there are *discoverable credentials* and *undiscoverable credentials*; there are *hardware-backed credentials*, and *software-backed credentials*; there are *attested* and *unattested* credentials, and more and more.

There are so many optional components to what a passkey can be that the specs read less like a standard and more like a parts catalogue. So, let’s go over exactly what other things are in the catalogue alongside the nice and perhaps-almost-intuitive kind of passkey I described earlier. I will present them all in the best light I can manage so that you can understand why some people genuinely recommend passkeys as a good security solution, but by the end of the list I hope you will be able to see the problem I see.

---

### Copyable vs Non-Copyable passkeys

Both kinds exist.

When you generate a passkey, it can be made to be *non-copyable*. The reason you might want this as a user is to be sure that so long as you have possession of your passkey – so long as your iPhone is in your pocket, say – nobody else can access your account. On the other hand, passkeys can be made to be *copyable* instead, and you might want this ability in order to share one key between your devices.

If you make a passkey, make sure you know which of these two kinds you’re making! If you think your passkey is one of these and it’s actually the other, you will end up having a bad time someday – either when you realize you can’t rescue your only passkey off your dying laptop, or when somebody else turns out to have a copy of your passkey and you didn’t know that was possible.

### Transferable vs Non-Transferable passkeys

Both kinds exist.

Surprisingly, even if a Passkey is *non-copyable*, it can still be *transferable*. This may violate your intuition about how data is supposed to work. Although it’s how physical objects have always worked, we don’t often encounter situations in the *digital* world where sending something to your friend causes it to disappear from your own device.

You might want your passkey to be non-transferable in order to be completely sure that physical possession of one specific device is absolutely required to access your account. On the other hand, you might want your non-copyable passkey to be transferable in order for it to be able to move with you when you replace your smartphone for next year’s model. (Or maybe you just want to be able to play some kind of avant-garde digital relay race among your friends as an artistic statement.)

### Hardware-Backed vs Software-Backed passkeys

Both kinds exist.

Even if you’re not digitally savvy, you probably know what *files* and *folders* are, at least if you have a desktop computer. Admittedly, smartphones are designed to muddy the waters regarding where exactly that file you downloaded is and if *folders* are even a copacetic concept. (Yes, smartphones *do* use files and folders. They just don’t typically come with a file browser like your desktop does.)

So all these passkeys we’ve talked about so far are just files right? Well… not really. That is, they *can* be. Or they might not be. As with all these other qualities a passkey can optionally have, passkeys can optionally not be files at all. Indeed, since files are copyable and transferable and all sorts of other intuitive things, if passkeys had to be files, it would not be clear how anyone could make a non-copyable passkey.

Enter *hardware-backed* passkeys. These make use of a secure chip that comes with all modern devices which can store data that cannot be exfiltrated (meaning the data cannot leave the safety of the secure chip). There are different kinds of chips with different names: your laptop has a Trusted Platform Module and an iPhone has a “Secure Enclave” and so on. You will not find this area of your device in your file browser anywhere.[^4] It is a separate component entirely. Because of their cryptographic use case (and perhaps their mystique), people have taken to calling these chips “cryptoprocessors.”

The consensus seems to be that cryptoprocessors are indeed very secure. You might wonder if someone with the know-how couldn’t just surgically open the chip with the right tools and extract the data off that way. That’s *theoretically* possible; however, such chips employ all kinds of chemical and electronic tamper-detection measures and will self-destruct if you try to do this.[^5] So unless you have the resources of a nation-state at your disposal, you can basically take as a given that (hypothetical manufacturer backdoors notwithstanding) nobody can remove the secret data from your cryptoprocessor; not Netflix, not your operating system, not even you.

You might prefer to use a software-backed key because you understand how files work and you already have a solution that works for you for storing your private data. You might want to use a hardware-backed key to get the extra security afforded by a nigh-impenetrable cryptoprocessor.

### User-Present vs Non-User-Present passkeys

Both kinds exist.

Some passkeys require somebody to press a button or click a prompt to confirm authentication. Others can be used without anyone in the loop at all.

You might want the former kind because you yourself are a human. You might want the latter kind in case you want to authorize a piece of software to act on your behalf.

### User-Verified vs Non-User-Verified passkeys

Both kinds exist.

Okay so maybe *a* user was present, but how do we know *the right* user was present? Passkeys can optionally require *biometrics* (e.g. fingerprint sensors or retina scanners) or the use of PINs or passwords of their own in order to be extra sure that only one specific intended human being can use them.

You might want a user-verified passkey in order to be safe even in the situation a thief pilfers your device. You might want a non-user-verified passkey because you expect to lend your tablet to another family member so they can read your ebooks on Amazon and listen to music on your Spotify account and watch your movies on Disney+.

### Attested vs Non-Attested passkeys

This is where things take a left turn.

I’ve presented all these properties so far as being *up to you to decide*. That may indeed be how it is on most websites – for now, at least. After all, what cause does Twitter have to tell me exactly which security measures out of the smorgasbord available I should opt into for my passkeys? But you should know that the FIDO Alliance has defined this standard such that your passkey software is required to tell the service you’re accessing *which* of these features are enabled. They’re called *authenticator data flags* in the WebAuthn standard.[^6]

This means Twitter (formally X) can say to you, “sorry, we only accept the User-Present User-Verified Non-Copyable Hardware-Backed varieties of passkey here. But hey! You can still choose between Transferable and Non-Transferable passkeys!” Actually, I’m being optimistic – I suspect they are unlikely to phrase it in such clear terms. They will likely just say “unfortunately your passkey isn’t secure enough; download our app.”

But it’s an open standard, isn’t it? And maybe you have a friend experienced in writing Python code. Can’t you just make your own passkey software which just does the nice file-based kind of passkeys with none of those extra security features, and then have it tell the website anyway that it’s a User-Present User-Verified Non-Copyable Hardware-Backed passkey? Can’t you just *lie*?

Oh yes absolutely you can. Your passkey software can lie about whatever passkey features you like. Unless we’re talking about an *Attested* User-Present User-Verified Non-Copyable Hardware-Backed passkey. In which case, no. That can’t be faked.

*Attested* passkeys[^7] are the last but most important type of passkeys you need to know about. These types of keys use what’s known as *remote attestation* to cryptographically verify – using the aforementioned tamper-proof cryptoprocessor that lives in all your modern devices – that you are using one of the several *approved* passkey managers, and *not* using a custom one that you vibecoded yourself and which can lie.

This is the feature that means you no longer get to make the calls about your passkeys. Fortunately, attested passkeys are not yet required on most websites. But the FIDO Alliance standard makes attestation a part of the passkey ecosystem, whether you want it or not. And even if the website doesn’t require attestation, they can still check that your setup supports it. This means that once Twitter (formally X) is satisfied that the overwhelming majority of its users would be unaffected, they can flip the switch and start rejecting non-attested passkeys.

Critically, remote attestation requires the co-operation of your cryptoprocessor, your passkey manager software, your device’s operating system, and your device’s firmware to all pass the remote attestation check. After all, your phone’s operating system has total access to all the 0s and 1s in every app that’s ever run, so it’s not enough for Twitter (formally X) to trust your passkey manager if it can’t even trust your phone’s underlying operating system. If any single one of those things were to fail – say, because your phone stopped receiving security updates so you installed a custom operating system like LineageOS to keep yourself safe without having to buy a new device – then Twitter (formally X) will be able to notice and prevent you from logging in.

I’d like to be clear that there are legitimate uses of remote attestation. By using a website that requires attested passkeys you can be sure you stay safe from accidentally installing a scammer’s fake passkey application that steals your data – the website will reject such a passkey. You might want an attested Passkey even if the website doesn’t require it, since you can use attestation to verify that your software has not been tampered with by a hacker while you weren’t looking. (Of course, attestation may be overkill for this; even if your device *were* hacked, the hardware-backing feature described above makes it impossible for the passkey to be exfiltrated from your device. Though admittedly that guarantee is less reassuring once you realize that even if the key stays firmly on your device a hacker could still use it if they have control of your phone otherwise. At the very least you can always power off the device to temporarily deny hackers access to your Non-Attested Hardware-Backed Non-Copyable Non-Transferable passkeys.)[^8]

As for reasons to *not* want attestation: you might want to be able to use software that Twitter (formally X) doesn’t specifically approve of, such as Linux. Or a phone with a refurbished operating system. (Or if you’re nefarious you might want to be able to lie to Netflix and tell them that *of course* you and your three friends are absolutely all the same person using the same device.)

(But with attestation, Netflix can finally prevent you from sharing your passkeys.)

## It’s not just about Netflix or Twitter (X)

There is ample reason for you to be hesitant before you set up a passkey. If you’ve used only websites that require one certain kind of passkey then you might not notice when a website has you set up a different kind of passkey. Don’t forget that unlike passwords and SMS codes and TOTP, passkeys are designed to function in the background without you ever seeing the details. They’ll offer you at most a “confirm” prompt. (That’s the convenience aspect.) My expectation is that the industry will start off with very few constraints on your passkeys, and gradually add more and more, not all at the same time, but staggered on different sites, and then in a few years people will forget that they were ever offered a choice in which security measures they want to enable on their passkeys (if they even knew there were different kinds of passkeys at all).

So far, almost nobody has even heard of remote attestation. The vast majority of people use one of the four major operating systems (Windows, Android, macOS, and iOS) and not alternative operating systems like Linux, LineageOS, postmarketOS, or GrapheneOS. The overwhelming majority of people don’t replace the operating system on their phone when it stops receiving updates; instead they just buy a new phone. So almost nobody will ever encounter a situation where their device fails a remote attestation check.

Are attested passkeys so bad, though? After all, we really aren’t meant be sharing Netflix accounts to begin with.

Take another look at the list of members in the FIDO Alliance, and put on your tinfoil hat. Why do intelligence agencies care if I am sharing my Netflix account? Heck, why does Microsoft care if I am sharing my Netflix account?

For intelligence agencies, and for corporations like Microsoft, Google, Apple, Facebook, Amazon – giving you convenience and security is likely not their primary goal. I think they have an entirely ulterior motive. **They can use passkeys to prevent you from running unapproved software**.

Remote attestation can allow them to verify that your device is not capable of, say, sending and receiving encrypted messages, or running a competitor’s app, or using social media without verifying your ID. They don’t want you to be able to turn off the mandatory built-in AI image scanner on your phone that scans everything your phone sees for nudity. ([Yes, I’m serious.](https://www.gov.uk/government/news/new-plans-to-stop-children-taking-sharing-or-viewing-nude-images))

But I rather like deciding for myself what software I approve of and what software I don’t. Something I value about my web browser is that I can install extensions to modify aspects of websites that bother me. I can say no to auto-playing videos on news websites; I can decide which advertisements are too intrusive for me to let through; I can filter out irrelevant search results and disable AI summaries; I can block the “recommended video” feature on YouTube which always seems to promote outrage and division (or as Big Tech calls it, “engagement”). And if a website ends up monopolizing my time anyway, I have an extension that locks them down after a certain span of time. These extensions give me control over how the internet affects me, even if Big Tech would much rather make those decisions for me. But Google owns Google Chrome, which is the world’s most popular web browser, and they can remove support for these useful extensions ([as they did earlier this year](https://www.androidauthority.com/ublock-origin-final-chrome-update-3703164/) with uBlock Origin); and with remote attestation they can prevent me from using any other browser that doesn’t follow suit.

Remember those authenticator data flags I mentioned? There used to be only 4 of them. Earlier revisions of the FIDO Alliance’s security standard (called “WebAuthn Level 1” and “WebAuthn Level 2”) had fewer catalog options to choose from. I’m sweeping some details[^9] under the rug here for brevity, but since you are given four distinct binary choices, you could call that 16 different kinds of passkey. In 2022 the FIDO Alliance added some more (“WebAuthn Level 3”), so that websites could know whether or not your credentials are copyable, or if backups of your credentials might exist somewhere. There are still two flags left “reserved for future use.” What might our passkeys require of us in the future?

I’m not one to argue about slippery slopes, so I won’t claim that the campaigns to protect children online today will tomorrow turn into laws designed to make it easy to identify political dissidents. But I will say that the widespread adoption of the passkey technology being advertised to you as convenient and secure is capable of permitting such laws to be easily enforced.

So if you care about your privacy and the privacy of others, if you believe people should be free to choose what software runs on their devices, that people should be allowed to learn how to write their own software and run it on their own devices, and that friends should be able to privately talk politics online without government interference, then I would ask you to reject these dozens of different security mechanisms which are all confusingly branded as the same “passkeys.” Wait for Big Tech to propose something just as convenient and secure but more clearly defined and with fewer strings attached. In the meantime if you want security, your Game Boy can provide you with TOTP.[^10]

Fortunately, if you want the level of high security passkeys can give you without the strings attached, there is actually an even *more* secure solution: security keys, such as a [YubiKey](https://en.wikipedia.org/wiki/YubiKey). These are basically just physical passkeys that you can carry around with you and use alongside your other devices. They are also part of the FIDO Alliance’s WebAuthn standard, but because they are entirely self-contained their remote attestation requirements don’t have to spill out and lock down your whole operating system.

[^1]: No relation to the Canadian mobile network of the same name.
[^2]: I jest, but Mozilla has a reputation for putting up a fight and then eventually surrendering on issues like these. For instance, they eventually implemented Google’s proprietary *Widevine* DRM system into the otherwise open-source Firefox browser, as rejecting it might have resulted in users being unable to watch Netflix.
[^3]: Yes, someone [really made TOTP for Game Boy](https://github.com/dmang-dev/totp-gb). I cannot in good conscience actually recommend using this, but it will make you popular at parties. (At my parties in any case.)
[^4]: In practice a hardware-backed key may have a file component too, but it will be encoded in such a way that it’s cryptographically useless without the cryptoprocessor it is made for.
[^5]: Devices for consumers will generally just scramble themselves electronically as their anti-tamper mechanism, but more imaginative booby-traps are rumoured to exist. XEROX once [made a chip](https://techxplore.com/news/2015-09-xerox-parc-chip-shatters-shards.html) that could shatter into tiny shards as a defence measure.
[^6]: The authenticator data flags don’t all line up *exactly* with the features I presented above, but it’s close enough for the purposes of this blog post. For example, authenticator data flag `UP` is *User-Present*, authenticator data flag `UV` is *User-Verified*, and authenticator data flag `BE` is *Copyability* (“Backup-Eligible”).
[^7]: Authenticator data flag `AT`, if you were wondering.
[^8]: One use case is particularly intriguing to me. In principle, remote attestation can also be run in reverse, to verify that the server you connect to is not doing anything *you* don’t want *it* to be doing (such as stealing your credit card number, or keeping backups of the posts you delete). Sadly, to my knowledge, no major platform has ever implemented “reverse” remote attestation this way.
[^9]: As I understand it, “User-Verified” requires “User Present” to be set, so that would imply 12 distinct flavours. But in practice, security measures outside of the specific flags mentioned (such as requiring biometrics specifically, or non-transferability) are queryable and enforceable via remote attestation, so that actually means there are arbitrarily many passkey restrictions possible already with WebAuthn.
[^10]: Addendum: I feel I have made a [compelling case](https://en.wiktionary.org/wiki/steelman) *for* passkeys in this article. And I haven’t even pointed out one of their best security features: they are (in most use cases) *domain-bound*, meaning they are resistant to what are called *Man-In-The-Middle attacks*. Passkeys have so many incredible properties that I really *want* to use and recommend them; it’s very unfortunate that the FIDO Alliance has ruined a good thing by slipping in remote attestation and by making no attempt to ensure the difference between these various kinds of passkeys remains evident to the user.