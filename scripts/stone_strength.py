"""Builds scripts/stone_strength.json and scripts/stone_strength.factcheck.md
(run: ./venv/Scripts/python scripts/stone_strength.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

MAC = "Macintosh, Pinhasi & Stock (2017). Prehistoric women's manual labor exceeded that of athletes through the first 5500 years of farming in Central Europe. Science Advances 3, eaao3893"
RYA = "Ryan & Shaw (2015). Gracility of the modern Homo sapiens skeleton is the result of decreased biomechanical loading. PNAS 112, 372-377"
RUF = "Ruff et al. (2015). Gradual decline in mobility with the adoption of food production in Europe. PNAS 112, 7147-7152"
CHI = "Chirchir et al. (2015). Recent origin of low trabecular bone density in modern humans. PNAS 112, 366-371"
CHU = "Churchill & Rhodes (2006). How strong were the Neandertals? Leverage and muscularity at the shoulder and elbow in Mousterian foragers. Periodicum Biologorum 108"
BER = "Berger & Trinkaus (1995). Patterns of trauma among the Neandertals. Journal of Archaeological Science 22, 841-852"
BEI = "Beier, Anthes, Wahl & Harvati (2018). Similar cranial trauma prevalence among Neanderthals and Upper Palaeolithic modern humans. Nature 563, 686-690"
SHA = "Shaw, Hofmann, Petraglia, Stock & Gottschall (2012). Neandertal humeri may reflect adaptation to scraping tasks, but not spear thrusting. PLoS ONE 7(7): e40349"
ONE = "O'Neill et al. (2017). Chimpanzee super strength and human skeletal muscle evolution. PNAS 114, 7343-7348"
FAI = "Fain & Weatherford (2016). Comparative study of millennials' (age 20-34 years) grip and lateral pinch with the norms. Journal of Hand Therapy 29, 483-488"
LEO = "Leong et al. (2015). Prognostic value of grip strength: findings from the Prospective Urban Rural Epidemiology (PURE) study. The Lancet 386, 266-273"
GUI = "Guinness World Records, heaviest deadlift (501 kg, Hafthor Bjornsson, 2 May 2020; Eddie Hall was first past 500 kg in 2016)"

# how each source was checked (goes into the fact-check file)
VERIFY = {
    MAC: ("Searched 2026-10-24; found the Science Advances record plus National Geographic, University of Vienna and Sci.News coverage. Neolithic women's humerus 11-16 percent stronger than rowers' and almost 30 percent stronger than Cambridge students'; Bronze Age 9-13 percent stronger arms but about 12 percent weaker legs; shins like sedentary women's on average; arm/leg balance most like semi-elite rowers; grain grinding is the authors' suggestion, and they said they could not name the behaviour. Percentages come from press materials; paper text not fully opened.", "Worded 'stronger for their size', 'suggested', 'could not name the exact behavior'; farmers, not hunters, stated outright."),
    RYA: ("Searched 2026-10-24; PNAS record and Sci.News coverage. Hip trabecular bone of four recent human groups plus a nonhuman primate sample; foragers comparable to similar-sized primates, clearly above sedentary farmers; activity is the best-supported explanation; two other hypotheses (different primate biology, large joint surfaces) not supported; diet (maize, calcium) may also contribute.", "'Other primates' not 'apes'; diet caveat stated; presented as the authors' conclusion."),
    RUF: ("Searched 2026-10-24; PNAS abstract via Carta and the PMC commentary. 1,842 individuals, Upper Paleolithic to the twentieth century; big drop in front-to-back bending strength of femur and tibia from the Neolithic; humerus and side-to-side strength changed much less and less consistently; mobility decline is the authors' reading; gradual; no clear directional change in the last 2,000 years.", "'More than eighteen hundred'; 'the authors read it as'; 'no clear change'."),
    CHI: ("Searched 2026-10-24; PubMed abstract and AMNH / Popular Archaeology coverage. Modern humans, chimps and fossil hominins (including Neanderthals and early Homo sapiens): only recent modern humans have low trabecular density throughout limb joints; strongest reduction in hip, knee, ankle; early members of our species about twenty thousand years ago still had dense bone; authors link the shift to sedentism and technology.", "Phrased as 'the researchers noted' / 'the authors tied'; sample sizes not stated."),
    CHU: ("Searched 2026-10-24. Abstract-level: attachment sites and leverage show pronounced upper-body strength relative to most modern humans, probably important for close-range hunting. Full text not opened; the venue is Periodicum Biologorum, not a major journal.", "Worded 'argued'; Shaw 2012 and Beier 2018 are placed right after as counterpoints."),
    BER: ("Searched 2026-10-24; Smithsonian and the reference list of Beier et al. Neanderthals had many head and neck injuries, compared to rodeo riders and tied to close-range hunting; Trinkaus later reanalysed with early modern humans and found no statistical difference.", "'Noticed' and 'linked'; immediately followed by the 2018 counter-study."),
    BEI: ("Searched 2026-10-24; Tubingen press release, Zenodo abstract and Nature record. Several hundred fossil specimens; no significant difference in cranial trauma prevalence between Neanderthals and early Upper Palaeolithic modern humans.", "'Similar rates' not 'identical'."),
    SHA: ("Searched 2026-10-24; PMC article and ScienceDaily. EMG on modern volunteers: spear thrusting gave more activity on the non-dominant side, scraping gave more on the dominant side. Title itself says 'may reflect'.", "'Closer to what the bones show'; experiments are on modern volunteers, said outright."),
    ONE: ("Searched 2026-10-24; PMC article, Penn State, ScienceDaily. Literature review: chimp mass-specific muscle performance about 1.5 times human on average; whole-muscle simulations 1.35 times; due mostly to fast-twitch fibre content (sampled chimp muscle about 67 percent fast-twitch); the decline in hominin muscle performance is a suggestion, not a finding.", "'About one and a half', 'they suggest'. The 'five to ten times' figure is called a popular claim and is not endorsed."),
    FAI: ("Searched 2026-10-24; NPR, WGBH, KQED, Workers' Comp Central coverage. 237 healthy adults aged 20-34; scores lower than the 1985 norms; men 20-24 right hand 121 lb to about 101 lb (numbers from press coverage); critics: small sample, only four men aged 30-34, follow-up wanted. Primary text not opened.", "'About', 'below the norms clinics still use'; the criticism is stated in the script."),
    LEO: ("Searched 2026-10-24; Healio, NEJM Journal Watch blog and other summaries. 139,691 adults aged 35-70 in 17 countries; each 5 kg drop in grip went with about 16 percent higher all-cause mortality; grip predicted death more strongly than systolic blood pressure; median follow-up about four years; the lead author said more research is needed on whether building strength lowers risk. Lancet text not opened.", "Called 'a link, not proof'; narrator says it is not medical advice."),
    GUI: ("Searched 2026-10-24; Guinness World Records page and several news reports. 501 kg, Hafthor Bjornsson, 2 May 2020, Kopavogur, Iceland; Eddie Hall first to 500 kg in 2016. Some commentators raised questions about the 2020 attempt (not an official competition).", "'Guinness lists'; comparison to a horse is rough."),
}

S = [
    # ---------------- hook (12 one-line scenes)
    ("Her arm bones were stronger than a rower's.", "The main character flexes one arm next to a long wooden rowing oar, wide-eyed and surprised.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Neolithic women in Central Europe beat modern athletes.", "Two ancient arm bones side by side on a flat stone, one clearly thicker than the other, soft light.", "hook", "awe", 2, "normal", 0, None, MAC),
    ("So were ancient humans simply stronger than us?", "The main character looks at his own thin arm, then at a huge round boulder, puzzled.", "hook", "curious", 2, "normal", 0, None, None),
    ("Chimps aren't ten times stronger than you. Not even close.", "A chimpanzee sitting calmly on the ground next to a thick rope and a wooden handle.", "hook", "excited", 2, "normal", 0, None, ONE),
    ("Because the answer says something about your own body.", "The main character pokes his own upper arm and looks down at it, curious.", "hook", "serious", 3, "normal", 0, None, None),
    ("Forager hip bones were as sturdy as other primates'.", "A cross-section of a hip joint bone showing a fine inner lattice, drawn simply on a plain background.", "hook", "curious", 2, "normal", 0, None, RYA),
    ("By the end, you'll know who really wins.", "The main character crosses his arms with a confident grin, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("Young adults' grip tested weaker than nineteen eighty-five norms.", "A hand squeezing a simple spring hand-grip tool against a plain pale background.", "hook", "tense", 2, "normal", 0, None, FAI),
    ("Is that progress, or something we quietly lost?", "The main character holds a heavy rock in both hands, strains, then looks at his palms.", "hook", "whisper", 2, "slow", 0, None, None),
    ("Guinness lists a deadlift of five hundred and one kilograms.", "A huge barbell loaded with big round plates resting on a plain floor.", "hook", "awe", 2, "normal", 0, None, GUI),
    ("So who wins, the ancient hunter or the modern lifter?", "The main character stands between a hunter holding a spear and an athlete holding a barbell, looking from one to the other.", "hook", "tense", 2, "normal", 0, None, None),
    ("Something changed in our legs when farming began.", "A single long leg bone lying on dry ground between a wheat stalk and a wooden spear, no people.", "hook", "whisper", 2, "slow", 500, None, RUF),
    # ---------------- how we know
    ("Quick honesty first. Nobody has ever measured an ancient person's muscles. Muscle doesn't fossilize, so everything here is read from bones.", "The main character holds a long old bone up to the light like a detective, squinting at it.", "build", "curious", 2, "normal", 0, None, None),
    ("The idea is simple. Bone responds to the loads it carries, so thick, strong bones point to a physically demanding life.", "Two bone cross-sections side by side, one thick-walled and one thin-walled, on a plain pale background.", "build", "curious", 2, "normal", 0, None, RYA),
    ("It's like reading someone's shoes. Worn heels, lots of walking. Mine mostly say I walk to the fridge.", "The main character holds up a badly worn sandal, inspecting the heel closely, grinning.", "build", "funny", 2, "fast", 0, None, None),
    # ---------------- the farming women
    ("Alison Macintosh's team CT-scanned the arm and leg bones of living women, from runners and rowers to sedentary people, and compared them with early farmers from Central Europe.", "A small tabletop scanner with a long arm bone resting inside its round opening.", "build", "neutral", 2, "normal", 0, None, MAC),
    ("So, who had the strongest arms? Take a guess. I'll wait.", "The main character taps his chin, thinking, beside three figures: one holding an oar, one running, one sitting.", "build", "curious", 2, "normal", 0, None, None),
    ("The early farming women's arm bones were eleven to sixteen percent stronger for their size than the rowers', and almost thirty percent stronger than typical Cambridge students'.", "Two ancient arm bones next to a modern rowing oar on a stone surface, soft light.", "punchline", "awe", 3, "normal", 600, "ding", MAC),
    ("Not stronger than office workers. Stronger than people who row for a living. So what was she doing all day?", "The main character stands with arms out, mouth open in amazement, in front of a field of golden wheat.", "build", "curious", 2, "normal", 0, None, None),
    ("The team suggested grinding grain by hand on a stone, for hours, as one possible cause. But they said they couldn't name the exact behavior.", "A flat stone slab with a smaller stone on top and a pile of golden grain beside it, close up.", "build", "neutral", 2, "normal", 0, None, MAC),
    ("Before we crown anyone, notice something. These were farmers, not hunters, and they weren't superheroes from head to toe.", "The main character holds a small crown above the head of a farmer figure, then pauses, unsure.", "build", "serious", 2, "normal", 0, None, None),
    ("Their shin bones looked a lot like those of sedentary women on average, and were weaker than those of living runners and football players.", "Two long shin bones on a stone, one thick and one slim, side by side, plain background.", "build", "neutral", 2, "normal", 0, None, MAC),
    # ---------------- hunter-gatherer bones
    ("So what about people who hunted and gathered, and walked everywhere?", "The main character walks across a dry savanna with a walking stick, tall grass around him, determined.", "build", "curious", 2, "normal", 0, None, None),
    ("Timothy Ryan and Colin Shaw compared the inner hip bone of four recent human groups and some other primates. Foragers' hips were comparable to similar-sized primates' and clearly stronger than those of sedentary farmers.", "A cross-section of a hip joint bone showing a fine inner lattice, drawn simply on a plain background.", "build", "curious", 2, "normal", 0, None, RYA),
    ("So a forager's hips were built like a primate's, and mine are built for sitting. I'm choosing not to take that personally.", "The main character sits sunk deep in a soft cushioned armchair, completely relaxed, eyes half closed.", "build", "funny", 2, "normal", 0, None, None),
    ("Their data best supported low physical activity as the reason modern skeletons are lighter, though they noted that a grain-heavy diet might play a part too.", "A balance scale with a small wheat bundle on one side and a bone on the other, plain background.", "build", "neutral", 2, "normal", 0, None, RYA),
    ("So lighter bones aren't a law of nature. They look more like the result of how we live.", "The main character looks at a long bone in his hand, thinking, in warm light.", "build", "serious", 2, "slow", 0, None, None),
    ("Habiba Chirchir's team measured the spongy bone inside limb joints in people, chimps and fossils. Only recent humans had low density throughout the limbs.", "A cross-section of a knee joint bone with a delicate honeycomb pattern inside, plain background.", "build", "curious", 2, "normal", 0, None, CHI),
    ("Recent. That's the word that matters. Not a million years of evolution. Just the last few thousand years of how we live.", "The main character stands beside a very long timeline strip drawn on the ground, pointing to the last tiny piece.", "build", "awe", 2, "slow", 300, "riser", None),
    ("The drop was biggest in the hip, knee and ankle, and smaller in the shoulder, elbow and hand.", "Three joint bones in a row, hip, knee and ankle, drawn simply on a plain background.", "build", "neutral", 2, "normal", 0, None, CHI),
    ("Legs lose the most. Honestly, that tracks. My legs mostly commute between the bed and the couch.", "The main character lies stretched on a couch with both tired legs up in the air, grinning.", "build", "funny", 2, "fast", 0, None, None),
    ("A study of more than eighteen hundred skeletons across Europe, from the Ice Age to the twentieth century, found a large drop in leg bone strength that began with the Neolithic.", "A long row of many leg bones laid out in order across a pale surface, plain background.", "build", "curious", 2, "normal", 0, None, RUF),
    ("Not the smartphone. Not the office chair. It began when people settled down to farm.", "The main character stands at the edge of a small wheat field next to a simple hut, looking out.", "punchline", "serious", 2, "normal", 300, None, None),
    ("Arm bones changed much less, and less consistently. The big loss was in how well the leg bones resisted front-to-back bending, which the authors read as less walking.", "An arm bone and a leg bone side by side on a pale plain background.", "build", "neutral", 2, "normal", 0, None, RUF),
    # ---------------- subscribe (mid-video, hero scene right after a fact)
    ("Quick pause. If this is making you curious, subscribe and stay with me. We're going to keep digging into the human story together, one strange question at a time. It's free, it takes a second, and it helps more curious people find the channel.", "The main character waves at the viewer with a friendly smile, standing in a sunny field.", "normal", "happy", 2, "normal", 300, None, None),
    # ---------------- Neandertals
    ("Now the Neandertals. Steven Churchill and Jill Rhodes studied the muscle attachment sites and leverage in their arms, and argued for pronounced upper-body strength compared with most modern humans.", "A thick fossil arm bone with a prominent ridge on it, lit softly on a stone.", "build", "curious", 2, "normal", 0, None, CHU),
    ("Picture hunting a big animal with a spear in your hand, not thrown from far away. You'd want serious shoulders.", "The main character braces with a long wooden spear held in both hands, wide-eyed, facing the huge shadow of an animal.", "build", "tense", 2, "normal", 0, "riser", None),
    ("In nineteen ninety-five, Berger and Trinkaus noticed that Neandertal skeletons showed many head and neck injuries, a pattern like rodeo riders', and linked it to hunting up close.", "A fossil skull with a healed dent on its forehead resting on a rock in dim light.", "build", "serious", 2, "normal", 0, None, BER),
    ("Rodeo riders. Meanwhile, I once pulled a muscle opening a pickle jar.", "The main character wearing a cowboy hat with a bandage on his head, holding a rope, dizzy but proud.", "build", "funny", 2, "fast", 0, None, None),
    ("But in twenty eighteen, Judith Beier, Katerina Harvati and colleagues compared several hundred fossil skulls and found that Neandertals and early modern humans had similar rates of head injuries.", "Two fossil skulls side by side on a flat rock, plain background.", "build", "neutral", 2, "normal", 0, None, BEI),
    ("So the rodeo story has a crack in it. Maybe Neandertals simply lived as dangerously as everyone else back then.", "The main character holds a small cracked clay plate, running a finger along the crack, thoughtful.", "build", "curious", 2, "normal", 0, None, None),
    ("Colin Shaw's team also tested the spear idea. They put sensors on volunteers' arm muscles. Spear thrusting loaded the non-dominant arm more, but scraping a hide loaded the dominant arm, closer to what the bones show.", "A stretched animal hide on a wooden frame with a stone scraper lying on it, plain background.", "build", "curious", 2, "normal", 0, None, SHA),
    ("So maybe the real Neandertal workout wasn't wrestling mammoths. It was cleaning animal hides. Nobody puts that on a poster.", "The main character scrapes a stretched hide on a wooden frame with a stone tool, sweating hard.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- chimps
    ("Now the chimp myth. Popular claims say they're five or ten times stronger than us. A careful review of the data found chimp muscle performs about one and a half times better.", "A chimpanzee hanging from a thick tree branch by one arm, calm.", "build", "neutral", 2, "normal", 0, None, ONE),
    ("One and a half times. I'd still lose the arm wrestle. Honestly, I'd lose to most of my friends too.", "The main character and a chimpanzee arm wrestling on a small tree stump table, the main character sweating, the chimp relaxed.", "build", "funny", 2, "fast", 0, None, None),
    ("Their simulations gave one point three five times. The gap comes mostly from fast-twitch fibers, and they suggest human muscle shifted toward cheap, repetitive movement, like walking.", "A chimpanzee silhouette leaping between two branches beside a long footpath winding into the distance.", "build", "neutral", 2, "normal", 0, None, ONE),
    ("So we traded explosive power for stamina. Like swapping a sports car for really good walking shoes.", "The main character happily holds a pair of sturdy walking sandals while a tiny toy sports car sits abandoned behind him.", "build", "funny", 2, "normal", 0, "boing", None),
    # ---------------- today
    ("Now the other direction. A twenty sixteen study of two hundred and thirty-seven adults aged twenty to thirty-four found grip strength below nineteen eighty-five norms. Men twenty to twenty-four averaged about one hundred and one pounds in the right hand, versus one hundred and twenty-one.", "A simple spring hand-grip tool with a gauge, resting on a plain wooden table.", "build", "curious", 2, "normal", 0, None, FAI),
    ("My hands mostly do one job: scroll. Let's not test my grip today.", "The main character holds a flat glowing slab in one hand, thumb scrolling, the other arm hanging limp.", "build", "funny", 2, "normal", 0, None, None),
    ("Grip isn't just a party trick, either. In the PURE study of about one hundred and forty thousand adults in seventeen countries, each five-kilogram drop in grip strength went with about sixteen percent higher risk of death from any cause.", "A thick rope pulled tight between two wooden posts, rough twisted fibres, plain background.", "build", "neutral", 2, "normal", 0, None, LEO),
    ("Now, that's a link, not proof. A weak grip doesn't cause anything on its own.", "The main character looks at a small glowing warning lamp on a stone panel, arms crossed, thoughtful.", "build", "serious", 2, "normal", 0, None, None),
    ("It predicted death more strongly than systolic blood pressure did. Even so, the lead author said more research is needed on whether building strength actually lowers anyone's risk.", "A rubber blood pressure bulb and cuff lying beside a hand-grip tool on a table, plain background.", "build", "neutral", 2, "normal", 0, None, LEO),
    ("I'm not a doctor, and this isn't advice. I'm just telling you the story the bones tell.", "The main character raises both palms in a calm gesture, shaking his head gently, in warm light.", "build", "serious", 2, "normal", 0, None, None),
    ("And yet at the very top, we are stronger than ever. Eddie Hall was first past five hundred kilograms in twenty sixteen. Hafthor Bjornsson lifted five hundred and one in twenty twenty, according to Guinness.", "A huge barbell loaded with big round plates resting on a plain floor.", "build", "excited", 2, "normal", 0, "impact", GUI),
    ("Five hundred and one kilograms is about the weight of a horse. I can barely lift my suitcase at the airport.", "The main character stands tiny under a giant loaded barbell, a calm horse standing patiently beside it.", "build", "funny", 2, "fast", 0, None, None),
    ("Notice the comparison in the rowing study, though. The rowers were semi-elite athletes who train on purpose. The farming women's arm pattern most resembled theirs, with no training plan at all.", "A wooden rowing boat with two oars resting on a calm shore next to a stone grinding slab, evening light.", "build", "curious", 2, "normal", 0, None, MAC),
    ("So 'stronger' can mean three things: the biggest single lift, the toughness of an everyday body, or stamina over a long day. Ancient people clearly won the second.", "The main character counts on three raised fingers, one eyebrow lifted, in front of a blank stone wall.", "build", "curious", 2, "normal", 0, None, None),
    ("Ryan and Shaw also tested the other explanations: that human bone biology is just different from other primates, or that our big joint surfaces spread the load. Neither fit the data.", "A large joint surface of a hip bone next to a small joint surface of another primate's bone, plain background.", "build", "neutral", 2, "normal", 0, None, RYA),
    ("That's the surprising part. Lighter bones don't seem to be about being human. They're about what our bones are asked to do.", "The main character carries a bundle of firewood on his shoulder up a grassy hill, smiling.", "build", "awe", 2, "normal", 0, None, None),
    ("To be fair, the grip study has critics. Some experts said the sample was small and wanted a follow-up, especially since only four men were in the thirty to thirty-four group.", "Four small pebbles sitting alone on a large flat stone, plain background.", "build", "neutral", 2, "normal", 0, None, FAI),
    ("I like that. A study that points out its own weak spots is a study I trust more.", "The main character gives a thumbs up beside a scroll with a small dent drawn in it, smiling.", "build", "happy", 2, "normal", 0, None, None),
    ("The bone density researchers noted that early members of our species, around twenty thousand years ago, still had bone about as dense as other primates.", "A pale fossil hip bone and a primate hip bone side by side on a flat stone, plain background.", "build", "awe", 2, "normal", 0, None, CHI),
    ("A teenager from twenty thousand years ago had hips built like a primate's. I get winded carrying groceries up one flight.", "The main character struggles up a short staircase carrying a big pile of baskets, panting.", "build", "funny", 2, "normal", 0, "boing", None),
    # ---------------- verdict
    ("Back to the women in Central Europe. Bronze Age women had arm bones nine to thirteen percent stronger than the rowers', but leg bones about twelve percent weaker.", "Two long bones, one thick arm bone and one slimmer leg bone, on a flat stone.", "build", "neutral", 2, "normal", 0, None, MAC),
    ("So the strongest arms in the study came with unremarkable legs. Strong at what? It depends on the job.", "The main character carries a heavy basket on his head with strong arms but wobbly legs, comically.", "build", "curious", 2, "normal", 0, None, None),
    ("The authors called the transition gradual: mobility first fell as food production began, and kept falling as farming intensified.", "A long winding footpath that grows fainter as it nears a wheat field, plain background, no people.", "build", "neutral", 2, "normal", 0, None, RUF),
    ("So who wins? Ancient people had sturdier bones because daily life loaded them. We win at the peak: the biggest lift, the best food, the best training.", "The main character holds a balance scale with a sturdy thick bone on one side and a small barbell on the other.", "punchline", "serious", 2, "normal", 400, None, None),
    ("The same European study found no clear change in the last two thousand years. So machines and cities mattered less than the shift to farming.", "A tall clay water jug next to an old stone road and a wheat bundle, plain background.", "build", "neutral", 2, "normal", 0, None, RUF),
    ("Which means this isn't a failure. It's a trade we made for farms, cities and medicine, and our bones quietly paid part of the price.", "The main character weighs a small bone against a loaf of bread on a balance scale, thoughtful.", "build", "whisper", 2, "slow", 300, None, None),
    ("The authors tied that late shift to settled life and our growing reliance on technology and culture.", "A simple stone house beside a wheat field with a thin bone resting on its doorstep, plain background.", "build", "neutral", 2, "normal", 0, None, CHI),
    ("So, were ancient humans stronger than us? In bone and everyday toughness, often yes. At the peak, no. Our bones build themselves around whatever life asks of them. Thanks for hanging out with me for these minutes. Hit like if it was worth your time, and tell me in the comments which kind of strong you'd rather be. I read every one. Next time: what could ancient humans do that we can't? See you soon, friend.", "The main character waves goodbye at sunrise beside a small campfire, a bright sky behind him, smiling warmly.", "normal", "happy", 2, "slow", 800, "pop", None),
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
    "title": "Were Ancient Humans STRONGER Than Us?",
    "title_alternatives": ["Stone Age vs Today: Who Was Really STRONGER?", "Why Ancient Women Had Stronger Arms Than ROWERS",
                           "The Truth About Chimp STRENGTH", "Why Are Our BONES So Light?"],
    "description": ("Her arm bones were stronger than a rower's. This video asks whether ancient humans were really stronger than us, using bone studies "
                    "of early farmers and foragers, the Neandertal debate, the chimp strength myth, grip strength today and the world deadlift record.\n\n"
                    "This video is history and science, not medical or fitness advice.\n\nSources:\n"
                    "- Macintosh, Pinhasi & Stock (2017). Science Advances.\n"
                    "- Ryan & Shaw (2015). PNAS.\n"
                    "- Ruff et al. (2015). PNAS.\n"
                    "- Chirchir et al. (2015). PNAS.\n"
                    "- O'Neill et al. (2017). PNAS.\n"
                    "- Fain & Weatherford (2016). Journal of Hand Therapy."),
    "tags": ["ancient humans", "stronger than us", "bone strength", "neanderthals", "hunter-gatherers", "chimpanzee strength", "grip strength",
             "prehistory", "animated explainer", "stickman"],
    "mood": "wholesome",
    "sources": [x for x in dict.fromkeys(s[8] for s in S if s[8])][:14],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

# ---- fact-check file
md = ["# Fact-check: Were Ancient Humans STRONGER Than Us?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-24.", ""]
md += ["## Method", "- Each claim came from a named, checkable source (peer-reviewed paper, university press release, major science outlet, Guinness).",
       "- Where only an abstract or press summary was opened, the claim is worded as 'about', 'roughly' or 'according to', and the file says so.",
       "- Where scientists disagree, both sides are told: Neandertal strength and injuries (Churchill, Berger and Trinkaus vs Shaw 2012 and Beier 2018), and the grip study (critics are voiced in the script).",
       "- Hypotheses are labelled as the authors' suggestions (grain grinding, muscle shifting toward cheap movement).",
       "- The narrator says outright that this is not medical advice; the description repeats it.", "",
       "## Fact scenes", "", "| # | Narration (shortened) | Source | How verified | Wording safeguard |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        src = sc["fact_source"]
        how, safe = VERIFY.get(src, ("", ""))
        md.append(f"| {i} | {sc['narration'][:90].replace('|', '/')}... | {src[:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Claims softened or dropped",
       "- 'Chimps are five to ten times stronger' is presented as a popular claim; the data support about 1.35 to 1.5 times.",
       "- 'Neandertals were X times stronger than us': no reliable multiplier exists in the sources found, so none is given.",
       "- Muscle size and strength of ancient people: muscle does not fossilize; the narrator says all conclusions are read from bones.",
       "- Hadza and other forager walking distances and daily calories: could not be verified, dropped.",
       "- Grip pounds (121 to about 101) come from press coverage of the 2016 study; worded 'about'.",
       "- Deadlift: Guinness lists 501 kg; doubts about the 2020 attempt are mentioned in this file, not in the narration (the narration says 'according to Guinness').",
       "", "## Human-voice checklist (all done)",
       "- Short and long sentences mixed; contractions used; personal takes ('I once pulled a muscle opening a pickle jar', 'my legs commute between the bed and the couch').",
       "- Modern comparisons: reading shoes, desk chair, sports car vs walking shoes, groceries up one flight, scrolling thumb.",
       "- No filler words ('delve', 'fascinating journey', 'it's important to note').",
       "- Numbers written as words; no ALL CAPS in narration; no long dashes.",
       "- Warm connection: friendly mid-video 'subscribe and stay with me' scene, thank-you and 'See you soon, friend' ending; 'like' asked once at the end.",
       "- The first 40 seconds say why to watch ('the answer says something about your own body') and what you get ('By the end, you'll know who really wins')."]
Path(__file__).with_name("stone_strength.factcheck.md").write_text("\n".join(md), encoding="utf-8")

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
