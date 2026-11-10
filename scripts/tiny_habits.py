"""Builds scripts/tiny_habits.json and scripts/tiny_habits.factcheck.md
(run: ./venv/Scripts/python scripts/tiny_habits.py).
Small daily habits and discipline: the 1% math, how much of life is habit, 66 days not 21, the willpower myth,
how disciplined people really win, small wins. ~9.5 minutes, a new anime picture every ~4 s
(import with --minutes 9 --seconds-per-image 4). Concept approved by the owner 2026-11-10. Modern hero, English.
No health advice; limits of each study told honestly; no ancient humans, no human-from-apes content."""
import json
from pathlib import Path

MATH = "Arithmetic illustration: 1.01^365 is about 37.8 and 0.99^365 is about 0.03 (a comparison, not a study)"
WOOD = "Wood, Quinn & Kashy (2002). Habits in everyday life. Journal of Personality and Social Psychology 83, 1281-1297; Wood & Rünger (2016)"
LAL = "Lally, van Jaarsveld, Potts & Wardle (2010). How are habits formed: modelling habit formation in the real world. European Journal of Social Psychology 40, 998-1009"
HAG = "Hagger et al. (2016). A multilab preregistered replication of the ego-depletion effect. Perspectives on Psychological Science 11, 546-573"
HOF = "Hofmann, Baumeister, Förster & Vohs (2012). Everyday temptations: an experience sampling study of desire, conflict and self-control. JPSP 102, 1318-1335"
GAL = "Galla & Duckworth (2015). More than resisting temptation: beneficial habits mediate the relationship between self-control and positive life outcomes. JPSP 109, 508-525"
AMA = "Amabile & Kramer (2011). The Progress Principle. Harvard Business Review Press (about 12,000 diary entries from 238 people)"
IFT = "Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement. Advances in Experimental Social Psychology 38"

VERIFY = {
    MATH: ("Computed: 1.01^365 = 37.78, 0.99^365 = 0.026.", "Said as 'just math', 'a way to picture it', not as a finding."),
    WOOD: ("Searched 2026-11-10; paper PDF on USC site and textbook summaries: hourly beeper diaries from 279 students; about 41% of behaviours habitual (same time and place); "
           "later reviews: about 43-47% of everyday actions repeated almost daily in the same place.",
           "'About four in ten', 'close to half', no exact single number."),
    LAL: ("Searched 2026-11-10; BPS Research Digest, University of Surrey interview with Lally, behavioural-science summaries: 96 volunteers, one daily behaviour for 84 days; "
          "time to reach automaticity averaged about 66 days, range 18 to a modelled 254 days; early repetitions gave the biggest gains; missing one opportunity did not materially affect habit formation.",
          "'About sixty-six days on average', 'up to around eight months, by the researchers' estimate', 'one study'."),
    HAG: ("Searched 2026-11-10; paper records and Discover coverage: 23 labs, 2,141 participants, effect d = 0.04 (95% CI includes zero) vs d = 0.62 in the earlier meta-analysis; debate continues about other task versions.",
          "'Close to zero in this test', 'scientists still argue'."),
    HOF: ("Searched 2026-11-10; JPSP paper (UMN PDF) and Chicago Booth summary: 205 adults with phones reporting desires for a week; high self-control people had as many desires "
          "but felt less conflict and resisted less often, apparently by avoiding tempting situations.",
          "'As many desires', 'resisted less often', 'seem to avoid'."),
    GAL: ("Searched 2026-11-10; PMC4731333 and abstracts: across six studies, beneficial habits mediated the link between self-control and good outcomes (exercise, study, meditation).",
          "'Mostly through habits', 'in these studies'."),
    AMA: ("Searched 2026-11-10; HBS Working Knowledge and summaries: about 12,000 daily diary entries from 238 professionals in 26 teams; progress in meaningful work was the most common feature of their best days; most events were small.",
          "'Small progress', 'at work', the professional sample is noted in the fact-check."),
    IFT: ("See broken_plans.factcheck.md (video #37); mentioned in one line only.", "Points back to the earlier video."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source, on_screen)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None, text=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src, text))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None, None))


