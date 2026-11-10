"""Builds scripts/broken_plans.json and scripts/broken_plans.factcheck.md
(run: ./venv/Scripts/python scripts/broken_plans.py).
Why we make plans we never keep: planning fallacy, intention-behaviour gap, the future self as a stranger,
procrastination, resolutions, if-then plans. ~9.5 minutes, a new anime picture every ~4 s
(import with --minutes 10 --seconds-per-image 4). Concept approved by the owner 2026-11-09.
No health advice; effect sizes told honestly; no human-from-apes content."""
import json
from pathlib import Path

BUE = "Buehler, Griffin & Ross (1994). Exploring the 'planning fallacy'. Journal of Personality and Social Psychology 67, 366-381"
WEB = "Webb & Sheeran (2006). Does changing behavioral intentions engender behavior change? Psychological Bulletin 132, 249-268"
HER = "Hershfield et al. (2011). Neural measures of future self-continuity predict temporal discounting (Stanford/UCLA fMRI study)"
STE = "Steel, P. (2007). The nature of procrastination: a meta-analytic and theoretical review. Psychological Bulletin 133, 65-94"
NOR = "Norcross & Vangarelli (1988-89). The resolution solution: longitudinal examination of New Year's change attempts. J. Substance Abuse"
OSC = "Oscarsson et al. (2020). A large-scale experiment on New Year's resolutions. PLOS ONE 15, e0234097"
GOL = "Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement: a meta-analysis. Adv. Exp. Social Psychology 38; Sheeran et al. (2024) update"
SOH = "Sydney Opera House: planned about 1963 at about A$7 million, opened 1973 at about A$102 million (Flyvbjerg; Classical Music; Architecture & Design)"
MIL = "Milne, Orbell & Sheeran (2002). Combining motivational and volitional interventions to promote exercise. British Journal of Health Psychology 7, 163-184"

VERIFY = {
    SOH: ("Searched 2026-11-09; ArchDaily, Classical Music, Architecture & Design and Planisware histories: estimate about A$7 million and completion around 1963; opened 20 October 1973; final cost about A$102 million (about 14-15x); roof shells forced rebuilds; Utzon resigned 1966.",
          "'About ten years late', 'roughly fourteen times the budget'."),
    BUE: ("Searched 2026-11-09; paper PDF (UF course copy) and summaries: 37 students; thesis predicted 33.9 days, took 55.5 days; about 30% finished within their estimate; "
          "the average 'worst case' (48.6 days) was also too short; outsiders predicting others' tasks are more pessimistic.",
          "'About thirty percent', 'in one classic study'."),
    WEB: ("Searched 2026-11-09; meta-analysis records and Sheeran & Webb 2016 review: 47 experiments; a medium-to-large change in intention (d = .66) led to a small-to-medium change in behaviour (d = .36).",
          "Said as 'a big change in intention bought only a small change in action'; the popular '47% of intenders fail' line is NOT used."),
    HER: ("Searched 2026-11-09; UCLA Health release and Boston Globe/NYU Stern coverage: brain activity when describing yourself in ten years looked less like describing your current self and "
          "more like describing another person (actors); people with the biggest difference chose small immediate rewards more often. Small Stanford sample.",
          "'Looked more like thinking about someone else', 'in a small study'."),
    STE: ("Searched 2026-11-09; Steel 2007 text: procrastination chronically affects some 15-20% of adults (citing Harriott & Ferrari 1996). The 80-95% student figure rests on old sources and is not used.",
          "'Roughly one in six to one in five adults'."),
    NOR: ("Searched 2026-11-09; Oscarsson 2020 literature review describing Norcross & Vangarelli's 200 resolvers: about 40% still successful after six months.",
          "'About four in ten after six months'; the viral '92% fail' figure is not used (no study found)."),
    OSC: ("Searched 2026-11-09; PLOS ONE paper (PMC7725288): 1,066 participants; approach goals ('start doing') 58.9% successful vs avoidance goals ('stop doing') 47.1% after one year.",
          "Exact percentages, framed as one large experiment."),
    GOL: ("Searched 2026-11-09; meta-analysis summaries: 94 independent tests, about 8,000 people, medium-to-large effect (d = .65); a 2024 meta-analysis finds a smaller average effect (d about .27-.36 for behaviour).",
          "'Worked across dozens of studies', the smaller 2024 estimate is said out loud; no 'doubles your success' claim."),
    MIL: ("Searched 2026-11-09; summaries of the study: 248 UK students; of those who also wrote when and where they would exercise, 91% reported doing it within two weeks; self-report. Control-group figure not verified, so not used.",
          "'Ninety-one percent said they did it', self-report mentioned."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source, on_screen)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None, text=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src, text))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None, None))


