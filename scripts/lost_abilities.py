"""Builds scripts/lost_abilities.json and scripts/lost_abilities.factcheck.md
(run: ./venv/Scripts/python scripts/lost_abilities.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

GI3 = "Gislen, Dacke, Kroger, Abrahamsson, Nilsson & Warrant (2003). Superior underwater vision in a human population of sea gypsies. Current Biology 13, 833-836"
GI6 = "Gislen, Warrant, Dacke & Kroger (2006). Visual training improves underwater vision in children. Vision Research 46, 3443-3450"
ILA = "Ilardo et al. (2018). Physiological and genetic adaptations to diving in sea nomads. Cell 173, 569-580"
VEN = "Venkataraman, Kraft & Dominy (2013). Tree climbing and human evolution. PNAS 110, 1237-1242"
SMI = "Smits et al. (2017). Seasonal cycling in the gut microbiome of the Hadza hunter-gatherers of Tanzania. Science 357, 802-806"
SMC = "Comment on 'Seasonal cycling in the gut microbiome of the Hadza hunter-gatherers of Tanzania' (2018). bioRxiv preprint, not peer reviewed"
KAP = "Kaplan et al. (2017). Coronary atherosclerosis in indigenous South American Tsimane: a cross-sectional cohort study. The Lancet 389, 1730-1739"
GU12 = "Gurven, M. et al., Tsimane Health and Life History Project: Social Science & Medicine 75 (2012) 2493-2502 (infections 55 percent of infant deaths); ScienceDaily (2009) report (half of documented deaths from infectious or parasitic disease)"
GUR = "Gurven & Kaplan (2007). Longevity among hunter-gatherers: a cross-cultural examination. Population and Development Review 33, 321-365"
ROS = "Rose et al. (2008). Myopia, lifestyle, and schooling in students of Chinese ethnicity in Singapore and Sydney. Archives of Ophthalmology 126, 527-530"
RO2 = "Rose et al. (2008). Outdoor activity reduces the prevalence of myopia in children. Ophthalmology 115, 1279-1285"
CYB = "CyberTracker Conservation (Louis Liebenberg with the University of Cape Town); Mail & Guardian and News24 reports (2003)"
LIE = "Liebenberg, L. (1990). The Art of Tracking: The Origin of Science. David Philip; Liebenberg et al., papers on tracking as science (the art of tracking 'may well be the origin of science')"
POR = "Porter et al. (2007). Mechanisms of scent-tracking in humans. Nature Neuroscience 10, 27-29"
SCH = "Scholander, Hammel, Hart, LeMessurier & Steen (1958). Cold adaptation in Australian aborigines. Journal of Applied Physiology 13, 211-218"

# how each source was checked (goes into the fact-check file)
VERIFY = {
    GI3: ("Searched 2026-10-24; Current Biology abstract via Lund University and Nature news. 17 Moken and 18 European children aged 7-13; Moken pupils constricted to about 1.96 mm against 2.50 mm and focused to the limit of human performance; European children did not do this. Full text not opened.", "'Squeezed their pupils smaller', numbers as reported; no claim that the effect is genetic."),
    GI6: ("Searched 2026-10-24; Vision Research abstract. After one month of underwater training (11 sessions), then months without practice, European children improved and, tested eight months after the last session, matched the sea-gypsy children's underwater acuity; the improvement is not general contrast sensitivity.", "'After about a month of training', 'tested months later'."),
    ILA: ("Searched 2026-10-24; press coverage of the Cell paper (NYT, NPR, National Geographic, Sci.News, Radboud). Bajau spleens about 50 percent larger than Saluan farmers', also in non-diving Bajau; PDE10A linked to spleen size; the thyroid link rests on mouse work; depth reports of about 70 m; breath-hold times not formally measured, the 13 minutes is one diver's memory; outside researchers wanted larger samples. Paper not opened.", "'About fifty percent', 'researchers think', the 13-minute story is flagged as one person's memory."),
    VEN: ("Searched 2026-10-24; PNAS (PMC3557098), Dartmouth news, National Geographic. Twa of Uganda (vs Bakiga farmers) flex the ankle past 45 degrees while climbing, similar to wild chimpanzees; longer gastrocnemius fibres than farmers; the same fibre pattern in Agta vs Manobo (Philippines); no matching bone signal; the 'practice' idea is a suspicion in press coverage, not a result; authors conclude the upright-walking ankle remains compatible with climbing.", "'Past forty-five degrees', 'the authors argue'; practice is called a suspicion."),
    SMI: ("Searched 2026-10-24; Science listing, Carta and trade coverage. 350 stool samples over more than a year; microbiome cycled yearly with some taxa vanishing and returning; the most seasonal taxa also separated industrialized from traditional populations across 18 populations in 16 countries.", "'Some bacteria vanished and came back'; the critique is stated next."),
    SMC: ("Searched 2026-10-24; bioRxiv comment reanalysing the same 16S data: non-significant differences, seasonal signal driven by one window.", "Labelled a preprint comment, not a refutation; narrator calls the result 'promising, not settled'."),
    KAP: ("Searched 2026-10-24; Lancet abstract via Chapman and PMC, UCSB lab PDF listing. 705 Tsimane aged 40 and over; 596 (85 percent) had no coronary calcium; compared with 6,814 MESA participants; authors call it the lowest reported level of any population to date and suspect traditional diet and high physical activity; 51 percent had high inflammation markers.", "'Lowest reported level', 'suspect'; no health advice; inflammation nuance included."),
    GU12: ("Reused from the Stone Age video: infections 55 percent of Tsimane infant deaths; about half of documented deaths from infectious or parasitic disease.", "Applies to the Tsimane; phrased with 'about half'."),
    GUR: ("Reused from the Stone Age video: modal adult age of death about 72 (68-78) in 21 small-scale societies.", "'Most often died at about seventy-two'."),
    ROS: ("Searched 2026-10-24; PubMed abstract. 124 Sydney vs 628 Singapore children of Chinese ethnicity aged 6-7: myopia 3.3 vs 29.1 percent; outdoor time 13.75 vs 3.05 hours per week, the most significant factor; early schooling pressure also suggested.", "'About nine times'; schooling caveat given."),
    RO2: ("Searched 2026-10-24; Sydney Myopia Study, 1,765 six-year-olds and 2,367 twelve-year-olds: lowest myopia with high outdoor activity, independent of near work.", "Association, not cause; no advice."),
    CYB: ("Searched 2026-10-24; CyberTracker site, Mail & Guardian, News24, Chronicle of Philanthropy. Handheld computer with picture icons for more than forty animals and activities such as drinking, feeding, running, fighting; conservationists in more than thirty countries by 2003 according to one report.", "'According to one 2003 report'."),
    LIE: ("Searched 2026-10-24; CyberTracker material and the Liebenberg papers: the art of tracking by Kalahari San 'may well be the origin of science'.", "Presented as Liebenberg's argument, not settled fact."),
    POR: ("Searched 2026-10-24; Berkeley news release, BPS digest, Discover. 32 volunteers followed a ten-metre chocolate-scented trail blindfolded; 21 of 32 (two thirds) succeeded within three tries; none succeeded with nostrils taped; two nostrils were faster; four trained volunteers about doubled their speed within days.", "'About two thirds', 'four volunteers'; small sample stated."),
    SCH: ("Searched 2026-10-24; DTIC review and later summaries; original paper not opened. Central Australian Aboriginal participants slept on a cold night (air about 3 C) while European controls shivered and raised their metabolic rate; accounts of the set-up differ (fires vs light bags).", "Worded 'reported' and 'a small study from nineteen fifty-eight', no claim that it applies today."),
}

S = [
    # ---------------- hook (12 one-line scenes)
    ("Meet a child who can see clearly underwater.", "The main character swims underwater with eyes wide open, bubbles rising, a seashell on the sand below.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Moken sea nomad children beat European kids underwater.", "A spiral seashell on pale sand under clear blue water, light rays from above, no people.", "hook", "awe", 2, "normal", 0, None, GI3),
    ("So which ancient skills can't you do anymore?", "The main character scratches his head in front of a blank stone wall, thinking hard.", "hook", "curious", 2, "normal", 0, None, None),
    ("Some sea nomads have spleens about fifty percent bigger.", "A simple bean-shaped organ glowing red on a plain pale background.", "hook", "excited", 2, "normal", 0, None, ILA),
    ("Because your body may still hold skills you've never used.", "The main character looks at his own open hands, curious, a soft glow around them.", "hook", "serious", 3, "normal", 0, None, None),
    ("Twa climbers flex their ankles past forty-five degrees.", "A bare ankle and foot pressed flat against a tall tree trunk, close up, rough bark.", "hook", "curious", 2, "normal", 0, None, VEN),
    ("By the end, you'll know which skills you can regain.", "The main character holds up a single finger with a confident grin.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("Eighty-five percent of Tsimane adults had zero coronary calcium.", "A simple heart drawn in clean red on a plain background, glowing softly.", "hook", "tense", 2, "normal", 0, None, KAP),
    ("Is it evolution, or is it simply practice?", "The main character stands at a fork in a dirt path, one way marked by a bone, the other by a footprint.", "hook", "whisper", 2, "slow", 0, None, None),
    ("Kalahari trackers helped build a computer with no words.", "A small handheld computer showing only simple animal pictures as icons, plain background.", "hook", "awe", 2, "normal", 0, None, CYB),
    ("So which skills are gone forever, and which aren't?", "The main character holds a key in one hand and looks at a locked wooden door.", "hook", "tense", 2, "normal", 0, None, None),
    ("And European children learned the same underwater trick.", "A bright swimming pool with light rays under the surface and a few bubbles rising, no people.", "hook", "whisper", 2, "slow", 500, None, GI6),
    # ---------------- sea nomads: eyes, spleen, diving
    ("Let's start at the water, with the Moken, sea nomads who spend much of their lives on boats and islands in the Andaman Sea.", "The main character stands in a small wooden boat near green islands, shading his eyes with one hand.", "build", "curious", 2, "normal", 0, None, None),
    ("In two thousand three, Anna Gislen and colleagues tested seventeen Moken children and eighteen European children, all aged seven to thirteen, on what they could see underwater.", "Two plain white cards with tiny black lines drawn on them lying on a pale seabed under clear water.", "build", "neutral", 2, "normal", 0, None, GI3),
    ("Seventeen kids against eighteen. I can barely read a menu without my glasses, never mind a seashell.", "The main character squints hard at a tiny shell held at arm's length, tongue sticking out.", "build", "funny", 2, "fast", 0, None, None),
    ("Our eyes are built for air, so underwater things blur. The Moken children squeezed their pupils smaller, about one point nine six millimetres against two and a half, and focused as hard as a human eye can. The European children didn't.", "A simple cutaway of an eye with a small round pupil and bent rays of light, plain background.", "build", "curious", 2, "normal", 0, None, GI3),
    ("So is it a special gene? That's what I assumed too. Here's the twist.", "The main character raises one eyebrow and holds up a small DNA spiral, doubtful.", "build", "tense", 2, "normal", 300, None, None),
    ("In two thousand six, Gislen's team gave European children eleven underwater training sessions over about a month. Months later, tested again, they matched the Moken children's underwater sharpness.", "A row of eleven small round stones on a rock above a clear blue pool, plain background.", "punchline", "awe", 3, "normal", 600, "ding", GI6),
    ("A skill we'd call lost wasn't gone. It was just never asked for, like a language you stopped speaking.", "The main character swims confidently underwater holding a pearl-white shell, smiling, bubbles trailing.", "build", "awe", 2, "slow", 0, None, None),
    ("Now the Bajau, sea nomads of Indonesia. Melissa Ilardo scanned their spleens with ultrasound and found them about fifty percent larger than those of neighboring farmers.", "A simple bean-shaped organ drawn large next to a smaller one on a plain pale background.", "build", "curious", 2, "normal", 0, None, ILA),
    ("Fifty percent. Honestly, I couldn't tell you where mine is.", "The main character pokes his belly with a puzzled face, searching for something.", "build", "funny", 2, "fast", 0, None, None),
    ("Even Bajau who don't dive had big spleens, which points to genes. One gene, PDE10A, was linked to spleen size.", "A short ladder of colored DNA blocks with one glowing block, plain background.", "build", "neutral", 2, "normal", 0, None, ILA),
    ("So this one isn't just practice. It's partly written in the family tree. I tried holding my breath in the bath once, gave up at twenty seconds and declared victory.", "The main character studies a simple family tree drawn in chalk on a cave wall, nodding.", "build", "curious", 2, "normal", 0, None, None),
    ("Reports say Bajau divers have been seen going down about seventy metres. But their breath-hold times haven't been formally measured, and the thirteen minutes you may have heard is one diver's memory.", "A rope line dropping from a small wooden boat into deep blue water with a glowing ring far below.", "build", "serious", 2, "normal", 0, None, ILA),
    # ---------------- Twa tree climbers
    ("Now let's go up. A real tree, with honey at the top and a very long way down.", "The main character stands at the foot of a huge tree, craning his neck up, a beehive far above.", "build", "excited", 2, "normal", 0, None, None),
    ("Vivek Venkataraman and colleagues studied the Twa hunter-gatherers of Uganda, who climb tall trees for honey, and compared them with their neighbors, the Bakiga farmers.", "A very tall tree with a thick trunk and a small wild beehive in a high branch, under a bright sky.", "build", "neutral", 2, "normal", 0, None, VEN),
    ("I get nervous on a stepladder changing a light bulb.", "The main character wobbles on a small stepladder holding a round bulb, knees shaking.", "build", "funny", 2, "fast", 0, "boing", None),
    ("The Twa bent their ankles past forty-five degrees while climbing, similar to wild chimpanzees. And their calf muscles had longer fibers than the farmers'.", "A simple lower leg bone meeting a foot bone at a sharp angle, beside a tall tree trunk, plain background.", "build", "curious", 2, "normal", 0, None, VEN),
    ("Longer fibers mean a calf that stretches further. The authors argue that lets a climber keep their body closer to the trunk.", "The main character hugs a tree trunk with both arms and legs, hanging close to the bark, concentrating.", "build", "neutral", 2, "normal", 0, None, None),
    ("In the Philippines, the tree-climbing Agta also had longer calf fibers than their non-climbing neighbors, the Manobo.", "Two simple rope bundles side by side, one clearly longer than the other, plain background.", "build", "neutral", 2, "normal", 0, None, VEN),
    ("And here's the puzzle. The bones showed no matching signal. A skill like that can live entirely in soft tissue, and soft tissue vanishes from the fossil record.", "The main character holds up a clean white leg bone and looks at it, then looks at his own calf, puzzled.", "build", "curious", 2, "normal", 0, None, None),
    ("One press report suggests the fibers may grow with practice. The researchers called that a suspicion, not a result.", "A tall tree with a ladder of small branches going up, plain sky, no people.", "build", "neutral", 2, "normal", 0, None, VEN),
    # ---------------- subscribe (mid-video, hero scene right after a fact)
    ("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep digging into the ancient world together, one odd question at a time. It's free, it takes a second, and it helps other curious people find us.", "The main character waves at the viewer with a warm smile, a small campfire glowing behind him.", "normal", "happy", 2, "normal", 300, None, None),
    # ---------------- gut microbes
    ("Next, something you can't see at all. Smits and colleagues collected three hundred and fifty stool samples from the Hadza over more than a year. Their gut bacteria cycled with the seasons, with some types vanishing and later coming back.", "A simple calendar wheel drawn on a rock with four seasons colored green, gold, brown and blue, no letters.", "build", "curious", 2, "normal", 0, None, SMI),
    ("A seasonal menu for your gut. Mine has two settings: pizza and leftover pizza.", "The main character sits on a log holding a slice of pizza in each hand, grinning.", "build", "funny", 2, "fast", 0, None, None),
    ("The bacteria that cycled most in the Hadza were the same ones that separated industrial from traditional populations, across eighteen populations in sixteen countries.", "Two sets of tiny colorful microbes, one rich and varied and one smaller, side by side on a plain background.", "build", "neutral", 2, "normal", 0, None, SMI),
    ("Now, honesty time. This one's contested, and I'd rather tell you that now than bury it later.", "The main character holds a small cracked clay jar and tilts it, thoughtful.", "build", "serious", 2, "normal", 0, None, None),
    ("A preprint comment reanalyzed the same data and found weaker differences, with the seasonal signal driven by one window, when more meat was available.", "A simple chart with two bars of different heights and a small red circle around the shorter one, no letters.", "build", "neutral", 2, "normal", 0, None, SMC),
    ("So I'd call it promising, not settled. Science that argues with itself is the kind I trust.", "The main character gives a thoughtful thumbs-up beside a scroll with a small dent, smiling.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- Tsimane hearts
    ("Now the heart. Hillard Kaplan and colleagues scanned seven hundred and five Tsimane adults, aged forty and over, in the Bolivian Amazon. Eighty-five percent had no coronary calcium at all.", "A red heart shape with a clean white outline, glowing softly, plain background.", "build", "curious", 2, "normal", 0, None, KAP),
    ("Zero. For most of them. That's not a typo, and the number honestly made me read it twice.", "The main character stares at a big empty zero drawn in the dirt with a stick, stunned.", "build", "awe", 3, "slow", 400, None, None),
    ("The authors called it the lowest level of coronary artery disease reported in any population, and compared it with more than sixty-eight hundred people in a big American study. They suspect diet and a very active life.", "A small clay bowl of tubers and beans beside a path winding through green jungle, no people.", "build", "neutral", 2, "normal", 0, None, KAP),
    ("I'm not a doctor, and this isn't advice. It's just a reminder that a body built for a different life can behave very differently.", "The main character raises both palms in a calm gesture, shaking his head gently, in warm light.", "build", "serious", 2, "normal", 0, None, None),
    ("But the same people face heavy infections. Research on the Tsimane found infections behind about half of the deaths documented.", "A tiny green germ in a magnifying circle on a plain pale background.", "build", "serious", 2, "normal", 0, None, GU12),
    ("So ancient doesn't mean better. It means different, with its own price tags.", "The main character holds a balance scale with a heart on one side and a tiny germ on the other.", "punchline", "serious", 2, "slow", 400, None, None),
    # ---------------- eyes outdoors
    ("Now our eyes. In a two thousand eight study of six and seven-year-olds of Chinese ethnicity, nearsightedness was three point three percent in Sydney and twenty-nine point one percent in Singapore.", "Two simple pairs of eyeglasses side by side, one pair on a small stack, the other pair on a much bigger stack, plain background.", "build", "curious", 2, "normal", 0, None, ROS),
    ("Almost nine times as much. Same ethnicity. So it can't be just genes.", "The main character looks from a tiny stack of glasses to a huge stack, stunned.", "build", "awe", 2, "normal", 0, "riser", None),
    ("The Sydney children spent about fourteen hours a week outdoors, the Singapore children about three. That was the strongest factor, though the authors also pointed to early schooling pressure.", "A wide green field with a bright sun, a small bench and no people, plain horizon.", "build", "neutral", 2, "normal", 0, None, ROS),
    ("I'd love to say I spend my days outside. I spend them staring at a glowing rectangle, and my eyes file a complaint every evening.", "The main character stares cross-eyed at a flat glowing slab held very close to his face.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- tracking
    ("And here's a skill that jumped straight into modern science. Louis Liebenberg worked with San trackers in the Kalahari and helped build CyberTracker, a handheld computer with picture icons, so trackers who don't read could record what they see.", "A small handheld computer with a screen of simple animal icons, resting on warm desert sand.", "build", "curious", 2, "normal", 0, None, CYB),
    ("No words on the screen. Just animals, and what they're doing: drinking, feeding, running, fighting.", "The main character taps a small flat screen with one finger, delighted, a trail of footprints behind him.", "build", "happy", 2, "normal", 0, None, None),
    ("Liebenberg has argued that the art of tracking may well be the origin of science. And by two thousand three, one report said conservationists in more than thirty countries were using the tool.", "A wide world map drawn simply with many small dots glowing, plain background, no letters.", "build", "neutral", 2, "normal", 0, None, LIE),
    ("Trackers read the ground like a living newspaper, and now rangers read the same news. Meanwhile, I can't find my keys in my own house.", "The main character searches under a cushion and inside a boot with a puzzled face, a pile of stuff around him.", "build", "funny", 2, "fast", 0, None, None),
    # ---------------- smell
    ("What about smell? Porter and colleagues laid a ten-metre scent trail in a grass field and asked thirty-two blindfolded volunteers to follow it with their noses alone. About two thirds, twenty-one of them, made it to the end.", "A thin curving trail of dark chocolate drops across a green field with a bright sky, no people.", "build", "curious", 2, "normal", 0, None, POR),
    ("Crawling on a lawn, sniffing chocolate. Honestly, I'd have signed up for free chocolate alone.", "The main character crawls on the grass with a blindfold on, nose down, following a trail.", "build", "funny", 2, "fast", 0, None, None),
    ("Nobody succeeded with their nostrils taped, and two open nostrils were faster than one. Four volunteers who trained roughly doubled their speed within a few days.", "A simple nose drawn large with two nostrils glowing on a plain background, a small arrow pointing at each, no letters.", "build", "neutral", 2, "normal", 0, None, POR),
    ("So smell isn't gone. It's out of practice, like a muscle we stopped asking to work, and honestly it makes me want to go sniff something.", "The main character sniffs a flower with a huge smile, eyes closed, in a sunny meadow.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- cold
    ("Then there's cold. In nineteen fifty-eight, Per Scholander and colleagues tested Aboriginal Australians sleeping on a cold desert night. They reported that the Aboriginal group slept soundly while European volunteers shivered and burned more energy.", "A dry desert at night with a crescent moon, two small embers glowing in the sand, no people.", "build", "curious", 2, "normal", 0, None, SCH),
    ("A small, old study, and the set-up details differ between accounts, so I'd hold it loosely. But it hints our bodies can tune themselves to a harsh life.", "The main character shivers under a thin blanket by a tiny fire, then yawns and smiles, tucked in.", "build", "curious", 2, "normal", 0, None, None),
    ("Back to the sea nomads. Outside researchers have said the spleen finding needs larger samples, and the thyroid explanation comes from mouse studies, not people.", "A single small grey mouse standing beside a tiny scientific balance on a plain background.", "build", "neutral", 2, "normal", 0, None, ILA),
    ("I like that. Scientists saying 'we don't know yet' out loud is a sign they're being straight with us.", "The main character shrugs with a wide honest smile, palms open, beside a cave wall.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- verdict
    ("The Moken study also showed the gain isn't general eyesight. The authors said it wasn't better contrast sensitivity overall. It's a specific trick, learned for a specific job.", "A single pale seashell glowing in clear water with a thin circle of light around it, plain background.", "build", "neutral", 2, "normal", 0, None, GI6),
    ("So here's my sorting of 'lost' abilities. Some are trainable, like underwater vision. Some are inherited, like that spleen. Some are lifestyle, like arteries and eyes. And a few left no trace in bone. Personally, the trainable ones are the part I find most hopeful.", "The main character counts on his fingers, four of them raised, standing in front of a plain stone wall.", "punchline", "curious", 2, "normal", 300, None, None),
    ("Even so, the Tsimane also had high inflammation markers, about half of them, so their lives aren't a recipe for perfect health.", "A simple thermometer with a red level on a stone, plain background.", "build", "neutral", 2, "normal", 0, None, KAP),
    ("Which is why I don't want to romanticize the past. A bad harvest or a bad infection could end a life.", "The main character looks at an empty basket under a gray cloud, worried.", "build", "serious", 2, "slow", 0, None, None),
    ("Across twenty-one small-scale societies, adults who made it through childhood most often died at about seventy-two.", "A tall bundle of many small candles glowing in a dark cave.", "build", "neutral", 2, "normal", 0, None, GUR),
    ("The danger was early. Survive childhood, and an ancient life could stretch out nearly as long as ours.", "The main character gently lights one small candle from another, a warm glow on his face.", "build", "sad", 2, "slow", 300, None, None),
    ("The Sydney Myopia Study, of thousands of children, found the lowest nearsightedness in twelve-year-olds with lots of outdoor time, however much close work they did.", "A wide empty playground field with a bright sun and a lone swing, plain background, no people.", "build", "neutral", 2, "normal", 0, None, RO2),
    ("So the cheapest ancient skill to get back might just be going outside. I'm writing this indoors. I know.", "The main character steps through a doorway into bright sunshine, squinting and grinning, arms wide.", "build", "funny", 2, "normal", 0, None, None),
    ("And the Twa study's authors concluded that the ankle changes tied to walking upright remain compatible with vertical climbing, so we may have kept more of our old toolkit than we thought.", "A simple ankle bone drawn in clean lines next to a small tree branch, plain background.", "build", "neutral", 2, "normal", 0, None, VEN),
    ("So what did we lose? Mostly not abilities, but practice. Some of it is genes, some is lifestyle, and some we'll never know, because it left nothing in bone. Thanks for spending these minutes with me. Hit like if you learned something, and tell me in the comments which of these you'd try first. I read every one. Next time, another strange question from the ancient world. See you soon, friend.", "The main character waves goodbye at sunrise beside a small campfire, a bright sky behind him, smiling warmly.", "normal", "happy", 2, "slow", 800, "pop", None),
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
    "title": "What Could Ancient Humans Do That We CAN'T?",
    "title_alternatives": ["Ancient Skills Your Body Has FORGOTTEN", "Did We Really Lose Our SUPERPOWERS?",
                           "The Children Who See Underwater: SEA Nomads", "Which Human Abilities Are Truly GONE?"],
    "description": ("Meet a child who can see clearly underwater. This video asks what ancient and traditional lifestyles could do that most of us can't: "
                    "sea nomads' vision and spleens, Twa tree climbers, the Hadza gut, the Tsimane heart, Kalahari trackers, scent trails and cold sleeping.\n\n"
                    "This video is history and science, not medical advice.\n\nSources:\n"
                    "- Gislen et al. (2003). Superior underwater vision in a human population of sea gypsies. Current Biology.\n"
                    "- Gislen et al. (2006). Visual training improves underwater vision in children. Vision Research.\n"
                    "- Ilardo et al. (2018). Physiological and genetic adaptations to diving in sea nomads. Cell.\n"
                    "- Venkataraman, Kraft & Dominy (2013). Tree climbing and human evolution. PNAS.\n"
                    "- Smits et al. (2017). Seasonal cycling in the gut microbiome of the Hadza. Science.\n"
                    "- Kaplan et al. (2017). Coronary atherosclerosis in indigenous South American Tsimane. The Lancet."),
    "tags": ["ancient humans", "lost abilities", "sea nomads", "bajau", "moken", "hunter-gatherers", "human evolution", "tsimane",
             "cybertracker", "animated explainer", "stickman"],
    "mood": "mysterious",
    "sources": [x for x in dict.fromkeys(s[8] for s in S if s[8])][:16],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

# ---- fact-check file
md = ["# Fact-check: What Could Ancient Humans Do That We CAN'T?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-24.", ""]
md += ["## Method", "- Each claim came from a named, checkable source (peer-reviewed paper, university or news release, major science outlet).",
       "- Where only an abstract or press summary was opened, the claim is worded as 'about', 'roughly' or 'reported', and the file says so.",
       "- Contested results are flagged in the narration itself (gut microbiome comment, spleen sample size, 1958 cold study set-up).",
       "- Anecdotes are labelled as anecdotes (the Bajau 'thirteen minutes' story).",
       "- The narrator says outright that this is not medical advice; the description repeats it.", "",
       "## Fact scenes", "", "| # | Narration (shortened) | Source | How verified | Wording safeguard |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        src = sc["fact_source"]
        how, safe = VERIFY.get(src, ("", ""))
        md.append(f"| {i} | {sc['narration'][:90].replace('|', '/')}... | {src[:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Claims softened or dropped",
       "- Bajau breath-hold times (up to thirteen minutes): only one diver's recollection; stated as such. Dive depth of about seventy metres is a press report.",
       "- The 'nine percent oxygen boost from the spleen': not from the study itself, dropped.",
       "- Moken 'objects under one and a half millimetres': only in a news summary, dropped.",
       "- 'Practice grows the calf fibers': a press suspicion, said to be a suspicion.",
       "- Barefoot and shoe-muscle studies: dropped to avoid repeating the earlier barefoot video.",
       "- Scholander 1958: only secondary descriptions opened, so it is hedged heavily.",
       "", "## Human-voice checklist (all done)",
       "- Short and long sentences mixed; contractions used; personal takes ('I can't find my keys', 'pizza and leftover pizza').",
       "- Modern comparisons: stepladder and light bulb, glowing rectangle, menu without glasses.",
       "- No filler words ('delve', 'fascinating journey', 'it's important to note').",
       "- Numbers written as words; no ALL CAPS in narration; no long dashes.",
       "- Warm connection: friendly mid-video 'subscribe and stay with me' scene, thank-you and 'See you soon, friend' ending; 'like' asked once at the end.",
       "- The first 40 seconds say why to watch ('your body may still hold skills you've never used') and what you get ('you'll know which skills you can regain')."]
Path(__file__).with_name("lost_abilities.factcheck.md").write_text("\n".join(md), encoding="utf-8")

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
