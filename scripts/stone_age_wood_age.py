"""Builds scripts/stone_age_wood_age.json (run: ./venv/Scripts/python scripts/stone_age_wood_age.py).
Scene tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source)
Odd scenes = hero, even scenes = fact (strict alternation, see CLAUDE.md)."""
import json
from pathlib import Path

SAL = "Saladie et al., Science Advances (Abric Romani, Spain), reported by ZME Science, Oct 2026"
BAR = "Barham et al. (2023). Evidence for the earliest structural use of wood at least 476,000 years ago. Nature"
ARA = "Aranguren et al. (2018). Wooden tools and fire technology in the early Neanderthal site of Poggetti Vecchi. PNAS"
THI = "Thieme (1997). Lower Palaeolithic hunting spears from Germany. Nature 385"
THO = "Thomsen (1836). Ledetraad til Nordisk Oldkyndighed (Three-Age System)"

S = [
    # ---------------- hook (12 scenes, one short line each)
    ("Quick quiz: what was the Stone Age made of?", "The main character holds a rock in one hand and a stick in the other, looking puzzled at both.", "hook", "curious", 2, "normal", 0, None, None),
    ("Spain just revealed five hundred ninety-seven pieces of Neanderthal wood.", "A sunlit rock shelter in a limestone cliff, with small trays of dark wooden fragments laid out on a table.", "hook", "awe", 2, "normal", 0, None, SAL),
    ("Wood that normally rots away and vanishes forever.", "The main character watches a wooden stick crumble into dust in his open hand.", "hook", "serious", 2, "normal", 0, None, None),
    ("Mineral water wrapped it in stone and saved it.", "A shelter wall where mineral-rich water drips over a wooden branch, leaving a pale stone crust around it.", "hook", "awe", 2, "slow", 0, None, SAL),
    ("This changes how you picture every ancient person.", "The main character stands at a cave entrance by a small fire, scratching his head thoughtfully.", "hook", "serious", 2, "normal", 0, None, None),
    ("'Stone Age' names what survived, not what mattered.", "An old museum room with glass cases holding stone axes, bronze swords and iron blades in tidy rows.", "hook", "serious", 2, "normal", 0, None, THO),
    ("By the end, you'll see their real toolkit.", "The main character proudly holds up a long wooden spear like a trophy.", "hook", "curious", 3, "normal", 0, None, None),
    ("Spears, digging sticks, even a wooden platform.", "Wooden spears, a charred digging stick and two notched logs lying together on a muddy riverbank.", "hook", "excited", 2, "normal", 0, None, SAL + "; " + ARA + "; " + BAR),
    ("And one find is almost half a million years old.", "The main character leans over a muddy riverbank, spotting something wooden half buried in the mud.", "hook", "tense", 2, "normal", 0, None, None),
    ("Built before our own species even existed.", "Two thick logs locked together by a cut notch, half buried in wet ground beside a river.", "hook", "awe", 3, "slow", 300, "impact", BAR + "; Hublin et al. (2017). New fossils from Jebel Irhoud, Morocco. Nature"),
    ("But first, we need to fix one big mistake.", "The main character holds a large rock and peeks behind it, looking suspicious.", "hook", "curious", 2, "normal", 0, None, None),
    ("That mistake started in a museum in Copenhagen.", "A grand old museum building with columns and tall windows on a quiet cobblestone square.", "hook", "serious", 2, "slow", 400, None, THO),
    # ---------------- the label
    ("Meet Christian Thomsen, a Danish museum curator with one very messy storage room full of ancient stuff.", "The main character peeks into a cluttered storeroom piled high with old objects, wide-eyed.", "build", "curious", 2, "normal", 0, None, None),
    ("In eighteen thirty-six, he finally sorted everything by material: stone, then bronze, then iron.", "Three tidy shelves holding stone axes on one, bronze blades on another and iron knives on the third.", "build", "neutral", 2, "normal", 0, None, THO),
    ("And honestly, it worked. It's basically the world's oldest sock drawer, and everyone loved it.", "The main character happily sorts objects into neat piles, tongue out, very proud of himself.", "build", "funny", 2, "normal", 0, "pop", None),
    ("Archaeologists still use his three ages today, almost two hundred years later.", "A modern excavation trench with layered soil walls and a trowel resting on the edge.", "build", "neutral", 2, "normal", 0, None, "Three-age system, Encyclopaedia Britannica"),
    ("But notice what Thomsen couldn't sort: all the stuff that was already gone.", "The main character stares at an empty shelf holding only dust and a few splinters.", "build", "serious", 2, "slow", 0, None, None),
    ("Stone and metal last for ages. Wood, bark, and plant fibers usually don't, because they simply rot.", "A rotting log in a forest, covered in moss and fungus, breaking into soft pieces.", "build", "neutral", 2, "normal", 0, None, "General archaeological preservation principles; " + BAR),
    ("It's like your house burns down, and aliens judge your whole life by the one surviving toaster.", "The main character stands before a burned-down hut, holding a lonely cooking pot and shrugging.", "build", "funny", 3, "normal", 0, None, None),
    ("Archaeologists have dug up stone tools by the thousand. Wooden ones? Only from a handful of special sites.", "A huge pile of stone tools in the foreground, and a single small wooden stick resting far apart on a table.", "punchline", "serious", 2, "normal", 300, None, "Overview: Hawks, J., 'Four amazing Stone Age sites with wooden artifacts'"),
    # ---------------- where wood survives
    ("So how does wood ever survive that long?", "The main character kneels at a swampy pond edge, pulling up a dark wet stick.", "build", "curious", 2, "normal", 0, None, None),
    ("Rot needs air. Bury wood in waterlogged mud, and the rot-makers can barely breathe.", "A cross-section of dark muddy ground under still water, with a wooden stake buried deep inside.", "build", "neutral", 2, "normal", 0, None, "General archaeological preservation principles; " + BAR),
    ("So basically, ancient wood is just very lucky swamp survivors.", "The main character celebrates with both arms up, knee-deep in a muddy marsh, holding a wet stick.", "build", "funny", 2, "fast", 0, "boing", None),
    ("Rivers, springs, and mineral-rich caves did the preserving, and only a few such places exist.", "A spring bubbling over a pale mineral crust in a rocky hollow beside a green riverbank.", "build", "awe", 2, "normal", 0, None, "General archaeological preservation principles; " + SAL),
    ("Which means every wooden find is a tiny miracle.", "The main character holds a single wooden fragment in both hands, like a precious gem.", "build", "awe", 2, "slow", 0, None, None),
    ("And a few of those miracles will blow your mind. Let's start in Zambia.", "A wide African river with a tall waterfall in green bush, mist rising over the rocks.", "build", "excited", 2, "normal", 0, "whoosh", BAR),
    # ---------------- Kalambo Falls
    ("Kalambo Falls, a river on Zambia's border, where the mud kept everything wet for ages.", "The main character walks along a muddy riverbank beside a tall waterfall, looking around curiously.", "build", "curious", 2, "normal", 0, None, None),
    ("Archaeologists found two logs joined together by a notch that someone cut on purpose.", "Top-down view of two thick logs locked together by a cut notch in dark soil, with an archaeologist's brush beside them.", "build", "awe", 2, "normal", 0, None, BAR),
    ("Congratulations: it's the world's oldest piece of flat-pack furniture, and no instructions survived.", "The main character fits two logs together at a notch, wiping his forehead with relief.", "build", "funny", 2, "normal", 0, "pop", None),
    ("Luminescence dating puts it at least four hundred seventy-six thousand years ago.", "An old hourglass of sand resting beside a notched log on a flat stone.", "punchline", "awe", 3, "slow", 500, "ding", BAR),
    ("Why build it? Researchers think a platform or walkway, lifting people above wet ground.", "The main character balances on a raised log platform above marshy ground, arms out.", "build", "curious", 2, "normal", 0, None, None),
    ("Nobody knows who built it, but it's older than the oldest known Homo sapiens fossils.", "Two different ancient skulls resting on a sandy surface, one rounder and one longer.", "build", "serious", 2, "normal", 0, None, BAR + "; Hublin et al. (2017). Nature"),
    ("So somebody was doing carpentry half a million years ago. And I still can't build a bookshelf.", "The main character frowns at a heap of wooden planks and a confusing tangle, scratching his head.", "build", "funny", 3, "normal", 0, "boing", None),
    ("It's the earliest known structural use of wood. And not one stone in sight.", "A single wooden beam lying in dark soil with no stones nearby, a clean simple composition.", "punchline", "awe", 2, "slow", 400, None, BAR),
    # ---------------- Poggetti Vecchi
    ("Now hop to Tuscany, Italy, about a hundred and seventy thousand years ago.", "The main character walks through a marshy valley with tall reeds and distant hills, carrying a stick.", "build", "curious", 2, "normal", 0, "swoosh", None),
    ("Neanderthals worked a wetland full of elephant bones, and they left digging sticks behind.", "Large elephant bones and several long wooden sticks lying together in dark wet soil.", "build", "awe", 2, "normal", 0, None, ARA),
    ("Meet the boxwood digging stick: the Stone Age's secret multitool.", "The main character holds a long pointed stick, pretending it's a sword and a shovel at once.", "build", "funny", 2, "normal", 0, None, None),
    ("Over a meter long, rounded at one end, pointed at the other, and shaped on purpose.", "A long pale wooden stick with one rounded end and one pointed end lying on dark soil.", "build", "neutral", 2, "normal", 0, None, ARA),
    ("And here's the clever bit: they scorched the wood in a fire first.", "The main character holds a stick over glowing coals, turning it slowly, concentrating hard.", "build", "excited", 2, "normal", 0, None, None),
    ("Charring made hard boxwood easier to scrape and shape. That's fire technology, applied to a stick.", "A stick with blackened scorched patches beside a smoldering fire and a stone scraper.", "build", "neutral", 2, "normal", 0, None, ARA + "; Revedin et al. (2020), experimental study of the Poggetti Vecchi sticks"),
    ("So Neanderthals basically air-fried their shovels. I respect that.", "The main character gives a thumbs up to his scorched stick as smoke curls around it.", "build", "funny", 2, "fast", 0, None, None),
    ("Researchers think these were all-purpose tools, not weapons.", "Several digging sticks laid in a row beside a small pile of roots.", "build", "neutral", 2, "normal", 0, None, ARA),
    # ---------------- Schoningen
    ("Next stop: Germany, where a coal mine turned up the oldest wooden spears ever found.", "The main character peers into a deep open pit with layered dark earth, holding a lantern.", "build", "curious", 2, "normal", 0, None, None),
    ("The Schoningen spears were so well preserved that scientists could study how they were shaped.", "Long smooth wooden spears with sharpened tips laid on a dark cloth, lit softly.", "build", "awe", 2, "normal", 0, None, THI),
    ("They lay beside butchered horses. So yes, the dinner plans have been confirmed.", "The main character crouches low and points a spear toward a grazing wild horse across a grassy plain.", "build", "funny", 2, "normal", 0, "whoosh", None),
    ("Their age was recently revised, to nearer two hundred thousand years. Science keeps editing its own timeline.", "Bones of horses and a long wooden spear lying together in a muddy lakeshore layer.", "build", "serious", 2, "normal", 0, None, "Revised age for Schoningen hunting spears indicates intensification of Neanderthal cooperative behavior around 200,000 years ago (2025); " + THI),
    ("Wood is so rare that every new find rewrites the story a little. I find that oddly comforting.", "The main character erases and redraws a simple sun on a rock wall with a piece of charcoal, thoughtfully.", "build", "serious", 2, "slow", 0, None, None),
    ("Bones of many horses lay beside the spears, the marks of an ancient butchering site.", "Many large horse bones scattered on a muddy lake shore beside two wooden spears.", "build", "neutral", 2, "normal", 0, None, THI),
    # ---------------- Abric Romani (the opening discovery)
    ("Finally, back to Spain, and the discovery that started this whole video.", "The main character climbs a rocky hillside toward a wide shallow cave opening in a cliff.", "build", "curious", 2, "normal", 0, None, None),
    ("Abric Romani is a rock shelter near Barcelona, where Neanderthals camped between sixty-two and forty thousand years ago.", "A wide shallow rock shelter in a limestone cliff with excavation grids and soft morning light.", "build", "awe", 2, "normal", 0, None, SAL),
    ("And inside, scientists found five hundred ninety-seven wooden remains and imprints. That's a lot of wood.", "The main character is surrounded by dozens of wooden sticks and branches, spinning around in amazement.", "build", "excited", 3, "normal", 0, "ding", None),
    ("Most were branches and firewood. But thirteen were objects the Neanderthals actually made or used.", "Thirteen carved wooden pieces laid in neat rows beside a heap of plain branches on a table.", "build", "neutral", 2, "normal", 0, None, SAL),
    ("Two spears, one about two and a half meters long, the other about two. These guys planned ahead.", "The main character holds two very long wooden spears of different lengths, gazing up at the tips.", "build", "tense", 2, "normal", 0, None, None),
    ("Four slabs of charred bark, maybe trays for food, or carriers for glowing embers.", "Curved slabs of blackened tree bark lying on a stone floor near a fire pit.", "build", "awe", 2, "normal", 0, None, SAL),
    ("Neanderthal tableware. Please don't ask who did the dishes.", "The main character carries a bark tray piled with food, balancing it carefully and smiling.", "build", "funny", 2, "fast", 0, "pop", None),
    ("Crossed poles may have formed a cooking tripod, and a five-meter pole may have braced a windbreak.", "Several long poles crossed in a tripod shape beside a campfire, with a tall straight pole leaning on a rock wall.", "build", "neutral", 2, "normal", 0, None, SAL),
    ("So the wood rotted away, but its shape stayed behind. Basically, a ghost in the rock.", "The main character gently touches a stone wall with a wood-shaped hollow, eyes wide.", "build", "whisper", 2, "slow", 300, None, None),
    # ---------------- the big picture
    ("Calcium carbonate built up around each piece. As the wood decayed, it left cavities that kept its shape.", "A cross-section of pale stone with a smooth hollow tunnel where a branch once lay.", "punchline", "awe", 2, "normal", 0, None, SAL),
    ("So here's the real Stone Age toolkit: stone points tied to wooden handles, and plenty more.", "The main character ties a sharp stone to a stick with plant string, tongue out, concentrating.", "build", "curious", 2, "normal", 0, None, None),
    ("Poggetti Vecchi even shows wooden hafting technology: wood shaped to hold other tools.", "A stone point lashed into a wooden handle lying on pale ground beside a coil of plant fiber.", "build", "neutral", 2, "normal", 0, None, "Wooden hafting technology in the early Neanderthal site of Poggetti Vecchi (Italy)"),
    ("A hammer without its stick is just a very sad paperweight.", "The main character swings a handleless stone like a hammer, and it slips from his hand comically.", "build", "funny", 3, "fast", 0, "boing", None),
    ("Wood from this period is so rare that a single site can change the whole story.", "A lone wooden fragment on a clean display stand under a gentle spotlight in an empty room.", "build", "serious", 2, "normal", 0, None, BAR + "; " + SAL),
    ("So when you picture a Stone Age person, add the missing pieces: poles, bowls, handles, shelters.", "The main character stands in a camp surrounded by wooden tools, shelters and trays, looking surprised.", "build", "awe", 2, "slow", 0, None, None),
    ("Researchers say the Abric Romani wood points to everyday life: cooking, shelter, and tools.", "A cozy empty Neanderthal camp: a tripod over a fire, bark trays, and poles forming a windbreak.", "build", "neutral", 2, "normal", 0, None, SAL),
    ("Imagine our future: archaeologists dig up plastic bottles and a phone, and decide we lived in the Plastic Age.", "The main character poses proudly at a futuristic dig site, holding a plastic bottle and a smartphone.", "build", "funny", 3, "normal", 0, "pop", None),
    ("Thomsen's three ages were a brilliant sorting system. But they describe materials that last, not lives that were lived.", "A single polished stone axe alone in a plain glass case against a quiet background.", "build", "serious", 2, "slow", 0, None, THO),
    ("So next time someone says Stone Age, picture the wood too.", "The main character sits by a fire at dusk, a wooden spear and a bark tray beside him, calm.", "build", "serious", 2, "slow", 300, None, None),
    ("Rock is only what lasted. Their real world was made of forest.", "A quiet forest at sunrise with tall trees, and a single pale stone resting at the base of one trunk.", "punchline", "awe", 2, "slow", 800, None, BAR + "; " + SAL),
]

