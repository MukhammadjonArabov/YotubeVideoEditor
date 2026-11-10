"""Builds scripts/food_preservation.json (run: ./venv/Scripts/python scripts/food_preservation.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

JAY = "Jay, Loessner & Golden (2005). Modern Food Microbiology (7th ed.), Springer"
MAI = "Maixner et al. (2018). The Iceman's last meal consisted of fat, wild meat, and cereals. Current Biology 28"
LIV = "Live Science report on the 500-year-old chuño found in an Inca storeroom in Peru (study in the Journal of Field Archaeology)"
STA = "Star et al. (2017). Ancient DNA reveals the Arctic origin of Viking Age cod from Haithabu, Germany. PNAS 114"
WEL = "Weller & Dumitroaia (2005). The earliest salt production in the world: an early Neolithic exploitation in Poiana Slatinei-Lunca, Romania. Antiquity 79"
GAR = "Smithsonian Magazine, 'Recovering the formula for garum' (Pompeii Garum Shop; Zephyrus 2018 study); Baelo Claudia fish-salting vats, Spain"
HON = "BBC Science Focus, 'Why doesn't honey go off?' (low moisture, acidity, hydrogen peroxide)"
PIC = "History.com, 'Pickles history timeline'; Wikipedia, 'Pickling' (Mesopotamian vinegar pickling c. 2400 BCE estimated; Tigris Valley cucumbers c. 2030 BCE)"
KUI = "Kuijt & Finlayson (2009). Evidence for food storage and predomestication granaries 11,000 years ago in the Jordan Valley. PNAS 106"
PRY = "Pryor et al. (2020). The chronology and function of a new circular mammoth bone structure at Kostenki 11. Antiquity 94"
YAK = "Wikipedia, 'Yakhchal'; Archaeology Now, 'Persian ice towers'"
SAL = "Salque et al. (2013). Earliest evidence for cheese making in the sixth millennium BC in northern Europe. Nature 493"
XIA = "Study of the Bronze Age kefir cheese from the Xiaohe cemetery, Xinjiang, Cell (2024), reported by SCMP and National Geographic"
CDC = "CDC, MMWR (2003). Botulism outbreak associated with eating fermented food, Alaska; CDC Emerging Infectious Diseases (2004) on foodborne botulism in Alaska"

S = [
    # ---------------- hook (12 one-line scenes)
    ("Fresh meat goes bad in just days.", "The main character holds his nose over a green, stinky steak with wavy stink lines rising from it.", "hook", "curious", 2, "normal", 0, None, None),
    ("Cheese, buried in a Chinese desert thirty-five hundred years ago.", "A small lump of pale hardened cheese on a scrap of cloth in a dry sandy burial pit.", "hook", "awe", 2, "slow", 0, None, XIA),
    ("Someone had beaten rot, long before the fridge.", "The main character leans on a cave wall with folded arms, looking smug beside an old cracked clay jar.", "hook", "curious", 2, "normal", 0, None, None),
    ("Eleven thousand years ago, villagers were already building granaries.", "A small round mud-brick granary raised on stone posts on a dry hillside near a salty sea.", "hook", "awe", 2, "normal", 0, None, KUI),
    ("Every meal you ate today is part of that fight.", "The main character takes a happy bite of bread while tiny cartoon germs run away from a small shield.", "hook", "serious", 2, "normal", 0, None, None),
    ("One bacterium can double every twenty minutes.", "A tiny glowing green dot splitting into two dots on a round dish seen through a magnifying circle.", "hook", "tense", 2, "normal", 0, None, JAY),
    ("Stay for six ancient tricks that beat rot.", "The main character holds up six fingers with a confident grin, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("One of those methods can still turn deadly.", "A tightly sealed plastic tub sitting alone on a snowy field with a faint green glow around its lid.", "hook", "whisper", 2, "slow", 0, None, CDC),
    ("And one trick made ice in the desert.", "The main character holds a sparkling ice cube in a blazing desert, grinning, sweat drops flying off him.", "hook", "tense", 2, "normal", 0, None, None),
    ("Salt was being made in Romania eight thousand years ago.", "A mound of grey ash beside a salty spring with a small clay pot of brine, early morning light.", "hook", "excited", 2, "normal", 0, None, WEL),
    ("Let's start with the oldest trick of all.", "The main character draws a line in the sand with a stick and points at it, grinning.", "hook", "curious", 2, "normal", 0, None, None),
    ("Archaeologists even found a freeze-dried potato, five hundred years old.", "Two small shrivelled dark lumps of dried potato resting on a flat stone in a stone-walled storeroom.", "hook", "awe", 3, "normal", 500, None, LIV),
    # ---------------- why food rots
    ("Let's start with a simple question. Why does food rot at all?", "The main character peers suspiciously at a fuzzy green apple on a stone table, one eyebrow raised.", "build", "curious", 2, "normal", 0, None, None),
    ("Mostly because microbes, bacteria and moulds, move in and multiply. In perfect conditions, one bacterium can divide about every twenty minutes.", "A tiny glowing green dot splitting into two, then four, then eight dots on a round dish seen through a magnifying circle.", "build", "neutral", 2, "normal", 0, None, JAY),
    ("Warm kitchen, plenty of time, and that family of germs grows fast. Basically a never-ending party, and your leftovers are the venue. Honestly, the fridge might be the most underrated invention ever.", "The main character watches tiny cartoon germs in party hats dancing on a slice of meat, horrified.", "build", "funny", 2, "fast", 0, None, None),
    ("Microbes need water, warmth and time. Take one of those away, and spoilage slows right down.", "Three simple objects side by side on a stone: a water drop, a small flame and a sand timer.", "build", "serious", 2, "normal", 0, None, JAY),
    # ---------------- trick one: dry
    ("Trick number one: steal the water. Dry the food, and the microbes lose their home.", "The main character squeezes a wet sponge until it is dry and crumbly, looking triumphant.", "build", "excited", 2, "normal", 0, None, None),
    ("Ötzi the Iceman died in the Alps about fifty-three hundred years ago. His last meal held ibex fat, red deer meat and wild grain, and some of that meat may have been dried.", "A small pile of dried strips of meat and a lump of white fat on a flat stone, a snowy mountain behind.", "build", "neutral", 2, "normal", 0, None, MAI),
    ("A prehistoric trail mix, then. Stiffer than ours, and nobody complained about the sell-by date.", "The main character chews a strip of tough dried meat with great effort, his cheek bulging.", "build", "funny", 2, "normal", 0, None, None),
    ("In the high Andes, people made chuño. Potatoes were left out to freeze overnight, then dried in the sun, and the cycle repeated until they were hard and light.", "Rows of small dark potatoes laid out on frosty ground at dawn with snowy mountain peaks behind.", "build", "curious", 2, "normal", 0, None, LIV),
    ("Nature's freezer at night, nature's drying rack by day. The mountains did the work, and no electricity was needed.", "The main character turns potatoes over on frozen rocks at sunrise, rubbing his shivering arms.", "build", "happy", 2, "normal", 0, None, None),
    ("It only works where hard frost is regular, so chuño was made in the mountains and carried onward by llama caravans.", "A line of laden llamas walking along a high mountain trail beside snowy peaks.", "build", "neutral", 2, "normal", 0, None, LIV),
    ("So a llama was basically the first delivery truck. Cute, slow, and slightly rude.", "The main character stands beside a very serious llama loaded with sacks, receiving a grumpy stare.", "build", "funny", 2, "fast", 0, None, None),
    ("Archaeologists recently found chuño in an Inca storeroom in Peru, about five hundred years old. It was only the second time it has been recovered from an Inca site.", "Two small shrivelled dark lumps of dried potato resting on a flat stone in a stone-walled storeroom.", "punchline", "awe", 2, "normal", 400, "ding", LIV),
    ("Five hundred years old, and still recognisably a potato. My leftover pizza can't even last the weekend.", "The main character holds a tiny shrivelled potato up to the light like a jewel, then gives a thumbs up.", "build", "funny", 2, "normal", 0, None, None),
    ("Dried fish went on long trips too. Ancient genetic evidence from Viking Age fish bones at Haithabu in Germany traces the cod back to the Lofoten waters of northern Norway.", "A wooden rack of split dried fish hanging in cold sea wind beside a rocky northern shoreline.", "build", "curious", 2, "normal", 0, None, STA),
    ("That's a long way to carry lunch. But dried cod is light, hard and patient, a perfect travelling snack. Like a very hard, very old protein bar.", "The main character carries a stack of stiff dried fish over his shoulder like a bundle of planks, grinning.", "build", "funny", 2, "normal", 0, None, None),
    ("Researchers still debate whether that fish was a trade good or food for a long journey, but either way, drying clearly worked.", "A wooden longship on calm grey water carrying stacked bundles of dried fish.", "build", "serious", 2, "normal", 0, None, STA),
    # ---------------- trick two: salt
    ("Trick number two: salt. It also pulls water out of food, so microbes can't settle in.", "The main character sprinkles salt over a fish with a very dramatic chef's flourish.", "build", "excited", 2, "normal", 0, None, None),
    ("At Poiana Slatinei in Romania, mounds of ash show people making salt from spring brine about eight thousand years ago.", "A mound of grey ash and charcoal beside a salty spring with a clay pot of brine, early morning light.", "build", "awe", 2, "normal", 0, None, WEL),
    ("Imagine boiling a whole spring just to get a pinch of salt. Your salt shaker has a very long family tree.", "The main character stirs a giant pot of brine over a fire, tongue out, tasting it with a squint.", "build", "funny", 2, "normal", 0, None, None),
    ("The Romans took salting to an industrial scale. At Baelo Claudia in Spain, rows of stone vats were used to salt big catches of fish.", "Rows of stone-lined rectangular vats beside a calm blue bay with a stack of large fish bones.", "build", "neutral", 2, "normal", 0, None, GAR),
    # ---------------- trick three: sweet and sour
    ("Trick number three: make it sweet or sour. Honey and vinegar keep microbes out, and I'll show you why.", "The main character carefully sets a clay jar of honey and a clay jar of vinegar side by side, smiling.", "build", "curious", 2, "normal", 0, None, None),
    ("Honey has very little free water, it's acidic, and bees add an enzyme that makes tiny amounts of hydrogen peroxide. Most microbes struggle in that. Though honey can ferment if it soaks up moisture.", "A dripping wooden dipper over a clay jar of golden honey with a bee hovering above.", "build", "neutral", 2, "normal", 0, None, HON),
    ("Sour works too. Acid makes life hard for microbes, so a pickle keeps going long after the cucumber should have given up.", "The main character wrinkles his whole face after biting a sour green pickle, eyes watering.", "build", "funny", 2, "fast", 0, None, None),
    ("Vinegar pickling is often traced to Mesopotamia, roughly four thousand years ago. The exact date is an estimate, but pickled cucumbers in the Tigris Valley are reported from around two thousand BCE.", "A row of clay jars filled with small green cucumbers and sprigs of herbs beside a river bank.", "build", "serious", 2, "normal", 0, None, PIC),
    # ---------------- trick four: store smartly
    ("Trick number four: store it smartly. And this one may have helped change history.", "The main character shuts the door of a small hut stuffed with sacks of grain, wedging it with a big stick.", "build", "curious", 2, "normal", 0, None, None),
    ("At Dhra' near the Dead Sea in Jordan, researchers found granaries with raised floors, built around eleven thousand years ago, before farming began.", "A small round mud-brick granary raised on stone posts on a dry hillside near a salty sea.", "build", "awe", 2, "normal", 0, None, KUI),
    ("Raised floors. Smart. Air flows underneath, and rodents have a much harder climb. Think of it as a pantry lock, minus the lock.", "The main character stands guard beside a raised hut while a tiny mouse looks up at the high floor in despair.", "build", "funny", 2, "normal", 0, None, None),
    ("The researchers argue that storing wild grain helped lead to farming, because stored food let communities stay in one place.", "A cutaway drawing of a granary with a raised floor, grain inside and open space underneath for air.", "punchline", "awe", 2, "normal", 300, None, KUI),
    # ---------------- trick five: cold
    ("Trick number five: chill it. Cold slows microbes to a crawl, and the Ice Age gave people a free freezer.", "The main character tucks a big piece of meat into a hole in the snow and pats the snow flat.", "build", "curious", 2, "normal", 0, None, None),
    ("At Kostenki in Russia, a twenty-five thousand year old circle of mammoth bones may have stored meat in the cold, researchers suggest, because the debris was too thin for a lived-in home.", "A circular wall of mammoth bones with cuts of meat stacked inside and snow piled on top.", "build", "neutral", 2, "normal", 0, None, PRY),
    # ---------------- subscribe (once)
    ("Quick pause. If you're enjoying this, tap subscribe, because a new ancient mystery lands every week. It's free, it takes one second, and it helps more curious people find stories like this.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    ("Persian builders went further. They made ice in the desert, in structures called yakhchals. Shallow pools froze on cold nights, and the ice was stored in a deep pit packed with straw.", "A tall cone-shaped mud-brick dome standing alone in a desert beside long shaded pools, bright sun.", "build", "awe", 2, "normal", 0, None, YAK),
    ("Ice. In the desert. In summer. They were basically wizards with mud bricks. My favourite trick on the whole list, and it's not close.", "The main character stares up at a giant mud-brick dome with a wizard hat on his head, mouth open.", "build", "funny", 2, "normal", 0, None, None),
    ("Wind towers pulled cool air down, and many yakhchals sat beside qanats, underground channels of cool water. Records suggest they go back to around four hundred BCE, though that date is debated.", "A cutaway drawing of a domed building with layers of ice and straw in a deep pit and a tall wind tower.", "build", "neutral", 2, "normal", 0, None, YAK),
    # ---------------- trick six: ferment
    ("Trick number six: let the friendly microbes win. It's called fermentation, and it might be the strangest trick of all.", "The main character cheers on a tiny cartoon germ in a boxing ring that is beating a bigger grumpy germ.", "build", "excited", 2, "normal", 0, None, None),
    ("About seven thousand years ago, farmers in Poland strained milk through pottery sieves full of small holes. Chemical analysis of the pots shows it was cheese.", "A clay sieve full of small holes next to a lump of white cheese on a wooden board.", "build", "curious", 2, "normal", 0, None, SAL),
    ("Why cheese? It keeps far longer than fresh milk.", "The main character proudly holds up a wedge of cheese in one hand and a jug of milk in the other, comparing them.", "build", "happy", 2, "normal", 0, None, None),
    ("The researchers suggested cheese making also cut the lactose, which may have let early farmers who couldn't digest fresh milk still enjoy dairy.", "A clay pot of milk on one side of a wooden table, a block of cheese on the other, with a small arrow drawn between them.", "build", "neutral", 2, "normal", 0, None, SAL),
    ("A built-in lactose workaround, thousands of years before anyone invented a pill for it. Clever, honestly.", "The main character happily nibbles a wedge of cheese while looking at a milk jug and shaking his head, no thanks.", "build", "funny", 2, "normal", 0, None, None),
    ("And cheese goes on long journeys. In the Xiaohe cemetery, in China's Taklamakan Desert, researchers found kefir cheese buried about thirty-five hundred years ago.", "A small lump of pale hardened cheese on a scrap of cloth in a dry sandy burial pit.", "build", "awe", 2, "slow", 0, None, XIA),
    ("A fermented snack for the afterlife. At least somebody planned ahead.", "The main character carefully tucks a wedge of cheese into a small pouch and zips up his fur coat, nodding.", "build", "funny", 2, "normal", 0, None, None),
    ("Researchers recovered genetic material from kefir microbes in that cheese, including Lactobacillus kefiranofaciens, plus traces of goat and cow milk.", "A tiny round glowing green microbe with thin hair-like edges beside a small lump of cheese seen through a magnifying circle.", "punchline", "awe", 2, "normal", 400, None, XIA),
    ("Tiny survivors, doing their job for thousands of years. Your yoghurt tub has some serious competition.", "The main character salutes a tiny cartoon microbe wearing a soldier's helmet, standing very straight.", "build", "funny", 2, "normal", 0, None, None),
    ("In Pompeii, Italian researchers found six sealed jars inside a workshop called the Garum Shop, where fish were being salted into fish sauce when the volcano erupted in seventy-nine CE.", "Rows of large round clay jars set halfway into a stone floor in a small workshop with fish bones nearby.", "build", "curious", 2, "normal", 0, None, GAR),
    ("But fermentation has a darker side. Done wrong, the wrong microbes win.", "The main character looks nervously at a covered pot with a faint green glow leaking out of the lid.", "build", "tense", 2, "slow", 0, None, None),
    ("Traditional fermentation in Alaska Native communities used grass-lined pits or barrels sunk into the ground, where the cold kept everything slow and steady.", "A grass-lined pit in the ground with a wooden barrel set into it on snowy tundra.", "build", "serious", 2, "normal", 0, None, CDC),
    ("That cold, slow method worked for generations. Keep that in mind, because the next part is about what changed.", "The main character gently pats the earth around a buried barrel, nodding with respect.", "build", "awe", 2, "slow", 0, None, None),
    ("Since the nineteen seventies, many people have used sealed plastic or glass containers and warmer storage, and the Centers for Disease Control reports that this raised the risk of botulism.", "A sealed plastic tub next to a grass-lined pit on a snowy field, side by side.", "punchline", "serious", 3, "slow", 500, None, CDC),
    ("Same food, different container, very different result. Old methods were never magic. They were careful, slow, and tested by generations.", "The main character looks at two jars, one old clay jar and one shiny modern jar, scratching his head.", "build", "serious", 2, "slow", 0, None, None),
    # ---------------- close
    ("The evidence stretches from granaries by the Dead Sea eleven thousand years ago to an Inca potato five hundred years old, and no single method ever did the job alone.", "A long stone shelf holding a clay jar of honey, a dried potato, a bag of salt, a cheese wedge and a small grain basket in a neat row.", "punchline", "awe", 2, "slow", 300, None, KUI + "; " + LIV),
    ("Dry it, salt it, sweeten it, store it, chill it, ferment it. They stacked the tricks like layers of armour against rot. So next time you open the fridge, thank a cave cook. Like the video if you enjoyed it, and tell me your weirdest food trick in the comments. Next time: when did dogs join the camp? See you there.", "The main character opens a glowing fridge door at night, smiling warmly, with a tiny cave painting of a dog on the wall behind him.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 55 <= len(S) <= 80, len(S)
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
    "title": "How Did Ancient Humans Keep Food From ROTTING?",
    "title_alternatives": ["Ancient Humans Had No FRIDGE. Here's What They Did", "The 6 Ancient Tricks That Stopped FOOD From Rotting",
                           "Cheese Buried 3,500 Years Ago? How Ancient FOOD Lasted", "How Did a 500-Year-Old POTATO Survive?"],
    "description": ("Fresh meat goes bad in days, yet people have kept food for years, even millennia. This video follows six ancient tricks "
                    "for beating rot: drying, salting, sweet and sour preserving, smart storage, cold, and fermentation. It covers a "
                    "500-year-old Inca potato, 8,000-year-old salt works, 11,000-year-old granaries, a desert ice house in Persia and "
                    "cheese buried 3,500 years ago.\n\nThis video is history and science, not food safety advice.\n\nSources:\n"
                    "- Maixner et al. (2018). The Iceman's last meal. Current Biology.\n"
                    "- Star et al. (2017). Ancient DNA reveals the Arctic origin of Viking Age cod from Haithabu. PNAS.\n"
                    "- Weller & Dumitroaia (2005). The earliest salt production in the world. Antiquity.\n"
                    "- Kuijt & Finlayson (2009). Granaries 11,000 years ago in the Jordan Valley. PNAS.\n"
                    "- Salque et al. (2013). Earliest evidence for cheese making in northern Europe. Nature.\n"
                    "- Pryor et al. (2020). A mammoth bone structure at Kostenki 11. Antiquity.\n"
                    "- CDC, MMWR (2003). Botulism outbreak associated with fermented food, Alaska."),
    "tags": ["food preservation", "ancient humans", "how did ancient people keep food fresh", "ancient history", "archaeology", "chuño",
             "yakhchal", "ancient cheese", "salt history", "fermentation history", "stone age", "animated explainer", "stickman"],
    "mood": "playful",
    "sources": [
        "Jay, J. M., Loessner, M. J. & Golden, D. A. (2005). Modern Food Microbiology (7th ed.). Springer.",
        "Maixner, F. et al. (2018). The Iceman's last meal consisted of fat, wild meat, and cereals. Current Biology 28, 2348-2355.",
        "Star, B. et al. (2017). Ancient DNA reveals the Arctic origin of Viking Age cod from Haithabu, Germany. PNAS 114, 9152-9157.",
        "Weller, O. & Dumitroaia, G. (2005). The earliest salt production in the world: an early Neolithic exploitation in Poiana Slatinei-Lunca, Romania. Antiquity 79.",
        "Kuijt, I. & Finlayson, B. (2009). Evidence for food storage and predomestication granaries 11,000 years ago in the Jordan Valley. PNAS 106, 10966-10970.",
        "Pryor, A. J. E. et al. (2020). The chronology and function of a new circular mammoth bone structure at Kostenki 11. Antiquity 94.",
        "Salque, M. et al. (2013). Earliest evidence for cheese making in the sixth millennium BC in northern Europe. Nature 493, 522-525.",
        "Centers for Disease Control and Prevention (2003). Botulism outbreak associated with eating fermented food, Alaska. MMWR.",
        "Live Science report on the 500-year-old chuño from an Inca storeroom (Journal of Field Archaeology).",
        "Smithsonian Magazine, 'Recovering the formula for garum'; Zephyrus (2018) study of the Pompeii Garum Shop jars.",
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