# ================= hook (12 short lines)
P("Sunday night. You write the perfect plan.",
  "The main character sits at a desk at night writing in a notebook under a warm lamp, rain on the window, determined.",
  "Gym at six. No phone. Finish the big project.",
  "A neat paper checklist pinned to a cork board beside an alarm clock, sneakers and a laptop, warm lamp light.",
  BUE, "curious", "excited", "hook", hsfx="click")
P("By Wednesday, the plan is gone.",
  "The main character lies on a sofa scrolling his phone, the notebook forgotten on the floor, evening light.",
  "Scientists asked students to predict their own deadlines.",
  "University students writing estimates on paper in a lecture hall, a big calendar on the wall.",
  BUE, "funny", "curious", "hook", hpace="fast", hsfx="boing")
P("Only about thirty percent finished on time.",
  "The main character stares in shock at a calendar full of crossed-out dates, rain outside.",
  "The rest blew past their own deadline by weeks.",
  "A desk calendar with many pages torn off and flying away in the wind, papers scattered.",
  BUE, "tense", "serious", "hook", text="30%")
P("If your plans keep dying, this is about you.",
  "The main character looks straight at the viewer, serious, holding a crumpled to-do list.",
  "And it's not because you're lazy.",
  "An empty chair and desk in a quiet room, a half-finished notebook glowing under a lamp.",
  WEB, "serious", "serious", "hook")
P("By the end, you'll know why plans really fail.",
  "The main character holds a glowing key in front of a locked door shaped like a calendar.",
  "And one simple trick that worked across dozens of studies.",
  "Dozens of small glowing notebooks floating in a dark library, each with a tiny light.",
  GOL, "curious", "excited", "hook")
P("Strange part? Your brain treats future you like a stranger.",
  "The main character faces an older version of himself standing in fog, both looking unsure.",
  "Scientists saw it inside a brain scanner.",
  "A person lying in a white brain scanner in a quiet hospital room, blue monitor glow.",
  HER, "whisper", "tense", "hook", fsfx="riser")

# ================= 1. the planning fallacy
P("So let's start with the biggest lie we tell ourselves.",
  "The main character points at his own reflection in a rainy window, half smiling.",
  "In nineteen ninety-four, researchers studied students writing their final thesis.",
  "A university library at night with students typing on laptops among tall shelves.",
  BUE, "curious", "neutral")
P("Simple question. When will you finish?",
  "The main character holds a pen over a form, thinking hard, chewing the pen.",
  "On average, they guessed about thirty-four days.",
  "A wall calendar with thirty-four days circled in green, a coffee cup in front.",
  BUE, "neutral", "neutral", text="34 DAYS")
P("Sounds reasonable. Very confident.",
  "The main character puffs out his chest, holding up a calendar proudly.",
  "It actually took them about fifty-five days.",
  "The same calendar with fifty-five days circled in red, many cold coffee cups around it.",
  BUE, "funny", "awe", fpause=500, text="55 DAYS")
P("Three extra weeks. On their own project.",
  "The main character slumps over a pile of papers, exhausted, rain on the window.",
  "Even their worst-case guess was still too short.",
  "A thermometer-like progress bar drawn on a whiteboard overflowing past its top line.",
  BUE, "sad", "serious")
P("Think about that. The worst case was too optimistic.",
  "The main character laughs nervously, scratching the back of his head.",
  "Psychologists call this the planning fallacy.",
  "A tidy plan on paper next to a messy real desk covered in papers, side by side.",
  BUE, "funny", "neutral")
P("And it's not just students. Think bigger.",
  "The main character stands on a harbour pier at sunset, looking at a city skyline.",
  "The Sydney Opera House was meant to open around nineteen sixty-three.",
  "A grand white sail-shaped opera house on a harbour at sunset, boats on the water.",
  SOH, "curious", "neutral")
P("Planned budget? About seven million dollars.",
  "The main character holds up a small coin purse proudly next to building plans.",
  "It opened in nineteen seventy-three. Ten years late.",
  "An old newspaper-style scene of a crowd and a queen at an opening ceremony by the harbour, no readable text.",
  SOH, "funny", "awe", text="10 YEARS LATE")
