"""Builds scripts/stone_vs_today.json and scripts/stone_vs_today.factcheck.md
(run: ./venv/Scripts/python scripts/stone_vs_today.py).
Eight-round comparison, ~10 minutes, a new anime picture every ~3 s (import with --minutes 10 --seconds-per-image 3).
P(...) adds one hero scene and one fact scene, so hero/fact always alternate. Approved by the owner 2026-10-29."""
import json
from pathlib import Path

VOL = "Volk & Atkinson (2013). Infant and child death in the human environment of evolutionary adaptation. Evolution and Human Behavior 34, 182-192"
IGME = "UN IGME (2024). Levels and trends in child mortality, report 2024 (2023 global under-five mortality 37 per 1,000)"
GUR = "Gurven & Kaplan (2007). Longevity among hunter-gatherers: a cross-cultural examination. Population and Development Review 33, 321-365"
WPP = "United Nations, World Population Prospects 2024 (global life expectancy at birth 73.3 years in 2024)"
DYB = "Dyble et al. (2019). Engagement in agricultural work is associated with reduced leisure time among Agta hunter-gatherers. Nature Human Behaviour 3, 792-796"
RAI = "Raichlen et al. (2017). Physical activity patterns and biomarkers of cardiovascular disease risk in hunter-gatherers. American Journal of Human Biology 29, e22919"
KAP = "Kaplan et al. (2017). Coronary atherosclerosis in indigenous South American Tsimane: a cross-sectional cohort study. The Lancet 389, 1730-1739"
YET = "Yetish et al. (2015). Natural sleep and its seasonal variations in three pre-industrial societies. Current Biology 25, 2862-2868"
HIL = "Hill et al. (2011). Co-residence patterns in hunter-gatherer societies show unique human social structure. Science 331, 1286-1289"
WHO = "WHO Commission on Social Connection (2025). From loneliness to social connection (1 in 6 people lonely; about 871,000 deaths a year linked)"

VERIFY = {
    VOL: ("Searched 2026-10-29; paper record (Evolution and Human Behavior 34(3)) and Yale HRAF hypothesis notes: 20 hunter-gatherer and 43 historical populations; average infant mortality about 26.8% (death before 1), child mortality about 48.8% (death before 15).",
          "Said as 'about one in four babies', 'close to half before fifteen', 'on average across the groups studied'."),
    IGME: ("Searched 2026-10-29; UNICEF data page and UN IGME 2024 report: global under-five mortality 37 per 1,000 live births in 2023 (range 35-41), about 4.8 million deaths.",
           "'About four in a hundred, worldwide, before age five'; different age cut-offs are said out loud."),
    GUR: ("Searched 2026-10-29; paper PDF on UCSB site (abstract and framing) and secondary discussion: modal age of adult death about seven decades, adaptive life span 68-78; low averages at birth are driven by child deaths; illness is the main cause of death in these groups.",
          "'Around seventy' (modal, not average); the exact 72 figure is not used."),
    WPP: ("Searched 2026-10-29; UN WPP 2024 key messages and press release: global life expectancy at birth 73.3 years in 2024.",
          "'About seventy-three, worldwide average at birth'; the narration notes it is a different measure from the forager modal age."),
    DYB: ("Searched 2026-10-29; Cambridge University release and Nature Human Behaviour abstract: Agta adults about 24 h/week out-of-camp work, 20 h domestic chores, 30 h daylight leisure; mostly-farming camps about 30 h/week out-of-camp work vs about 20 h for foragers; women in farming camps had about half the leisure; co-author warns against extrapolating to prehistory.",
           "'About twenty hours', 'one group in the Philippines', the caution is said."),
    RAI: ("Searched 2026-10-29; AJHB abstract: 46 Hadza adults with heart-rate monitors, about 135 minutes a day of moderate-to-vigorous activity; press releases give a lower ~75-minute figure.",
          "'Over two hours a day, by heart-rate monitor'; compared with the 150 minutes a week guideline."),
    KAP: ("Searched 2026-10-29; Lancet abstract via repositories and TCTMD/CBC coverage: 705 Tsimane adults, 85% had a coronary calcium score of zero, the lowest of any population recorded; observational; high burden of infection and intestinal worms, most common age of death about 70.",
          "'Lowest ever measured', 'this is a link, not proof', the worms are said."),
    YET: ("Searched 2026-10-29; Current Biology highlights, UCSB PDF and UCLA release: Hadza, San and Tsimane, 94 people with wrist monitors, 5.7-7.1 hours of sleep, sleep onset about 3.3 h after sunset; insomnia so rare that San and Tsimane have no word for it.",
          "'Between about six and seven hours', 'no word for it in two of the groups'."),
    HIL: ("Searched 2026-10-29; Science abstract via PubMed and ASU coverage: 32 foraging societies, about 5,000 people, average band about 28 adults, most band members not close genetic relatives.",
          "'About twenty-eight adults', 'most not close relatives'; loneliness in the past is not claimed to be zero."),
    WHO: ("Searched 2026-10-29; WHO Commission page and 30 June 2025 news item: 1 in 6 people worldwide lonely; loneliness linked to about 871,000 deaths a year.",
          "'Linked to', not 'causes'."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None))


