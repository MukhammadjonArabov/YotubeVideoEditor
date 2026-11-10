"""Builds scripts/laughter.json and scripts/laughter.factcheck.md
(run: ./venv/Scripts/python scripts/laughter.py).
Why humans laugh: the 1962 laughter epidemic, ape and rat laughter, laughter as social glue, ~10 minutes,
a new anime picture every ~4 s (import with --minutes 10 --seconds-per-image 4).
P(...) adds one hero scene and one fact scene, so hero/fact always alternate. Concept approved by the owner 2026-11-08.
No health claims: laughter is never called a cure; the pain-threshold study is told as a link."""
import json
from pathlib import Path

TAN = "Rankin & Philip (1963). An epidemic of laughing in the Bukoba district of Tanganyika. Central African Journal of Medicine 9; Hempelmann (2007). Humor 20"
DR = "Davila Ross, Owren & Zimmermann (2009). Reconstructing the evolution of laughter in great apes and humans. Current Biology 19, 1106-1111"
PAN = "Panksepp & Burgdorf (2003). 'Laughing' rats and the evolutionary antecedents of human joy? Physiology & Behavior 79, 533-547"
WB = "Winkler & Bryant (2021). Play vocalisations and human laughter: a comparative review. Bioacoustics 30, 499-526"
PRO = "Provine, R. (2000). Laughter: A Scientific Investigation. Viking"
DUN = "Dunbar et al. (2012). Social laughter is correlated with an elevated pain threshold. Proceedings of the Royal Society B 279, 1161-1167"
BLA = "Blakemore, Wolpert & Frith (1998). Central cancellation of self-produced tickle sensation. Nature Neuroscience 1, 635-640"
SUM = "McDonald (2008). The world's oldest jokes, University of Wolverhampton (Sumerian proverb, about 1900 BCE; Westcar Papyrus riddle)"
CAI = "Cai, Chen, White & Scott (2019). Modulation of humor ratings of bad jokes by other people's laughter. Current Biology 29, R677-R678"
BRY = "Bryant et al. (2016). Detecting affiliation in colaughter across 24 societies. PNAS 113, 4682-4687"

