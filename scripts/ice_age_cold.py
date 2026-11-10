"""Builds scripts/ice_age_cold.json (run: ./venv/Scripts/python scripts/ice_age_cold.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

CLK = "Clark et al. (2009). The Last Glacial Maximum. Science 325"
PRY = "Pryor et al. (2020). The chronology and function of a new circular mammoth bone structure at Kostenki 11. Antiquity 94"
RUF = "Ruff, C. (1994). Morphological adaptation to climate in modern and fossil hominids. Yearbook of Physical Anthropology 37"
SOR = "Sorensen, Claud & Soressi (2018). Neandertal fire-making technology inferred from microwear analysis. Scientific Reports 8"
WRA = "Wrangham, R. (2009). Catching Fire: How Cooking Made Us Human"
FRO = "Froehle & Churchill (2009). Energetic competition between Neandertals and anatomically modern humans. PaleoAnthropology"
YAN = "Pitulko et al. (2004). The Yana RHS site: humans in the Arctic before the Last Glacial Maximum. Science 303"
SOS = "Soressi et al. (2013). Neandertals made the first specialized bone tools in Europe. PNAS 110"
COL = "Collard et al. (2016). Faunal evidence for a difference in clothing use between Neanderthals and early modern humans in Europe. Journal of Anthropological Archaeology 44"
DEN = "Archaeology magazine (2016). Denisova Cave yields a 50,000-year-old needle (report on the Siberian excavations)"
ZAV = "Zavala et al. (2021). Pleistocene sediment DNA reveals hominin and faunal turnovers at Denisova Cave. Nature 595"
MEZ = "Mezhyrich mammoth-bone dwellings, Ukraine: redated to about 18,000 years ago (Live Science, Wikipedia summaries of the excavation reports)"
HIG = "Higham et al. (2014). The timing and spatiotemporal patterning of Neanderthal disappearance. Nature 512"

S = [
    # ---------------- hook (12 one-line scenes)
    ("Minus twenty degrees. No heater, no jacket shop, no rescue.", "The main character shivers in a snowstorm, hugging himself, teeth chattering, a small icicle hanging from his nose.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Twenty thousand years ago, ice buried Canada and northern Europe.", "A towering white wall of ice stretching across a frozen plain under a pale sky.", "hook", "awe", 2, "normal", 0, None, CLK),
    ("And people still lived right beside it.", "The main character peeks around a boulder at a huge ice wall in the distance, wide-eyed.", "hook", "curious", 2, "normal", 0, None, None),
    ("Some lived above the Arctic Circle, thirty thousand years ago.", "A few small hide tents on a snowy plain beside a frozen river under a low pale sun.", "hook", "awe", 2, "normal", 0, None, YAN),
    ("If you hate winter, their story will humble you.", "The main character sits at a cave opening wrapped in furs, glaring at falling snow.", "hook", "serious", 2, "normal", 0, None, None),
    ("Even Neanderthal bodies, built for cold, needed help.", "A Neanderthal skeleton beside a modern human skeleton, the Neanderthal ribcage wider and its limbs shorter.", "hook", "curious", 2, "normal", 0, None, RUF),
    ("Stay for four survival tricks that kept them alive.", "The main character holds up four fingers with a determined grin, snowflakes on his hair.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("One winter home was built from a mammoth skeleton.", "A round hut built from mammoth bones and curved tusks, snow falling around it.", "hook", "whisper", 2, "slow", 0, None, MEZ),
    ("And one trick, you still use every single winter.", "The main character smirks and pulls his fur collar up over his chin, pointing at the viewer.", "hook", "tense", 2, "normal", 0, None, None),
    ("It starts with fire, possibly made fifty thousand years ago.", "A flint hand axe with tiny scratches beside a shiny golden mineral chunk, with a few bright sparks.", "hook", "excited", 2, "normal", 0, None, SOR),
    ("But fire alone wasn't enough. Not even close.", "The main character sits very close to a small campfire, still shivering, frost on his shoulders.", "hook", "tense", 2, "normal", 0, None, None),
    ("Models say a Neanderthal needed about four thousand calories daily.", "A towering pile of meat, bones and fat stacked on a flat stone.", "hook", "awe", 3, "normal", 500, None, FRO),
    # ---------------- the cold
    ("Let's set the scene. The coldest stretch of the last Ice Age lasted for thousands of years.", "The main character stands in a blowing snowstorm holding a small map, squinting at a white horizon.", "build", "curious", 2, "normal", 0, None, None),
    ("Researchers date the peak of the great ice sheets to roughly twenty-six thousand to nineteen thousand years ago.", "A huge ice sheet edge with blue cracks meeting a frozen gravel plain, low sun on the horizon.", "build", "neutral", 2, "normal", 0, None, CLK),
    ("Now picture living there. Not visiting. Living. Every winter, for your whole life.", "The main character stands tiny at the foot of a giant ice wall, holding a small bundle, looking up in dismay.", "build", "serious", 2, "slow", 0, None, None),
    ("In places, winter temperatures probably dropped to around minus twenty Celsius or lower, with summers short and cool.", "A frozen landscape at dusk with a tall wooden post carrying a drawn thermometer whose blue line is almost at the bottom.", "build", "tense", 2, "normal", 0, None, PRY),
    ("Your breath would freeze in your beard. Your phone? You don't have one. Small blessing.", "The main character's breath turns into a tiny ice cloud that freezes and drops to the ground, his eyes crossed.", "build", "funny", 2, "fast", 0, None, None),
    ("Bodies helped. Neanderthals had broad chests and short limbs, a build often linked to cold climates, though scientists still debate how much.", "A Neanderthal skeleton beside a modern human skeleton on a plain cloth, the Neanderthal ribcage broad and its limbs shorter.", "build", "neutral", 2, "normal", 0, None, RUF),
    # ---------------- trick one: fire
    ("Trick number one: fire. Easy, right? Rub two sticks together and relax.", "The main character rubs two sticks together, sweating and tired, with only a thin wisp of smoke.", "build", "funny", 2, "normal", 0, "boing", None),
    ("In twenty eighteen, researchers reported wear marks on fifty thousand year old French hand axes. The marks match striking flint against pyrite to make sparks.", "Two flint hand axes with fine scratches beside a shiny golden mineral chunk, a few bright sparks flying.", "build", "curious", 2, "normal", 0, None, SOR),
    ("So Neanderthals may have made fire on demand. Some scientists still want more proof, so we'll say may.", "The main character strikes a stone against a shiny golden rock, sparks flying, looking delighted and surprised.", "punchline", "excited", 2, "normal", 0, "ding", None),
    ("Fire needs fuel, and trees were scarce on cold plains. At Kostenki in Russia, hearths hold charcoal and burnt bone, hinting that bones may have fed the flames too.", "A stone-ringed hearth with black charcoal and small burnt bones scattered around it, ash and a thin line of smoke.", "build", "neutral", 2, "normal", 0, None, PRY),
    ("Heating your home with leftovers. Recycling at its most extreme.", "The main character tosses a bone onto a campfire like a log, looking pleased with himself.", "build", "funny", 2, "fast", 0, None, None),
    ("Fire also cooked meat, and cooked food is easier to digest, which leaves the body more energy to spare.", "A large joint of roasted meat on a wooden spit over glowing coals.", "build", "serious", 2, "normal", 0, None, WRA),
    ("And it kept the whole camp together, everyone elbowing closer to the flames.", "The main character squeezes into a tight circle of stick figures around a fire, shoulder to shoulder, smiling.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- trick two: calories
    ("Trick number two: eat. Models estimate a Neanderthal needed around thirty-five hundred to forty-five hundred calories a day in winter.", "A huge heap of meat, marrow bones and fat chunks on a flat stone table.", "punchline", "awe", 2, "normal", 300, None, FRO),
    ("That's roughly two large pizzas a day, just to stay warm. And no delivery.", "The main character staggers under a gigantic pile of food that is taller than he is, wobbling.", "build", "funny", 3, "fast", 0, None, None),
    ("At Yana in Arctic Siberia, thirty thousand years ago, hunters left spear tips made from rhinoceros horn and mammoth ivory.", "A long pointed spear foreshaft carved from pale horn and ivory lying on frozen ground.", "build", "neutral", 2, "normal", 0, None, YAN),
    ("Big animals meant big meals: fat, meat and marrow in one hunt. Winter's best deal.", "The main character carries a giant bone over his shoulder, grinning, a trail of footprints in the snow behind him.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- trick three: clothes
    ("Trick number three: clothes. Fifty thousand years ago, Neanderthals in France shaped deer ribs into smooth tools for softening and waterproofing animal hides.", "A smooth polished bone tool made from a deer rib lying on a piece of tanned hide.", "build", "curious", 2, "normal", 0, None, SOS),
    ("Leather, basically. The original waterproof jacket.", "The main character rubs a hide with a bone tool, then pours water on it and watches the drops roll off.", "build", "excited", 2, "normal", 0, None, None),
    ("A twenty sixteen study found fewer fox and wolf remains at Neanderthal sites than at modern human sites, hinting that Neanderthals wore simple capes rather than tailored outfits. That's an inference, not proof.", "Fox and wolf fur pelts hanging over a wooden rack beside a plain animal hide cape lying on a stone.", "build", "neutral", 2, "normal", 0, None, COL),
    ("So Neanderthals may have worn capes. Cozy up top, windy around the ankles.", "The main character in a plain hide cape shivers as the wind blows the cape up over his head.", "build", "funny", 2, "fast", 0, None, None),
    ("Then came tailoring. At Denisova Cave in Siberia, researchers found a seven centimetre bird bone needle with an eye for thread, dated to about fifty thousand years ago.", "A thin carved bone needle with a small eye at one end lying on a flat stone in soft light.", "punchline", "awe", 3, "slow", 500, "ding", DEN),
    ("Yes, a needle. The first tailor shop opened in a cave. Hold your applause.", "The main character squints and threads a bone needle through a fur scrap, pricking his finger with a yelp.", "build", "funny", 2, "normal", 0, None, None),
    ("Who made it is still debated, Denisovans or modern humans, but it shows that sewing is very, very old.", "Several small bone needles of different sizes lined up on a piece of tanned hide.", "build", "serious", 2, "normal", 0, None, DEN),
    ("Sewn fur traps warm air in layers. That's the trick you still use: a coat, a sweater, a scarf. Same idea, fifty thousand years later.", "The main character proudly shows off three stacked fur layers like a model, puffed up like a ball.", "punchline", "happy", 2, "normal", 300, None, None),
    ("That cave was home to Neanderthals and Denisovans at different times, so whoever held that needle is a real puzzle.", "A wide rocky cliff above a river valley with a dark cave mouth, in autumn colours.", "build", "curious", 2, "normal", 0, None, ZAV),
    # ---------------- trick four: shelter
    ("Trick number four: shelter. And now, as promised, the house built from a mammoth.", "The main character knocks politely on the bone door of a giant round shelter, holding a tiny gift.", "build", "whisper", 2, "slow", 0, None, None),
    ("At Mezhyrich in Ukraine, ice age builders stacked hundreds of mammoth bones and tusks into round huts.", "A dome shaped hut made of stacked mammoth jaw bones and curved tusks with a hide roof, snow on the ground.", "build", "awe", 2, "normal", 0, None, MEZ),
    # ---------------- subscribe (once)
    ("Quick pause. If you're enjoying this, tap subscribe, because a new ancient mystery lands every week. It's free, it takes one second, and it helps more curious people find stories like this.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    ("Newer dating puts those huts at roughly eighteen thousand years old, older than the earlier estimate of fifteen thousand.", "A cutaway drawing of a round bone-framed hut covered in thick hide, a small fire pit glowing inside.", "build", "neutral", 2, "normal", 0, None, MEZ),
    ("Picture it. A skeleton for walls, hides for a roof, a fire inside. Cozy, in a slightly spooky way.", "The main character peeks out of a bone hut doorway with a warm glow behind him, grinning.", "build", "funny", 2, "normal", 0, None, None),
    ("Researchers think the bones formed a frame for thick hides, which would keep the wind out.", "A close view of mammoth tusks bent into an arch with a thick hide draped over the frame.", "build", "neutral", 2, "normal", 0, None, MEZ),
    ("But a house made of dead animals does come with a smell. Let's not talk about the smell.", "The main character pinches his nose in the doorway of a bone hut, eyes watering, a green cloud drifting out.", "build", "funny", 2, "fast", 0, None, None),
    ("At Kostenki in Russia, a twenty-five thousand year old circle used fifty-one mammoth jaws and sixty-four skulls.", "A ring-shaped wall of mammoth jaws and skulls seen from above on snowy ground.", "build", "awe", 2, "normal", 0, None, PRY),
    ("So that must be a home, right? Plot twist. It might not be.", "The main character stands inside a ring of giant skulls, scratching his head, looking suspicious.", "punchline", "curious", 2, "normal", 300, None, None),
    ("The debris inside was far too thin for a lived-in house, and bones still carried fat. The site may have stored meat, like a giant ice age freezer.", "A circular wall of mammoth bones with cuts of meat stacked inside and snow piled on top.", "build", "serious", 2, "normal", 0, None, PRY),
    ("A freezer made of bones. Nature supplied the cold. All you needed was a lot of mammoth.", "The main character carefully lays a huge steak inside a snowy bone circle, then pats it goodnight.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- how far it worked
    ("And the Yana site sits at seventy-one degrees north, more than twice as old as any other Arctic site known when it was announced.", "A wide frozen river plain in the far north under a pale low sun, the outline of a distant hide tent camp.", "build", "awe", 2, "slow", 0, None, YAN),
    ("Seventy-one degrees north is about as far north as Utqiagvik, Alaska. Now that's commitment.", "The main character stands on a glowing arctic horizon wearing a ridiculous number of fur layers, giving a thumbs up.", "build", "funny", 2, "normal", 0, None, None),
    ("Neanderthals were still living in Europe until about forty thousand years ago, after many ice age cycles.", "A long stone cave ledge with a single glowing hearth looking out over a snowy valley at dusk.", "build", "serious", 2, "slow", 0, None, HIG),
    ("No single trick saved them. Fire, food, clothes and shelter worked together, and each one was taught from person to person.", "The main character teaches a smaller stick figure to hold a bone needle, by a warm fire.", "punchline", "serious", 2, "slow", 400, None, None),
    ("When the ice finally began to retreat, around nineteen to twenty thousand years ago, their knowledge didn't vanish with it.", "A thin blue river of meltwater running out of the edge of a huge ice sheet toward green ground.", "build", "awe", 2, "slow", 0, None, CLK),
    ("So next time you pull on a coat, thank a cave tailor. Like the video if you enjoyed it, and tell me your coldest day in the comments. Next time: when did dogs join the camp? See you there.", "The main character zips up a fluffy coat that is far too big for him, smiling warmly as snow falls.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 45 <= len(S) <= 80, len(S)
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
    "title": "How Did Ancient Humans Survive the ICE AGE Cold?",
    "title_alternatives": ["How Did Humans Survive MINUS 20 Without Heat?", "The Mammoth Bone HOUSE Nobody Expected",
                           "What Did Neanderthals Wear in the ICE AGE?", "Neanderthals Needed 4,000 CALORIES a Day. Why?"],
    "description": ("Twenty thousand years ago, ice sheets buried Canada and northern Europe, and people still lived beside them. This video "
                    "follows the four tricks that kept ancient humans alive: fire, food, clothes and shelter. It covers Neanderthal fire-making, "
                    "a fifty thousand year old needle, a house built from mammoth bones, and a bone circle that may have been an ice age freezer.\n\n"
                    "Sources:\n"
                    "- Clark et al. (2009). The Last Glacial Maximum. Science.\n"
                    "- Pryor et al. (2020). A new circular mammoth bone structure at Kostenki 11. Antiquity.\n"
                    "- Sorensen, Claud & Soressi (2018). Neandertal fire-making technology. Scientific Reports.\n"
                    "- Froehle & Churchill (2009). Energetic competition between Neandertals and modern humans. PaleoAnthropology.\n"
                    "- Soressi et al. (2013). Neandertals made the first specialized bone tools in Europe. PNAS.\n"
                    "- Collard et al. (2016). Faunal evidence for clothing use. Journal of Anthropological Archaeology.\n"
                    "- Pitulko et al. (2004). The Yana RHS site. Science."),
    "tags": ["ice age", "ancient humans", "neanderthals", "how did humans survive the cold", "mammoth bone house", "stone age",
             "prehistory", "archaeology", "last glacial maximum", "ancient clothing", "animated explainer", "stickman"],
    "mood": "mysterious",
    "sources": [
        "Clark, P. U. et al. (2009). The Last Glacial Maximum. Science 325, 710-714.",
        "Pryor, A. J. E. et al. (2020). The chronology and function of a new circular mammoth bone structure at Kostenki 11. Antiquity 94.",
        "Ruff, C. B. (1994). Morphological adaptation to climate in modern and fossil hominids. Yearbook of Physical Anthropology 37.",
        "Sorensen, A. C., Claud, E. & Soressi, M. (2018). Neandertal fire-making technology inferred from microwear analysis. Scientific Reports 8, 10065.",
        "Wrangham, R. (2009). Catching Fire: How Cooking Made Us Human.",
        "Froehle, A. W. & Churchill, S. E. (2009). Energetic competition between Neandertals and anatomically modern humans. PaleoAnthropology.",
        "Pitulko, V. V. et al. (2004). The Yana RHS site: humans in the Arctic before the Last Glacial Maximum. Science 303, 52-56.",
        "Soressi, M. et al. (2013). Neandertals made the first specialized bone tools in Europe. PNAS 110, 14186-14190.",
        "Collard, M. et al. (2016). Faunal evidence for a difference in clothing use between Neanderthals and early modern humans in Europe. Journal of Anthropological Archaeology 44.",
        "Zavala, E. I. et al. (2021). Pleistocene sediment DNA reveals hominin and faunal turnovers at Denisova Cave. Nature 595.",
        "Higham, T. et al. (2014). The timing and spatiotemporal patterning of Neanderthal disappearance. Nature 512, 306-309.",
    ],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]))
em = [s["emotion"] for s in scenes]
run = 1
for i in range(1, len(em)):
    run = run + 1 if em[i] == em[i - 1] else 1
    if run > 3:
        print("4+ same emotion in a row at scene", i + 1, em[i])