BOARD = "A wooden scoreboard made of two flat stones on a hill, one with a cave painting, one with a tiny skyscraper drawing, pebbles stacked under each."

# ================= hook (12 short lines)
P("Half of all Stone Age children never grew up.", "The main character kneels by a small campfire at dusk, gently holding a sleeping baby, looking worried.",
  "Yet many who reached adulthood lived past seventy.", "An old forager couple with grey hair sitting outside a grass hut, smiling, evening light.",
  GUR, "tense", "curious", "hook", hsfx="riser")
P("And they had more free time than you.", "The main character lies in a hammock between two trees, arms behind his head, a modern office tower far away.",
  "Some foragers work about twenty hours a week.", "A forest camp in the Philippines with people resting in the shade near a river, baskets beside them.",
  DYB, "funny", "curious", "hook")
P("So who really lived better? Them, or us?", "The main character stands at a fork in a path, one way leads to a cave, the other to a glowing city.",
  "This matters, because your body was built for their world.", "A human skeleton walking across a golden savanna, a modern city far behind it.",
  KAP, "curious", "serious", "hook", fsfx="whoosh")
P("It may explain why your sleep and stress feel off.", "The main character sits up in a modern bed at night, eyes wide, a phone glowing on the pillow.",
  "By the end, you'll judge eight rounds yourself.", BOARD,
  YET, "serious", "excited", "hook")
P("Sleep, work, friends, hearts, children, and more.", "The main character counts on his fingers in front of a row of eight small stones.",
  "Every number comes from a real study.", "A stack of old research papers tied with string next to a stone axe, top view.",
  HIL, "curious", "neutral", "hook")
P("And one round flips what nearly everyone believes.", "The main character leans close to the viewer and holds a finger to his lips, campfire behind him.",
  "Keep score with me. The final count surprises.", BOARD,
  YET, "whisper", "tense", "hook", fpause=400, fsfx="ding")

# ================= intro: how do we even know?
P("Quick problem first. Nobody filmed the Stone Age.", "The main character holds an old film camera and scratches his head in front of a cave.",
  "There are bones, tools and old campsites, but no diaries.", "Stone tools, a few animal bones and ash from an old hearth on dusty ground, top view.",
  GUR, "curious", "neutral")
P("So how do we know how they lived?", "The main character squints at a cave wall with a magnifying glass, puzzled.",
  "Much of it comes from groups who still forage today.", "A small Hadza camp of dome-shaped grass huts under acacia trees in Tanzania, morning light.",
  RAI, "curious", "neutral")
P("People like the Hadza, the Tsimane and the Agta.", "The main character waves hello to three distant villages: savanna, rainforest and river valley.",
  "Researchers follow them with heart monitors and wrist trackers.", "A wrist activity tracker and a heart-rate chest strap lying on a woven mat.",
  YET, "happy", "neutral")
P("And scientists stress they aren't living ancestors.", "The main character shakes his head while holding an empty wooden picture frame.",
  "They're modern people, with neighbours, trade and even phones.", "A Hadza man in a red cloth sitting under a tree holding a small mobile phone.",
  RAI, "serious", "neutral")