P("And the final bill?",
  "The main character covers his eyes, peeking through his fingers.",
  "About one hundred two million. Roughly fourteen times the plan.",
  "A towering stack of banknotes next to a tiny coin purse on a construction table.",
  SOH, "tense", "awe", fpause=500, text="14x")
P("Even geniuses with blueprints fall for it.",
  "The main character looks at a huge rolled blueprint with a sympathetic smile.",
  "The roof shells were too heavy, and parts had to be rebuilt.",
  "Construction cranes lifting huge curved concrete shells over a harbour, workers below.",
  SOH, "neutral", "serious")
P("We picture the best day, every single time.",
  "The main character daydreams of himself working perfectly, a glowing bubble above his head.",
  "We forget the traffic, the tired days, the surprises.",
  "A city street at evening in heavy rain with traffic lights and a crowded bus stop.",
  BUE, "neutral", "neutral")
P("But here's a twist I love.",
  "The main character raises one finger with a sly smile.",
  "When people guessed other people's deadlines, they were more pessimistic.",
  "Two friends at a cafe, one confidently pointing at the other's laptop schedule.",
  BUE, "excited", "curious")
P("So your friend knows your timeline better than you do.",
  "The main character looks at a friend who is holding his calendar and shaking her head.",
  "Outsiders see the past. We only see the plan.",
  "A wall of old sticky notes with dates, some faded, lit by a desk lamp.",
  BUE, "funny", "serious")

# ================= 2. intention-behaviour gap
P("Okay. But what if we just want it more?",
  "The main character clenches his fists with fiery determination in front of a mountain.",
  "Researchers tested that idea in forty-seven experiments.",
  "A research office with many folders and charts spread across a long table.",
  WEB, "excited", "neutral")
P("They made people really want to change.",
  "The main character watches a motivational speaker on a stage with a huge crowd, inspired.",
  "Intentions went up a lot.",
  "A tall glowing bar rising high on a dark chart, bright and dramatic.",
  WEB, "excited", "awe")
P("And the actual behaviour?",
  "The main character holds his breath, waiting, eyes wide.",
  "It moved only about half as much.",
  "A short dim bar next to a tall bright bar on a dark chart.",
  WEB, "tense", "serious", fpause=500)
P("Wanting is not the same as doing.",
  "The main character stands in front of a gym door in the rain, not going in.",
  "Scientists call this the intention behaviour gap.",
  "A wide canyon at sunset with a broken rope bridge between two cliffs.",
  WEB, "serious", "neutral")
P("Motivation is like a bonfire. Big, bright, and gone by morning.",
  "The main character sits by a big bonfire at night, then by cold ashes at dawn.",
  "A big change in what people wanted bought only a small change in what they did.",
  "Morning ashes of a campfire with a thin line of smoke under a grey sky.",
  WEB, "funny", "neutral")
P("I've felt this. Bought the gym membership. Went twice.",
  "The main character holds a shiny gym card and looks at a dusty pair of sneakers.",
  "Sheeran's later review called the gap one of the most stubborn findings in psychology.",
  "A thick academic journal open on a desk next to a cup of tea, rain on the window.",
  WEB, "funny", "serious")
P("Wanting feels like progress. That's the trap.",
  "The main character pats himself on the back while sitting on the sofa, very pleased.",
  "Planning gives a small reward of its own, before any work is done.",
  "A colourful planner full of stickers on a desk, no work started beside it.",
  WEB, "awe", "neutral")
P("So we need something sturdier than motivation.",
  "The main character carries a heavy stone block and sets it down as a foundation.",
  "And the next study shows why the gap exists.",
  "A long dark hallway with a door at the end, light leaking from under it.",
  HER, "serious", "curious")

# ================= 3. the future self is a stranger
P("Remember the stranger in the brain scanner?",
  "The main character leans toward the viewer, whispering, in a dark room.",
  "Scientists asked people to think about themselves now.",
  "A young woman lying in a brain scanner, a monitor showing a glowing brain pattern.",
  HER, "whisper", "neutral")
P("Then about themselves ten years from now.",
  "The main character looks at an older version of himself in a misty mirror.",
  "And then about famous actors they had never met.",
  "A red carpet with blurred celebrities and camera flashes at night.",
  HER, "curious", "neutral")