# ================= hook (12 short lines)
P("You've heard it takes twenty-one days to build a habit.",
  "The main character marks day one on a wall calendar in his apartment at dawn, full of hope.",
  "Scientists tested it. It's wrong.",
  "A research office with a wall chart of daily tick marks stretching far beyond three weeks, morning light.",
  LAL, "curious", "tense", "hook", fsfx="impact")
P("On average, it took about sixty-six days.",
  "The main character stares at a calendar where day sixty-six is circled in gold, eyebrows raised.",
  "For some people, around eight months.",
  "A long winding road of calendar pages through seasons, summer turning into snowy winter.",
  LAL, "awe", "tense", "hook", text="66 DAYS")
P("If you keep quitting on day ten, this is why.",
  "The main character sits on the floor by an abandoned yoga mat, looking defeated, rain on the window.",
  "And it's not a willpower problem.",
  "An empty gym in the early morning with one light on and a towel left on a bench.",
  HAG, "serious", "serious", "hook")
P("By the end, you'll know how small habits really grow.",
  "The main character waters a tiny plant on his windowsill at sunrise, smiling.",
  "And why disciplined people barely use willpower.",
  "A tidy apartment with running shoes by the door and a phone left charging in another room.",
  HOF, "curious", "excited", "hook")
P("One famous willpower study fell apart in twenty-three labs.",
  "The main character whispers behind his hand, eyes wide, in a dim room.",
  "And skipping one day? That surprised researchers.",
  "A calendar with a long row of ticks and one empty square, a pen lying beside it.",
  HAG, "whisper", "tense", "hook", hsfx="riser")
P("Let's start with the math of tiny steps.",
  "The main character draws a small dot on a whiteboard and taps it with a marker.",
  "One percent. Every day. Watch what happens.",
  "A single glowing step on a dark staircase rising into the sky.",
  MATH, "curious", "excited", "hook")

# ================= 1. the math of 1%
P("One percent sounds like nothing.",
  "The main character holds up a tiny pebble between two fingers, unimpressed.",
  "But multiply one point zero one by itself every day for a year.",
  "A calculator glowing on a desk at night next to a notebook full of ones.",
  MATH, "neutral", "curious")
P("You don't end the year one percent better.",
  "The main character shakes his head slowly, smiling knowingly.",
  "You end it about thirty-seven times better.",
  "A tiny seed beside a towering tree in the same garden, sunrise light.",
  MATH, "curious", "awe", fpause=500, text="37x")
P("Now flip it. One percent worse, every day.",
  "The main character watches a sandcastle crumble slowly at the beach.",
  "After a year you're left with almost nothing.",
  "A melted candle stub on a dark table, a last thin line of smoke.",
  MATH, "tense", "sad")
P("Think of one page of reading a day.",
  "The main character reads a single page of a book on a crowded train, calm.",
  "One page a day is about three hundred sixty-five pages a year.",
  "A neat stack of finished books growing on a shelf, one thin book beside a thick pile.",
  MATH, "neutral", "awe")
P("That's a whole book. From one page.",
  "The main character holds up a finished book proudly at a cafe table.",
  "Ten push-ups a day is over three thousand in a year.",
  "A small tally board on a wall with thousands of tiny marks, morning sun.",
  MATH, "excited", "neutral", text="3,650")
P("Nobody notices day one. Everyone notices day three hundred.",
  "The main character's friends look surprised at how fit and calm he looks, at a park.",
  "Small steps are invisible at first, then suddenly obvious.",
  "A bamboo shoot barely visible in soil next to the same bamboo grown tall months later.",
  MATH, "funny", "awe")
P("To be honest, real life isn't this neat.",
  "The main character shrugs, holding a messy notebook full of crossed-out lines.",
  "This is math, not a study. But it shows how small things stack.",
  "Coins stacking slowly into a tall tower on a wooden desk, one by one.",
  MATH, "neutral", "neutral")