P("Still, they're the closest window we have.", "The main character peeks through a round window made of branches at a distant camp.",
  "I'll tell you which group each number comes from.", "A map-like painted landscape showing a savanna, a rainforest and a river valley side by side.",
  HIL, "curious", "neutral")

# ================= round 1: children
P("Round one. The hardest one. Kids.", "The main character holds up one finger in front of the stone scoreboard, face serious.",
  "Researchers compared twenty hunter-gatherer groups.", "Twenty small campfires scattered across a wide valley at dusk, seen from a hill.",
  VOL, "serious", "neutral")
P("And the numbers are heavy.", "The main character sits quietly by the fire, head lowered.",
  "About one in four babies died before their first birthday.", "A tiny pair of woven grass baby shoes resting on a flat stone, soft evening light.",
  VOL, "sad", "sad", fpace="slow", fpause=500)
P("And it didn't stop at babies.", "The main character watches children playing near a river, looking protective.",
  "Close to half of children didn't reach fifteen.", "A small empty wooden toy canoe drifting on a quiet river under a grey sky.",
  VOL, "serious", "sad", fpace="slow")
P("Childhood itself was the dangerous part of life.", "The main character puts a fur blanket around a coughing child by the fire.",
  "Infections and accidents caused most of those deaths.", "A grass hut at night with a small fire and a bowl of herbs by the doorway.",
  VOL, "serious", "neutral")
P("Today the picture is almost unrecognisable.", "The main character smiles in a bright modern clinic, holding a laughing baby.",
  "Worldwide, about four in a hundred children die before five.", "A modern hospital nursery with rows of small cots and soft blue light.",
  IGME, "happy", "awe")
P("Still too many. But look at that drop.", "The main character holds his hands far apart, amazed.",
  "Child deaths have roughly halved since the year two thousand.", "A long staircase going steeply down a hillside at sunrise.",
  IGME, "awe", "neutral")
P("I think about that every time I complain about a waiting room.", "The main character sits in a clinic waiting room, sighing at a clock, then smiling.",
  "Vaccines, clean water and antibiotics did most of that work.", "A glass of clean water, a vaccine vial and a pill bottle on a white table.",
  IGME, "funny", "neutral", hpace="fast")
P("This round isn't close. One point to today.", "The main character drops a pebble under the skyscraper stone on the scoreboard.",
  "Score: today one, Stone Age zero.", BOARD,
  IGME, "excited", "neutral", fsfx="ding")

# ================= round 2: lifespan
P("Round two. You've heard cavemen died at thirty.", "The main character holds a stone tablet with a big crossed-out circle carved on it, grinning.",
  "That idea comes from averages at birth.", "A pile of pebbles heaped at the left end of a long wooden plank, another pile far to the right.",
  GUR, "funny", "curious")
P("And it's mostly a maths trick.", "The main character juggles pebbles, raising an eyebrow.",
  "When many babies die, the average age at death drops.", "A balance scale tipped down by many tiny pebbles on one side.",
  GUR, "curious", "neutral")
P("Even if plenty of adults live long lives.", "The main character points at a grey-haired elder telling a story by the fire.",
  "So scientists look at adults instead.", "A circle of adult foragers of different ages sitting on logs around a fire.",
  GUR, "neutral", "neutral")
P("If you survived childhood, what happened next?", "The main character walks along a long path marked with stones, getting older step by step.",
  "The most common age for adults to die was around seventy.", "An old forager man with a walking stick teaching two children to twist string.",
  GUR, "curious", "awe", fpause=400)
P("Honestly, that one surprised me.", "The main character stares wide-eyed at an elder, jaw dropped.",
  "Today's world life expectancy at birth is about seventy-three.", "A big city park full of elderly people doing slow exercises together in the morning.",
  WPP, "awe", "neutral")
P("Not a perfect comparison. Different measures.", "The main character holds two different measuring sticks side by side, frowning.",
  "And infections were the main killer of adults back then.", "A person resting under animal skins inside a grass hut at dawn.",
  GUR, "serious", "serious")
P("Closer than you'd think, but today still wins.", "The main character places a second pebble under the skyscraper stone and shrugs.",
  "Score: today two, Stone Age zero.", BOARD,
  WPP, "neutral", "neutral", fsfx="ding")

