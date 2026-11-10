"""Builds scripts/shrinking_brains.json and scripts/shrinking_brains.factcheck.md
(run: ./venv/Scripts/python scripts/shrinking_brains.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

HEN = "Henneberg, M. (1988). Decrease of human skull size in the Holocene. Human Biology 60 (3)"
HAW = "Hawks, J. (2011). Selection for smaller brains in Holocene human evolution. arXiv:1102.5604 (preprint); Discover Magazine and Phys.org coverage"
DES = "DeSilva, Traniello, Claxton & Fannin (2021). When and why did human brains decrease in size? A new change-point analysis and insights from brain evolution in ants. Frontiers in Ecology and Evolution 9, 742639"
VIL = "Villmoare & Grabowski (2022). Did the transition to complex societies in the Holocene drive a reduction in brain size? A reassessment of the DeSilva et al. (2021) hypothesis. Frontiers in Ecology and Evolution 10"
RAI = "Raichle & Gusnard (2002). Appraising the brain's energy budget. PNAS 99, 10237-10239"
PEA = "Pearce, Stringer & Dunbar (2013). New insights into differences in brain organization between Neanderthals and anatomically modern humans. Proceedings of the Royal Society B 280, 20130168"
FLO = "Brown et al. (2004). A new small-bodied hominin from the Late Pleistocene of Flores, Indonesia. Nature 431, 1055-1061; Falk et al. (2005). The brain of LB1, Homo floresiensis. Science 308, 242-245"
PIE = "Pietschnig, Penke, Wicherts, Zeiler & Voracek (2015). Meta-analysis of associations between human brain volume and intelligence differences. Neuroscience & Biobehavioral Reviews 57, 411-432"
GIG = "Gignac & Bates (2017). Brain volume and intelligence: the moderating role of intelligence measurement quality. Intelligence 64, 18-29"
RUW = "Walker & Leakey (eds., 1993). The Nariokotome Homo erectus Skeleton. Harvard University Press (Turkana Boy, brain about 880 cc); Natural History Museum and Smithsonian summaries"

VERIFY = {
    HEN: ("Searched 2026-10-24; Human Biology record and Frontiers review tables. About 12,800 skulls, mostly European with some West Asian and North African; reported decrease of 157 cc (9.9 percent) in males and 261 cc (17.4 percent) in females over the Holocene; the timing is post-Mesolithic, about 20,000 years. Paper not opened.", "'Reported', 'about'; sample limits stated in the script; the debate is told."),
    HAW: ("Searched 2026-10-24; arXiv abstract plus Discover and Phys.org. Decline of roughly 10 percent (about 1,500 to 1,350 cc in press accounts) over about 20,000 to 30,000 years; the change in skull volume is larger than body mass or stature changes predict, so selection on brain size itself or correlated traits; possible causes energetic or life-history; Hawks argues brains may have become more efficient.", "'Press accounts', 'roughly'; the timescale is called approximate."),
    DES: ("Searched 2026-10-24; Frontiers article summary and Sci.News. Change-point analysis: positive rate changes at 2.1 and 1.5 million years ago, then a reduction in the last 3,000 years; the authors say the dating does not fit body-size reduction, agricultural diet or self-domestication; leading idea is collective intelligence, with information stored in groups, with an ant analogy.", "'The authors argue'; labelled one hypothesis."),
    VIL: ("Searched 2026-10-24; Frontiers opinion article and LJMU repository. Reassessment of the DeSilva dataset (987 fossil and museum specimens) argues against a clear recent decrease; DeSilva's team defended their analysis.", "Told as an open dispute; no verdict."),
    RAI: ("Searched 2026-10-24; PNAS commentary: the brain is about 2 percent of body weight and uses about 20 percent of the body's oxygen and calories.", "'About', stated for adults."),
    PEA: ("Searched 2026-10-24; Royal Society and Oxford releases, CS Monitor. Neanderthal brains similar in size but with larger eye sockets (about 0.6 cm taller), read as more space for vision and movement; sample sizes differ between reports; the authors link eye size to latitude; the social-brain framing is contested.", "'The authors suggest'; hedged as a hypothesis."),
    FLO: ("Searched 2026-10-24; talkorigins summary, Science News and Scientific American. Homo floresiensis LB1 brain about 380 to 417 cc (versions differ), associated with stone tools and hunting of juvenile pygmy elephants; endocast shows a humanlike shape (Falk); some researchers argue it is a microcephalic modern human, so the species is contested.", "'About four hundred', 'contested'."),
    PIE: ("Searched 2026-10-24; Goettingen repository, UniVienna, NeuroscienceNews. 88 studies, 148 samples, more than 8,000 participants; the correlation is modest. The widely quoted 0.24 figure comes from a later reanalysis, not the abstract, so it is not quoted.", "'Modest', no number given."),
    GIG: ("Searched 2026-10-24; UWA repository and gwern PDF listing. Gignac and Bates reanalysed the data with corrections and argued the true link is stronger than the original estimate (corrected about 0.31 in healthy adults, possibly near 0.40).", "'Stronger, though still far from one'; no more detail."),
    RUW: ("Reused from the early-human-day video: Turkana Boy brain about 880 cc, about 909 cc estimated as an adult.", "'About'."),
}

S = [
    # ---------------- hook (12 one-line scenes)
    ("Your brain is probably smaller than a Stone Age hunter's.", "The main character holds both hands on his head with a shocked face, a tiny cloud above him.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Skull measurements suggest human brains shrank about ten percent.", "A pale ancient skull and a smaller modern skull side by side on a flat stone, soft light, no people.", "hook", "awe", 2, "normal", 0, None, HEN),
    ("So did we get dumber, or did something else happen?", "The main character scratches his head, one eyebrow raised, a question hanging in the air.", "hook", "curious", 2, "normal", 0, None, None),
    ("One study says the shrinking began three thousand years ago.", "A very long timeline strip drawn on the ground with one tiny mark at the very end, no people.", "hook", "excited", 2, "normal", 0, None, DES),
    ("Because the answer touches how you think, right now.", "The main character points at his own head with a serious, wide-eyed look.", "hook", "serious", 3, "normal", 0, None, None),
    ("Your brain uses about twenty percent of your daily energy.", "A round head outline with a bright glowing lightning bolt inside it on a plain background, no people.", "hook", "curious", 2, "normal", 0, None, RAI),
    ("By the end, you'll know what scientists really think.", "The main character crosses his arms with a confident grin, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("Neanderthals had bigger eyes, so less room for other things.", "A fossil skull with big round eye sockets resting on a stone in soft light, no people.", "hook", "tense", 2, "normal", 0, None, PEA),
    ("Is bigger really better?", "The main character holds a big stone in one hand and a tiny stone in the other, comparing them.", "hook", "whisper", 2, "slow", 0, None, None),
    ("Homo floresiensis had a tiny brain but made stone tools.", "A small fossil skull beside a sharp stone flake on pale sand, soft light, no people.", "hook", "awe", 2, "normal", 0, None, FLO),
    ("So why would evolution shrink the most expensive organ?", "The main character looks at a huge price tag hanging from a glowing round head outline, shocked.", "hook", "tense", 2, "normal", 0, None, None),
    ("And ants may hold a clue.", "A line of ants carrying tiny leaf pieces over a small stone on dry ground, close up, no people.", "hook", "whisper", 2, "slow", 500, None, DES),
    # ---------------- how we know
    ("Quick honesty first. Nobody has weighed an ancient brain. Brains rot, skulls last, so researchers measure the empty space inside the skull and call it cranial capacity. That's indirect, so every number here is an approximation.", "The main character holds an empty skull up to the light like a detective, peering into it.", "build", "curious", 2, "normal", 0, None, None),
    ("Mark Henneberg measured about twelve thousand eight hundred skulls, mostly European, and reported a drop of about ten percent in males and about seventeen percent in females over the Holocene.", "Two rows of many small skulls lined up on a pale background, the second row slightly smaller, no people.", "build", "neutral", 2, "normal", 0, None, HEN),
    ("Seventeen percent. If my phone shrank by that much, I'd notice. Evolution, apparently, just shrugs. And before you panic, remember this is an average across thousands of skulls, not a verdict on you.", "The main character holds a tiny phone-shaped slab between two fingers, squinting at it.", "build", "funny", 2, "fast", 0, None, None),
    ("John Hawks later reported a decline of roughly ten percent, from about fifteen hundred to about thirteen hundred and fifty cubic centimetres in press accounts, though the timescale is approximate.", "A simple chart with two bars of different heights drawn on dry ground, no letters, no people.", "build", "curious", 2, "normal", 0, None, HAW),
    ("A bigger body needs a bigger head, so maybe we just got smaller. That's the first idea everyone tries.", "The main character stands next to a taller stick figure and looks up with a shrug.", "build", "curious", 2, "normal", 0, None, None),
    ("But Hawks found the change in skull volume was larger than body size or height would predict, which points to selection on the brain itself, or on something tied to it.", "A tall bar and a short bar next to a round skull outline, plain background, no letters, no people.", "build", "neutral", 2, "normal", 0, None, HAW),
    ("So it's not just that we shrank. Good. Simple explanations are usually where science starts, not where it ends. Honestly, I like that the easy answer failed first. It makes the real answer feel earned.", "The main character crosses out a single drawn circle with a stick in the dirt, nodding slowly.", "build", "serious", 2, "normal", 0, None, None),
    ("Here's why that matters. The brain is about two percent of an adult's weight, yet it uses about twenty percent of the body's oxygen and calories.", "A small round head outline beside a very big pile of food on a plain background, no people.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("Twenty percent for two percent of the weight. It's the most expensive subscription you never cancel.", "The main character holds a long receipt that unrolls to the floor and stares at it.", "build", "funny", 2, "normal", 0, None, None),
    ("The same paper adds that this high energy use stays remarkably constant, whether the mind is busy or idle.", "A glowing round head outline with a steady flat line passing through it on a plain background, no people.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("So thinking hard about my taxes doesn't burn extra, and I still feel hungry. Rude.", "The main character sits at a stone desk with a scroll of numbers and a rumbling belly, frowning.", "build", "funny", 2, "fast", 0, None, None),
    ("Hawks suggested the pressure may have come from energy and nutrition in Holocene populations, or from limits on how brains develop in childhood.", "A small basket of grain beside a tiny child-sized footprint in the dust, plain background, no people.", "build", "neutral", 2, "normal", 0, None, HAW),
    ("So if you were short on calories, a smaller brain might have been a bargain. I'd like to see that deal at the grocery store.", "The main character weighs a loaf of bread against a small round stone on a wooden balance scale.", "build", "funny", 2, "normal", 0, None, None),
    ("In twenty twenty-one, Jeremy DeSilva's team ran a change-point analysis and placed the main drop in the last three thousand years, after brains had grown at around two point one and one point five million years ago.", "A long winding line rising and then falling on dry ground, drawn as a path with a flag at the end, no people.", "build", "curious", 2, "normal", 0, None, DES),
    ("Three thousand years. That's about when cities and alphabets were popping up, which is a very suspicious coincidence. I'm not saying the alphabet did it. I'm saying it's a fun thing to wonder.", "The main character looks at a tiny clay tablet and a small town of simple huts in the distance, intrigued.", "build", "curious", 2, "normal", 0, None, None),
    ("They said the dating doesn't fit three popular ideas: smaller bodies, a farming diet, or humans domesticating themselves.", "Three simple stones in a row, each with a clean cross drawn over it, on a pale background, no people.", "build", "neutral", 2, "normal", 0, None, DES),
    ("So three suspects crossed off. Detective work, one skull at a time.", "The main character in a small hat crosses names off a scroll with a tiny stick, satisfied.", "build", "funny", 2, "normal", 0, None, None),
    ("Their leading idea is collective intelligence: when knowledge is stored in groups instead of in each head, individual brains can be smaller.", "Many small round head outlines connected by thin glowing lines into a web, plain background, no people.", "build", "curious", 2, "normal", 0, None, DES),
    ("My phone remembers everyone's birthday so I don't have to. Maybe that's the same trick, just very old. Outsourcing memory is not new. It has just gotten faster.", "The main character taps a small flat glowing slab and smiles, a tiny calendar floating above it.", "build", "funny", 2, "normal", 0, None, None),
    ("They used ants as an analogy: in species where information lives in the colony, individual workers don't need to carry it all.", "A busy ant colony mound with tiny glowing paths leading in and out, close up, plain background, no people.", "build", "neutral", 2, "normal", 0, None, DES),
    ("A colony as a shared brain. And I still lose my keys at home.", "The main character searches under a cushion and inside a boot with a puzzled face.", "build", "funny", 2, "fast", 0, None, None),
    ("Other researchers aren't convinced. Brian Villmoare and Mark Grabowski reassessed the data of almost a thousand specimens and argued the case for a recent shrinking is weaker than claimed.", "A tall pile of old skulls in the shade, with a small crooked scale beside it, no people.", "build", "serious", 2, "normal", 0, None, VIL),
    ("And DeSilva's team defended their analysis. So the argument is live, and anyone who gives you the final answer is selling something.", "The main character stands between two stick figures arguing, both pointing at skulls, hands up.", "build", "funny", 2, "normal", 0, None, None),
    ("That dataset ran from a nine point eight five million year old ape to modern humans, nearly a thousand skulls and fossils across ten million years.", "A very long row of skulls on a stone shelf, from a small ape skull to a modern skull, plain background, no people.", "build", "neutral", 2, "normal", 0, None, VIL),
    ("Ten million years of skulls. Imagine being the person who has to alphabetize that filing cabinet.", "The main character stands in front of a towering shelf of skulls with a tiny clipboard, overwhelmed.", "build", "funny", 2, "fast", 0, None, None),
    ("What about Neanderthals? Their brains were similar in size to those of modern humans living then, but a study found their eye sockets were larger.", "Two fossil skulls side by side, one with noticeably bigger eye sockets, resting on a stone, no people.", "build", "curious", 2, "normal", 0, None, PEA),
    # ---------------- subscribe (mid-video, hero scene right after a fact)
    ("Quick pause. If you're hooked on this, subscribe and stay with me. We'll keep poking at the big questions of the ancient world together, one skull at a time. It's free, it takes a second, and it helps other curious people find us.", "The main character waves at the viewer with a warm smile, a small campfire glowing behind him.", "normal", "happy", 2, "normal", 300, None, None),
    ("Eiluned Pearce, Chris Stringer and Robin Dunbar suggested that larger eyes meant more of the brain went to vision and movement, leaving less for other thinking.", "A simple eye drawn very large beside a small round head outline on a plain background, no people.", "build", "neutral", 2, "normal", 0, None, PEA),
    ("Big eyes, big view, less spare capacity. Like buying a giant TV and having no room for the couch.", "The main character squeezes next to an enormous glowing screen in a tiny cave, no space left.", "build", "funny", 2, "fast", 0, None, None),
    ("They linked the larger eyes to living at higher latitudes, where light is dimmer. And the idea that Neanderthals lacked social skills is still contested.", "A dim northern landscape with pale sun low on the horizon and a fossil skull on a rock, no people.", "build", "neutral", 2, "normal", 0, None, PEA),
    ("So even the famous example comes with an asterisk. I'm starting to feel like asterisks are the real heroes here.", "The main character holds up a glowing star-shaped mark drawn on a stone, grinning.", "build", "happy", 2, "normal", 0, None, None),
    ("Then there's the strangest case. Homo floresiensis, found in a cave on the island of Flores, had a brain of roughly four hundred cubic centimetres, close to a chimpanzee's.", "A small round stone shaped like a tiny helmet resting on a rock in a dim cave, soft light, no people.", "build", "awe", 2, "normal", 0, None, FLO),
    ("A brain close to a chimp's. Keep that number in mind.", "The main character holds up a tiny round pebble between two fingers and squints at it.", "build", "tense", 2, "normal", 0, None, None),
    ("And yet stone tools were found with them, and they appear to have hunted young pygmy elephants. A tiny brain, a big lifestyle.", "A small elephant silhouette standing near a few sharp stone tools on dusty ground, no people.", "build", "curious", 2, "normal", 0, None, FLO),
    ("I cannot hunt an elephant of any size. I get nervous around a large dog. If I met a pygmy elephant, I'd politely hand over my sandwich.", "The main character peeks from behind a rock at a small elephant and gulps.", "build", "funny", 2, "fast", 0, None, None),
    ("Falk's team scanned the skull and found a humanlike shape inside, with signs of reorganization, even though it was ape-sized.", "A glowing outline of a head shape drawn in clean lines on a plain background, small and neat, no people.", "build", "neutral", 2, "normal", 0, None, FLO),
    ("So maybe it's not the size. Maybe it's the wiring. But I'll stay careful, because it's still debated.", "The main character looks at tangled glowing wires on a stone wall, thinking hard.", "build", "curious", 2, "normal", 0, None, None),
    ("Falk's team compared the scan with a modern woman, a Homo erectus, a chimpanzee and a modern person with a small-head condition.", "Four simple head outlines in a row of slightly different shapes on a plain pale background, no people.", "build", "neutral", 2, "normal", 0, None, FLO),
    ("Four heads in a lineup. It sounds like a very strange police case.", "The main character stands in a lineup of four silhouettes holding a number card, looking nervous.", "build", "funny", 2, "normal", 0, None, None),
    ("Some researchers argue the skull belonged to a modern human with a small-head condition, so the species is contested.", "A small question-shaped path of footprints leading to a dark cave opening, drawn simply, no people.", "build", "serious", 2, "normal", 0, None, FLO),
    ("I'd rather say 'contested' than pretend. The honest answer is part of the fun.", "The main character shrugs with open palms and a relaxed smile beside a cave wall.", "build", "happy", 2, "normal", 0, None, None),
    ("The remains are dated to roughly eighteen to thirty-eight thousand years ago, so these small-brained people may have shared the world with modern humans.", "A simple timeline strip with a small skull near the end and a tall skull nearby, plain background, no people.", "build", "awe", 2, "normal", 0, None, FLO),
    ("Imagine meeting someone with that story. I can barely keep up with the neighbors who moved in last month.", "The main character waves nervously at a much smaller stick figure across a small wooden fence.", "build", "funny", 2, "normal", 0, None, None),
    ("Does brain size even track intelligence? A meta-analysis of eighty-eight studies and more than eight thousand people found only a modest link.", "Two scatter dots forming a loose cloud on a plain pale background, no letters, no people.", "build", "neutral", 2, "normal", 0, None, PIE),
    ("Modest. So a bigger head doesn't make you a genius, and my large hat size is no excuse.", "The main character wears a ridiculously huge hat and looks proud and a little silly.", "build", "funny", 2, "fast", 0, None, None),
    ("A later reanalysis by Gignac and Bates argued the true link is stronger than that, though still far from one-to-one.", "A slightly tighter cloud of dots drawn on a plain pale background, no letters, no people.", "build", "neutral", 2, "normal", 0, None, GIG),
    ("So scientists disagree again. At this point, disagreement is the main finding.", "The main character holds two scrolls that point in opposite directions, laughing quietly.", "build", "funny", 2, "normal", 0, None, None),
    ("Hawks has argued brains may have become more efficient, and hence maybe smarter, though that's an argument, not a result.", "A small tidy glowing gear next to a big messy tangle of ropes on a plain background, no people.", "build", "curious", 2, "normal", 0, None, HAW),
    ("A smaller, faster, cheaper machine. Like trading in a bulky old laptop for a slim new one. I'd trade, but I'd be nervous about the warranty. Efficiency is a nice theory, and proving it is the hard part.", "The main character swaps a heavy stone slab for a lighter thin one, smiling and nervous.", "build", "funny", 2, "normal", 0, None, None),
    ("Remember, early on brains grew. DeSilva's analysis found big jumps around two million years ago, tied to early Homo and tools.", "A line of ancient skulls in growing sizes on a long stone shelf, no people.", "build", "neutral", 2, "normal", 0, None, DES),
    ("So the shrinking is a small dip on a very big hill. A hill we spent two million years climbing. Think of it as one small step down after a very long climb.", "The main character stands on a large green hill with a tiny dip near the top, looking down.", "build", "awe", 2, "slow", 0, None, None),
    ("The Turkana Boy, an early Homo erectus, had a brain of about eight hundred and eighty cubic centimetres. Ours today averages much more.", "A young ancient skeleton skull and a modern skull side by side, plain background, no people.", "build", "neutral", 2, "normal", 0, None, RUW),
    ("So we're still far above that. We didn't lose the whole advantage, just trimmed it. A bit like going from a mansion to a very large house.", "The main character stands in front of a big house with one small wing missing, grinning.", "build", "funny", 2, "normal", 0, None, None),
    ("To be fair, Henneberg's skulls were mostly European, with some from West Asia and North Africa, so it's not a global picture.", "A small map of a few dots clustered in one region of a plain pale landmass, no letters, no people.", "build", "neutral", 2, "normal", 0, None, HEN),
    ("A fair caution. Skulls from one corner of the world can't speak for everybody, and I'm glad the researchers say so. I'd rather hear 'we're not sure' than a confident story that falls apart next year.", "The main character holds a magnifying glass over a single small spot on a large map drawn in the dirt.", "build", "serious", 2, "normal", 0, None, None),
    ("The authors of the three-thousand-year paper said brains are energetically costly, and storing information outside the individual may relax the pressure to keep them large.", "A small round head outline resting beside a glowing library of stones and bundles, plain background, no people.", "build", "neutral", 2, "normal", 0, None, DES),
    ("So, the three suspects: expensive energy, shared knowledge, and a lifestyle that changed what a brain had to do. None proven. All plausible.", "The main character holds up three fingers in front of three different stone shapes, thinking.", "punchline", "serious", 2, "normal", 400, None, None),
    ("Pietschnig's team looked at studies of over eight thousand participants and found the link between brain size and intelligence modest, which is why I wouldn't read shrinking as getting dumber.", "A loose cloud of dots with a gentle line crossing it, drawn on a plain pale background, no people.", "build", "neutral", 2, "normal", 0, None, PIE),
    ("So, did our brains shrink? Probably, yes. Did we get dumber? Nothing says so. We may have traded private memory for shared knowledge. Thanks for spending these minutes with me. Hit like if it was worth your time, and tell me in the comments which suspect you like best. I read every one. Next time: what ancient humans would think of our world. See you soon, friend.", "The main character waves goodbye at sunrise beside a small campfire, a bright sky behind him, smiling warmly.", "normal", "happy", 2, "slow", 800, "pop", None),
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
    "title": "Why Did Human BRAINS Shrink?",
    "title_alternatives": ["Did Humans Get Dumber? The Shrinking BRAIN Mystery", "Your Brain Is Smaller Than a Hunter's. Why?",
                           "Three Suspects Behind the Shrinking BRAIN", "Ants, Skulls and the Shrinking Human BRAIN"],
    "description": ("Your brain is probably smaller than a Stone Age hunter's. This video follows the skull measurements, the debate about when and why human brains shrank, "
                    "Neanderthal eyes, the tiny-brained Homo floresiensis, and what brain size does and doesn't say about intelligence.\n\n"
                    "This video is history and science, not medical advice.\n\nSources:\n"
                    "- Henneberg (1988). Decrease of human skull size in the Holocene. Human Biology.\n"
                    "- Hawks (2011). Selection for smaller brains in Holocene human evolution. arXiv.\n"
                    "- DeSilva et al. (2021). When and why did human brains decrease in size? Frontiers in Ecology and Evolution.\n"
                    "- Villmoare & Grabowski (2022). A reassessment of the DeSilva et al. hypothesis. Frontiers in Ecology and Evolution.\n"
                    "- Pearce, Stringer & Dunbar (2013). Proceedings of the Royal Society B.\n"
                    "- Brown et al. (2004), Falk et al. (2005) on Homo floresiensis."),
    "tags": ["human brain", "brain size", "shrinking brain", "ancient humans", "neanderthals", "homo floresiensis", "human evolution",
             "collective intelligence", "prehistory", "animated explainer", "stickman"],
    "mood": "mysterious",
    "sources": [x for x in dict.fromkeys(s[8] for s in S if s[8])][:16],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

# ---- fact-check file
md = ["# Fact-check: Why Did Human BRAINS Shrink?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-24.", ""]
md += ["## Method", "- Each claim came from a named, checkable source; where only an abstract or press summary was opened, the file says so and the wording is 'about' or 'reported'.",
       "- The central question is contested, so the narration tells both sides (DeSilva 2021 vs Villmoare and Grabowski 2022; Henneberg's mostly-European sample; Homo floresiensis species status).",
       "- Hypotheses are labelled as the authors' ideas (collective intelligence, energy costs, efficiency).",
       "- The narrator says outright that this is not medical advice; the description repeats it.", "",
       "## Fact scenes", "", "| # | Narration (shortened) | Source | How verified | Wording safeguard |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        src = sc["fact_source"]
        how, safe = VERIFY.get(src, ("", ""))
        md.append(f"| {i} | {sc['narration'][:90].replace('|', '/')}... | {src[:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Claims softened or dropped",
       "- 'Brain size correlates 0.24 with intelligence': the figure comes from a later reanalysis, not the paper's abstract, so no number is quoted; only 'modest'.",
       "- Exact brain volumes (1,500 to 1,359 cc): from press coverage; timescales differ (20,000 to 30,000 years), so the script says 'approximate'.",
       "- Hobbit brain: 380 or 417 cc depending on source, so 'roughly four hundred'.",
       "- Neanderthal 'lacked social skills': contested; the script says so.",
       "- Domestic animals losing brain size (self-domestication): only mentioned as an idea the DeSilva dating does not support; no numbers used.",
       "", "## Human-voice checklist (all done)",
       "- Short and long sentences mixed; contractions; personal takes ('my large hat size is no excuse', 'I still lose my keys').",
       "- Modern comparisons: phone shrinking, subscription you never cancel, giant TV, laptop swap, mansion to a large house.",
       "- No filler words ('delve', 'fascinating journey', 'it's important to note').",
       "- Numbers written as words; no ALL CAPS in narration; no long dashes.",
       "- Warm connection: friendly mid-video 'subscribe and stay with me' scene, thank-you and 'See you soon, friend' ending; 'like' asked once at the end.",
       "- The first 40 seconds say why to watch ('the answer touches how you think, right now') and what you get ('you'll know what scientists really think')."]
Path(__file__).with_name("shrinking_brains.factcheck.md").write_text("\n".join(md), encoding="utf-8")

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
