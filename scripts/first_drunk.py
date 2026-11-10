"""Builds scripts/first_drunk.json (run: ./venv/Scripts/python scripts/first_drunk.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

CAR = "Carrigan et al. (2015). Hominids adapted to metabolize ethanol long before human-directed fermentation. PNAS 112"
HOC = "Hockings et al. (2015). Tools to tipple: ethanol ingestion by wild chimpanzees using leaf-sponges. Royal Society Open Science 2"
RAQ = "Liu, Wang & Rosenberg (2018). Fermented beverage and food storage in 13,000 y-old stone mortars at Raqefet Cave, Israel. Journal of Archaeological Science: Reports 21"
DIE = "Dietrich et al. (2012). The role of cult and feasting in the emergence of Neolithic communities: new evidence from Göbekli Tepe. Antiquity 86; German Archaeological Institute Göbekli Tepe project reports"
JIA = "McGovern et al. (2004). Fermented beverages of pre- and proto-historic China. PNAS 101"
GEO = "McGovern et al. (2017). Early Neolithic wine of Georgia in the South Caucasus. PNAS 114"
ARE = "Barnard et al. (2011). Chemical evidence for wine production around 4000 BCE in the Late Chalcolithic Near Eastern highlands. Journal of Archaeological Science 38; Areshian et al. (2012), Antiquity 86 (Areni-1 winery)"

S = [
    # ---------------- hook (12 one-line scenes)
    ("Your gut carries a ten million year old alcohol upgrade.", "The main character looks down at his own see-through belly where a tiny glowing machine hums, eyebrows raised.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("It appeared when our ancestors came down from the trees.", "A tall tree with ripe round fruit on its branches and a few fallen fruits lying on the grass below.", "hook", "awe", 2, "normal", 0, None, CAR),
    ("So when did humans first get drunk?", "The main character raises a clay cup with a puzzled look and one eyebrow up.", "hook", "curious", 2, "normal", 0, None, None),
    ("Chemical traces hint at beer thirteen thousand years ago.", "A heavy round stone mortar with a pestle resting inside a dim cave beside a small fire.", "hook", "awe", 2, "normal", 0, None, RAQ),
    ("Because the answer may explain why we started farming.", "The main character stands in a field of golden wild grain, scratching his head, a mug in his other hand.", "hook", "serious", 2, "normal", 0, None, None),
    ("Wild chimpanzees soak leaf sponges in fermented palm sap.", "A folded green leaf soaking in a hollow of a palm tree trunk with frothy golden sap, jungle behind.", "hook", "curious", 2, "normal", 0, None, HOC),
    ("By the end, you'll judge five clues like a detective.", "The main character holds up five fingers with a big confident grin, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("One drink may have been brewed for the dead.", "A quiet stone graveyard cave with small candles glowing beside a stone bowl.", "hook", "whisper", 2, "slow", 0, None, RAQ),
    ("And a giant stone vat in Turkey hides a clue.", "The main character peers over the rim of a gigantic stone basin, eyes wide, holding a small torch.", "hook", "tense", 2, "normal", 0, None, None),
    ("Pottery in China held a nine thousand year old drink.", "A narrow-necked clay pot beside rice stalks and a small beehive on a hillside.", "hook", "excited", 2, "normal", 0, None, JIA),
    ("Rice, honey and fruit, all in one cup.", "The main character happily holds up a big clay cup with rice, a honey drip and red berries floating in it.", "hook", "happy", 2, "normal", 0, None, None),
    ("Georgia has wine jars dating back eight thousand years.", "Large clay jars partly buried in the ground in a field with grapevines in warm light.", "hook", "awe", 3, "normal", 500, None, GEO),
    # ---------------- the ape upgrade
    ("Let's start with a surprise. The story of alcohol begins long before we were human.", "The main character stands in a forest of fruit trees holding a round fruit, grinning.", "build", "curious", 2, "normal", 0, None, None),
    ("Researchers rebuilt ancient versions of an enzyme called alcohol dehydrogenase four. About ten million years ago, one change in our ape ancestors made it far better at breaking down alcohol.", "A glowing spiral-shaped enzyme drawn like a tiny machine beside a ripe fruit on a plain pale background.", "build", "neutral", 2, "normal", 0, None, CAR),
    ("Researchers think it may have helped our ancestors eat fallen, fermenting fruit when food was scarce. Free calories, with a slight kick.", "The main character picks a squishy fallen fruit off the ground, surrounded by tiny cartoon bubbles, delighted.", "build", "funny", 2, "normal", 0, None, None),
    ("Chimpanzees still do something similar. At Bossou in Guinea, researchers watched wild chimps raid raffia palm sap that ferments into palm wine, using folded leaves as sponges.", "A folded green leaf soaking in a hollow of a palm tree trunk with frothy golden sap, dense jungle behind.", "build", "curious", 2, "normal", 0, None, HOC),
    ("Leaf sponges. Honestly, more elegant than a plastic cup.", "The main character admires a folded leaf sponge like a fancy wine glass, little finger raised.", "build", "funny", 2, "fast", 0, None, None),
    ("The sap averaged about three percent alcohol, with peaks near seven percent, and some chimps seemed sleepy afterwards. The researchers couldn't tell whether they wanted the buzz or just the sweetness.", "A cartoon chimpanzee curled up asleep at the foot of a palm tree beside a pile of used leaf sponges.", "build", "neutral", 2, "normal", 0, None, HOC),
    ("So a taste for fermented fruit is older than our species. The real question is when we started making it on purpose.", "The main character holds a fruit in one hand and a cup in the other, looking back and forth between them.", "build", "serious", 2, "slow", 0, None, None),
    ("Funny detail: the same enzyme change appeared separately in the aye-aye, a lemur from Madagascar. Evolution loves a coincidence.", "A cartoon aye-aye lemur with huge eyes and a long thin finger hanging from a tree branch at night.", "build", "curious", 2, "normal", 0, None, CAR),
    # ---------------- clue one: Raqefet
    ("Enough about animals. Clue one: a cave in Israel, and I'm not sure we'd call it a pub.", "The main character walks into a dim cave with a torch, looking around nervously for a bartender.", "build", "funny", 2, "normal", 0, None, None),
    ("At Raqefet Cave in Israel, researchers studied residues in stone mortars left by the Natufians, hunter-gatherers who lived about thirteen thousand years ago.", "A large round stone mortar with a heavy pestle inside a dim cave, a small fire glowing in the background.", "build", "neutral", 2, "normal", 0, None, RAQ),
    ("A cave brewery. No taps, no pints, just a stone bowl and a lot of patience.", "The main character stirs a big stone bowl with a long stick, tongue out in concentration.", "build", "funny", 2, "normal", 0, None, None),
    ("The team proposes that wild grain was malted, mashed, heated and fermented with wild yeast, and when they recreated those steps, they got a beer-like drink.", "A row of three stone bowls on a flat rock: sprouted grain, a steaming grain porridge and a bubbling frothy brew.", "build", "curious", 2, "normal", 0, None, RAQ),
    ("Brewing from scratch, with no instruction manual. Somebody must have been very, very curious.", "The main character scratches his head over a bowl of bubbling brew, then takes a tiny careful sip.", "build", "excited", 2, "normal", 0, None, None),
    ("They think it was made for feasts honouring the dead, since Raqefet was a Natufian graveyard with around thirty burials.", "A quiet stone graveyard cave with small candles glowing beside a stone bowl and a few flat grave stones.", "punchline", "awe", 2, "slow", 400, "ding", RAQ),
    ("A toast for the departed, thirteen thousand years before the first pub.", "The main character raises a stone cup toward a row of flat grave stones with a gentle, respectful smile.", "build", "serious", 2, "slow", 0, None, None),
    ("Not everyone is convinced. Some archaeologists say the residue could be bread, not beer, so the debate is open.", "A split drawing: a round loaf of bread on the left and a foaming clay mug on the right, on a flat stone.", "build", "neutral", 2, "normal", 0, None, RAQ),
    # ---------------- clue two: Gobekli Tepe
    ("I like that. A good clue is one people argue about. Now, clue two, in Turkey.", "The main character shrugs with both hands out, then points off to a far distant hilltop.", "build", "curious", 2, "normal", 0, None, None),
    ("At Göbekli Tepe in Turkey, a site more than eleven thousand years old, archaeologists found large stone vats holding up to a hundred and sixty litres.", "A large carved stone basin built into a limestone floor with dark residue on its lower walls beside tall T-shaped stone pillars.", "build", "awe", 2, "normal", 0, None, DIE),
    ("A hundred and sixty litres. That's either a lot of party or a very big soup.", "The main character stands next to a gigantic stone basin that is twice as tall as him, holding a tiny ladle.", "build", "funny", 2, "normal", 0, None, None),
    ("Early tests on the residue showed oxalate, a compound linked to steeped and fermented grain. But the researchers called the result preliminary, and it isn't conclusive.", "A small glass test tube with a pale liquid standing on a flat stone beside a pinch of dark crusty residue.", "build", "serious", 2, "normal", 0, None, DIE),
    ("Smoke, but no smoking gun. That's archaeology in one sentence.", "The main character squints through a magnifying glass at a tiny dark smudge on a stone, very suspicious.", "build", "funny", 2, "normal", 0, None, None),
    ("The site shows no signs of everyday living, so the team suggests grain may have been prepared elsewhere and brought in for special occasions.", "An empty flat hilltop of pale rock with a few huge T-shaped stone pillars standing alone and no houses anywhere.", "build", "neutral", 2, "normal", 0, None, DIE),
    # ---------------- subscribe (once)
    ("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring the ancient world together, one question at a time. It's free, it takes one second, and it helps more curious people find us.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    ("Their idea is that feasts at places like this may have pulled hunter-gatherers together to build huge monuments, with drinks as part of the reward. It's a hypothesis, not a fact.", "A ring of huge T-shaped stone pillars on a hilltop at sunset with many clay pots arranged beside a stone vat.", "build", "serious", 2, "normal", 0, None, DIE),
    ("Pay your builders in beer. Honestly, some things never change.", "The main character carries a heavy stone block on his back while a foaming mug floats in front of him like a carrot on a stick.", "build", "funny", 2, "fast", 0, None, None),
    ("In nineteen fifty-three, a scholar named Braidwood asked whether people first farmed for bread or for beer. Researchers still debate the question today.", "A wooden seesaw on a flat stone with a loaf of bread on one end and a foaming clay mug on the other, a wheat sheaf in the middle.", "build", "neutral", 2, "normal", 0, None, DIE),
    # ---------------- clue three: China
    ("Bread or beer, the argument is older than most of us. Let's head east, to China.", "The main character spins a large wooden globe and points at a far eastern shape, grinning.", "build", "excited", 2, "normal", 0, "swoosh", None),
    ("Clue three. At Jiahu, residues absorbed into pottery from around seven thousand BCE show a mixed drink: rice, honey and fruit, probably hawthorn or wild grape.", "Three clay jars in a row on a wooden shelf: one with rice, one with golden honey and one with red hawthorn berries.", "build", "curious", 2, "normal", 0, None, JIA),
    ("Rice, honey and fruit in one cup. Cocktails were invented before the written word.", "The main character holds a cup with rice grains, a honey drip and berries, looking very pleased with his invention.", "build", "funny", 2, "normal", 0, None, None),
    ("Researchers call it a fermented beverage, and the date is about nine thousand years ago. The earlier record then was from Iran, around fifty-four hundred BCE.", "Broken pieces of old painted pottery laid on a cloth with a pale sticky residue inside one piece.", "build", "neutral", 2, "normal", 0, None, JIA),
    ("Nine thousand years. Some of your ancestors had a signature drink.", "The main character strikes a proud pose beside a small clay mug with a heart drawn on it.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- clue four: Georgia
    ("Clue four. In Georgia, large pottery jars from about six thousand to fifty-eight hundred BCE held tartaric acid, the signature of grape wine.", "Large clay jars partly buried in the ground in a field with grapevines, golden light across the hills.", "build", "awe", 2, "normal", 0, None, GEO),
    ("Tartaric acid. Chemistry's polite way of saying, yes, this was wine.", "The main character holds up a tiny glass flask of purple liquid with a very serious scientist expression.", "build", "funny", 2, "normal", 0, None, None),
    ("That's roughly six hundred to a thousand years older than the earlier wine evidence from Iran, and the jars were partly buried, like the qvevri still used in Georgia today.", "A row of large clay jars buried up to their necks in the earth floor of a stone-walled shed.", "build", "neutral", 2, "normal", 0, None, GEO),
    ("A cellar, underground and cool. Even back then, wine had standards.", "The main character carries a clay jar down a few stone steps into a cool underground cellar, humming.", "build", "curious", 2, "normal", 0, None, None),
    ("A co-author said it may be the earliest example of domesticating a wild grapevine just for making wine.", "A single twisting grapevine climbing a wooden pole with heavy purple grapes and clay jars at its foot.", "punchline", "awe", 2, "normal", 400, None, GEO),
    ("Someone grew a plant just to drink it later. That's patience.", "The main character waits beside a tiny grape sprout with folded arms, tapping his foot, a calendar page flipping behind him.", "build", "funny", 2, "normal", 0, None, None),
    ("And at Areni cave in Armenia, a winemaking installation from around four thousand one hundred BCE had a grape press, fermentation vats and storage jars.", "A cave floor with a shallow stone-lined pressing platform, a large clay vat and several storage jars in a row.", "build", "awe", 2, "normal", 0, None, ARE),
    ("A press, a vat, jars and a cup. They basically had a tasting room.", "The main character stands behind a rock counter in a cave, polishing a clay cup with a cloth like a bartender.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- why it matters
    ("Some scientists suggest the desire for beer may have motivated early farmers to cultivate cereals. It's debated, and the Raqefet authors present it as one possibility.", "A field of golden grain with a clay mug resting on a stone in the middle, sunlight beaming down on it.", "build", "serious", 2, "normal", 0, None, RAQ),
    ("So the drink may have come first, and the farm followed. Even if that's only partly true, it's a great plot twist.", "The main character looks at a mug and then at a field of grain, jaw dropping in surprise.", "build", "excited", 2, "normal", 0, None, None),
    ("Researchers who study these places often connect early alcohol with feasting and ritual, a way of marking big moments together.", "A big circle of clay cups and bowls laid out on a flat stone around a small fire in the middle.", "build", "serious", 2, "normal", 0, None, RAQ + "; " + DIE),
    ("That's the part that surprises me. In this story, the drink looks like part of the occasion, not the point. My pick for the strongest clue? Georgia's wine jars, because the chemistry is clear.", "The main character sits in a warm circle of stick figures raising cups around a fire, smiling softly.", "punchline", "awe", 2, "slow", 300, None, None),
    ("So the earliest chemical evidence for drinking is about thirteen thousand years old, but the enzyme story reaches back ten million years.", "A long horizontal line on the ground with a tiny clay cup at one end and a distant tree with fruit at the other.", "build", "neutral", 2, "slow", 300, None, CAR + "; " + RAQ),
    ("So when did ancient humans first get drunk? Somewhere between ten million and thirteen thousand years ago, depending on how you count. Thank you for spending these minutes with me. Like the video if you enjoyed it, and tell me in the comments which clue surprised you most, I read every one. Next time: when did dogs join the camp? I'll be here, and I hope you will too. See you there, friend.", "The main character raises a clay cup toward the viewer with a warm smile, a small cave painting of a dog on the wall behind him.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 50 <= len(S) <= 80, len(S)
scenes = []
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, src) in enumerate(S):
    hero = i % 2 == 0
    assert ("the main character" in prompt.lower()) == hero, (i + 1, prompt[:60])
    assert (beat == "hook") == (i < 12), i + 1
    assert src or hero, (i + 1, "fact scene needs a source")
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
                   "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
                   "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})

data = {
    "title": "When Did Ancient Humans First Get DRUNK?",
    "title_alternatives": ["Did Beer Come Before BREAD? What Archaeologists Found", "Ancient Humans Brewed Beer for the DEAD?",
                           "The Oldest WINE Jars Ever Found", "Wild Chimps Drink Palm WINE. Why?"],
    "description": ("Your gut carries a ten million year old alcohol upgrade. So when did ancient humans first get drunk? This video follows five "
                    "clues: wild chimpanzees drinking palm wine, a thirteen thousand year old brewing cave in Israel, giant stone vats at Göbekli Tepe, "
                    "a nine thousand year old drink from China, and the oldest known wine jars from Georgia.\n\n"
                    "This video is history and science. It does not encourage drinking.\n\nSources:\n"
                    "- Carrigan et al. (2015). Hominids adapted to metabolize ethanol long before human-directed fermentation. PNAS.\n"
                    "- Hockings et al. (2015). Tools to tipple: ethanol ingestion by wild chimpanzees using leaf-sponges. Royal Society Open Science.\n"
                    "- Liu, Wang & Rosenberg (2018). Fermented beverage and food storage in 13,000 y-old stone mortars at Raqefet Cave, Israel. J. Archaeol. Sci.: Reports.\n"
                    "- Dietrich et al. (2012). The role of cult and feasting in the emergence of Neolithic communities. Antiquity.\n"
                    "- McGovern et al. (2004). Fermented beverages of pre- and proto-historic China. PNAS.\n"
                    "- McGovern et al. (2017). Early Neolithic wine of Georgia in the South Caucasus. PNAS.\n"
                    "- Barnard et al. (2011) and Areshian et al. (2012) on the Areni-1 winery."),
    "tags": ["ancient alcohol", "history of alcohol", "ancient beer", "ancient wine", "when did humans first drink", "raqefet cave",
             "gobekli tepe", "jiahu", "georgia wine", "neolithic", "ancient humans", "archaeology", "animated history", "stickman"],
    "mood": "playful",
    "sources": [
        "Carrigan, M. A. et al. (2015). Hominids adapted to metabolize ethanol long before human-directed fermentation. PNAS 112, 458-463.",
        "Hockings, K. J. et al. (2015). Tools to tipple: ethanol ingestion by wild chimpanzees using leaf-sponges. Royal Society Open Science 2, 150150.",
        "Liu, L., Wang, J. & Rosenberg, D. (2018). Fermented beverage and food storage in 13,000 y-old stone mortars at Raqefet Cave, Israel. Journal of Archaeological Science: Reports 21, 783-793.",
        "Dietrich, O. et al. (2012). The role of cult and feasting in the emergence of Neolithic communities: new evidence from Göbekli Tepe. Antiquity 86, 674-695.",
        "McGovern, P. E. et al. (2004). Fermented beverages of pre- and proto-historic China. PNAS 101, 17593-17598.",
        "McGovern, P. et al. (2017). Early Neolithic wine of Georgia in the South Caucasus. PNAS 114, E10309-E10318.",
        "Barnard, H. et al. (2011). Chemical evidence for wine production around 4000 BCE in the Late Chalcolithic Near Eastern highlands. Journal of Archaeological Science 38, 977-984.",
        "Areshian, G. E. et al. (2012). The Chalcolithic winery of Areni-1, Armenia. Antiquity 86.",
    ],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]), "max hook line:", max(len(s["narration"].split()) for s in scenes[:12]))
em = [s["emotion"] for s in scenes]
run = 1
for i in range(1, len(em)):
    run = run + 1 if em[i] == em[i - 1] else 1
    if run > 3:
        print("4+ same emotion in a row at scene", i + 1, em[i])