# ================= round 3: free time
P("Round three. Free time.", "The main character sits at a desk buried in paper piles, rubbing his eyes.",
  "In twenty nineteen, a team studied the Agta of the Philippines.", "A river valley in the Philippines with bamboo huts and canoes pulled onto the bank.",
  DYB, "curious", "neutral")
P("This is the round Stone Age fans love.", "The main character rubs his hands together with a mischievous grin.",
  "They recorded what each adult did, hour by hour.", "A notebook, a pencil and a wristwatch on a bamboo floor, top view.",
  DYB, "excited", "neutral")
P("Here's what made it clever.", "The main character taps his temple, smiling.",
  "Some Agta camps still mostly forage. Others now farm rice.", "A forest camp with fishing spears on one side and a small rice field on the other.",
  DYB, "curious", "neutral")
P("Same people, different jobs.", "The main character holds a fishing spear in one hand and a rice sickle in the other.",
  "Foragers did about twenty hours of outside work a week.", "A small stack of stones beside a fishing spear on a riverbank.",
  DYB, "neutral", "awe")
P("Farmers? Noticeably more.", "The main character wipes sweat while bending over in a rice field.",
  "Farmers did about thirty hours a week.", "A taller stack of stones beside a rice sickle in a muddy field.",
  DYB, "funny", "neutral")
P("And women in farming camps lost the most.", "The main character watches a woman carry heavy rice bundles, looking sympathetic.",
  "In the most farming-heavy camps, about half their leisure was gone.", "Rice bundles stacked high next to an empty hammock.",
  DYB, "serious", "serious")
P("So what did the free time look like?", "The main character lounges on a riverbank, curious, chewing a grass stem.",
  "The average adult had about thirty hours of daylight leisure a week.", "People resting in the shade, chatting and weaving baskets beside a calm river.",
  DYB, "curious", "happy")
P("Now compare that with your inbox at ten p.m.", "The main character sits at a laptop late at night, surrounded by coffee cups, sighing.",
  "Or with a long commute, twice a day.", "A crowded city train at rush hour with tired passengers holding rails.",
  DYB, "funny", "neutral", hpace="fast")
P("I'll wait.", "The main character taps his foot, arms crossed, smirking at the viewer.",
  "The authors do warn us about one thing.", "A single footprint in mud next to a large area of unknown dark ground, top view.",
  DYB, "funny", "serious")
P("One modern group can't speak for all of prehistory.", "The main character holds up one small stone against a giant mountain, thoughtful.",
  "And farming, not phones, started this squeeze.", "An early farming village with fields, granaries and people bent over crops.",
  DYB, "serious", "neutral")
P("Fair enough. One point to the Stone Age.", "The main character drops a pebble under the cave-painting stone on the scoreboard, smiling.",
  "Score: today two, Stone Age one.", BOARD,
  DYB, "happy", "neutral", fsfx="ding")

# ================= round 4: movement
P("Round four. Moving your body.", "The main character stands up from an office chair, stretching his back with a groan.",
  "Scientists fitted forty-six Hadza adults with heart-rate monitors.", "A Hadza woman digging for roots with a stick, a heart monitor strap on her chest, dry grass around.",
  RAI, "funny", "curious")
P("Brace yourself, office workers. I'm one of you.", "The main character salutes a row of tired office workers at desks.",
  "They tracked them through normal days of foraging.", "Hadza men walking in single file across a wide savanna at sunrise, bows on their shoulders.",
  RAI, "funny", "neutral")
P("The result made me look at my step counter in shame.", "The main character stares at a smartwatch, shoulders slumped.",
  "They averaged over two hours a day of moderate to hard activity.", "A Hadza woman carrying a heavy bundle of firewood up a dusty slope.",
  RAI, "funny", "awe", fpause=400)
P("My record day was a trip to the fridge and back.", "The main character walks to a glowing fridge in slippers at night.",
  "Health guidelines ask for about two and a half hours a week.", "A pair of running shoes next to a calendar-like row of seven pebbles.",
  RAI, "funny", "neutral", hpace="fast")
