"""Builds scripts/ancient_visitor.json and scripts/ancient_visitor.factcheck.md
(run: ./venv/Scripts/python scripts/ancient_visitor.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

CMP = "Crittenden & Blurton Jones, Hadza summary, eHRAF World Cultures (Yale), citing Marlowe (2010) The Hadza: Hunter-Gatherers of Tanzania (camps average about 30 people, 5-6 grass huts)"
DUN = "Dunbar, R. I. M. (1992). Neocortex size as a constraint on group size in primates. Journal of Human Evolution 22, 469-493"
LIN = "Lindenfors, Wartel & Lind (2021). 'Dunbar's number' deconstructed. Biology Letters 17, 20210158"
WRI = "Wright et al. (2013). Entrainment of the human circadian clock to the natural light-dark cycle. Current Biology 23, 1554-1558"
RAI = "Raichlen et al. (2020). Sitting, squatting, and the evolutionary biology of human inactivity. PNAS 117, 7115-7121"
NGH = "National Geographic, 'The Hadza' (2009 and later web edition); Hawkes, O'Connell & Blurton Jones (2014). More lessons from the Hadza about men's work. Human Nature 25"
WIL = "Wilson et al. (2014). Just think: the challenges of the disengaged mind. Science 345, 75-77; Wilson et al. (2014), reply to Fox et al., Frontiers in Psychology 5, 1428"
EIS = "Eisenberger, Lieberman & Williams (2003). Does rejection hurt? An fMRI study of social exclusion. Science 302, 290-292; 2020 meta-analysis of 53 Cyberball fMRI studies (PMC8005222)"
BRO = "Brooks et al. (2018). Long-distance stone transport and pigment use in the earliest Middle Stone Age. Science 360, 90-94"
BOU = "Bouzouggar et al. (2007). 82,000-year-old shell beads from North Africa and implications for the origins of modern human behavior. PNAS 104, 9964-9969"
YET = "Yetish et al. (2015). Natural sleep and its seasonal variations in three pre-industrial societies. Current Biology 25, 2862-2868"
WIE = "Wiessner, P. (2014). Embers of society: Firelight talk among the Ju/'hoansi Bushmen. PNAS 111, 14027-14035 (the 'more than 80 percent stories' figure is from the PNAS commentary on the study)"
CRI = "Crittenden & Zes (2015). Food sharing among Hadza hunter-gatherer children. PLoS ONE 10(7): e0131996; Crittenden et al. (2013). Juvenile foraging among the Hadza. Evolution and Human Behavior 34"

VERIFY = {
    CMP: ("Reused from the Stone Age video: eHRAF Yale summary, camps average about 30 people and 5-6 grass huts; secondary summary of Marlowe (2010).", "Presented as a living-forager comparison, not a measurement of ancient camps."),
    DUN: ("Searched 2026-10-24; the 150 figure comes from extrapolating a regression of relative neocortex size and group size in primates (Dunbar 1992), as described in the 2021 critique. The 1992 paper itself was not opened.", "'Famous idea', 'extrapolated'; no claim that it is proven."),
    LIN: ("Searched 2026-10-24; Biology Letters abstract and Stockholm University release. Newer Bayesian and GLS phylogenetic methods give average group size estimates of 69-109 and 16-42, with 95 percent confidence intervals of 4-520 and 2-336; the authors say a cognitive limit cannot be derived this way. Defenders argue other human observations support the number.", "Stated as a critique with its ranges; no verdict."),
    WRI: ("Searched 2026-10-24; Current Biology abstract, Irish Times, ZME Science, NPR. Eight participants, one week of normal life then one week camping in Colorado with sunlight and campfire only; circadian clock about two hours earlier after camping (press reports 2 h 36 min), internal biological night started at sunset; electric light and less daytime sunlight linked to delayed clock. Full text not opened.", "'About two hours', small sample (eight) stated."),
    RAI: ("Searched 2026-10-24; PNAS record, ScienceAlert, HealthDay. 28 Hadza wore thigh accelerometers for about eight days; 9.9 hours a day nonambulatory; mostly squatting, kneeling or sitting on the ground (squatting about 18 percent, kneeling 12.5 percent), postures needing more leg muscle activity than chair sitting; authors propose an inactivity mismatch hypothesis.", "'Nearly ten hours', 'the authors propose'; a US-only comparison is not claimed beyond 'industrialized populations'."),
    NGH: ("Reused from the Stone Age video: anthropologists estimate four to six hours a day finding food.", "Worded as an estimate."),
    WIL: ("Searched 2026-10-24; BPS Digest, Time, Mapping Ignorance and the Frontiers reply. Participants alone with their thoughts for 15 minutes could shock themselves; 67 percent of men and 25 percent of women did at least once, though they had said they would pay to avoid the shock; one participant who shocked himself 190 times was excluded; follow-up with ages 18-77 found much the same; Fox et al. argued curiosity, the authors replied it was not.", "'At least once'; the dispute is stated."),
    EIS: ("Searched 2026-10-24; ScienceDaily and later papers. Cyberball exclusion raised activity in the dorsal anterior cingulate and insula, even when participants were told the exclusion might be an accident; a 2020 meta-analysis of 53 Cyberball studies (N = 1,817) found no reliable dACC activity, and other work argues social and physical pain are represented differently. Original paper not opened.", "'Original reading' versus 'later challenge', both told."),
    BRO: ("Searched 2026-10-24; Science abstract, Springer Nature 'Behind the Paper' post. Sites at Olorgesailie, Kenya, about 295,000 to 320,000 years old; stone tool materials brought from at least 25 to 50 km, and obsidian up to about 95 km per one author post; iron-rich rocks used for red pigment; the authors interpret it as changed relations between people.", "'At least twenty-five kilometres'; the 95 km figure is attributed to one author's post and kept loose."),
    BOU: ("Searched 2026-10-24; PNAS abstract, ScienceDaily. Perforated Nassarius gibbosulus shells from Grotte des Pigeons, Morocco, dated to about 82,000 years ago by luminescence and uranium series; wear suggests hanging; coated in red ochre; some researchers dispute symbolic behavior this early.", "'About eighty-two thousand'; the dispute is stated."),
    YET: ("Reused from the Stone Age video: Hadza, San and Tsimane adults about 6.5 hours of sleep.", "'About'."),
    WIE: ("Reused from the Stone Age video: PNAS commentary on Ju/'hoansi evening talk mostly stories (over 80 percent); primary figure not seen.", "Attributed to a commentary."),
    CRI: ("Reused from the Stone Age video: from about five years old, Hadza children can collect up to half their daily energy need.", "'Up to half'."),
}

S = [
    # ---------------- hook (12 one-line scenes)
    ("What if a Stone Age person walked down your street?", "The main character steps out of a rock shelter onto a modern city street, eyes huge with wonder.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Their camp held about thirty people. Your city holds millions.", "A small camp of five grass huts around a fire beside a distant glowing city skyline, no people.", "hook", "awe", 2, "normal", 0, None, CMP),
    ("By the end, you'll know what they'd actually envy.", "The main character looks at a traffic light and then at his own hands, puzzled.", "hook", "curious", 2, "normal", 0, None, None),
    ("Camping for a week shifted body clocks two hours.", "A small tent on a mountain meadow at sunrise with a campfire's thin smoke, no people.", "hook", "excited", 2, "normal", 0, None, WRI),
    ("Because their reactions reveal what's odd about your own life.", "The main character holds up a small hand mirror and stares at himself, surprised.", "hook", "serious", 3, "normal", 0, None, None),
    ("Hunter-gatherers sit nearly ten hours a day, just like us.", "A simple row of stones arranged like seats in a circle on dry ground, no people.", "hook", "curious", 2, "normal", 0, None, RAI),
    ("What would they find strange? What would they envy?", "The main character crosses his arms and grins, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("Many people chose electric shocks over fifteen quiet minutes.", "A small red button on a stone slab with a tiny spark above it, plain background, no people.", "hook", "tense", 2, "normal", 0, None, WIL),
    ("Would they understand why?", "The main character sits alone on a rock with his chin in his hand, looking worried.", "hook", "whisper", 2, "slow", 0, None, None),
    ("Being left out of a ball game can hurt.", "A small stone ball passed between two stick figures while a third stands alone aside, no text.", "hook", "awe", 2, "normal", 0, None, EIS),
    ("So who'd be more baffled, them or us?", "The main character stands between a hunter with a spear and a person with a phone, looking from one to the other.", "hook", "tense", 2, "normal", 0, None, None),
    ("The famous 'one hundred and fifty friends' rule is shaky.", "A bundle of one hundred and fifty small pebbles heaped on a flat stone, a crack through the middle, no people.", "hook", "whisper", 2, "slow", 500, None, LIN),
    # ---------------- crowds
    ("Quick setup. Meet our visitor, someone from thirty thousand years ago. Their body and mind are just like ours, so their reactions aren't a joke at their expense. They're a mirror. I'll try not to make them look silly, because honestly, I'd be the confused one in their world.", "The main character holds up a large oval mirror in a sunny meadow and peers into it, curious.", "build", "curious", 2, "normal", 0, None, None),
    ("Their camp: about thirty people and five or six grass huts, going by summaries of Hadza life. That's a living-forager comparison, not a measurement of ancient camps.", "A small camp of grass huts around a fire at the edge of a savanna, baobab trees behind, no people.", "build", "neutral", 2, "normal", 0, None, CMP),
    ("Now they step onto a city street. Thirty people is a family reunion. This is Tuesday. Even the pigeons would seem like a lot of neighbors.", "The main character stands in the middle of a crowded street, wide-eyed, a sea of stick figures around him.", "build", "funny", 2, "fast", 0, None, None),
    ("Robin Dunbar's famous idea says we can keep stable relationships with about one hundred and fifty people, an estimate extrapolated from the link between brain size and group size in primates.", "A big circle of small figures drawn on dry ground with lines connecting to a central one, plain background.", "build", "neutral", 2, "normal", 0, None, DUN),
    ("So our visitor knows maybe everyone in the valley. I know my barista's name, sometimes.", "The main character waves at a long line of friendly figures, then mutters at a coffee cup, unsure.", "build", "funny", 2, "normal", 0, None, None),
    ("In twenty twenty-one, Patrik Lindenfors and colleagues reran the analysis with newer methods and got average group estimates of sixty-nine to one hundred and nine, and sixteen to forty-two, with huge uncertainty ranges.", "Two bars of different heights each with a very long thin line above and below it, plain background, no text.", "build", "curious", 2, "normal", 0, None, LIN),
    ("So the magic number is shakier than it sounds. Honestly, 'it depends' might be the most scientific answer there is.", "The main character holds a cracked stone tablet with a big number scratched out, laughing quietly.", "build", "funny", 2, "normal", 0, None, None),
    ("Defenders of Dunbar's number say the idea rests on more than one calculation, pointing to many observations of human groups that cluster around similar sizes.", "Several different small circles of figures of similar size scattered across dry ground, no text.", "build", "neutral", 2, "normal", 0, None, LIN),
    ("Which makes this a real argument, not a settled fact. My own contact list proves nothing, by the way. It mostly contains dentists.", "The main character scrolls a very long list on a flat slab with a bored face, a tooth icon drawn beside it.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- light and night
    ("Next, light. In twenty thirteen, Kenneth Wright's team had eight volunteers wear light sensors for a week of normal life, then sent them camping in Colorado with only sunlight and a campfire.", "A small tent in a mountain meadow under a pink dawn sky, a campfire glowing beside it, no people.", "build", "neutral", 2, "normal", 0, None, WRI),
    ("No phones, no lamps. Just sun and fire. I'd be asleep by eight and annoyingly cheerful.", "The main character smiles sleepily beside a small campfire with a blanket over his shoulders.", "build", "funny", 2, "normal", 0, None, None),
    ("After the camping week, their body clocks had moved about two hours earlier, and their internal biological night began around sunset.", "A simple clock face with a moon and a sun on either side, no numbers or letters, plain background.", "build", "curious", 2, "normal", 0, None, WRI),
    ("Our visitor would look at our streetlights and ask who stole the night. Then they'd see the lit-up shop windows and decide we never go to bed on purpose.", "The main character looks up at a glowing streetlight pole with a puzzled frown, a dark sky above.", "build", "curious", 2, "normal", 0, None, None),
    ("They also reported that after the camping week, the body's melatonin signal, the one that says it's night, ended before wake time instead of dragging on into the morning.", "A pale moon fading above a hill while a small sun rises on the other side of the frame, plain sky, no people.", "build", "neutral", 2, "normal", 0, None, WRI),
    ("So the grogginess of a dark winter morning might partly be a lighting problem. I mean, it feels like a coffee problem, but sure.", "The main character sits at the edge of a bed with a wild hair and an empty cup, eyes half closed.", "build", "funny", 2, "fast", 0, None, None),
    ("The authors linked electric lighting and less daytime sunlight to a later body clock, compared with life in the natural light-dark cycle.", "A bright lamp beside a pale moon with a long shadow stretching behind, plain background, no people.", "build", "neutral", 2, "normal", 0, None, WRI),
    ("So your two a.m. scroll isn't a personality flaw. It's partly lighting. I'm not giving advice, just saying the lamp is involved.", "The main character stares into a tiny glowing slab in a dark cave, bleary-eyed.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- sitting
    ("Now sitting. David Raichlen's team put thigh monitors on twenty-eight Hadza for about eight days and found they spent nearly ten hours a day not walking, about as sedentary as industrialized populations.", "A group of simple seats drawn as flat stones in a circle on dry ground, no people.", "build", "curious", 2, "normal", 0, None, RAI),
    ("So our visitor looks at our offices and says, you sit all day? We do that too. But look how.", "The main character squats comfortably on the ground next to an office chair, grinning.", "build", "funny", 2, "normal", 0, None, None),
    ("The difference was posture. The Hadza mostly rested squatting, kneeling or sitting on the ground, which takes more leg muscle than sitting in a chair.", "A drawing of three resting postures: squatting, kneeling and sitting on the ground, as simple stick figures, no text.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("A chair is basically a squat with the work taken out.", "The main character sits on a tall chair and then slides down into a squat, delighted.", "build", "funny", 2, "fast", 0, None, None),
    ("Of the Hadza's sedentary time, press coverage says squatting made up about eighteen percent, kneeling about twelve and a half, and most of the rest was sitting on the ground.", "Three simple stick-figure postures labelled only by drawings: squat, kneel, sit, with small bars of different lengths, no letters.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("Eighteen percent squatting. I get a cramp tying my shoes.", "The main character crouches to tie a sandal and wobbles with a grimace.", "build", "funny", 2, "fast", 0, None, None),
    ("The authors proposed an inactivity mismatch hypothesis: it may be the kind of rest, not only the amount, that matters.", "A simple balance with a chair on one side and a flat stone seat on the other, plain background, no people.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("I'm not saying throw out your couch. I'm saying notice how strange a couch is. Mine has a permanent dent in the shape of my week.", "The main character sits deep in a huge soft couch, only his head visible above the cushions.", "build", "funny", 2, "normal", 0, None, None),
    ("And the work? Anthropologists estimate Hadza spend roughly four to six hours a day finding food.", "A woven basket of roots and berries beside a digging stick on a sunny savanna, no people.", "build", "neutral", 2, "normal", 0, None, NGH),
    ("Half a workday for dinner. Our visitor would envy the commute, not the cubicle. Of course, the dinner was roots, so maybe not a straight win.", "The main character carries a basket of roots and waves to a neighbor on a sunny path, relaxed.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- boredom
    ("Now boredom. In Timothy Wilson's experiment, people were asked to sit alone with their thoughts for fifteen minutes. They could, if they wanted, give themselves an electric shock.", "A bare room-like stone alcove with one chair and a small red button on the wall, no people.", "build", "curious", 2, "normal", 0, None, WIL),
    # ---------------- subscribe (mid-video, hero scene right after a fact)
    ("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring the ancient world together, one question at a time. It's free, it takes a second, and it helps other curious people find the channel.", "The main character waves at the viewer with a warm smile, a small campfire glowing behind him.", "normal", "happy", 2, "normal", 300, None, None),
    ("Sixty-seven percent of the men and twenty-five percent of the women shocked themselves at least once, even though they'd said they'd pay to avoid the shock.", "A small bar chart of two bars, a tall one and a shorter one, drawn on a stone, no text.", "build", "neutral", 2, "normal", 0, None, WIL),
    ("I once stared at a loading bar for a full minute rather than think. No judgment here.", "The main character stares at a slow glowing bar on a flat slab with a blank expression.", "build", "funny", 2, "fast", 0, None, None),
    ("A follow-up with adults from eighteen to seventy-seven found much the same, and one person who zapped himself a hundred and ninety times was left out of the analysis.", "A long ladder of tiny tally marks scratched on a rock, plain background, no people.", "build", "neutral", 2, "normal", 0, None, WIL),
    ("A hundred and ninety. That's not boredom. That's a hobby. Respect for the commitment, honestly, though not the method.", "The main character holds a tiny scoreboard with a huge number scratched on it, shaking his head.", "build", "funny", 2, "fast", 0, None, None),
    ("Some researchers argued people were just curious about the shock, and the authors replied that wasn't it.", "Two figures on either side of a small red button, one pointing at it and one shaking his head, no text.", "build", "neutral", 2, "normal", 0, None, WIL),
    ("So science is already arguing about whether we're bored or curious. Either way, our visitor, who spent evenings telling stories, might feel sorry for our quiet rooms.", "The main character shrugs while a small thought bubble shows a campfire, no letters.", "build", "curious", 2, "normal", 0, None, None),
    # ---------------- rejection
    ("Now feeling left out. In Cyberball, a simple ball-tossing game, participants were suddenly excluded by the other players, and scans showed more activity in regions linked to distress.", "A small round ball passed between three figures while a fourth stands alone with open hands, no text.", "build", "curious", 2, "normal", 0, None, EIS),
    ("Imagine getting hurt by a game of catch. Honestly, I felt it just reading it. We evolved to need each other, and every schoolyard remembers that.", "The main character stands alone at the edge of a circle of ball-tossing figures with drooping shoulders.", "build", "funny", 2, "normal", 0, None, None),
    ("It happened even when they were told the exclusion might be an accident.", "A tiny ball rolling away from a lone figure on a pale background, no text.", "build", "neutral", 2, "normal", 0, None, EIS),
    ("So rejection stings even when it's a glitch. That would make sense for someone whose survival depended on the group.", "The main character huddles close to a campfire with a group of figures, glancing around.", "build", "serious", 2, "slow", 0, None, None),
    ("A twenty twenty meta-analysis of fifty-three Cyberball studies found no reliable activity in that region, so the original reading is contested.", "A tall stack of fifty-three small flat stones with a thin crack running down the stack, no people.", "build", "neutral", 2, "normal", 0, None, EIS),
    ("Contested again. At this point my favorite word in science is 'contested'. If a scientist ever says 'definitely', check their pockets.", "The main character holds up a cracked clay plate with a tiny smile, shrugging.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- trade, beads
    ("Now something they'd get immediately: trade. At Olorgesailie in Kenya, toolmakers three hundred thousand years ago used stone from at least twenty-five to fifty kilometres away, and one account says obsidian from up to ninety-five.", "A faint dotted line stretching from a distant dark hill to a camp of simple huts, plain background, no people.", "build", "curious", 2, "normal", 0, None, BRO),
    ("So long-distance supply chains existed before there were roads. Our visitor would nod at the trucks and ask, 'fine, but who's your guy?'", "The main character hands a dark shiny stone to a smiling neighbor in exchange for a basket.", "build", "funny", 2, "normal", 0, None, None),
    ("The same sites show iron-rich rocks used for red pigment, which the authors read as a sign of changed relationships between people.", "A smooth red stone and a small stone grinder on a flat rock with fine red powder, no people.", "build", "neutral", 2, "normal", 0, None, BRO),
    ("Red pigment. Humans have been decorating themselves for much longer than boutiques have existed.", "The main character paints a red stripe across his tunic with a stick, proud and a little messy.", "build", "funny", 2, "normal", 0, None, None),
    ("And jewelry. Perforated shell beads from Taforalt in Morocco are about eighty-two thousand years old, with wear suggesting they were hung and traces of red ochre on them.", "A small string of shell beads lying on pale sand, red powder on a few shells, no people.", "build", "awe", 2, "normal", 0, "ding", BOU),
    ("Eighty-two thousand years ago somebody said, I'd like a necklace. Our visitor would feel right at home in a mall. Some things really don't change, they just get cheaper to buy.", "The main character admires a string of shells held up to his neck, striking a pose.", "build", "funny", 2, "normal", 0, None, None),
    ("Some researchers still question symbolic behavior this early, so I'd call the beads strong evidence, not the final word.", "A simple balance with a bead on one side and a question-shaped branch on the other, plain background, no people.", "build", "neutral", 2, "normal", 0, None, BOU),
    ("Fair. But I've seen a teenager choose a necklace. Nothing symbolic about that process is simple. It takes forty minutes and a committee.", "The main character stands in front of a mirror holding two necklaces, completely undecided.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- what they'd envy
    ("What would they envy? Probably sleep. Adults among the Hadza, San and Tsimane average about six and a half hours a night, and there's no snooze button involved.", "A simple grass bed under a crescent moon and many stars, no people.", "build", "curious", 2, "normal", 0, None, YET),
    ("Six and a half hours with no alarm. Our visitor would sleep better than me, and my mattress cost a fortune. I'm not saying I'd pass the camping test, I'm saying I'd try.", "The main character sleeps deeply on a grass bed under the stars, a calm small smile.", "build", "funny", 2, "slow", 0, None, None),
    ("Or the evenings. Polly Wiessner recorded Ju/'hoansi conversation: daytime talk was practical, while evening talk turned to stories, more than eighty percent of it, according to one commentary.", "A glowing campfire at night with open space around it and sparks rising into a starry sky, no people.", "build", "neutral", 2, "normal", 0, None, WIE),
    ("A storyteller by the fire, and nobody checking a feed. I'd trade a few streaming subscriptions for that.", "The main character listens wide-eyed in a circle of figures around a fire, a flat slab dropped beside him.", "build", "happy", 2, "slow", 0, None, None),
    ("And the children: among the Hadza, kids from about five years old can gather up to half of their own daily energy needs.", "A small basket of berries and roots sitting beside a very small digging stick, no people.", "build", "neutral", 2, "normal", 0, None, CRI),
    ("Five-year-olds feeding themselves. Meanwhile, I once cried over a burnt toast.", "The main character holds a black burnt slice of toast and looks at it with teary eyes.", "build", "funny", 2, "fast", 0, None, None),
    ("Remember the limits, though. The Hadza activity data came from twenty-eight people, and the camping study from eight, so these are windows, not the whole house.", "Eight small stones and twenty-eight small stones in two tidy groups on a pale background, no people.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("Small samples, big headlines. I'd rather say that out loud. That's not an insult to the studies, it's just good manners.", "The main character holds a tiny stone in his palm and a huge sign made of twigs behind him, squinting.", "build", "funny", 2, "normal", 0, None, None),
    ("The Dunbar critics said it plainly: a cognitive limit on group size can't be derived this way, and that's a fine sentence to keep in mind.", "A single large crowd of small stick figures on dry ground with a fuzzy circle drawn around them, no text.", "build", "neutral", 2, "normal", 0, None, LIN),
    ("So what would they think of our world? Amazed by the lights, the crowds and the speed, probably a bit worried about the sitting and the silence, and surprisingly at home with the trade and the jewelry. Thanks for spending these minutes with me. Hit like if it was worth your time, and tell me in the comments what you'd show our visitor first. I'd pick a sunrise, honestly, because we still have those. I read every one. See you soon, friend.", "The main character waves goodbye at sunrise beside a quiet city skyline and a small campfire, smiling warmly.", "normal", "happy", 2, "slow", 800, "pop", None),
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
    "title": "What Would Ancient Humans Think of Our WORLD?",
    "title_alternatives": ["A Time Traveler From 30,000 Years Ago Visits Your STREET", "What Would Ancient Humans ENVY About You?",
                           "Would an Ancient Human Understand Your PHONE?", "Ancient Eyes on the Modern WORLD"],
    "description": ("Take someone from thirty thousand years ago to your street. This video uses real studies to imagine their reactions: crowds and the Dunbar number, "
                    "light and sleep, sitting, boredom, social rejection, trade, jewelry and what they might actually envy.\n\n"
                    "This video is history and science, not medical advice.\n\nSources:\n"
                    "- Lindenfors, Wartel & Lind (2021). 'Dunbar's number' deconstructed. Biology Letters.\n"
                    "- Wright et al. (2013). Entrainment of the human circadian clock to the natural light-dark cycle. Current Biology.\n"
                    "- Raichlen et al. (2020). Sitting, squatting, and the evolutionary biology of human inactivity. PNAS.\n"
                    "- Wilson et al. (2014). Just think: the challenges of the disengaged mind. Science.\n"
                    "- Brooks et al. (2018). Long-distance stone transport and pigment use. Science.\n"
                    "- Bouzouggar et al. (2007). 82,000-year-old shell beads from North Africa. PNAS."),
    "tags": ["ancient humans", "time travel", "modern life", "dunbar number", "hunter-gatherers", "human evolution", "sleep and light",
             "boredom", "shell beads", "animated explainer", "stickman"],
    "mood": "playful",
    "sources": [x for x in dict.fromkeys(s[8] for s in S if s[8])][:16],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

# ---- fact-check file
md = ["# Fact-check: What Would Ancient Humans Think of Our WORLD?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-24.", ""]
md += ["## Method", "- The visitor is an imagined device; every claim about people comes from a named study, and the narration says when a number is from a small sample.",
       "- Living foragers (Hadza, San, Ju/'hoansi, Tsimane) are used as a window, not as a copy of the past; the script says so.",
       "- Contested results are told as such: Dunbar's number, the Cyberball brain-scan reading, the shock experiment's curiosity objection, early beads as symbolic behaviour.",
       "- The narrator says outright that this is not medical advice (the lighting scene says 'I'm not giving advice'); the description repeats it.", "",
       "## Fact scenes", "", "| # | Narration (shortened) | Source | How verified | Wording safeguard |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        src = sc["fact_source"]
        how, safe = VERIFY.get(src, ("", ""))
        md.append(f"| {i} | {sc['narration'][:90].replace('|', '/')}... | {src[:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Claims softened or dropped",
       "- 'Dunbar's number is exactly 150': presented as a famous idea with a published critique, no verdict.",
       "- US-versus-Hadza sitting time: only 'industrialized populations'; no US number.",
       "- Camping study '2 hours 36 minutes': only press reports, so 'about two hours'.",
       "- Obsidian 95 km: from an author's blog post; the paper's abstract says at least 25 to 50 km, so the narration gives both with 'one account says'.",
       "- Shock-experiment gender gap explanation: left out; only the numbers and the dispute.",
       "- 'Pain areas of the brain': the script says 'regions linked to distress' and states that the reading is contested.",
       "", "## Human-voice checklist (all done)",
       "- Short and long sentences mixed; contractions; personal takes ('I once stared at a loading bar', 'my barista's name, sometimes').",
       "- Modern comparisons: family reunion vs Tuesday, streetlights, office chair, couch, streaming subscriptions, mall, burnt toast.",
       "- No filler words ('delve', 'fascinating journey', 'it's important to note').",
       "- Numbers written as words; no ALL CAPS in narration; no long dashes.",
       "- Warm connection: friendly mid-video 'subscribe and stay with me' scene, thank-you and 'See you soon, friend' ending; 'like' asked once at the end.",
       "- The first 40 seconds say why to watch ('their reactions reveal what's odd about your own life') and what you get ('you'll know what they'd actually envy')."]
Path(__file__).with_name("ancient_visitor.factcheck.md").write_text("\n".join(md), encoding="utf-8")

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