P("The tiny daily choice is the one we ignore.",
  "The main character steps past a skipping rope on the floor without noticing it.",
  "And tiny daily choices make up a big part of every day.",
  "A morning kitchen with coffee brewing, keys on a hook and a phone on the counter.",
  WOOD, "serious", "neutral")

# ================= 2. how much of life is habit
P("How much of your day is on autopilot? Guess.",
  "The main character brushes his teeth half asleep, eyes closed, toothbrush moving by itself.",
  "Researchers gave students watches that beeped every hour.",
  "A student wearing a simple wristwatch writing a short note in a diary on a bus.",
  WOOD, "funny", "neutral")
P("Every beep, write what you're doing and what you're thinking.",
  "The main character jumps as his watch beeps, then scribbles in a notebook.",
  "About four in ten of their actions were habits.",
  "Ten small glowing figures doing daily tasks, four of them highlighted in warm light.",
  WOOD, "funny", "awe", text="40%")
P("Same place. Same time. Almost every day.",
  "The main character sits on the same bench at the same bus stop with the same coffee, rain falling.",
  "Later reviews put it close to half of everyday behaviour.",
  "A city street at morning rush hour, everyone following familiar paths, soft rain.",
  WOOD, "neutral", "neutral")
P("Think about this morning.",
  "The main character wakes up, reaches for his phone and scrolls before even sitting up.",
  "Habits often started with a cue, like a place or a time of day.",
  "A bedside table at dawn with a phone glowing right next to the pillow.",
  WOOD, "curious", "neutral")
P("Wake up. Phone. Scroll. No decision at all.",
  "The main character scrolls half asleep, eyes barely open, morning light.",
  "The same place and time kept triggering the same action.",
  "The same coffee cup on the same counter at the same hour in three different days, side by side.",
  WOOD, "funny", "serious")
P("Half your life runs on habits you never chose.",
  "The main character watches himself scroll his phone in bed like a puppet on strings.",
  "During habits, people often think about something else entirely.",
  "A person driving home at dusk, mind drifting, thought bubbles of dinner and work floating.",
  WOOD, "awe", "neutral")
P("Your brain loves shortcuts. It saves energy.",
  "The main character walks the same way to work without looking up, listening to music.",
  "In habits, people's minds often wandered while their hands kept going.",
  "A person washing dishes at a sink by a rainy window, eyes on the clouds.",
  WOOD, "neutral", "neutral")
P("Which is great news. Habits run without effort.",
  "The main character relaxes as his hands make coffee on their own, smiling.",
  "So the goal isn't more effort. It's better autopilot.",
  "A neat morning routine laid out on a table: water glass, book, running shoes.",
  WOOD, "happy", "excited")

# ================= 3. 66 days, not 21
P("So how long does a new habit take to stick?",
  "The main character looks at his calendar, tapping his chin thoughtfully.",
  "In twenty ten, Phillippa Lally's team followed ninety-six volunteers.",
  "Volunteers of different ages each doing a small daily task: drinking water, a walk, push-ups.",
  LAL, "curious", "neutral")
P("Each person picked one small thing. Every day.",
  "The main character drinks a glass of water first thing in the morning by a sunny window.",
  "A glass of water. A short walk. Some sit-ups.",
  "A glass of water, a pair of walking shoes and a yoga mat in a bright room.",
  LAL, "neutral", "neutral")
P("They rated how automatic it felt. For twelve weeks.",
  "The main character marks a simple slider on a phone app each evening, rain outside.",
  "The habit got easier fastest at the start, then slowly levelled off.",
  "A glowing curve on a chart rising steeply then flattening, like a hill.",
  LAL, "neutral", "awe")
P("And the average time to feel automatic?",
  "The main character holds his breath, eyes on a calendar.",
  "About sixty-six days. Not twenty-one.",
  "A calendar with the sixty-sixth day circled, many days before it ticked.",
  LAL, "tense", "awe", fpause=500, text="66 DAYS")