P("A day for them. A week for us.", "The main character holds one pebble in one hand and seven pebbles in the other, amazed.",
  "And activity stayed high across their whole lifespan.", "An elderly Hadza woman striding along a path with a digging stick.",
  RAI, "awe", "neutral")
P("That's the part that impressed me most.", "The main character watches an old woman stride past him uphill, mouth open.",
  "Grandparents still walked, dug and carried every day.", "An old Hadza man carrying a gourd of water back to camp at sunset.",
  RAI, "awe", "neutral")
P("Easy point. Stone Age.", "The main character drops a pebble under the cave-painting stone, then stretches his back again.",
  "Score: two each.", BOARD,
  RAI, "excited", "neutral", fsfx="ding")

# ================= subscribe
P("Quick break before round five. If you're keeping score with me, subscribe and stay for the rest.",
  "The main character sits by the scoreboard stones and waves warmly at the viewer, campfire glowing.",
  "Two rounds each so far, and the hardest ones are still ahead.", BOARD,
  RAI, "happy", "excited")
P("We'll keep comparing their world and ours together. It's free, and it really helps.",
  "The main character holds a glowing campfire torch and smiles, inviting the viewer to sit down.",
  "Round five takes us to the Bolivian rainforest.", "A wide river winding through dense green rainforest in Bolivia, morning mist.",
  KAP, "happy", "curious")

# ================= round 5: heart
P("Round five. Your heart.", "The main character puts a hand on his chest and listens, eyebrows raised.",
  "Doctors scanned the hearts of seven hundred and five Tsimane adults.", "A riverside village in the rainforest with thatched houses and a small wooden boat.",
  KAP, "curious", "neutral")
P("The muscle that never gets a day off.", "The main character lies on a sofa, then sits up as his chest glows softly.",
  "The Tsimane farm, fish and hunt for most of their food.", "A man fishing with a bow from a canoe on a brown jungle river.",
  KAP, "funny", "neutral")
P("No cars. No lifts. They walk and paddle everywhere.", "The main character paddles a dugout canoe down a jungle river, sweating and smiling.",
  "The scans looked for calcium in the heart's arteries.", "A clean glowing red heart with smooth open blood vessels, simple medical drawing without labels.",
  KAP, "happy", "curious")
P("And the result was startling.", "The main character leans toward a glowing heart drawing, eyes wide.",
  "Eighty-five percent had no calcium build-up at all.", "A row of glowing healthy hearts floating above a rainforest village at dusk.",
  KAP, "tense", "awe", fpause=500, fsfx="impact")
P("The lowest levels ever measured in any population.", "The main character claps slowly, impressed.",
  "Even many of the oldest people had clean arteries.", "An elderly Tsimane woman weaving a palm-leaf roof outside her house.",
  KAP, "awe", "neutral")
P("Before anyone sells a miracle jungle diet, there's a catch.", "The main character holds up a hand to stop a salesman carrying a basket of jungle fruit.",
  "About two-thirds carry intestinal worms.", "A muddy riverbank path and a simple clay water pot under a cloudy sky.",
  KAP, "funny", "serious", hpace="fast")
P("And infections are common there.", "The main character looks worried at a muddy puddle near a hut.",
  "The authors pointed to activity, low blood fat and almost no smoking.", "A fishing net, a bowl of fish and plantains and a walking stick on a wooden table.",
  KAP, "serious", "neutral")
P("It's a link, not proof. Still, those scans are hard to ignore.", "The main character drops a pebble under the cave-painting stone, nodding.",
  "Score: Stone Age three, today two.", BOARD,
  KAP, "serious", "neutral", fsfx="ding")

# ================= round 6: sleep (the loop)
P("Round six. Sleep. The round I promised.", "The main character lies on a grass bed under the stars, eyes open, looking up.",
  "Everyone assumes our ancestors slept long, blissful nights.", "A night sky full of stars above a quiet camp of grass huts, a dim fire.",
  YET, "whisper", "curious", hpace="slow")
P("Nine hours, maybe ten. No alarm clock.", "The main character snores happily in a cave, a tiny smashed alarm clock beside him.",
  "So in twenty fifteen, researchers checked.", "Three small sleeping camps side by side: a savanna, a desert and a rainforest, all at night.",
  YET, "funny", "curious")