VERIFY = {
    BLA: ("Searched 2026-11-08; paper copies and Scientific American explainer: the cerebellum predicts the touch your own movement makes and damps the brain's response, so self-tickling feels weaker; a delay makes it tickle more.",
          "'The brain predicts it', no exact numbers."),
    SUM: ("Searched 2026-11-08; University of Wolverhampton news release (Aug 2008), Guinness World Records, Chortle: Sumerian proverb about a young woman breaking wind in her husband's lap, dated to at least 1900 BCE, possibly older; second on the list an Egyptian riddle from the Westcar Papyrus (1800-1600 BCE).",
          "'About four thousand years old', 'one of the oldest recorded jokes'; joke told gently."),
    CAI: ("Searched 2026-11-08; ScienceDaily, NPR and Neuroscience News on the Current Biology paper: 40 weak 'dad jokes', 72 adults; added laughter raised funniness ratings, spontaneous laughter more (about 15-20%) than posed laughter (about 10%).",
          "'A little funnier', 'real laughter more than fake'; percentages not overstated."),
    TAN: ("Searched 2026-11-08; several accounts based on Rankin & Philip 1963 and Hempelmann 2007: started 30 January 1962 with three girls at a mission boarding school in Kashasha; "
          "95 of 159 pupils affected; school closed 18 March; spread to villages and other schools; about 14 schools closed and about 1,000 people affected by 1964; "
          "explained as mass psychogenic illness, Hempelmann links it to stress after independence. Enrolment is 195 in one secondary account.",
          "'About ninety-five', 'about a thousand people', 'more than a dozen schools'; told respectfully, no mocking; cause told as 'researchers think'."),
    DR: ("Searched 2026-11-08; National Geographic, ScienceDaily and phys.org on the Current Biology paper: tickling-induced sounds of young chimpanzees, bonobos, gorillas, orangutans and human babies compared; "
         "acoustic tree matched the family tree; common origin at least 10-16 million years ago; human laughter changed after our line split, about 4.5-6 million years ago.",
         "'At least ten million years', 'our laugh is a changed version'; ape sounds called 'laugh-like panting'."),
    PAN: ("Searched 2026-11-08; Panksepp & Burgdorf papers and summaries: young rats tickled by hand make about 50 kHz chirps, too high for human ears; "
          "the authors read them as a sign of positive feeling; rats seek the tickling hand.",
          "'Something like laughter', 'researchers argue', 'too high for us to hear'."),
    WB: ("Searched 2026-11-08; UCLA newsroom, NPR, Smithsonian on the Bioacoustics review: play sounds documented in at least 65 species, mostly mammals plus three birds (kea, parakeets, Australian magpies); "
         "only some are play-specific; list likely incomplete.",
         "'At least sixty-five species', 'play sounds', not 'all animals laugh'."),
    PRO: ("Searched 2026-11-08; Discover interview and First Things essay quoting Provine: about 30 times more laughter in company than alone (student logbooks, excluding TV); "
          "speakers laugh about 46% more than listeners; most conversational laughter does not follow jokes. No percentage for joke-laughter is used.",
          "'About thirty times', 'about forty-six percent more', 'most laughs follow ordinary lines'."),
    DUN: ("Searched 2026-11-08; paper record and abstract: six studies in lab and theatre; pain thresholds higher after laughing in groups; endorphins inferred from pain threshold, not measured.",
          "'A link', 'scientists suspect endorphins'; no health advice, laughter never called a treatment."),
    BRY: ("Searched 2026-11-08; PNAS abstract and NPR/Aarhus coverage: 966 listeners in 24 societies heard brief co-laughter of friends or new acquaintances; accuracy about 53-67%; "
          "friends' laughter louder, higher and more varied.",
          "'Better than chance, not perfect', 'one second of laughter'."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source, on_screen)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None, text=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src, text))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None, None))


# ================= hook (12 short lines)
P("In nineteen sixty-two, three schoolgirls started laughing.",
  "The main character peeks through the window of an old brick school building on a rainy afternoon, curious.",
  "And they could not stop.",
  "Three African schoolgirls in nineteen-sixties uniforms laughing helplessly at their desks in an old classroom.",
  TAN, "curious", "tense", "hook", hsfx="riser")
P("Within weeks, about ninety-five students were laughing.",
  "The main character stands in a school corridor, eyes wide, as laughter fills every classroom.",
  "The school had to close its doors.",
  "An old mission school with its wooden gate closed, empty yard, grey rainy sky.",
  TAN, "tense", "serious", "hook", text="95")
P("Then it spread to villages nearby. Like a cold.",
  "The main character walks down a red dirt road between villages, looking back at houses where people laugh.",
  "Doctors found no poison, no germ, no infection.",
  "A nineteen-sixties doctor examining notes at a wooden table in a village clinic, lamp light.",
  TAN, "awe", "serious", "hook")
P("You probably laughed today. Do you know why?",
  "The main character laughs at a campfire with friends, then stops and looks puzzled at the viewer.",
  "Most laughs don't even follow a joke.",
  "Two friends chatting at a cafe table and laughing at an ordinary moment, coffee cups between them.",
  PRO, "funny", "serious", "hook")
P("By the end, you'll know what your laugh secretly says.",
  "The main character holds a glowing sound wave in his hands like a precious stone.",
  "And why laughter is older than humans themselves.",
  "A young chimpanzee rolling on the forest floor, mouth open in a playful face, sunlight through trees.",
  DR, "curious", "excited", "hook")
P("Here's a clue. Strangers can hear who your friends are.",
  "The main character whispers behind his hand to the viewer, eyes narrowed playfully.",
  "Even rats make laugh-like sounds when tickled.",
  "A small white rat lying on its back on a researcher's palm in a bright lab, looking happy.",
  BRY, "whisper", "funny", "hook", fsfx="pop")