P("Guess which one future you looked like?",
  "The main character holds up two cards, a mirror and a movie star, unsure.",
  "Thinking of your future self looked more like thinking of someone else.",
  "A glowing brain scan with the same pattern appearing twice, one labelled by a face in fog.",
  HER, "curious", "awe", fpause=600)
P("Your brain treats future you like a stranger.",
  "The main character waves at his older self across a foggy street; the older self doesn't wave back.",
  "People who felt most distant from future selves grabbed small rewards now.",
  "A hand reaching for one candy on a table instead of a big gift box further away.",
  HER, "awe", "serious")
P("Imagine saving for a stranger's retirement.",
  "The main character hands his wallet to a blurry stranger, confused.",
  "That is roughly how the brain scan made future selves look.",
  "Two faces in mist, one sharp and close, one faint and far away, soft blue light.",
  HER, "funny", "neutral")
P("So present you eats the cake. Future you pays.",
  "The main character eats cake happily while his older self in the background holds a bill.",
  "The bigger the distance, the more people chose now.",
  "A long bridge disappearing into fog, a small lantern glowing at the near end.",
  HER, "funny", "serious")
P("Of course you skip the gym. It's for some stranger.",
  "The main character pushes a gym bag toward a blurry stranger, shrugging.",
  "It was a small study. But it fits a lot of what we see.",
  "Three scientists discussing at a whiteboard covered in sketches of faces and arrows.",
  HER, "funny", "neutral")
P("Here's my take. Be kind to the stranger. He's you.",
  "The main character hands a warm cup of tea to his older self on a rainy porch.",
  "Seeing your future self more clearly can make waiting feel worth it.",
  "An old man smiling on a porch in light rain, holding a warm cup, autumn trees behind him.",
  HER, "happy", "neutral")

# ================= subscribe (after a fact, mid-video)
P("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring how the human mind works, one question at a time. It's free, it takes one second, and it helps more curious people find us.",
  "The main character waves warmly at the viewer beside a desk lamp, rain on the window behind him.",
  "Back to it. Next, the habit almost everyone admits to.",
  "A pile of unopened envelopes and a laptop with many open tabs on a messy desk at night.",
  STE, "happy", "curious", fpause=300)

# ================= 4. procrastination
P("Procrastination. The art of tomorrow.",
  "The main character lies on his bed watching videos while a deadline clock ticks on the wall.",
  "Piers Steel reviewed hundreds of studies on procrastination.",
  "A huge stack of research papers on a wooden desk in a quiet library, a lamp glowing.",
  STE, "funny", "neutral")
P("Hundreds of studies. Imagine how long he put that off.",
  "The main character grins and taps a dusty, half-finished pile of papers.",
  "He found roughly one in six adults are chronic procrastinators.",
  "A crowd of commuters at a rainy bus stop, one in six faintly glowing.",
  STE, "funny", "awe", text="1 IN 6")
P("Not once in a while. As a way of life.",
  "The main character lies in a hammock surrounded by sticky notes saying nothing, sighing.",
  "Tasks that feel boring or unclear get delayed most.",
  "A grey, foggy pile of paperwork next to a bright, colourful game controller.",
  STE, "serious", "neutral")
P("We don't avoid the work. We avoid the feeling.",
  "The main character turns away from a glowing, scary-looking laptop as if it were a monster.",
  "The further away a reward is, the weaker it pulls us.",
  "A tiny prize far away at the end of a long road under a stormy sky.",
  STE, "awe", "serious")
P("Ever said I'll start on Monday?",
  "The main character circles Monday on a wall calendar with a big confident smile.",
  "Planners often push the start to a clean date, then the date passes.",
  "A wall calendar with Monday circled several weeks in a row, each circle crossed out.",
  STE, "funny", "neutral")
P("Monday. Then next Monday. Then next month.",
  "The main character flips calendar pages faster and faster, looking guilty.",
  "Every delay feels small. Together they eat whole years.",
  "An hourglass with sand falling over a stack of unopened notebooks, dusk light.",
  STE, "funny", "serious")
P("I once cleaned my whole room to avoid one email.",
  "The main character scrubs a spotless floor while an unopened email glows on a laptop.",
  "Steel found tasks with delayed rewards get pushed back the most.",
  "A calendar with a reward star drawn far away at the end of the month, a long empty road of days.",
  STE, "funny", "serious")