P("Wrist trackers, ninety-four people, three groups.", "The main character fastens a tiny tracker to his wrist by firelight, curious.",
  "The Hadza, the San and the Tsimane, on two continents.", "A San camp in the Kalahari desert at night with a small fire and grass shelters.",
  YET, "curious", "neutral")
P("Ready for it?", "The main character leans toward the camera, holding his breath.",
  "They slept only about six to seven hours a night.", "A sleeping forager under a starry sky, a low fire glowing, quiet savanna.",
  YET, "tense", "awe", fpause=600, fsfx="impact")
P("The same as many of us. Or even less.", "The main character sits up in bed, shocked, holding the tracker close to his face.",
  "They fell asleep about three hours after sunset.", "A sunset over the savanna with people still talking around a fire.",
  YET, "excited", "neutral")
P("Up late talking by the fire. Like us with our shows.", "The main character laughs with friends around a campfire late at night.",
  "But here's the twist inside the twist.", "A calm night camp with a cool breeze moving the leaves.",
  YET, "funny", "tense")
P("My favourite fact in this whole video.", "The main character holds up one finger, grinning.",
  "Insomnia was so rare the San and Tsimane have no word for it.", "A peaceful sleeping person on a grass bed, a cool night breeze, stars above.",
  YET, "happy", "awe", fpause=500)
P("Same hours. Much better sleep.", "The main character sleeps soundly on a grass bed, smiling.",
  "The night-time drop in temperature seems to help time their sleep.", "A night sky with stars over a camp, mist settling low on the cool grass.",
  YET, "neutral", "curious")
P("Something our heated bedrooms quietly remove.", "The main character fans himself in a hot modern bedroom, kicking off the blanket.",
  "Their nights also had no screens and no street lights.", "A dark savanna at night lit only by stars and one small campfire.",
  YET, "funny", "neutral")
P("I'd always believed the opposite. So I'm calling it a draw.", "The main character places one pebble on top of both scoreboard stones at once, laughing.",
  "Score: Stone Age three, today two, one draw.", BOARD,
  YET, "funny", "neutral", fsfx="ding")

# ================= round 7: friends
P("Round seven. Friends.", "The main character holds a phone in a dark apartment, scrolling through contacts, lonely.",
  "Researchers studied thirty-two foraging societies.", "Many small camps spread across different landscapes, seen from a mountaintop at sunset.",
  HIL, "sad", "curious")
P("Be honest. Who would you call at two a.m.?", "The main character hesitates over a phone, thumb hovering, at night.",
  "Around five thousand people, in total.", "A large gathering of foragers trading and talking at a river crossing.",
  HIL, "sad", "neutral")
P("You'd think a band was one big family.", "The main character draws a family tree in the sand with a stick.",
  "An average band had about twenty-eight adults.", "A circle of about thirty people sitting around a big fire, sharing food.",
  HIL, "curious", "neutral")
P("Surprisingly, most weren't close relatives at all.", "The main character shakes hands with a stranger at the fire, both grinning.",
  "Friendship and sharing held the group together.", "Two hunters from different families sharing meat from one basket, laughing.",
  HIL, "happy", "happy")
P("Today we have more contacts than ever.", "The main character sits on a sofa, a huge cloud of tiny contact bubbles floating above him.",
  "Hundreds of names in our phones, group chats that never sleep.", "A glowing phone on a table buzzing with dozens of tiny notification bubbles, no letters.",
  WHO, "neutral", "neutral")
P("And somehow, more silence.", "The main character sits alone at a kitchen table, phone face-up, no messages.",
  "In twenty twenty-five, the World Health Organization reported on loneliness.", "A city at night with one lit window in each tall building, one person in each.",
  WHO, "sad", "serious", fpace="slow")
P("I find this the saddest round.", "The main character stares out of a rainy window, quiet.",
  "About one in six people worldwide feel lonely.", "Six empty park benches in a row, one with a lone person sitting on it, autumn leaves.",
  WHO, "sad", "serious")
P("And it isn't only a feeling.", "The main character puts a hand on his chest, thoughtful.",
  "The WHO links loneliness to about eight hundred and seventy thousand deaths a year.", "A long empty park bench under a streetlamp, autumn leaves on the ground.",
  WHO, "serious", "serious")