P("Imagine being a teacher that week.",
  "The main character stands at the front of a classroom where every student is giggling, chalk in his hand, confused.",
  "Pupils sent home took the laughter with them to their villages.",
  "Children walking home along a red dirt road between banana trees under a cloudy sky.",
  TAN, "funny", "serious")
P("Every family, every village, the same strange sound.",
  "The main character sits outside a village hut at dusk, hearing laughter from every direction.",
  "More than a dozen schools closed before it ended.",
  "A row of empty wooden school desks in a quiet classroom, dust in the afternoon light.",
  TAN, "awe", "serious")

# ================= laughter before jokes
P("So let's find the very first laugh.",
  "The main character walks into a misty green rainforest at dawn, pushing aside giant leaves.",
  "In two thousand nine, scientists tickled young apes and recorded the sounds.",
  "A scientist gently tickling a baby orangutan in a sanctuary, both relaxed, sunlight through leaves.",
  DR, "curious", "neutral")
P("Yes. Tickling apes. For science.",
  "The main character grins and wiggles his fingers like a tickle monster.",
  "Chimpanzees, bonobos, gorillas and orangutans all made breathy, panting laugh sounds.",
  "Four young great apes playing together in a forest clearing, mouths open in play faces.",
  DR, "funny", "neutral", hpace="fast")
P("Then they compared them with human babies laughing.",
  "The main character sits on the grass holding a giggling baby, both laughing.",
  "The pattern of the sounds matched the family tree of the apes.",
  "A tree made of glowing sound waves with branches labelled by small ape faces, no letters.",
  DR, "happy", "awe")
P("The closer the cousin, the closer the laugh.",
  "The main character stands beside a chimpanzee, both laughing with the same open mouth.",
  "So laughter likely goes back at least ten million years.",
  "A misty ancient forest at dawn with a primitive ape ancestor sitting on a branch.",
  DR, "excited", "awe", fpause=500, text="10 MILLION YEARS")
P("Ten million years. Before stone tools. Before fire.",
  "The main character holds a stone tool and a torch, then sets them down, amazed.",
  "Long before anyone told a single joke.",
  "An empty prehistoric forest clearing at sunset with birds flying overhead.",
  DR, "awe", "neutral")
P("So laughing came first. Humour came much later.",
  "The main character taps his head and smiles, as if a puzzle clicked.",
  "Ape laughs pant in and out. Ours mostly flows on the out-breath.",
  "Two sound waves side by side floating over a forest pond, one short and choppy, one smooth.",
  DR, "curious", "neutral")
P("Our laugh is basically an upgraded ape laugh.",
  "The main character laughs loudly with his head thrown back, like a cartoon.",
  "The change likely happened after our line split from chimpanzees.",
  "A forest path splitting in two at dawn, apes walking one way, early humans the other.",
  DR, "funny", "neutral")
P("Somewhere along the way, we learned to laugh out loud.",
  "The main character laughs with a group of early humans around a campfire at night.",
  "That split is usually placed around five to six million years ago.",
  "Early upright humans walking across a grassy savanna at sunrise, long shadows.",
  DR, "happy", "neutral")

# ================= animals laugh too
P("But wait. Are we the only ones laughing?",
  "The main character raises an eyebrow at a group of animals watching him from the bushes.",
  "Neuroscientist Jaak Panksepp tickled young rats.",
  "A smiling scientist in a white coat tickling a young rat on a lab table, warm lamp.",
  PAN, "curious", "neutral")
P("Imagine putting that on your resume.",
  "The main character holds a paper sign-shaped scroll and laughs, a tiny rat on his shoulder.",
  "The rats chirped at about fifty kilohertz, too high for human ears.",
  "A glowing sound wave rising from a tiny rat into the dark air of a quiet lab.",
  PAN, "funny", "neutral", text="50 kHz")
P("A tiny laugh we can't even hear.",
  "The main character cups his ear toward a small rat, straining to hear.",
  "They chased the tickling hand and came back for more.",
  "A young rat running happily toward a gloved hand on a clean lab table.",
  PAN, "awe", "happy")