P("If the payoff is far away, the couch wins.",
  "The main character sinks into a giant comfy couch, a tiny distant trophy on a shelf.",
  "And deadlines that feel far away barely feel real at all.",
  "A distant mountain flag almost hidden in fog, a road leading toward it.",
  STE, "funny", "neutral")
P("And that brings us to the most famous broken plan of all.",
  "The main character holds up a party popper with a sheepish face.",
  "New Year's resolutions.",
  "Fireworks over a city skyline at midnight, crowds cheering in the cold.",
  NOR, "curious", "excited", fsfx="pop")

# ================= 5. resolutions
P("January first. New year, new me.",
  "The main character stands on a snowy rooftop at midnight, fireworks behind him, fist raised.",
  "Researchers followed two hundred people who made resolutions.",
  "Two hundred small paper notes pinned on a wall, each with a different goal drawn as an icon.",
  NOR, "excited", "neutral")
P("Six months later, how many were still going?",
  "The main character looks at a calendar flipped to July, sweating in the summer heat.",
  "About four in ten.",
  "Ten small lanterns in a row at night, four still glowing, six gone dark.",
  NOR, "curious", "serious", fpause=400, text="40%")
P("Honestly? Better than I expected.",
  "The main character shrugs and smiles, giving a small thumbs up.",
  "But in twenty twenty, a huge experiment found something more useful.",
  "A large Swedish research team looking at charts on a big screen in a bright office.",
  OSC, "happy", "curious")
P("Over a thousand people. One year. Two kinds of goals.",
  "The main character holds two signs, one with a green arrow, one with a red cross, both without letters.",
  "Goals like start doing something worked for about fifty-nine percent.",
  "A person starting a morning run in light rain on a park path, smiling.",
  OSC, "neutral", "happy", text="59%")
P("And goals like stop doing something?",
  "The main character frowns at a cookie jar, trying hard not to touch it.",
  "About forty-seven percent.",
  "A cookie jar on a kitchen counter at night with one cookie missing.",
  OSC, "curious", "funny", text="47%")
P("Why do so many quit by February?",
  "The main character sits on a snowy bench in February, a crumpled list in his hand.",
  "Vague goals like be healthier give the brain nothing to do.",
  "A blank foggy sign on an empty winter road, no direction visible.",
  OSC, "curious", "serious")
P("Clear goals give it a target.",
  "The main character holds a bright map with one clear path marked by a glowing line.",
  "The approach goals in the study were concrete actions to start.",
  "A neat row of running shoes, a water bottle and a small map on a bench at sunrise.",
  OSC, "excited", "neutral")
P("And here's what most people get wrong after slipping once.",
  "The main character looks at one missed day on a calendar, ready to give up.",
  "In the big resolution experiment, many participants slipped but kept going.",
  "A runner who stumbled getting back up on a wet track at dawn, others running past.",
  OSC, "serious", "neutral")
P("Missing one day isn't failing. Quitting is.",
  "The main character picks up a fallen notebook and dusts it off, determined.",
  "Success was measured after a whole year, not one perfect week.",
  "A calendar with a few empty days but most days ticked, morning light on the desk.",
  OSC, "excited", "happy")
P("Your brain likes a target, not a ban.",
  "The main character aims a dart at a bright target and hits the centre.",
  "Moving toward something beat pushing away from something.",
  "A path leading toward a sunrise, with a closed door left behind in the shadows.",
  OSC, "excited", "awe")

# ================= 6. the fix: if-then plans
P("So what actually works? Here's the trick I promised.",
  "The main character opens a glowing notebook, eager, at a desk in the morning light.",
  "Psychologists call it an if-then plan.",
  "A notebook page with two simple drawn icons connected by an arrow: a clock and running shoes.",
  GOL, "excited", "neutral")
P("Not I will exercise. That's a wish.",
  "The main character waves away a floating cloud-shaped thought, unimpressed.",
  "Instead: if it's seven a.m., then I put on my shoes and walk out.",
  "Running shoes by a front door at seven in the morning, rain stopping, sunrise outside.",
  GOL, "funny", "neutral")
P("When. Where. What. Decided in advance.",
  "The main character pins three cards on a board with a clock, a door and a shoe drawn on them.",
  "Ninety-four experiments tested this idea.",
  "Ninety-four tiny glowing jars in rows on shelves in a dark laboratory.",
  GOL, "serious", "awe", text="94 STUDIES")