P("Loneliness wasn't zero back then, of course.", "The main character watches a man walk away from a camp alone into the hills.",
  "People could be pushed out of a group.", "A lone figure walking away from a distant camp at dusk.",
  HIL, "serious", "neutral")
P("But this point goes to the campfire.", "The main character drops a pebble under the cave-painting stone, then looks at his phone.",
  "Score: Stone Age four, today two, one draw.", BOARD,
  HIL, "happy", "neutral", fsfx="ding")

# ================= round 8: sickness
P("Round eight. Getting sick.", "The main character sneezes into his hand by the fire, others stepping back.",
  "Among foragers, illnesses caused most deaths.", "A grass hut at dawn, a person resting inside under animal skins, a small bowl of herbs.",
  GUR, "tense", "serious")
P("With the score this close, this one decides the game.", "The main character grips a pebble tightly, sweating.",
  "Mostly infections, like pneumonia and stomach bugs.", "A rainforest village with a puddle of brown water and mosquitoes above it.",
  GUR, "tense", "neutral")
P("No antibiotics. No modern surgery.", "The main character looks at a small cut on his leg, worried, a leaf bandage in hand.",
  "The Tsimane study also found heavy infection, despite clean hearts.", "A simple clay pot of river water next to a fire, steam rising.",
  KAP, "serious", "neutral")
P("A simple wound or a bad tooth could turn deadly.", "The main character holds his swollen cheek, wincing beside the fire.",
  "Today, child deaths fell mostly through vaccines and medicine.", "A modern pharmacy shelf with neat rows of medicine boxes without labels.",
  IGME, "serious", "neutral")
P("Today, a scratch is a plaster and a shrug.", "The main character in a modern kitchen sticks a plaster on his finger and shrugs.",
  "And an infection is often a short course of pills.", "A small pill bottle and a glass of water on a kitchen counter, morning light.",
  IGME, "funny", "neutral")
P("Point to today. And that's the last round.", "The main character drops a pebble under the skyscraper stone, triumphant.",
  "Let's count.", BOARD,
  IGME, "excited", "excited", fsfx="riser")

# ================= final score and ending
P("Stone Age: four.", "The main character stands beside the scoreboard, pointing at four pebbles under the cave stone.",
  "Free time, movement, hearts and friends.", "Four warm scenes in one painting: a hammock, a walking hunter, a glowing heart and a campfire circle.",
  HIL, "awe", "neutral", hpause=400, hsfx="impact")
P("Today: three.", "The main character points at three pebbles under the skyscraper stone.",
  "Children, lifespan and medicine. And one draw for sleep.", BOARD,
  IGME, "awe", "neutral", fpause=600)
P("So who lived better?", "The main character sits by a campfire with a phone face-down beside him, thinking.",
  "Their world gave more time, more movement and more people around the fire.", "A Stone Age camp at sunset with people talking, children playing and a fire burning.",
  DYB, "serious", "serious", hpace="slow")
P("Here's my honest answer.", "The main character looks straight at the viewer, calm and warm.",
  "Our world keeps far more children alive.", "A modern hospital at sunrise with parents carrying a baby out of the door.",
  IGME, "serious", "happy")
P("They often had better days. We have better odds of seeing tomorrow.", "The main character stands between a cave and a city at sunset, smiling.",
  "Researchers who study this mismatch rarely say go back.", "A Stone Age camp and a modern city side by side in one landscape, soft sunset.",
  GUR, "awe", "neutral", hpause=400)
P("Me? I'd keep the antibiotics and the hot showers.", "The main character in a towel gives a thumbs up from a steamy bathroom.",
  "The interesting question is what we lost by accident.", "A modern family walking barefoot on grass in a city park at sunset.",
  DYB, "funny", "curious")
P("And I'd steal their free time, their walks and their friends.", "The main character walks in a park with friends, phone in his pocket, laughing.",
  "Those three showed up again and again in the studies.", "A group of friends sitting around a small fire in a city backyard at night.",
  RAI, "happy", "neutral")