P("And for some people, much longer.",
  "The main character flips through calendar pages across seasons, from summer to snow.",
  "From eighteen days to around eight months, by the researchers' estimate.",
  "A long timeline across four seasons with a tiny flag far at the end in the snow.",
  LAL, "serious", "neutral", text="18-254")
P("Sixty-six days. That's more than two months.",
  "The main character counts on his fingers, looking slightly worried.",
  "Most people quit long before a habit has time to become automatic.",
  "A path with many abandoned bikes lying on the side near the start, few further along.",
  LAL, "serious", "serious")
P("Quitting at day ten is like leaving before the bread finishes baking.",
  "The main character opens an oven too early and frowns at flat, raw dough.",
  "Early on, each repetition added the most automaticity.",
  "A loaf of bread rising slowly in a warm oven, glowing orange light.",
  LAL, "funny", "awe")
P("Simple habits stuck faster than hard ones.",
  "The main character easily drinks water, then struggles with a heavy barbell, laughing.",
  "Water was quicker to become automatic than exercise for many.",
  "A glass of water next to a heavy dumbbell on a wooden floor, morning light.",
  LAL, "funny", "neutral")
P("Now the part that surprised me most.",
  "The main character leans toward the viewer with a hopeful look.",
  "Missing one day did not really hurt the habit.",
  "A calendar with one empty square among many ticks, a small green sprout growing beside it.",
  LAL, "curious", "awe", fpause=500)
P("I used to think one bad day ruined everything.",
  "The main character throws a planner in the trash after one missed day, then pauses.",
  "That all-or-nothing thinking is what ends many habits early.",
  "A long chain of paper clips with one missing link, still connected on both sides.",
  LAL, "sad", "serious")
P("One missed day isn't failure. Quitting is.",
  "The main character picks up his running shoes after a lazy day, smiling with resolve.",
  "Coming back the next day was what mattered.",
  "A runner tying shoelaces at sunrise after rain, puddles shining on the path.",
  LAL, "excited", "happy")
P("So be patient. The first weeks are the steepest climb.",
  "The main character climbs a steep grassy hill toward a gentle plateau at sunset.",
  "This was one study, and the eight-month figure was a projection.",
  "Researchers looking at a chart with a dotted line extending beyond the measured data.",
  LAL, "serious", "neutral")

# ================= subscribe (after a fact, mid-video)
P("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring how the human mind works, one small step at a time. It's free, it takes one second, and it helps more curious people find us.",
  "The main character waves warmly at the viewer beside a sunny window with a small plant.",
  "Back to it. Now, the biggest myth about discipline.",
  "A cracked stone statue of a muscular figure lifting a weight, moss growing on it.",
  HAG, "happy", "curious", fpause=300)

# ================= 4. the willpower myth
P("You've probably heard willpower is like a battery.",
  "The main character holds a phone with a low battery icon pressed to his chest, tired.",
  "Use it up, and you run out. That was a famous idea.",
  "A battery icon draining from full to empty on a dark background.",
  HAG, "curious", "neutral")
P("Resist cookies in the morning, fail at the gym at night.",
  "The main character resists a plate of cookies, then collapses on the sofa in the evening.",
  "Hundreds of earlier studies seemed to support it.",
  "Stacks of old journals and papers on a professor's desk, lamp light.",
  HAG, "funny", "neutral")
P("Then, in twenty sixteen, scientists tried a big test.",
  "The main character puts on glasses and opens a thick report, serious.",
  "Twenty-three labs. Over two thousand people. The same procedure.",
  "Many university labs on a world map connected by thin glowing lines.",
  HAG, "serious", "awe", text="23 LABS")
P("And the willpower battery?",
  "The main character holds his breath, staring at a sealed envelope.",
  "The effect came out close to zero.",
  "A flat line on a chart where a big bar used to be, quiet office light.",
  HAG, "tense", "awe", fpause=600)