P("Panksepp thought this was a kind of joy.",
  "The main character smiles warmly, watching rats play in a box of wood shavings.",
  "Not everyone agrees it's laughter. But it looks a lot like play.",
  "Two young rats wrestling playfully in wood shavings under soft light.",
  PAN, "neutral", "serious")
P("Panksepp even noticed the rats picked favourites.",
  "The main character holds two tiny rats who both stretch toward his hand.",
  "Rats tickled often chirped more when that same hand came near.",
  "A young rat standing on its hind legs reaching toward a gloved hand on a clean table.",
  PAN, "funny", "happy")
P("A rat with a best friend. I love that.",
  "The main character smiles softly at a rat sleeping in his palm.",
  "Young animals play most, and laugh most, in safe places.",
  "Fox cubs tumbling over each other outside their den in soft morning light.",
  WB, "happy", "neutral")
P("And rats aren't alone.",
  "The main character sits in a meadow surrounded by playful animals.",
  "A review found play sounds in at least sixty-five species.",
  "A collage-like meadow with puppies, monkeys, dolphins jumping in a lake and birds, all playing.",
  WB, "excited", "awe", text="65 SPECIES")
P("Dogs pant when they play. Dolphins whistle.",
  "The main character plays tug of war with a happy dog on a beach.",
  "Even three kinds of birds, including the kea parrot.",
  "A green kea parrot rolling playfully in snow on a mountain, beak open.",
  WB, "happy", "funny")
P("A parrot that laughs in the snow. Honestly, goals.",
  "The main character lies in the snow laughing next to a kea parrot.",
  "These sounds mean one thing: this is play, not a fight.",
  "Two wolf pups play-biting each other in tall grass, tails wagging.",
  WB, "funny", "serious")

# ================= why you can't tickle yourself
P("Quick test. Try tickling yourself right now.",
  "The main character tries to tickle his own ribs, then frowns, completely unimpressed.",
  "Almost nobody can. Scientists found out why in nineteen ninety-eight.",
  "A researcher adjusting a small robotic arm with a soft foam tip in a quiet lab.",
  BLA, "funny", "curious")
P("Nothing. Not even a giggle. Rude.",
  "The main character crosses his arms and pouts at his own hand.",
  "Your brain predicts the touch before your fingers even arrive.",
  "A glowing brain with a bright spot at the back, small arrows pointing to a hand.",
  BLA, "funny", "neutral")
P("It's like a magician who knows the trick.",
  "The main character pulls a rabbit from a hat and yawns, bored.",
  "A part called the cerebellum dampens the feeling of your own touch.",
  "The back of a glowing transparent head with the small cerebellum lit in soft blue.",
  BLA, "curious", "neutral")
P("But when someone else does it, surprise wins.",
  "The main character bursts out laughing as a friend tickles him from behind.",
  "When a machine added a tiny delay, people's own touch tickled more.",
  "A soft foam paddle moving slowly over a person's palm, a small clock beside it.",
  BLA, "excited", "awe")
P("So tickling needs two. It was always a social game.",
  "The main character and a child tickle each other on a blanket by the river, both laughing.",
  "Just like apes tickling their young in the forest.",
  "A mother chimpanzee tickling her baby on a mossy log, both with open play faces.",
  DR, "happy", "neutral")

# ================= why ancient humans needed it
P("Now picture an ancient camp.",
  "The main character sits among early humans in a cave camp at dusk, a fire crackling.",
  "Early humans lived in small groups that depended on each other.",
  "A small band of early humans sharing food around a fire in front of a cave at dusk.",
  WB, "curious", "neutral")
P("Two young hunters wrestle. It looks dangerous.",
  "The main character and a friend wrestle on the grass, both grinning.",
  "A laugh during rough play signals: relax, it's a game.",
  "Two early human boys wrestling playfully while elders smile nearby, sunset light.",
  WB, "tense", "neutral")
P("Without that laugh, play-fighting could turn into real fighting.",
  "The main character holds up his hands, laughing, as his friend pretends to punch him.",
  "Scientists see laughter as a signal that grew out of play.",
  "Young chimpanzees chasing each other around a tree trunk with open play faces.",
  WB, "serious", "neutral")