H("Thank you for keeping score with me all the way to the end. If it was worth your time, hit like, and tell me in the comments which round you'd hand to the Stone Age. I read every one. Next time, we'll find out what ancient humans ate when the hunt failed. See you there, friend.",
  "The main character waves goodbye beside the scoreboard stones at sunset, a campfire glowing next to him.", "happy", pace="slow", pause=800, sfx="pop")

# ---- build
EMOS = ["curious", "neutral", "serious", "tense", "excited", "happy", "awe", "funny"]
scenes, problems, last = [], [], []
hook_n = sum(1 for s in S if s[2] == "hook")
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, src) in enumerate(S):
    hero = i % 2 == 0
    if ("the main character" in prompt.lower()) != hero:
        problems.append(f"scene {i + 1} kind mismatch: {narr[:50]}")
    if not hero and not src:
        problems.append(f"scene {i + 1} fact without source")
    if len(prompt.split()) > 40:
        problems.append(f"scene {i + 1} prompt too long ({len(prompt.split())} words)")
    if emo is None or last[-3:] == [emo] * 3:
        emo = next(e for e in EMOS if e != (last[-1] if last else None) and last[-2:].count(e) < 2)
    last.append(emo)
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
                   "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
                   "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})
for p in problems:
    print("PROBLEM", p)

data = {
    "title": "Stone Age vs Today: Who Really Lived BETTER?",
    "title_alternatives": ["Would You Survive a Week as a Stone Age HUMAN?", "They Worked Less and Moved More. So Why Did We CHANGE?",
                           "Half Their Kids Died, Yet They Had More FREE TIME", "The Stone Age Was Better at FOUR Things",
                           "Stone Age Life vs Modern Life: The Honest SCORE"],
    "description": ("Half of all Stone Age children never grew up, yet many adults lived past seventy and had more free time than we do. "
                    "Eight rounds, real studies of today's hunter-gatherers, and an honest final score.\n\n"
                    "This video is history and science, not medical advice.\n\nSources:\n"
                    "- Volk & Atkinson (2013). Infant and child death in the human environment of evolutionary adaptation. Evolution and Human Behavior.\n"
                    "- UN IGME (2024). Levels and trends in child mortality.\n"
                    "- Gurven & Kaplan (2007). Longevity among hunter-gatherers. Population and Development Review.\n"
                    "- United Nations, World Population Prospects 2024.\n"
                    "- Dyble et al. (2019). Agricultural work and reduced leisure time among Agta hunter-gatherers. Nature Human Behaviour.\n"
                    "- Raichlen et al. (2017). Physical activity patterns in hunter-gatherers. American Journal of Human Biology.\n"
                    "- Kaplan et al. (2017). Coronary atherosclerosis in the Tsimane. The Lancet.\n"
                    "- Yetish et al. (2015). Natural sleep in three pre-industrial societies. Current Biology.\n"
                    "- Hill et al. (2011). Co-residence patterns in hunter-gatherer societies. Science.\n"
                    "- WHO Commission on Social Connection (2025)."),
    "tags": ["stone age vs today", "ancient humans", "hunter gatherers", "prehistoric life", "modern life", "hadza",
             "tsimane", "human evolution", "stone age life", "life expectancy", "stickman", "animated explainer"],
    "mood": "wholesome",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Stone Age vs Today: Who Really Lived BETTER?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-29.", "",
      "## Method",
      "- Every study was found online and its abstract, release or a reliable summary opened; contested points are told as such.",
      "- The video says out loud that modern foragers are not living ancestors and that one group cannot stand for all prehistory.",
      "- No health advice: rounds describe what studies found; the ending says 'borrow the good parts' as scientists' framing, not a recommendation.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- 'Average adult died at 72' (Gurven & Kaplan): only from forum readings, dropped; 'most common age around seventy' used.",
       "- Raichlen 2017 activity: press gave ~75 min/day, abstract ~135 min/day; 'over two hours a day' follows the abstract.",
       "- Agta leisure: one modern group; the authors' caution against extrapolating is in the narration.",
       "- Tsimane hearts: observational, 'a link, not proof'; worms and infection burden stated.",
       "- Violence rates in prehistory: strongly debated, not used as a round.",
       "- 'Scientists say borrow the good parts' is a general framing of the mismatch literature, kept non-specific."]
Path(__file__).with_name("stone_vs_today.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