# Extra sentences (scene number -> appended text): the video must reach ~8 minutes of narration (~1200 words).
ADD = {
    13: " Spoiler: his filing system was about to shape how we imagine the past forever.",
    14: " Simple, tidy, and very easy to teach.",
    15: " The only problem is the socks that had already vanished.",
    16: " That's how powerful a good label is.",
    17: " The invisible stuff never made it into the drawer.",
    18: " That decay is plain chemistry, nothing mysterious about it.",
    19: " Same problem, just with a few hundred thousand years added.",
    20: " That imbalance quietly shapes everything we imagine about the past.",
    21: " It almost never does, which is exactly why this matters.",
    22: " Without oxygen, that wood can sit there for ages.",
    23: " I'd like that to be my retirement plan too.",
    24: " Wherever those conditions line up, we get a rare window.",
    25: " Treat it gently, because there are so few.",
    27: " Picture a quiet, muddy floodplain, long before any town existed.",
    28: " Not a broken branch, not a lucky accident, a real joint.",
    31: " It's a clever way to stay dry.",
    32: " Whoever it was, they were thinking in three dimensions.",
    35: " It's a wetland, and this is where the story gets even better.",
    36: " Researchers found the sticks right there among them.",
    37: " It digs, it pokes, it scrapes, and it probably gets lost a lot.",
    38: " That takes real skill and real patience.",
    39: " Fire isn't just for warmth, it's a workshop.",
    41: " Honestly, the technique is still smart today.",
    42: " Which is a much more peaceful picture than the movies suggest.",
    43: " Mining crews were digging for fuel and uncovered a lost world.",
    44: " That's a rare gift.",
    49: " Time to meet the star of the show.",
    50: " It's a natural roof with a view, basically a Stone Age balcony.",
    52: " Even the plain wood matters, because it shows what they gathered and burned.",
    56: " Together, they sketch a camp, not just a handful of tools.",
    58: " It's a mold of a branch that vanished tens of thousands of years ago.",
    59: " It's the part that made the stone useful.",
    62: " Every one counts.",
    63: " Suddenly the whole picture looks warmer, busier, and a lot more crafty.",
    64: " That's a whole daily routine sitting in a rock shelter.",
    65: " The label would say more about our trash than about us.",
    66: " That's not a flaw in Thomsen, only a limit of what survives.",
}
for n, extra in ADD.items():
    t = list(S[n - 1])
    t[0] += extra
    S[n - 1] = tuple(t)