P("Scientists still argue about other versions.",
  "The main character nods, being fair, palms open.",
  "But the simple battery story got much weaker.",
  "A once-bright light bulb flickering dimmer in an empty room.",
  HAG, "neutral", "serious")
P("I believed in the battery for years. Honestly.",
  "The main character sits on a sofa with a dead phone, laughing at himself.",
  "Popular books had made the idea famous around the world.",
  "A bookshop window full of self-help books about willpower, rain on the glass.",
  HAG, "funny", "neutral")
P("Turns out the story was too simple.",
  "The main character tears a page labelled with a battery drawing out of a notebook.",
  "When a big careful test fails, scientists rethink the idea.",
  "Scientists in a meeting room pointing at a chart with a crossed-out battery icon.",
  HAG, "serious", "neutral")
P("So if willpower isn't the secret, what is?",
  "The main character scratches his head in front of a whiteboard full of question marks.",
  "A study that followed people's desires all day had an answer.",
  "A person checking a phone notification about a snack craving on a busy street.",
  HOF, "curious", "curious")

# ================= 5. how disciplined people win
P("Researchers pinged two hundred five adults during the day.",
  "The main character's phone buzzes at a cafe, he looks at it, curious.",
  "Each time: what do you want right now? Are you resisting it?",
  "A phone screen with simple icons of food, sleep and a phone, no words.",
  HOF, "neutral", "neutral")
P("Here's the twist. Disciplined people had just as many desires.",
  "The main character looks at a disciplined friend staring at a cake too, both tempted.",
  "But they fought them less often.",
  "Two people walking past a bakery, one stopping, one already walking on calmly.",
  HOF, "awe", "awe")
P("I find that weirdly comforting.",
  "The main character relaxes on a bench in a park, smiling, phone face down beside him.",
  "Feeling tempted wasn't the problem. Constant fighting was.",
  "A tug of war rope lying loose on grass, no one pulling it, sunny afternoon.",
  HOF, "happy", "neutral")
P("They weren't stronger. They avoided the fight.",
  "The main character walks the long way home to avoid a fast food shop, grinning.",
  "They seemed to stay away from tempting situations in the first place.",
  "A phone left charging in the kitchen while a bedroom stays calm and dark.",
  HOF, "excited", "neutral")
P("No chips in the house. Phone in another room.",
  "The main character places his phone on a shelf in the hallway before bed.",
  "Another set of studies found self-control works mostly through habits.",
  "A neat desk set up the night before with a book open and a pen ready.",
  GAL, "funny", "neutral")
P("One study even followed people after a meditation retreat.",
  "The main character sits cross-legged in a quiet room at sunrise, eyes closed, peaceful.",
  "Those with more self-control built stronger daily habits three months later.",
  "A calm room with a small cushion and a candle, used every morning, soft light.",
  GAL, "neutral", "awe")
P("And the habits, not the struggle, carried them.",
  "The main character rolls out of bed and sits down to meditate without hesitation.",
  "Habits helped explain who reached their goals.",
  "A mountain path with a smooth worn trail where many feet have walked every day.",
  GAL, "happy", "neutral")
P("People with good self-control just had better routines.",
  "The main character jogs past his own house at the same time as yesterday, relaxed.",
  "Their good habits explained much of their success.",
  "A morning routine checklist made of small icons glowing softly on a fridge.",
  GAL, "happy", "awe")
P("Discipline isn't fighting yourself every day.",
  "The main character stands calmly in a quiet room, not struggling with anything.",
  "It's setting things up so the right choice is the easy one.",
  "Running clothes folded on a chair by the bed, alarm clock and water bottle beside them.",
  GAL, "awe", "serious")
P("Here's mine. My gym bag lives by the front door.",
  "The main character picks up a gym bag from beside the front door with a grin.",
  "Small changes to your space change what happens on autopilot.",
  "A front door with a gym bag and umbrella ready beside it, morning rain outside.",
  GAL, "happy", "neutral")