P("A laugh was like a white flag. Peace. We're friends.",
  "The main character waves a big leaf like a flag, laughing with the group.",
  "And it worked best in a crowd.",
  "A crowd of early humans laughing together around a big fire at night, sparks rising.",
  PRO, "happy", "excited")

# ================= subscribe (after a fact, mid-video)
P("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring the ancient world together, one question at a time. It's free, it takes one second, and it helps more curious people find us.",
  "The main character waves warmly at the viewer beside a campfire under a starry sky.",
  "Back to the crowd. Because laughter is mostly social.",
  "A busy city street at night in light rain with groups of friends laughing under umbrellas.",
  PRO, "happy", "neutral", fpause=300)

# ================= laughter as social glue
P("Robert Provine spent years just watching people laugh.",
  "The main character sits on a park bench with a notebook, secretly watching people laugh.",
  "His students kept laughter diaries for a week.",
  "A student writing in a small notebook on a bus at dusk, rain on the window.",
  PRO, "curious", "neutral")
P("Every laugh, every place, every person.",
  "The main character scribbles tally marks on a cave wall with charcoal, laughing.",
  "They laughed about thirty times more with others than alone.",
  "A lonely student in a dark room next to the same student laughing with friends in a bright kitchen.",
  PRO, "funny", "awe", text="30x")
P("Thirty times! Alone, we barely laugh at all.",
  "The main character sits alone in a quiet cave, unsmiling, then a friend arrives and he bursts out laughing.",
  "Even the person telling a story laughs more than the listeners.",
  "A woman telling a story at a dinner table while laughing, friends smiling politely around her.",
  PRO, "excited", "funny")
P("About forty-six percent more. We laugh at our own stories.",
  "The main character tells a story by the fire, laughing hardest at his own joke while others smile.",
  "And most laughs follow ordinary lines like, see you later.",
  "Two coworkers laughing while saying goodbye at an office door, evening light.",
  PRO, "funny", "neutral", text="46%")
P("So laughing isn't about being funny. It's about being together.",
  "The main character puts an arm around a friend's shoulder at the campfire, both laughing.",
  "Laughter tells the group: we're fine, we're on the same side.",
  "A family laughing together around a table in a cozy home during a rainy evening.",
  PRO, "awe", "neutral", hpause=400)

# ================= the oldest joke
P("So when did humour finally show up?",
  "The main character scratches his head in front of a wall of ancient clay tablets.",
  "In two thousand eight, researchers hunted for the oldest recorded joke.",
  "A historian reading old clay tablets with a magnifying glass in a museum basement.",
  SUM, "curious", "neutral")
P("Something deep. Philosophical. Wise.",
  "The main character strokes an imaginary beard, trying to look wise.",
  "It came from Sumer, at least about four thousand years ago.",
  "An ancient Sumerian city by a river at sunset, mud-brick walls glowing orange.",
  SUM, "funny", "awe", text="1900 BCE")
P("And the joke was about... someone passing gas.",
  "The main character covers his mouth, trying hard not to laugh.",
  "A young wife breaking wind in her husband's lap. That was the punchline.",
  "Two Sumerian scribes laughing over a clay tablet in lamp light, hands on their bellies.",
  SUM, "funny", "funny", hpace="fast", fsfx="boing")
P("Four thousand years, and fart jokes still work.",
  "The main character laughs so hard he falls off a stone bench.",
  "Second on the list: an Egyptian riddle from an old papyrus.",
  "An ancient Egyptian papyrus scroll on a wooden table, a lamp and a reed pen beside it.",
  SUM, "excited", "neutral")
P("Our humour got fancier. Our laugh stayed ancient.",
  "The main character holds a clay tablet in one hand and a smartphone in the other, smiling.",
  "Laughing came millions of years first. Jokes are the new part.",
  "A long timeline drawn in the sand on a beach, a tiny clay tablet at the very end.",
  DR, "awe", "serious")