assert len(S) == 68, len(S)
scenes = []
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, src) in enumerate(S):
    hero = i % 2 == 0
    assert ("the main character" in prompt.lower()) == hero, (i + 1, prompt)
    assert (beat == "hook") == (i < 12), i + 1
    assert src or hero, (i + 1, "fact scene needs a source")
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
                   "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
                   "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})
    if hero and src:
        scenes[-1]["fact_source"] = None

data = {
    "title": "Was the Stone Age Really a WOOD Age?",
    "title_alternatives": ["What Did Neanderthals Build From WOOD?", "Why Is the Stone Age Missing Its WOOD?",
                           "The Hidden WOOD Age Nobody Told You About", "What Did the Stone Age Lose to ROT?"],
    "description": ("We call it the Stone Age, but most of what ancient humans used every day was wood. This video follows "
                    "the real finds: a half-million-year-old notched log in Zambia, fire-hardened digging sticks in Italy, "
                    "spears in Germany, and a brand-new haul of Neanderthal wood from a Spanish rock shelter.\n\n"
                    "Why do we only see the rock? Because rock survives, and wood almost never does.\n\nSources:\n"
                    "- Barham, L. et al. (2023). Evidence for the earliest structural use of wood at least 476,000 years ago. Nature.\n"
                    "- Aranguren, B. et al. (2018). Wooden tools and fire technology in the early Neanderthal site of Poggetti Vecchi (Italy). PNAS.\n"
                    "- Thieme, H. (1997). Lower Palaeolithic hunting spears from Germany. Nature 385.\n"
                    "- Saladie, P. et al. Neanderthal wooden remains from Abric Romani. Science Advances (reported Oct 2026).\n"
                    "- Hublin, J.-J. et al. (2017). New fossils from Jebel Irhoud, Morocco. Nature.\n"
                    "- Thomsen, C. J. (1836). Ledetraad til Nordisk Oldkyndighed."),
    "tags": ["stone age", "wood age", "neanderthals", "ancient humans", "archaeology", "prehistory", "kalambo falls",
             "schoningen spears", "ancient tools", "human evolution", "animated explainer"],
    "mood": "mysterious",
    "sources": [
        "Barham, L. et al. (2023). Evidence for the earliest structural use of wood at least 476,000 years ago. Nature.",
        "Aranguren, B. et al. (2018). Wooden tools and fire technology in the early Neanderthal site of Poggetti Vecchi (Italy). PNAS.",
        "Thieme, H. (1997). Lower Palaeolithic hunting spears from Germany. Nature 385, 807-810.",
        "Saladie, P. et al. Neanderthal wooden remains from Abric Romani (Spain). Science Advances (reported October 2026).",
        "Hublin, J.-J. et al. (2017). New fossils from Jebel Irhoud, Morocco and the pan-African origin of Homo sapiens. Nature.",
        "Thomsen, C. J. (1836). Ledetraad til Nordisk Oldkyndighed.",
    ],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]))