P("And the effect was big.",
  "The main character's eyes widen as a chart bar grows in front of him.",
  "People with if-then plans reached their goals far more often.",
  "A mountain trail with more climbers reaching the sunny summit than giving up below.",
  GOL, "excited", "happy")
P("To be fair, a newer review found a smaller effect.",
  "The main character holds up a hand, being honest, a little sheepish.",
  "In twenty twenty-four, the average effect was more modest. Still real.",
  "A researcher comparing two charts on a laptop at night, rain on the window.",
  GOL, "serious", "neutral")
P("One study with students made it very concrete.",
  "The main character sits among students writing on small cards in a classroom.",
  "Students who wrote down when and where they'd exercise:",
  "A small card with a drawn clock and a park bench, held in a student's hand.",
  MIL, "curious", "neutral")
P("Ninety-one percent said they actually did it.",
  "The main character jogs past the camera on a rainy morning, grinning.",
  "That's what they reported themselves, two weeks later.",
  "A park path after rain with joggers in the distance, puddles reflecting the sky.",
  MIL, "awe", "neutral", hpause=400, text="91%")
P("Here's mine. If I pour my morning tea, then I write one page.",
  "The main character pours tea and opens a notebook at a sunny window, smiling.",
  "Linking a new habit to something you already do is what if-then plans are about.",
  "A cup of tea steaming next to an open notebook and a pen on a wooden table at sunrise.",
  GOL, "happy", "neutral")
P("Small. Specific. Tied to a moment.",
  "The main character holds up three fingers, counting, confident.",
  "Plans fail at the moment of choice. If-then plans decide that moment for you.",
  "A clock striking seven above a door that is already open, morning light pouring in.",
  GOL, "serious", "awe")
P("Another one. If I sit on the bus, then I read ten pages.",
  "The main character reads a book on a city bus while rain streaks the window.",
  "The trigger can be a time, a place, or something you already do every day.",
  "A city bus stop in the rain with a person opening a book under the shelter.",
  GOL, "happy", "neutral")
P("And if I feel like quitting, then I do just two minutes.",
  "The main character sets a small kitchen timer and starts working, calm.",
  "Studies also used if-then plans to handle obstacles, not just to start.",
  "A small obstacle stone on a mountain path with a clear way drawn around it.",
  GOL, "serious", "neutral")
P("Why does it work? The decision is already made.",
  "The main character walks past a fork in the road without stopping, calm.",
  "The plan waits for the moment, so willpower doesn't have to.",
  "An alarm clock ringing at sunrise next to neatly prepared clothes and shoes.",
  GOL, "serious", "neutral")

# ================= ending
P("So, why do we make plans we never keep?",
  "The main character sits at his desk at dusk, looking at an old crumpled plan.",
  "We underestimate time.",
  "A sand hourglass running out on a desk, a lamp glowing beside it.",
  BUE, "curious", "serious")
P("We trust motivation too much.",
  "The main character watches a bonfire shrink to embers in the rain.",
  "We treat future us like a stranger.",
  "A foggy street at night with a lone figure under a street lamp.",
  WEB, "neutral", "awe")
P("None of that makes you lazy. It makes you human.",
  "The main character puts a hand on his chest and smiles softly at the viewer.",
  "And small, specific plans beat big promises.",
  "A tiny green sprout growing out of cracked pavement after rain, morning light.",
  GOL, "awe", "happy", hpause=500)
P("I think that's the real lesson.",
  "The main character closes his laptop and looks out at a calm sunrise over the city.",
  "Plans don't fail because people are weak. They fail because they're vague.",
  "A blurry foggy map next to a sharp clear map on a table, morning light.",
  BUE, "awe", "serious")
P("So make yours sharp. One moment. One action.",
  "The main character draws a single clear arrow on a whiteboard, confident.",
  "Clear plans, honest timelines and a kinder view of future you.",
  "Three glowing cards on a desk: a clock, a calendar and a smiling older face.",
  GOL, "excited", "happy")
P("So tonight, write one if-then plan. Just one.",
  "The main character writes a single line on a small card under a warm lamp, rain outside.",
  "Future you is waiting. Be kind to them.",
  "An older version of the hero smiling and waving through a sunlit window.",
  HER, "excited", "happy")
