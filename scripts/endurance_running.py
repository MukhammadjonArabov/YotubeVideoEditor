"""Builds scripts/endurance_running.json (run: ./venv/Scripts/python scripts/endurance_running.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

BRA = "Bramble & Lieberman (2004). Endurance running and the evolution of Homo. Nature 432, 345-352"
BC = "Bramble & Carrier (1983). Running and breathing in mammals. Science 219, 251-256"
KAM = "Kamberov et al. (2018). Comparative evidence for the independent evolution of hair and sweat gland traits in primates. Journal of Human Evolution 125"
LIE = "Liebenberg, L. (2006). Persistence hunting by modern hunter-gatherers. Current Anthropology 47"
PIC = "Pickering & Bunn (2007). The endurance running hypothesis and hunting and scavenging in savanna-woodlands. Journal of Human Evolution 53"
LI7 = "Lieberman et al. (2007). The evolution of endurance running and the tyranny of ethnography: a reply to Pickering and Bunn. Journal of Human Evolution 53, 434-437"
MVH = "Guinness World Records, 'Most Man vs Horse Marathon wins by a man'; NBC News (2004), 'Marathon mind-blower: Man beats horse'; Shropshire Star (2022)"
SPD = "Graubner & Nixdorf (2011). Biomechanical analysis of the sprint and hurdles events at the 2009 IAAF World Championships. New Studies in Athletics 26 (Usain Bolt's peak speed about 12.2 m/s); American Quarter Horse Association (racing speeds around 55 mph)"
ROL = "Rolian et al. (2009). Walking, running, and the evolution of short toes in humans. Journal of Experimental Biology 212, 713-721"
RUF = "Ruff & Walker (1993). Body size and body shape. In Walker & Leakey (eds.), The Nariokotome Homo erectus Skeleton. Harvard University Press"
WOL = "Mech, L. D. & Boitani, L. (eds.) (2003). Wolves: Behavior, Ecology, and Conservation. University of Chicago Press"

S = [
    # ---------------- hook (12 one-line scenes)
    ("Race a horse over twenty-two miles. You might win.", "The main character stands on a starting line next to a big brown horse, both looking at each other, tense.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("In Wales, runners have beaten horses over a marathon distance.", "A wide green Welsh hillside with a winding dirt trail, wooden fence posts and a finish gate in the distance.", "hook", "awe", 3, "normal", 0, None, MVH),
    ("How? Because humans are built for endurance.", "The main character flexes one arm proudly, then wobbles, grinning at the camera.", "hook", "curious", 2, "normal", 0, None, None),
    ("Researchers say this began almost two million years ago.", "A long dusty African plain with a single acacia tree at sunrise and faint animal tracks in the dirt.", "hook", "awe", 2, "normal", 0, None, BRA),
    ("This explains why your body works the way it does.", "The main character looks down at his own legs and arms with a surprised expression, eyes wide.", "hook", "serious", 2, "normal", 0, None, None),
    ("Our skin packs ten times more sweat glands than chimps.", "A cartoon chimpanzee and a cartoon sweat drop on a plain pale background, with a tiny magnifying glass between them.", "hook", "curious", 2, "normal", 0, None, KAM),
    ("By the end, you'll know why we outlast animals.", "The main character holds up a finger with a determined grin, a big water drop dripping from his forehead.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("But some scientists doubt we ever hunted this way.", "Two big question marks made of stones standing on dry savanna ground under a harsh sun.", "hook", "tense", 2, "normal", 0, None, PIC),
    ("So did our ancestors really chase animals to exhaustion?", "The main character watches a running antelope far away with a hand over his eyes, squinting in the heat.", "hook", "whisper", 2, "slow", 0, None, None),
    ("In the Kalahari, hunters have been seen doing it.", "A dry sandy plain with animal footprints stretching across it under a blazing sun, a lone tree on the horizon.", "hook", "excited", 2, "normal", 0, None, LIE),
    ("Let's start with the body that makes it possible.", "The main character stretches his legs in a field wearing a tiny headband, ready to run.", "hook", "curious", 2, "normal", 0, None, None),
    ("The legs and feet store energy like springs.", "A drawing of a foot with a coiled spring in place of the arch beside a long tendon, plain pale background.", "hook", "awe", 3, "normal", 500, None, BRA),
    # ---------------- the running machine
    ("It looks ordinary, but your body hides some very clever running gear.", "The main character opens his own fur tunic like a coat to reveal tiny gears and springs inside, delighted.", "build", "curious", 2, "normal", 0, None, None),
    ("The Achilles tendon and the arch of the foot work like springs, storing energy with every step and giving it back. Bramble and Lieberman listed these among the running adaptations of the genus Homo.", "A drawing of foot bones with a curved arch drawn like a coil spring beside a long thin tendon, plain pale background.", "build", "neutral", 2, "normal", 0, None, BRA),
    ("Your feet are basically built-in trampolines. Free bounce, no batteries.", "The main character bounces on a tiny trampoline made of two feet drawn under his own, grinning.", "build", "funny", 2, "fast", 0, None, None),
    ("A large gluteus maximus, the big muscle in your backside, helps keep your upper body steady while you run, and a ligament in the neck helps steady the head.", "A simple anatomy drawing of a pelvis and thigh bones with the big rear muscle coloured red and a thin ligament at the neck, no letters.", "build", "neutral", 2, "normal", 0, None, BRA),
    ("A big backside as an evolutionary advantage. You're welcome, ancestors.", "The main character jogs past with a very large round backside bouncing behind him, looking proud.", "build", "funny", 2, "normal", 0, None, None),
    ("The paper also points to long legs for our body size, which means longer, springier strides.", "Two simple skeleton legs side by side, one short and one long, with a ruler line drawn between them.", "build", "neutral", 2, "normal", 0, None, BRA),
    ("And look at your toes. Tiny, compared with an ape's.", "The main character wiggles his small toes proudly in front of a chimpanzee's much longer toes, comparing them.", "build", "funny", 2, "normal", 0, None, None),
    ("A study found that shorter toes reduce the energy cost of running, which fits our short toes compared with other apes.", "Two foot bone drawings side by side, one with long toes and one with short toes, with a small arrow pointing to the short one.", "build", "neutral", 2, "normal", 0, None, ROL),
    ("Short toes, big win. Evolution doesn't care about sandals. Now, when did this body show up?", "The main character kicks off a tiny sandal and runs, with his short toes glowing and a stopwatch in the air.", "build", "curious", 2, "normal", 0, None, None),
    ("The Turkana Boy, a skeleton about one point six million years old from Kenya, had long legs and a slim body, a build much closer to ours than to earlier hominins.", "A tall slim skeleton lying on a Kenyan savanna floor at sunrise, long leg bones clearly visible.", "build", "awe", 2, "normal", 0, None, RUF),
    ("But running makes you hot. So how do we avoid cooking ourselves?", "The main character runs with a small cloud of steam rising off his head, eyes wide.", "build", "tense", 2, "normal", 0, None, None),
    ("A study of primate skin found that humans have about ten times the density of the sweat glands that cool us compared with chimpanzees and macaques.", "A magnified circle of smooth skin with many tiny glowing drops of sweat next to a smaller circle of hairy skin.", "build", "curious", 2, "normal", 0, None, KAM),
    ("Thin hair and lots of sweat: one of the best cooling systems among mammals, if you ignore the smell.", "The main character wrings out his sweaty tunic over a bucket, nose wrinkled, a small cloud of stink lines around him.", "build", "funny", 2, "normal", 0, None, None),
    ("At peak, humans can sweat about three and a half litres an hour, roughly five to ten times what chimpanzees manage, though chimp data are limited.", "A tall clear bottle filling with water drops, next to a smaller bottle filling slowly, on a flat stone.", "build", "neutral", 2, "normal", 0, None, KAM),
    ("That's almost two big bottles every hour. Pretty impressive for an ape.", "The main character drinks from a huge water bottle with his eyes closed, then looks at the empty bottle in shock.", "build", "funny", 2, "fast", 0, None, None),
    ("Many four-legged animals tie their breathing to their stride when they gallop, which limits how much they can pant to cool down.", "A galloping horse drawn from the side with a small arrow showing a breath in and out matching each stride.", "build", "neutral", 2, "normal", 0, None, BC),
    ("So a horse is faster, but it overheats. You, on the other hand, can keep going.", "The main character jogs steadily beside a panting horse that has stopped to rest under a tree, looking smug.", "build", "excited", 2, "normal", 0, None, None),
    ("Usain Bolt's peak speed was about twenty-seven miles an hour. A fast racehorse can pass fifty.", "A horse and a runner racing side by side on a track, the horse far ahead with dust flying behind it.", "build", "serious", 2, "normal", 0, None, SPD),
    ("So in a short race, don't bet on yourself. Bet on the horse.", "The main character holds a betting ticket with a horse drawn on it, whispering to the viewer.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- man versus horse
    ("In Llanwrtyd Wells, Wales, a Man versus Horse marathon has run since nineteen eighty. Runners and horses race over roughly twenty-two miles of hills and trails.", "A green Welsh valley with sheep on the hills, a small stone bridge, and a rough dirt trail winding between fences.", "build", "neutral", 2, "normal", 0, None, MVH),
    ("Twenty-two miles of hills. Sensible, right?", "The main character looks up at an enormous green hill with his hands on his hips, a tiny bead of sweat on his forehead.", "build", "funny", 2, "normal", 0, None, None),
    ("For twenty-four years, the horses won. In two thousand four, a runner named Huw Lobb finished first, in about two hours and five minutes.", "A wooden finish arch on a Welsh trail with a tiny trophy cup at its base and a ribbon fluttering.", "build", "awe", 2, "normal", 300, None, MVH),
    ("Quick pause. If you're enjoying this, subscribe and stay with me, because there's so much more of the ancient world for us to explore together. It's free, it takes one second, and it helps others find the channel.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    ("Humans have won since. Ricky Lightfoot won in twenty twenty-two, in two hours and twenty-two minutes. Guinness lists several human wins.", "A golden trophy cup standing alone on a grass hill with a small ribbon, sunlight on it.", "build", "excited", 2, "normal", 0, None, MVH),
    ("Beating a horse is one thing. But did our ancestors really chase animals this way?", "The main character scratches his head while looking at a distant trail of animal footprints in the dust.", "build", "curious", 2, "normal", 0, None, None),
    # ---------------- persistence hunting
    ("The idea is called persistence hunting: follow an animal through the heat of the day until it overheats and can't keep fleeing.", "A lone antelope standing in the shade of a tree, panting, with a heat shimmer rising over a dry plain.", "build", "neutral", 2, "normal", 0, None, LIE),
    ("Picture chasing an antelope at noon. And you're the one who's sweating.", "The main character jogs under a blazing sun with a big drop of sweat flying off his chin, a distant antelope ahead.", "build", "funny", 2, "normal", 0, None, None),
    ("Louis Liebenberg described such hunts by San hunters in the Kalahari, where trackers followed animals for hours across the sand.", "A long line of animal footprints stretching across pale desert sand toward a faraway hill.", "build", "neutral", 2, "normal", 0, None, LIE),
    ("The hard part is following the footprints. Reading the sand like a book.", "The main character crouches over footprints in the sand with a tiny magnifying glass, very focused.", "build", "curious", 2, "normal", 0, None, None),
    ("In two thousand seven, critics Pickering and Bunn argued that persistence hunting is rare today, happens in dry places, and always needs skilled tracking.", "A dry savanna scene with a few acacia trees and a single footprint line, the sky pale and empty.", "build", "serious", 2, "normal", 0, None, PIC),
    ("Fair point. Maybe running was just one tool in the toolbox.", "The main character opens a big wooden toolbox full of stone tools and a small pair of running shoes drawn as footprints.", "build", "curious", 2, "normal", 0, None, None),
    ("Lieberman and colleagues replied that rare cases in recent times don't rule out a bigger role in the distant past.", "An old, dusty path in a dry landscape curving back into a pale distant horizon.", "build", "neutral", 2, "normal", 0, None, LI7),
    ("Science argues, that's normal. But the bones keep telling the same story.", "The main character weighs two stones in his hands like a scale, one labelled by a tiny sun, one by a tiny bone.", "build", "serious", 2, "normal", 0, None, None),
    ("Bramble and Lieberman concluded that the fossils suggest endurance running appeared in the genus Homo about two million years ago.", "A row of ancient skulls and leg bones laid out on a flat rock in warm light with a faint sunrise behind.", "punchline", "awe", 2, "slow", 400, "ding", BRA),
    ("Two million years ago. Long before farms, towns or shoes.", "The main character runs barefoot across a wide open plain at sunrise, arms pumping, smiling.", "build", "happy", 2, "normal", 0, None, None),
    ("Some researchers suggest early Homo may have used running to scavenge, reaching a kill before rivals, rather than chasing live animals.", "A lone carcass bone on the savanna with a few vultures circling in the distance under a bright sky.", "build", "neutral", 2, "normal", 0, None, PIC),
    ("Hunting, scavenging, or both: running paid in calories.", "The main character carries a large bone over his shoulder, tired but smiling, a long trail of footprints behind him.", "build", "serious", 2, "normal", 0, None, None),
    ("Humans aren't the only endurance runners. Wolves are known to travel dozens of kilometres in a day while hunting.", "A grey wolf trotting steadily across a wide snowy plain with a long line of paw prints behind it.", "build", "curious", 2, "normal", 0, None, WOL),
    ("So we ran, and wolves ran. Maybe that's one reason dogs and people became such a good team.", "The main character jogs beside a friendly cartoon wolf cub, both with their tongues out, laughing.", "build", "happy", 2, "slow", 0, None, None),
    ("The wolf evidence is general, and the team-up idea is a hypothesis, not a fact. I love it anyway.", "A simple cave painting of a person and a wolf running side by side, with soft light on the rock.", "build", "funny", 2, "normal", 0, None, WOL),
    ("So why can humans run for hours? Springs in the legs, sweat on the skin, and maybe two million years of practice. Thanks for running this whole way with me. If it sparked something, like the video and tell me in the comments which clue you trust most. I read every one. Next time: when did dogs join the camp? I hope you'll be there. See you soon, friend.", "The main character jogs towards the viewer with a big smile, a small cartoon wolf cub trotting beside him on a grassy plain at sunrise.", "normal", "happy", 2, "slow", 800, "pop", None),
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
    "title": "Why Can Humans Run for HOURS?",
    "title_alternatives": ["Humans vs Horses: Who Wins a MARATHON?", "The Body Built for ENDURANCE: Humans Outlast Horses",
                           "Did Our Ancestors Hunt by Running ANIMALS to Death?", "Why Do Humans SWEAT So Much? The Running Apes"],
    "description": ("Race a horse over twenty-two miles, and you might win. Why can humans run for hours? This video follows the springs in our legs, "
                    "the sweat glands in our skin, a marathon between men and horses in Wales, and the debate over whether our ancestors really "
                    "hunted by running animals to exhaustion.\n\nThis video is history and science, not training or health advice.\n\nSources:\n"
                    "- Bramble & Lieberman (2004). Endurance running and the evolution of Homo. Nature.\n"
                    "- Bramble & Carrier (1983). Running and breathing in mammals. Science.\n"
                    "- Kamberov et al. (2018). Independent evolution of hair and sweat gland traits in primates. J. Hum. Evol.\n"
                    "- Liebenberg (2006). Persistence hunting by modern hunter-gatherers. Current Anthropology.\n"
                    "- Pickering & Bunn (2007). The endurance running hypothesis and hunting and scavenging in savanna-woodlands. J. Hum. Evol.\n"
                    "- Lieberman et al. (2007). The evolution of endurance running and the tyranny of ethnography. J. Hum. Evol.\n"
                    "- Guinness World Records and NBC News on the Man versus Horse marathon."),
    "tags": ["endurance running", "persistence hunting", "human evolution", "why humans run", "man vs horse marathon", "sweat glands",
             "ancient humans", "homo erectus", "kalahari", "animated explainer", "stickman"],
    "mood": "playful",
    "sources": [
        "Bramble, D. M. & Lieberman, D. E. (2004). Endurance running and the evolution of Homo. Nature 432, 345-352.",
        "Bramble, D. M. & Carrier, D. R. (1983). Running and breathing in mammals. Science 219, 251-256.",
        "Kamberov, Y. G. et al. (2018). Comparative evidence for the independent evolution of hair and sweat gland traits in primates. Journal of Human Evolution 125.",
        "Liebenberg, L. (2006). Persistence hunting by modern hunter-gatherers. Current Anthropology 47, 1017-1026.",
        "Pickering, T. R. & Bunn, H. T. (2007). The endurance running hypothesis and hunting and scavenging in savanna-woodlands. Journal of Human Evolution 53, 434-438.",
        "Lieberman, D. E. et al. (2007). The evolution of endurance running and the tyranny of ethnography: a reply to Pickering and Bunn. Journal of Human Evolution 53, 434-437.",
        "Graubner, R. & Nixdorf, E. (2011). Biomechanical analysis of the sprint and hurdles events at the 2009 IAAF World Championships in Athletics. New Studies in Athletics 26.",
        "Mech, L. D. & Boitani, L. (eds.) (2003). Wolves: Behavior, Ecology, and Conservation. University of Chicago Press.",
        "Guinness World Records, 'Most Man vs Horse Marathon wins by a man'; NBC News (2004), 'Marathon mind-blower: Man beats horse'.",
    ],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]), "max hook line:", max(len(s["narration"].split()) for s in scenes[:12]))
em = [s["emotion"] for s in scenes]
run = 1
for i in range(1, len(em)):
    run = run + 1 if em[i] == em[i - 1] else 1
    if run > 3:
        print("4+ same emotion in a row at scene", i + 1, em[i])