P("And if you want the exact trigger, there's a simple trick.",
  "The main character points to a small card pinned on the wall with a clock and shoe icon.",
  "If-then plans, from my last video, help a habit start on cue.",
  "A notebook page with a clock icon and an arrow pointing to a pair of shoes.",
  IFT, "curious", "neutral")

# ================= 6. small wins
P("One last thing keeps you going. Small wins.",
  "The main character ticks one box on a sticky note and smiles quietly.",
  "Teresa Amabile's team collected about twelve thousand daily diaries.",
  "Stacks of handwritten diary pages on a long office table, warm light.",
  AMA, "excited", "awe", text="12,000")
P("From two hundred thirty-eight people at work.",
  "The main character writes a short note at the end of a workday at his desk.",
  "On their best days, one thing showed up again and again.",
  "A sunny office with a person smiling at a finished task on a screen.",
  AMA, "neutral", "curious")
P("Not big promotions. Not huge breakthroughs.",
  "The main character waves away a giant trophy, smiling.",
  "Simply making progress on meaningful work, even small progress.",
  "A single brick being placed on a growing wall at sunset.",
  AMA, "funny", "awe", fpause=400)
P("Think about your own best day this month.",
  "The main character smiles, remembering finishing a small task at his desk.",
  "Small events made up nearly two thirds of what people reported.",
  "A calendar with many small colourful stickers and only a few big ones.",
  AMA, "curious", "neutral")
P("Usually it's not something huge. It's moving forward.",
  "The main character crosses out one item on a short list, satisfied, rain outside.",
  "Even small steps forward lifted people's mood and motivation.",
  "A person walking up a staircase lit by small warm lights, one step at a time.",
  AMA, "awe", "happy")
P("Small progress makes you feel good. Feeling good keeps you going.",
  "The main character puts a sticky note on a wall that is filling up with ticks, proud.",
  "Most of the events that mattered were small ones.",
  "A wall covered in small colourful notes forming a bright mosaic.",
  AMA, "happy", "neutral")
P("Write one line at night: what moved forward today?",
  "The main character writes one short line in a small notebook before bed, lamp glowing.",
  "Keeping a simple daily record helped the researchers spot these wins.",
  "A small open diary with short lines on each page, a pen and a cup of tea.",
  AMA, "neutral", "neutral")
P("So track tiny wins. A tick on a calendar is enough.",
  "The main character draws a tick on a calendar with a red marker, satisfied.",
  "Seeing progress is part of what keeps people moving.",
  "A long row of ticks on a calendar under a lamp, rain on the window.",
  AMA, "excited", "neutral")

# ================= ending
P("So, how do you actually improve a little every day?",
  "The main character stands at his window at sunrise, coffee in hand, thinking.",
  "Start smaller than feels useful.",
  "A tiny green sprout in a big empty pot on a sunny windowsill.",
  LAL, "curious", "serious")
P("And make it easy to start.",
  "The main character lays out his workout clothes the night before, nodding.",
  "Disciplined people in the studies relied on easy routines, not on struggle.",
  "Clothes, shoes and a water bottle neatly ready by a door at dawn.",
  GAL, "neutral", "neutral")
P("Expect around two months, not three weeks.",
  "The main character pins a calendar with two months highlighted, nodding calmly.",
  "Don't trust a willpower battery. Change your surroundings.",
  "A room arranged so a guitar sits on a stand right next to the sofa.",
  HAG, "neutral", "neutral")
P("Miss a day? Come back tomorrow.",
  "The main character steps back onto his running path after a rainy day off, smiling.",
  "And count every tiny win.",
  "A jar slowly filling with small paper stars on a bedside table.",
  AMA, "happy", "awe")
P("Make it so small you can't say no.",
  "The main character puts on just one running shoe, laughing at how easy it is.",
  "The easiest habits in the study became automatic the fastest.",
  "A single glass of water on a nightstand at sunrise.",
  LAL, "funny", "neutral")