P("Here's something you never noticed about your own laugh.",
  "The main character pauses mid-sentence at a dinner table, finger raised.",
  "Provine found we almost never laugh in the middle of a sentence.",
  "Two friends talking on a park bench, speech bubbles without letters floating between them.",
  PRO, "curious", "neutral")
P("We wait for the pause. Like a full stop in speech.",
  "The main character speaks, stops, then laughs, like punctuation.",
  "He called it the punctuation effect.",
  "A row of glowing dots and pauses floating in the air between two laughing people at night.",
  PRO, "neutral", "awe")
P("Your brain schedules your laughs without asking you.",
  "The main character looks at a tiny clock inside a glass head, amazed.",
  "Laughter and speech share the same breath, so they take turns.",
  "A misty breath cloud from a laughing person on a cold autumn evening, street lamp glowing.",
  PRO, "funny", "neutral")

# ================= laughter and pain
P("And here's where it gets strange.",
  "The main character leans toward the viewer, eyebrows raised mysteriously.",
  "In twenty twelve, Robin Dunbar's team made people laugh, then tested pain.",
  "A row of people in a theatre laughing at a comedy show, warm stage light.",
  DUN, "whisper", "neutral")
P("They used things like a tight cuff on the arm.",
  "The main character winces at a blood pressure cuff on his arm, then laughs.",
  "After laughing together, people put up with more discomfort.",
  "A smiling volunteer in a lab with a frozen sleeve on her arm, a clock on the wall.",
  DUN, "funny", "awe")
P("Laughing made them tougher. At least for a while.",
  "The main character flexes his arm proudly while still giggling.",
  "The researchers suspect the body's own endorphins are involved.",
  "Glowing particles flowing through a calm human silhouette in the dark, soft blue light.",
  DUN, "excited", "neutral")
P("Endorphins are the same family of chemicals as feel-good runner's high.",
  "The main character jogs along a riverbank at sunrise, smiling.",
  "It's a link, not proof. Endorphins weren't measured directly.",
  "Two scientists at a laptop looking at charts, a whiteboard behind them, coffee mugs.",
  DUN, "happy", "serious")
P("But for ancient humans, a warm group feeling mattered a lot.",
  "The main character sits shoulder to shoulder with his tribe in a cave during a storm.",
  "Dunbar thinks laughter helped bond groups too big for one-on-one grooming.",
  "Monkeys grooming each other on a branch while a big group of early humans laughs below.",
  DUN, "serious", "awe")
P("Monkeys groom one friend at a time. We laugh with ten.",
  "The main character laughs with ten people at once around a huge fire.",
  "A shared laugh reaches many people at the same moment.",
  "A large outdoor gathering at night with lanterns and everyone laughing together.",
  DUN, "funny", "happy")

# ================= the open loop: friends vs strangers
P("Remember the clue? Strangers can hear who your friends are.",
  "The main character holds up a finger, remembering, in front of a cafe window.",
  "In twenty sixteen, researchers recorded pairs laughing together.",
  "Two university students laughing together into a microphone in a small recording room.",
  BRY, "curious", "neutral")
P("Some pairs were old friends. Some had just met.",
  "The main character stands between two pairs of people, one hugging, one shaking hands awkwardly.",
  "Then nine hundred sixty-six people in twenty-four societies listened.",
  "People of many cultures wearing headphones in villages, cities and markets around the world.",
  BRY, "neutral", "awe", text="24 SOCIETIES")
P("From farmers to students. Different languages. Same test.",
  "The main character wears headphones in a rice field, listening carefully.",
  "With about a second of laughter, they often guessed right.",
  "A short glowing sound wave floating above a quiet village at sunset.",
  BRY, "curious", "awe")
P("Not perfectly. But better than chance, almost everywhere.",
  "The main character shrugs with a little smile, holding a coin as if flipping it.",
  "Friends' laughs were louder, higher and more uneven.",
  "Two close friends laughing loudly on a rooftop at night, city lights behind them.",
  BRY, "neutral", "happy")
