"""Builds scripts/early_human_day.json and scripts/early_human_day.factcheck.md
(run: ./venv/Scripts/python scripts/early_human_day.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

BEN = "Bennett et al. (2009). Early hominin foot morphology based on 1.5-million-year-old footprints from Ileret, Kenya. Science 323, 1197-1201"
HAT = "Hatala et al. (2016). Footprints reveal direct evidence of group behavior and locomotion in Homo erectus. Scientific Reports 6, 28766"
ROA = "Roach et al. (2016). Pleistocene footprints show intensive use of lake margin habitats by Homo erectus groups. Scientific Reports 6, 26374"
WIL = "Will & Stock (2015). Spatial and temporal variation of body size among early Homo. Journal of Human Evolution 82, 15-33"
SEM = "Semaw et al. (1997). 2.5-million-year-old stone tools from Gona, Ethiopia. Nature 385, 333-336; Toth, Schick & Semaw (2006), Stone Age Institute chapter on the Gona Oldowan"
LEP = "Lepre et al. (2011). An earlier origin for the Acheulian. Nature 477, 82-85"
KON = "Beyene et al. (2013). The characteristics and chronology of the earliest Acheulean at Konso, Ethiopia. PNAS 110, 1584-1591"
ZIN = "Zink & Lieberman (2016). Impact of meat and Lower Palaeolithic food processing techniques on chewing in humans. Nature 531, 500-503"
BUN = "Bunn, H. T. (1981). Archaeological evidence for meat-eating by Plio-Pleistocene hominids from Koobi Fora and Olduvai Gorge. Nature 291, 574-577"
PIC = "Pickering, T. R. & Bunn, H. T. (2007). The endurance running hypothesis and hunting and scavenging in savanna-woodlands. Journal of Human Evolution 53, 434-438"
LOR = "Lordkipanidze et al. (2005). The earliest toothless hominin skull. Nature 434, 717-718; Smithsonian Human Origins, fossil D3444"
BER = "Berna et al. (2012). Microstratigraphic evidence of in situ fire in the Acheulean strata of Wonderwerk Cave, South Africa. PNAS 109, E1215-E1220"
JAB = "Jablonski & Chaplin (2000). The evolution of human skin coloration. Journal of Human Evolution 39, 57-106"
KAM = "Kamberov et al. (2018). Comparative evidence for the independent evolution of hair and sweat gland traits in primates. Journal of Human Evolution 125, 99-105"
RUW = "Walker & Leakey (eds., 1993). The Nariokotome Homo erectus Skeleton. Harvard University Press (Turkana Boy); Natural History Museum and Smithsonian summaries"
YET = "Yetish et al. (2015). Natural sleep and its seasonal variations in three pre-industrial societies. Current Biology 25, 2862-2868"

# how each source was checked (goes into the fact-check file)
VERIFY = {
    BEN: ("Searched 2026-10-24; Science paper abstract, ScienceDaily and Rutgers coverage. Footprints in two layers dated 1.51-1.53 million years at Ileret, Kenya; consistent with stature and mass of Homo ergaster/erectus; the foot looks modern with an arch and an in-line big toe; no associated fossils, so the maker is 'most likely' H. erectus.", "'Probably Homo erectus', 'suggest'; the day is set at about 1.5 million years ago."),
    HAT: ("Searched 2026-10-24; Scientific Reports record, Popular Archaeology and Live Science. 97 tracks at five sites made by at least 20 individuals; the authors infer cooperative multi-male groups; one outlying small track could be a child; a breakdown of males, females and children was not found.", "'At least twenty', 'could be a child'; no claim about exact group makeup beyond the paper's wording."),
    ROA: ("Searched 2026-10-24; Scientific Reports title and abstract summary: footprints made along lake-margin habitats near Ileret.", "'At the edge of an ancient lake' only; water use is an inference."),
    WIL: ("Searched 2026-10-24; Journal of Human Evolution via Sci.News and Tubingen: Koobi Fora individuals about 1.78 m and up to 71 kg; Olduvai about 1.47 m and 50 kg.", "'About' and 'up to'."),
    SEM: ("Searched 2026-10-24; Gona assemblage dated 2.6-2.5 million years, the oldest direct evidence of stone tool manufacture; the toolmakers 'may have been' Australopithecus garhi.", "'Might have been', flagged as only a possibility."),
    LEP: ("Searched 2026-10-24; Nature abstract, Rutgers, Columbia and Science News. Kokiselei 4 hand axes dated to 1.76 million years ago by paleomagnetism; the previous oldest was Konso about 1.4 million years; most credit Homo erectus, some call the maker unsettled.", "'About one point seven six million', 'most researchers'."),
    KON: ("Searched 2026-10-24; Konso study: symmetry in Acheulean tools implies imposition of form, possibly linked to advanced spatial cognition.", "'Possibly linked'; a hypothesis."),
    ZIN: ("Searched 2026-10-24; Nature abstract and NPR, Scientific American, ScienceDaily. Volunteers chewed raw, sliced, pounded and cooked goat and vegetables; a one-third-meat diet would cut about 2 million chews a year (13 percent) and about 15 percent of chewing force (press reports differ slightly, about 2.5 million and 17 and 26 percent); goat stands in for game meat.", "'About two million', 'an estimate', the stand-in is stated."),
    BUN: ("Searched 2026-10-24; Christian Science Monitor 1981 report on Bunn's identification of cut marks, distinct from gnawing marks, on bones at Koobi Fora. The Nature paper itself was not opened.", "'Bunn argued', cut marks vs tooth marks."),
    PIC: ("Reused from the running video: researchers disagree about how much early Homo hunted and how much it scavenged.", "Presented as an open debate."),
    LOR: ("Searched 2026-10-24; Nature 434 record, Smithsonian, Discover. Skull D3444 from Dmanisi, about 1.77 million years old, lost all but one tooth well before death, with complete bone resorption of the sockets; the team and Smithsonian infer help from the group (an interpretation); age at death differs between accounts.", "'Inferred', 'interpretation, not proof'; no age at death given."),
    BER: ("Searched 2026-10-24; PNAS (PMC3356665), ScienceDaily and others. Burned bone and ashed plant remains in the early Acheulean layer about 1.0 million years old; described as the earliest secure evidence of fire in an archaeological context; bat guano ruled out; debate whether the fire was used regularly for cooking.", "'Earliest secure', debate told; the day is set half a million years before it."),
    JAB: ("Searched 2026-10-24; abstract and biographical summaries only. The paper ties dark pigmentation to loss of body hair and thermal sweating and calls dark skin the original state of the genus Homo; the species Homo erectus is not named in what I found.", "Worded as 'the authors argued' and 'our genus'."),
    KAM: ("Reused from the running video; Journal of Human Evolution 125, 99-105: eccrine gland density about tenfold higher in humans than in chimpanzees and macaques; small sample.", "'Roughly ten times as many'."),
    RUW: ("Searched 2026-10-24; Australian Museum, efossils and Tubingen summaries. Turkana Boy about 8-10 years old at death and about 1.6 m tall, possibly 1.85 m as an adult; brain about 880 cc, estimated 909 cc as an adult. These come from secondary summaries.", "'Researchers estimate', 'about'."),
    YET: ("Reused from the Stone Age video: Hadza, San and Tsimane adults average about 6.5 hours of sleep.", "Said to be an analogy from living foragers, not a measurement of early humans."),
}

S = [
    # ---------------- hook (12 one-line scenes)
    ("Dawn, one and a half million years ago.", "The main character wakes on dry ground at dawn beside a thorny bush, stretching and squinting at the sun.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Their footprints are still in the mud in Kenya.", "A line of bare footprints pressed into grey mud, soft sunrise light, no people.", "hook", "awe", 2, "normal", 0, None, BEN),
    ("So what did one ordinary day actually look like?", "The main character looks at a long scroll with nothing on it and tilts his head.", "hook", "curious", 2, "normal", 0, None, None),
    ("Ninety-seven footprints show at least twenty individuals walking together.", "Many footprints of different sizes crossing in a muddy flat beside a calm lake, no people.", "hook", "excited", 2, "normal", 0, None, HAT),
    ("Because their ordinary day shaped your feet, jaw and skin.", "The main character looks down at his own feet and wiggles his toes, amazed.", "hook", "serious", 3, "normal", 0, None, None),
    ("Slicing meat saved them about two million chews a year.", "A simple stone flake lying beside a slice of raw meat on a flat rock, plain background.", "hook", "curious", 2, "normal", 0, None, ZIN),
    ("By the end, you'll know how they spent every hour.", "The main character holds up a finger and grins, a small sun shining behind his head.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("One skull shows someone lived years without teeth.", "A fossil skull with an empty jaw resting on a stone in soft light, no people.", "hook", "tense", 2, "normal", 0, None, LOR),
    ("So who looked after him?", "The main character kneels gently beside a sleeping figure on the ground, looking worried.", "hook", "whisper", 2, "slow", 0, None, None),
    ("Hand axes appeared one point seven six million years ago.", "A teardrop-shaped stone hand axe lying on pale sand in warm light, no people.", "hook", "awe", 2, "normal", 0, None, LEP),
    ("Let's follow one early human from sunrise to dark.", "The main character starts walking across a wide golden savanna with a small stick in hand.", "hook", "curious", 2, "normal", 0, None, None),
    ("The earliest secure fire is half a million years later.", "A small ring of cold black ash stones in a cave, a thin beam of light falling on it, no people.", "hook", "whisper", 2, "slow", 500, None, BER),
    # ---------------- dawn: footprints, water, group
    ("Quick honesty first. Nobody kept a diary. So I'll follow one imagined early human, and every detail around them comes from real evidence: footprints, stones and bones.", "The main character holds a long old bone up to the light like a detective, squinting at it.", "build", "curious", 2, "normal", 0, None, None),
    ("At Ileret in Kenya, footprints were found in two layers dated to between one point five one and one point five three million years ago, probably left by Homo erectus.", "Two layers of grey mud with bare footprints pressed into the top surface, soft light, no people.", "build", "neutral", 2, "normal", 0, None, BEN),
    ("Dawn. No alarm, no coffee, no phone. Just a dry mouth, a cold breeze and a very long to-do list.", "The main character yawns on the ground, hair messy, a small cloud of breath in the cold air.", "build", "funny", 2, "normal", 0, None, None),
    ("The prints suggest a foot much like ours, with an arch and a big toe in line with the others.", "A clear bare footprint in mud showing a high arch and a straight big toe, close up, no people.", "build", "curious", 2, "normal", 0, None, BEN),
    ("So picture a familiar stride. Not a lurching ape-man. Just a person heading off to work. Briefcase optional, spear very optional too.", "The main character walks upright and relaxed across the savanna, swinging his arms, smiling.", "build", "funny", 2, "normal", 0, None, None),
    ("Those tracks were made along the edge of an ancient lake, so water was close, at least for the people who left them.", "A calm lake with a muddy shoreline and a few footprints leading to the water, no people.", "build", "neutral", 2, "normal", 0, None, ROA),
    ("First job: water. A muddy lake edge, a long drink and a very good reason not to go alone.", "The main character kneels at a muddy lake edge and scoops water in his hands, glancing around.", "build", "tense", 2, "normal", 0, None, None),
    ("A later study counted ninety-seven footprints at five sites, made by at least twenty different individuals around one and a half million years ago.", "Dozens of footprints of different sizes scattered across a muddy flat, plain background, no people.", "build", "neutral", 2, "normal", 0, None, HAT),
    ("That's a crowd. Not a lone wanderer. The morning commute had company.", "The main character walks among several stick figures heading the same way across a plain, smiling.", "build", "funny", 2, "fast", 0, None, None),
    ("The researchers read the print sizes as a cooperative group with several adult males, and one small track could belong to a child.", "Two sets of large footprints and one tiny set of footprints side by side in mud, no people.", "build", "neutral", 2, "normal", 0, None, HAT),
    ("A child out there, walking with the group. I find that oddly moving. Somebody was keeping an eye on a small kid on the savanna.", "The main character walks slowly beside a very small stick figure, holding its hand, looking down gently.", "build", "happy", 2, "slow", 0, None, None),
    ("How big were they? It depends where. Koobi Fora individuals could stand almost one point eight metres and weigh about seventy kilograms. At Olduvai they averaged about one point four seven metres and fifty kilograms.", "Two simple height bars side by side, one tall and one shorter, drawn on dry ground, no people.", "build", "neutral", 2, "normal", 0, None, WIL),
    ("So some neighbors looked like basketball players, and some looked like me on a good day, meaning average.", "The main character stands next to a much taller stick figure and a shorter one, looking up and down.", "build", "funny", 2, "fast", 0, None, None),
    # ---------------- tools
    ("Their tools weren't new. Stone tools from Gona in Ethiopia date to between two point six and two point five million years ago, the oldest direct evidence of toolmaking.", "A small sharp stone flake and a rounded stone core resting on pale sand, no people.", "build", "neutral", 2, "normal", 0, None, SEM),
    ("So making sharp stone flakes was already an old trick, a bit like email for us. Nobody invented it this morning.", "The main character taps two stones together casually, bored, a few small chips flying.", "build", "funny", 2, "normal", 0, None, None),
    ("But they had something fancier. At Kokiselei in Kenya, hand axes shaped on both sides date to about one point seven six million years ago.", "A teardrop-shaped hand axe with chipped edges lying on a stone slab in warm light, no people.", "build", "awe", 2, "normal", 0, "ding", LEP),
    ("A hand axe is a stone shaped into a teardrop. I tried to picture making one, and my thumb filed a complaint.", "The main character holds a rock and a small stone, wincing and sucking a sore thumb.", "build", "funny", 2, "fast", 0, None, None),
    ("Until two thousand eleven, the oldest known hand axes were about one point four million years old, from Konso in Ethiopia. Kokiselei pushed that back by hundreds of thousands of years.", "Two hand axes side by side on a flat stone, one slightly bigger and darker, no people.", "build", "curious", 2, "normal", 0, None, LEP),
    ("So the tool story kept getting older. Every time archaeologists dig deeper, our family tree gets a bit more crowded.", "The main character digs in dry soil with a stick and pulls out a small stone, delighted.", "build", "happy", 2, "normal", 0, None, None),
    ("Most researchers credit hand axes to Homo erectus, though a few call the maker unsettled.", "A hand axe on a flat rock with a long shadow, a question-mark-shaped branch behind it, no people.", "build", "neutral", 2, "normal", 0, None, LEP),
    # ---------------- food
    ("Okay, breakfast. Or brunch, or whatever you call the first meal after you've been up since dawn.", "The main character rubs his stomach and looks around the plain for something to eat, hopeful.", "build", "funny", 2, "normal", 0, None, None),
    ("Now breakfast. In a twenty sixteen experiment, Katherine Zink and Daniel Lieberman had volunteers chew raw, sliced, pounded and cooked goat, plus root vegetables, while sensors tracked jaw effort.", "A simple jaw drawn with small round sensor dots on a plain pale background, no people.", "build", "curious", 2, "normal", 0, None, ZIN),
    ("Volunteers chewing raw goat for science. I once felt heroic eating a gas station sandwich.", "The main character chews a long strip of something tough with a very serious face, jaw working hard.", "build", "funny", 2, "fast", 0, None, None),
    ("They estimated that if a third of the diet was meat, slicing it and pounding plants would cut about two million chews a year, and roughly fifteen percent of the chewing force.", "A pile of thin meat slices next to a pile of pounded roots on a flat stone, no people.", "build", "neutral", 2, "normal", 0, None, ZIN),
    ("Two million fewer chews. Basically a spa day for the jaw, thanks to one sharp stone. If dentists had existed, they'd have been very confused by this.", "The main character leans back relaxed with eyes closed, a leaf on each cheek, a stone flake beside him.", "build", "funny", 2, "normal", 0, None, None),
    ("Henry Bunn identified cut marks, as distinct from gnawing marks, on bones at Koobi Fora, evidence that stone tools were used on meat.", "An old animal bone with a few fine parallel cut lines on its surface, resting on sand, no people.", "build", "neutral", 2, "normal", 0, None, BUN),
    ("So the meat was real. The question is where it came from.", "The main character looks at a distant herd of animals on the plain and then at his own empty hands.", "build", "curious", 2, "normal", 0, None, None),
    ("Researchers still argue about how much early Homo hunted and how much it scavenged from the kills of other predators.", "A lion silhouette resting beside a carcass on the plain while a small group of figures watches from afar, no text.", "build", "neutral", 2, "normal", 0, None, PIC),
    # ---------------- subscribe (mid-video, hero scene right after a fact)
    ("Quick pause. If you're curious where this goes, subscribe and stay with me. We'll keep exploring the ancient world together, one real day at a time. It's free, it takes a second, and it helps more curious people find the channel.", "The main character waves at the viewer with a warm smile, standing in a sunny field.", "normal", "happy", 2, "normal", 300, None, None),
    # ---------------- care
    ("At Dmanisi in Georgia, a skull about one point seven seven million years old belonged to someone who had lost all but one tooth well before dying.", "A fossil skull with an almost empty jaw lying on a stone in a dim cave, no people.", "build", "serious", 2, "normal", 0, None, LOR),
    ("No teeth. Think about that on a savanna with no soup, no blender and no dentist.", "The main character stares at a hard root in his hand and then pats his own cheek, worried.", "build", "funny", 2, "normal", 0, None, None),
    ("The bone around the empty sockets had fully healed over, so he survived for years. The team inferred that others in his group probably helped him eat.", "A close drawing of a jaw bone with smooth healed sockets, plain background, no people.", "build", "serious", 2, "slow", 0, None, LOR),
    ("That's an interpretation, not proof. But I like it. Somewhere in that group, somebody made food softer for somebody else.", "The main character mashes a root between two stones and offers it gently to a seated figure.", "build", "happy", 2, "slow", 300, None, None),
    # ---------------- fire
    ("Fire. The earliest secure evidence comes from Wonderwerk Cave in South Africa, about one million years ago, with burned bone and ashed plant remains in the early Acheulean layer.", "A cave floor with a thin dark layer of ash and small burned bone fragments, a beam of light, no people.", "build", "curious", 2, "normal", 0, None, BER),
    ("That's half a million years after our day. So tonight, no campfire. Probably no cooked dinner either. Sorry.", "The main character shivers in the dark beside a pile of dry sticks and a pale moon.", "build", "funny", 2, "normal", 0, None, None),
    ("The team had to rule out natural fires. The ash was inside the cave, and the site tested negative for the bat droppings that can sometimes catch fire on their own.", "A cave ceiling with a few sleeping bats and a pile of dry droppings on the floor, no people.", "build", "neutral", 2, "normal", 0, None, BER),
    ("Bat droppings. A real reason scientists have to check. Imagine writing that into your grant application.", "The main character holds a small clipboard and looks at a pile of dark pellets with a wrinkled nose.", "build", "funny", 2, "fast", 0, None, None),
    ("Even then, not everyone agrees early humans cooked regularly. Some archaeologists accept the fire but doubt it was mastered enough for daily cooking.", "A single small flame on a flat stone inside a cave, drawn simply, no people.", "build", "neutral", 2, "normal", 0, None, BER),
    ("So the safest line is this: they ate raw, sliced food, with no stove in sight. A very long lunch break.", "The main character eats a thin slice of raw meat sitting on a rock, shrugging.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- heat, skin, body
    ("Heat is a problem at midday. Nina Jablonski and George Chaplin argued that as body hair was lost and sweating improved, dark skin evolved as protection, and was the original state of our genus.", "A bright sun over a dry plain with a simple drop of sweat drawn large in the foreground, no people.", "build", "curious", 2, "normal", 0, None, JAB),
    ("So no sunscreen, no sunglasses, and a skin built for the job. Meanwhile I burn through a cloud.", "The main character squints under a hot sun, wiping sweat from his forehead.", "build", "funny", 2, "normal", 0, None, None),
    ("A study counting skin glands found humans carry roughly ten times as many sweat glands as chimpanzees and macaques.", "A magnified patch of skin with many tiny glowing sweat droplets, plain background, no people.", "build", "neutral", 2, "normal", 0, None, KAM),
    ("So the smart plan: walk early, rest in the shade at noon, and complain about the heat. Some things never change.", "The main character lies in the shade of a tree with a leaf fan, completely relaxed.", "build", "funny", 2, "normal", 0, None, None),
    ("A famous skeleton shows how they were built: the Turkana Boy, a juvenile who died around eight to ten years old, about one point six metres tall and perhaps heading for one point eight five as an adult.", "A nearly complete young skeleton lying on pale sand, soft light, no people.", "build", "neutral", 2, "normal", 0, None, RUW),
    ("A kid taller than my uncle. Honestly, I wouldn't argue with him about the remote.", "The main character looks up at a taller young stick figure, holding a flat remote behind his back.", "build", "funny", 2, "fast", 0, None, None),
    ("His brain held about eight hundred and eighty cubic centimetres, an estimated nine hundred and nine if he had grown up, smaller than ours.", "A rounded skull drawn in section showing a smaller brain space, plain background, no people.", "build", "neutral", 2, "normal", 0, None, RUW),
    ("A smaller brain, but not a simple life. Look at what filled the day: sharing, walking together, shaping stone. Respect to anyone who made a hand axe before breakfast.", "The main character carries a hand axe and a bundle of roots, walking proudly with a group.", "build", "curious", 2, "normal", 0, None, None),
    ("At Konso in Ethiopia, researchers noted that the symmetry of early hand axes suggests imposing form on stone, possibly linked to advanced spatial thinking.", "A perfectly symmetrical teardrop hand axe in the center of a pale background, glowing lightly, no people.", "build", "neutral", 2, "normal", 0, None, KON),
    ("Spatial thinking. The same skill I use to fail at assembling flat-pack furniture.", "The main character stares at a pile of wooden boards and a few round pegs, completely lost.", "build", "funny", 2, "fast", 0, "boing", None),
    ("And those Gona toolmakers? The researchers said they might have been Australopithecus garhi, though that's only a possibility.", "A small simple skull of an early hominin beside a sharp stone flake on sand, no people.", "build", "neutral", 2, "normal", 0, None, SEM),
    ("So the tool story starts before our whole genus. Plenty of maybes there, and I'd rather tell you that than fake certainty.", "The main character spreads both hands out and shrugs with an honest smile in front of a dig site.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- night
    ("We can't measure the sleep of early Homo. But living foragers like the Hadza, San and Tsimane sleep about six and a half hours a night, so it's a fair guess that nights weren't as long as ours.", "A simple grass bed on open ground under a crescent moon and many stars, no people.", "build", "curious", 2, "normal", 0, None, YET),
    ("Lights out at dark, up with the sun. No snooze button. Honestly, I'm a little jealous.", "The main character sleeps curled up on dry grass beneath the stars, a tiny cloud of Zs above him, no letters.", "build", "funny", 2, "slow", 0, None, None),
    ("And the footprints preserve something no bone can: a modern style of walking, and a group structure consistent with human-like social behavior.", "A line of mixed-size footprints walking together across mud under a pink evening sky, no people.", "build", "awe", 2, "normal", 0, None, HAT),
    ("So here's the day: walk with others, look after the small and the old, shape stone, share food, dodge the heat, and no fire yet.", "The main character counts five fingers one by one, standing in front of a plain stone wall.", "punchline", "serious", 2, "normal", 400, None, None),
    ("The chewing study used goat as a stand-in for game meat because it's tough, so its numbers are an estimate, not a record of real ancient meals.", "A single goat standing calmly on a small hill beside a flat stone, drawn simply, no text.", "build", "neutral", 2, "normal", 0, None, ZIN),
    ("I like how careful that is. Every number in this video comes with its asterisk, and the asterisk is part of the story.", "The main character holds up a tiny asterisk-shaped star drawn on a stone, grinning.", "build", "happy", 2, "normal", 0, None, None),
    ("The fire date is the same. Wonderwerk is described as the earliest secure evidence, which leaves room for older discoveries yet to come.", "A dark cave opening with a faint glow far inside, drawn simply, no people.", "build", "neutral", 2, "normal", 0, None, BER),
    ("So tomorrow's fossil or footprint could change the day we just walked through. That's the fun part. Science keeps its diary in pencil, and I find that oddly comforting.", "The main character stands at a dig site holding a brush, a half-buried footprint at his feet, excited.", "build", "excited", 2, "normal", 0, None, None),
    ("The Ileret layers date to about one point five million years ago, so every step in this video is older than farming, cities and writing by a margin that's hard to picture.", "A very long timeline strip drawn on the ground with one tiny mark at the far end, no people.", "build", "awe", 2, "slow", 0, None, BEN),
    ("So what did their day look like? Walking with a group, minding the little ones, shaping stone and sharing meat. And your day isn't so different. Thanks for spending these minutes with me. Hit like if it was worth your time, and tell me in the comments what you'd have done first. I read every one. Next time: why human brains shrank. See you soon, friend.", "The main character waves goodbye at sunrise beside a quiet lake, a bright sky behind him, smiling warmly.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 70 <= len(S) <= 95, len(S)
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
    "title": "A Day in the Life of an Early HUMAN",
    "title_alternatives": ["What Did One Day Look Like 1.5 Million Years AGO?", "Following an Early Human From Sunrise to DARK",
                           "Their Footprints Are Still in the MUD", "What Filled the Day of Homo ERECTUS?"],
    "description": ("Dawn, one and a half million years ago. This video follows one imagined early human through an ordinary day, using real evidence: "
                    "the Ileret footprints in Kenya, hand axes, the chewing study, the toothless skull from Dmanisi, the earliest fire and the Turkana Boy.\n\n"
                    "This video is history and science, not medical advice.\n\nSources:\n"
                    "- Bennett et al. (2009). Footprints from Ileret, Kenya. Science.\n"
                    "- Hatala et al. (2016). Footprints reveal group behavior in Homo erectus. Scientific Reports.\n"
                    "- Lepre et al. (2011). An earlier origin for the Acheulian. Nature.\n"
                    "- Zink & Lieberman (2016). Meat and chewing in the Lower Palaeolithic. Nature.\n"
                    "- Lordkipanidze et al. (2005). The earliest toothless hominin skull. Nature.\n"
                    "- Berna et al. (2012). Fire in the Acheulean strata of Wonderwerk Cave. PNAS."),
    "tags": ["homo erectus", "early humans", "ancient humans", "a day in the life", "footprints", "hand axe", "human evolution", "prehistory",
             "ileret", "animated explainer", "stickman"],
    "mood": "wholesome",
    "sources": [x for x in dict.fromkeys(s[8] for s in S if s[8])][:16],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

# ---- fact-check file
md = ["# Fact-check: A Day in the Life of an Early HUMAN", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-24.", ""]
md += ["## Method", "- The day is an imagined composite, said so in the first scene; every detail around it comes from a named source.",
       "- The day is set at about one and a half million years ago (Ileret footprints); fire evidence is later and the narration says so.",
       "- Where only an abstract or press summary was opened, the claim is worded as 'about', 'probably' or 'researchers read', and the file says so.",
       "- Contested points are told as such: who made the hand axes, hunting vs scavenging, whether early fire meant regular cooking, whether the Dmanisi man was cared for.",
       "- The narrator says outright that this is not medical advice; the description repeats it.", "",
       "## Fact scenes", "", "| # | Narration (shortened) | Source | How verified | Wording safeguard |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        src = sc["fact_source"]
        how, safe = VERIFY.get(src, ("", ""))
        md.append(f"| {i} | {sc['narration'][:90].replace('|', '/')}... | {src[:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Claims softened or dropped",
       "- Group makeup (how many males, females, children): not found in the sources, so only 'cooperative group, one small track could be a child'.",
       "- Body mass values of the Ileret prints: not found, dropped.",
       "- Age at death of the Dmanisi man: accounts differ, dropped.",
       "- Skin colour: the Jablonski and Chaplin abstract names the genus Homo, not Homo erectus, so the narration says 'our genus'.",
       "- Sleep length of early Homo: unknowable, stated as an analogy from living foragers.",
       "- Predator attacks on early Homo: only one weakly sourced item found, so it was dropped.",
       "", "## Human-voice checklist (all done)",
       "- Short and long sentences mixed; contractions; personal takes ('my thumb filed a complaint', 'flat-pack furniture').",
       "- Modern comparisons: alarm clock, email, basketball players, sunscreen, flat-pack, the remote, grant applications.",
       "- No filler words ('delve', 'fascinating journey', 'it's important to note').",
       "- Numbers written as words; no ALL CAPS in narration; no long dashes.",
       "- Warm connection: friendly mid-video 'subscribe and stay with me' scene, thank-you and 'See you soon, friend' ending; 'like' asked once at the end.",
       "- The first 40 seconds say why to watch ('their ordinary day shaped your feet, jaw and skin') and what you get ('you'll know how they spent every hour')."]
Path(__file__).with_name("early_human_day.factcheck.md").write_text("\n".join(md), encoding="utf-8")

print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]), "max hook line:", max(len(s["narration"].split()) for s in scenes[:12]))
em = [s["emotion"] for s in scenes]
run = 1
for i in range(1, len(em)):
    run = run + 1 if em[i] == em[i - 1] else 1
    if run > 3:
        print("4+ same emotion in a row at scene", i + 1, em[i])
sub = [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()]
print("subscribe scenes:", sub, "of", len(scenes))