H("Thank you for spending these minutes with me. If this helped, hit like, and tell me in the comments the one plan you'll finally keep. I read every one. Next time, we'll find out why habits are so hard to break. See you there, friend.",
  "The main character waves goodbye at his desk at dusk, a small card with a clock drawing pinned to the wall.",
  "happy", pace="slow", pause=800, sfx="pop")

# ---- build
EMOS = ["curious", "neutral", "serious", "tense", "excited", "happy", "awe", "funny"]
scenes, problems, last = [], [], []
hook_n = sum(1 for s in S if s[2] == "hook")
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, src, text) in enumerate(S):
    hero = i % 2 == 0
    if ("the main character" in prompt.lower()) != hero:
        problems.append(f"scene {i + 1} kind mismatch: {narr[:50]}")
    if not hero and not src:
        problems.append(f"scene {i + 1} fact without source")
    if len(prompt.split()) > 40:
        problems.append(f"scene {i + 1} prompt too long ({len(prompt.split())} words)")
    if beat == "hook" and len(narr.split()) > 12:
        problems.append(f"scene {i + 1} hook line too long ({len(narr.split())} words)")
    if emo is None or last[-3:] == [emo] * 3:
        emo = next(e for e in EMOS if e != (last[-1] if last else None) and last[-2:].count(e) < 2)
    last.append(emo)
    sc = {"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
          "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
          "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause}
    if text:
        sc["on_screen_text"] = text
    scenes.append(sc)
for p in problems:
    print("PROBLEM", p)

data = {
    "title": "Why Do We Make Plans We Never KEEP?",
    "title_alternatives": ["Why Your Plans FAIL (And What Science Says)", "Your Brain Thinks Future You Is a STRANGER",
                           "Why 'Starting Monday' Never WORKS", "The 30% Problem: Why We Never FINISH on Time",
                           "You're Not Lazy. Your Plans Are BROKEN"],
    "description": ("Sunday night you write the perfect plan. By Wednesday it's gone. Only about 30% of students in a classic study finished on time, "
                    "and brain scans suggest we treat our future selves like strangers. Here's why plans fail, and the one simple if-then trick that works across dozens of studies.\n\n"
                    "This video is psychology for education, not medical or professional advice.\n\nSources:\n"
                    "- Buehler, Griffin & Ross (1994). Exploring the planning fallacy. Journal of Personality and Social Psychology.\n"
                    "- Webb & Sheeran (2006). Does changing behavioral intentions engender behavior change? Psychological Bulletin.\n"
                    "- Hershfield et al. (2011). Neural measures of future self-continuity predict temporal discounting.\n"
                    "- Steel (2007). The nature of procrastination. Psychological Bulletin.\n"
                    "- Norcross & Vangarelli (1988-89). The resolution solution.\n"
                    "- Oscarsson et al. (2020). A large-scale experiment on New Year's resolutions. PLOS ONE.\n"
                    "- Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement; Sheeran et al. (2024).\n"
                    "- Milne, Orbell & Sheeran (2002). British Journal of Health Psychology.\n"
                    "- Sydney Opera House history (Flyvbjerg; ArchDaily; Classical Music)."),
    "tags": ["why do we procrastinate", "planning fallacy", "why plans fail", "psychology of motivation", "procrastination",
             "new year's resolutions", "implementation intentions", "future self", "how to keep your plans", "habits", "self improvement", "animated explainer"],
    "mood": "playful",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Why Do We Make Plans We Never KEEP?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-11-09.", "",
      "## Method",
      "- Every study was found online and its abstract, record or a reliable summary opened; contested points are told as such.",
      "- No health or professional advice; the if-then tip is told as what studies tested, with the smaller 2024 estimate said out loud.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- '47% of intenders fail to act': not found in any source, dropped; 'intentions rose a lot, behaviour about half as much' used (d .66 vs .36).",
       "- '92% of resolutions fail': no study found, dropped; Norcross 'about 40% after six months' used.",
       "- '80-95% of students procrastinate': rests on old non-measured sources, dropped; '15-20% of adults chronic' used.",
       "- Milne 2002 comparison groups (often quoted 38%/35%): not verified, dropped; only the 91% self-report is said.",
       "- 'If-then plans double success': not claimed; 'worked across dozens of studies' plus the smaller 2024 estimate.",
       "- Fresh-start effect (Dai et al. 2014): not verified in this search, dropped."]
Path(__file__).with_name("broken_plans.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