P("Fake polite laughs sound different. Our brains notice.",
  "The main character forces a stiff polite laugh at a dinner, looking uncomfortable.",
  "A real laugh is hard to fake, and listeners pick up on it.",
  "A smiling waiter laughing politely at a table of customers, warm restaurant light.",
  BRY, "funny", "neutral")

# ================= laugh tracks
P("This also explains the weird laughter on old TV shows.",
  "The main character sits on a sofa watching an old TV with a sitcom audience laughing.",
  "In twenty nineteen, scientists tested forty really bad jokes.",
  "A researcher in headphones playing jokes to a volunteer in a small sound booth.",
  CAI, "curious", "neutral")
P("Dad jokes. The worst kind.",
  "The main character groans, face in his hands, while an old man laughs at his own joke.",
  "Adding laughter afterwards made the jokes seem funnier.",
  "A theatre audience laughing, sound waves floating up toward the stage lights.",
  CAI, "funny", "neutral")
P("Even fake laughter helped a bit.",
  "The main character holds a cardboard sign shaped like a laughing face, grinning.",
  "Real, spontaneous laughter helped even more.",
  "Friends laughing genuinely on a beach at sunset, heads tilted back.",
  CAI, "neutral", "happy")
P("Your brain hears others laugh and thinks, I should join.",
  "The main character starts laughing on a bus because everyone around him laughs.",
  "Laughter spreads from person to person almost on its own.",
  "A bus full of strangers at night slowly catching the giggles, rain on the windows.",
  CAI, "funny", "awe")

P("And who was easiest to read?",
  "The main character squints at two laughing pairs, judging carefully.",
  "Listeners were especially good at spotting pairs of female friends.",
  "Two young women laughing together at a cafe window on a rainy day, sharing headphones.",
  BRY, "curious", "neutral")
P("So your laugh is like a passport. It shows where you belong.",
  "The main character holds up a small glowing badge shaped like a laughing mouth.",
  "Across all twenty-four societies, the pattern held.",
  "A world map made of tiny glowing lanterns on a dark table, each one pulsing softly.",
  BRY, "awe", "neutral")

# ================= back to 1962
P("So, back to that school in nineteen sixty-two.",
  "The main character stands at the gate of the old brick school in the rain, thoughtful.",
  "Researchers later called it mass psychogenic illness.",
  "Old typewritten medical reports and a fountain pen on a desk beside a rainy window.",
  TAN, "serious", "neutral")
P("A fancy way of saying: stress spreading through a group.",
  "The main character sits on the school steps, chin on his hands.",
  "One scholar links it to the pressure after independence.",
  "A nineteen-sixties classroom with a strict teacher and nervous students at their desks.",
  TAN, "neutral", "serious")
P("New country. New hopes. Big pressure on kids.",
  "The main character looks at a classroom full of anxious young faces, concerned.",
  "Laughter is contagious because our brains are built to join in.",
  "A group of strangers on a train all starting to laugh after one person laughs.",
  TAN, "sad", "awe")
P("Usually that's beautiful. Once, it got out of hand.",
  "The main character laughs with others on a train, then looks thoughtful.",
  "The outbreak faded by about nineteen sixty-four.",
  "The same old school yard full of students playing calmly on a sunny day.",
  TAN, "serious", "neutral")

P("And there's one more thing laughter does.",
  "The main character holds up one finger by the campfire, smiling mysteriously.",
  "Laughing together is a quick way to show you share the same view.",
  "A group of hikers laughing at a misty mountain top at sunrise.",
  PRO, "curious", "neutral")
P("Two strangers laugh at the same thing. Suddenly they're not strangers.",
  "The main character and a stranger laugh at a puddle splash on a rainy street.",
  "Shared laughter is one of the fastest social signals humans have.",
  "Two strangers sharing an umbrella and laughing on a rainy autumn sidewalk.",
  BRY, "happy", "awe")

# ================= ending
P("So why do humans laugh?",
  "The main character sits by a campfire at dusk, looking into the flames.",
  "Laughter began as a play signal at least ten million years ago.",
  "A young ape and a human child laughing at each other across a stream in a forest.",
  DR, "curious", "awe")