P("Then let the habit grow by itself.",
  "The main character jogs further each week on the same riverside path, seasons changing.",
  "Once a habit is automatic, it costs far less effort.",
  "A riverside path in autumn with a runner moving easily, leaves falling.",
  WOOD, "happy", "awe")
P("Here's my honest take. Motivation starts it. Habits keep it.",
  "The main character puts a hand on his chest and smiles warmly at the viewer.",
  "Small, boring, daily steps are how big changes usually happen.",
  "A mountain trail at sunrise with a long line of footprints leading to the top.",
  WOOD, "awe", "awe", hpause=500)
P("Not ten habits. Just one.",
  "The main character puts nine sticky notes away and keeps one on the mirror.",
  "One small habit at a time is easier to keep.",
  "A single sticky note on a bathroom mirror in the morning light, no text visible.",
  LAL, "funny", "neutral")
P("So pick one tiny thing. Start it tomorrow.",
  "The main character writes one short line on a small card under a warm lamp.",
  "Sixty-six days from now, it might just feel automatic.",
  "A calendar page far in the future with a small gold star, morning light.",
  LAL, "excited", "happy")
H("Thank you for spending these minutes with me. If this helped, hit like, and tell me in the comments the one tiny habit you'll start tomorrow. I read every one. Next time, we'll find out why we're so bad at saying no. See you there, friend.",
  "The main character waves goodbye by his sunny window, a small plant and a calendar full of ticks beside him.",
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
    if beat == "hook" and len(narr.split()) > 10:
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
    "title": "Why Tiny Daily Habits Beat MOTIVATION",
    "title_alternatives": ["The Science of Getting 1% BETTER Every Day", "Why Discipline Is Easier Than You THINK",
                           "It Takes 66 Days, Not 21: The Truth About HABITS", "Disciplined People Don't Use More WILLPOWER",
                           "Small Habits, Big Change: What Science ACTUALLY Says"],
    "description": ("It doesn't take 21 days to build a habit. In one study it took about 66 on average, and for some people around eight months. "
                    "Why tiny daily steps beat motivation, why the willpower battery story fell apart in 23 labs, and how disciplined people really win.\n\n"
                    "This video is psychology for education, not medical or professional advice.\n\nSources:\n"
                    "- Lally et al. (2010). How are habits formed. European Journal of Social Psychology.\n"
                    "- Wood, Quinn & Kashy (2002). Habits in everyday life. Journal of Personality and Social Psychology.\n"
                    "- Hagger et al. (2016). A multilab preregistered replication of the ego-depletion effect. Perspectives on Psychological Science.\n"
                    "- Hofmann et al. (2012). Everyday temptations. Journal of Personality and Social Psychology.\n"
                    "- Galla & Duckworth (2015). More than resisting temptation. Journal of Personality and Social Psychology.\n"
                    "- Amabile & Kramer (2011). The Progress Principle.\n"
                    "- Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement."),
    "tags": ["tiny habits", "how long to form a habit", "66 days habit", "discipline", "self discipline", "willpower",
             "1 percent better every day", "habit formation", "psychology of habits", "consistency", "self improvement", "animated explainer"],
    "mood": "wholesome",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Why Tiny Daily Habits Beat MOTIVATION", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-11-10.", "",
      "## Method",
      "- Every study was found online and its abstract, record or a reliable summary opened; limits and debates are said out loud.",
      "- No health advice: habits are examples (water, walking), never treatment.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- '21 days to form a habit': no scientific basis found; used only as the myth that is tested.",
       "- Lally's 254-day upper figure is a statistical projection beyond the 84-day study; said as 'around eight months, by the researchers' estimate'.",
       "- 'Exactly 43% of behaviour is habit': sources give 41-47%; 'about four in ten', 'close to half' used.",
       "- Ego depletion: the 2016 replication used one task version; 'scientists still argue about other versions' is said.",
       "- '1% better every day = 37x': arithmetic only, told as a picture, not a finding.",
       "- Amabile & Kramer: professional workers; 'at work' kept in the narration."]
Path(__file__).with_name("tiny_habits.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