P("Then we turned it into the glue that holds groups together.",
  "The main character laughs with friends of every age around a big fire.",
  "We laugh far more with people than with jokes.",
  "Friends laughing on a city rooftop at sunset, string lights above them.",
  PRO, "happy", "neutral")
P("Here's my take. Your laugh is a tiny ancient message.",
  "The main character puts a hand on his heart and smiles at the viewer.",
  "It says: I'm safe with you.",
  "Two old friends laughing together on a bench under autumn trees in light rain.",
  BRY, "awe", "happy", hpause=500)
H("Thank you for spending these minutes with me. If this made you smile even once, hit like, and tell me in the comments who makes you laugh the most. I read every one. Next time, we'll find out why ancient humans started to sing. See you there, friend.",
  "The main character waves goodbye by a campfire at dusk, laughing, a small rat and a kea parrot beside him.",
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
    "title": "Why Do Humans LAUGH?",
    "title_alternatives": ["Your Laugh Is 10 Million Years OLD", "Laughter Is Older Than HUMANS", "Why Can't You Stop LAUGHING?",
                           "The Real Reason We LAUGH (It's Not Jokes)", "The Town That Couldn't Stop LAUGHING"],
    "description": ("In 1962, three schoolgirls started laughing and couldn't stop. Weeks later, a school had to close. "
                    "From tickled apes and laughing rats to a laugh that reveals who your friends are, this is the strange, ancient story of why humans laugh.\n\n"
                    "This video is history and science for education, not medical advice.\n\nSources:\n"
                    "- Rankin & Philip (1963). An epidemic of laughing in the Bukoba district of Tanganyika. Central African Journal of Medicine.\n"
                    "- Hempelmann (2007). The laughter of the 1962 Tanganyika 'laughter epidemic'. Humor.\n"
                    "- Davila Ross, Owren & Zimmermann (2009). Reconstructing the evolution of laughter in great apes and humans. Current Biology.\n"
                    "- Panksepp & Burgdorf (2003). 'Laughing' rats and the evolutionary antecedents of human joy? Physiology & Behavior.\n"
                    "- Winkler & Bryant (2021). Play vocalisations and human laughter. Bioacoustics.\n"
                    "- Provine (2000). Laughter: A Scientific Investigation.\n"
                    "- Dunbar et al. (2012). Social laughter is correlated with an elevated pain threshold. Proceedings of the Royal Society B.\n"
                    "- Bryant et al. (2016). Detecting affiliation in colaughter across 24 societies. PNAS."),
    "tags": ["why do humans laugh", "laughter", "evolution of laughter", "ancient humans", "do animals laugh", "rats laugh",
             "tanganyika laughter epidemic", "human evolution", "psychology of laughter", "great apes", "science explained", "animated explainer"],
    "mood": "playful",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Why Do Humans LAUGH?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-11-08.", "",
      "## Method",
      "- Every study was found online and its abstract, record or a reliable summary opened; contested points are told as such.",
      "- No health advice: laughter is never called a cure or treatment; the pain study is told as a link with an unmeasured mechanism.",
      "- The 1962 epidemic is told with respect for the people involved; no mockery.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- 'People laugh about 18 times a day': no reliable source found, dropped.",
       "- 'Only 10-20% of laughs follow jokes': no percentage confirmed; said as 'most laughs don't follow a joke'.",
       "- Tanganyika numbers differ between accounts (159 vs 195 pupils, timeline); 'about ninety-five', 'about a thousand people' used.",
       "- Rat 'laughter': told as 'laugh-like sounds' and the disagreement is said.",
       "- Endorphins: inferred from pain thresholds, not measured; said as 'suspect' and 'a link, not proof'.",
       "- Friends vs strangers: accuracy only 53-67%; said as 'not perfectly, better than chance'.",
       "- 'Fake laughs sound different' is a general framing of the Bryant findings on spontaneous vs volitional laughter, kept non-numeric."]
Path(__file__).with_name("laughter.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
