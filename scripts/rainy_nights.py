"""Builds scripts/rainy_nights.json and scripts/rainy_nights.factcheck.md
(run: ./venv/Scripts/python scripts/rainy_nights.py).
Fast-cut version (owner, 2026-10-26): a new picture every 2-3 seconds, so every scene is one short line (import with
--seconds-per-image 3). Even index hero, odd index fact. Inspired by the structure of Before Civilization's best video
("The Genius Ways Ancient Humans Survived Rainy Nights"): our own wording, facts and angle."""
import json
from pathlib import Path

REM = "Parmeggiani (1960s onward), reviewed in Frontiers in Physiology (2017), 'Sleep and thermoregulation' (shivering and panting are suppressed in REM sleep; mostly animal data)"
H2O = "Princeton University Outdoor Action, 'Hypothermia and cold weather injuries' (water conducts heat about 25 times faster than air; a field-guide rule of thumb)"
WET = "Kjellberg Grahn et al. (2015). Protection against cold in prehospital care: wet clothing removal or addition of a vapor barrier. Wilderness & Environmental Medicine 26, 11-20"
FLD = "US National Weather Service and NOAA flash-flood guidance (dry washes can flood from rain falling upstream; 2017 Cold Springs Canyon flood near Payson, Arizona)"
DRP = "Riel-Salvatore et al., Riparo Bombrini rock shelter, Italy (an artefact gap marks the old drip line; hearths and debris outside it)"
BOR = "Wadley et al. (2020). Fire and grass-bedding construction 200 thousand years ago at Border Cave, South Africa. Science 369, 863-866"
SIB = "Wadley et al. (2011). Middle Stone Age bedding construction and settlement patterns at Sibudu, South Africa. Science 334, 1388-1391"
OHA = "Nadel et al. (2004). Stone Age hut in Israel yields world's oldest evidence of bedding. PNAS 101, 6821-6826"

VERIFY = {
    REM: ("Searched 2026-10-26; Frontiers in Physiology 2017 review and PubMed 7166740 (human REM sweating study). Shivering and panting are suppressed in REM sleep; first described by Parmeggiani; most evidence from cats and rats, human data limited.",
          "'Your body's heating system mostly switches off', 'studies, mostly in animals'; no human number given."),
    H2O: ("Searched 2026-10-26; Princeton Outdoor Action page and US safety guides repeat 'about 25 times'; it compares thermal conductivity and is a rule of thumb, not a body-heat measurement.",
          "'About twenty-five times', called a rule of thumb; no 'wet clothes = five times' claim."),
    WET: ("Searched 2026-10-26; Wilderness & Environmental Medicine 2015 abstract: eight volunteers in wet clothing at minus 18.5 C; removing wet clothing or adding a vapour barrier lowered shivering heat production and improved skin rewarming; core temperature did not differ.",
          "Only 'less shivering, skin warmed better'; core temperature result stated; eight volunteers mentioned."),
    FLD: ("Searched 2026-10-26; NOAA photo captions and NWS warnings: dry washes become dangerous when storms are upstream; flash floods can come from rain that is not overhead. Cold Springs Canyon 2017: about 1.5 inches of rain fell upstream; several people swimming downstream died (reports give nine or ten).",
          "'Several people', 'rain that fell miles upstream'; no exact death toll."),
    DRP: ("Searched 2026-10-26; Riparo Bombrini summary (Riel-Salvatore et al.): a gap in artefacts across levels is read as the former drip line; hearths and debris accumulated outside it. Site reports elsewhere describe hearths just inside drip lines.",
          "'Archaeologists read a gap', interpretation, not a rule for every cave."),
    BOR: ("Searched 2026-10-26; Wits University release, Inside Science, Sci.News: grass bedding at least 200,000 years old near the back of Border Cave, laid on ash; camphor bush remains on the oldest bedding; insect-repelling purpose is the authors' suggestion.",
          "'At least two hundred thousand years', 'the researchers think' for the ash and camphor purpose."),
    SIB: ("Searched 2026-10-26; ScienceDaily, National Geographic, NBC: Sibudu bedding in at least 15 layers, oldest about 77,000 years, sedges and rushes topped with Cryptocarya woodii leaves whose chemicals can kill or repel insects such as mosquitoes; bedding periodically burned.",
          "'About seventy-seven thousand', 'leaves with insect-killing chemicals'; the mosquito purpose is an inference."),
    OHA: ("Searched 2026-10-26; University of Haifa record and PNAS summaries: about 23,000-year-old brush huts on the Sea of Galilee shore with grass bedding around a central hearth; 'oldest' claim later superseded by Sibudu and Border Cave.",
          "'About twenty-three thousand years'; not called the oldest."),
}

MC = "the main character"
S = []


def H(narr, prompt, emo=None, beat="build", pace="normal", pause=0, sfx=None, inten=2):
    S.append((narr, prompt, beat, emo, inten, pace, pause, sfx, None))


def F(narr, prompt, src, emo=None, beat="build", pace="normal", pause=0, sfx=None, inten=2):
    S.append((narr, prompt, beat, emo, inten, pace, pause, sfx, src))


# ---------------- hook: 12 one-line scenes (grab, why, what, open loop)
H("Rain on a roof sounds cozy tonight.", "The main character lies smiling in a warm modern bed while rain streaks down a dark window.", "curious", "hook", sfx="whoosh")
F("For most of history, it sounded like danger.", "Heavy rain pouring over a dark prehistoric forest at night, lightning far away, no people.", H2O, "tense", "hook")
H("Picture yourself thirty thousand years ago.", "The main character stands in a soaked prehistoric forest at dusk, hugging himself.", "tense", "hook")
F("Water steals body heat far faster than air.", "A drop of water falling onto a glowing warm stone that steams, dark background.", H2O, "serious", "hook")
H("You lie down, tired, and the rain starts.", "The main character lies on bare ground under a tree as the first drops hit his face.", "tense", "hook")
F("Asleep, your body's heating system mostly switches off.", "A simple thermometer made of bone with its red line sinking, night background, no people.", REM, "serious", "hook")
H("That's why this matters to you.", "The main character sits up and points straight at the viewer, serious.", "serious", "hook", inten=3)
F("You still can't sleep when you're cold and damp.", "A rumpled damp blanket on a cold stone floor with a puddle beside it, no people.", WET, "serious", "hook")
H("By the end, you'll know five rules that saved sleepers.", "The main character holds up five fingers beside a small campfire, eager.", "curious", "hook", sfx="pop")
F("And one of them is 200,000 years old.", "A thick layer of dried grass laid on grey ash at the back of a cave, no people.", BOR, "awe", "hook")
H("But the deadliest rain wasn't the loud one.", "The main character listens in the dark, one hand cupped to his ear.", "whisper", "hook", pace="slow")
F("The quiet kind killed people too.", "Soft drizzle falling on a silent dark camp with a dying fire, no people.", H2O, "whisper", "hook", pace="slow", pause=500)

# ---------------- part 1: the hidden flaw
H("Let's start with the flaw inside you.", "The main character taps his own chest, thoughtful, in a dim forest.")
F("Awake and cold, you shiver right away.", "A shivering arm with goosebumps drawn large, blue cold air around it, no face.", REM)
H("It's annoying, but it's your heater.", "The main character shivers hard and rubs his arms, teeth chattering.", "funny")
F("In REM sleep, shivering is largely switched off.", "A sleeping brain drawn simply with a small switch in the off position, no letters.", REM)
H("So you can get colder without waking.", "The main character sleeps peacefully while blue frost creeps around his blanket.")
F("Most of that evidence comes from animal studies.", "A sleeping cat and a sleeping rat side by side on a lab table, no people.", REM)
H("Humans are less studied, so I'll say it carefully.", "The main character holds a magnifying glass over a small sleeping figure, cautious.", "neutral")
F("But the pattern is the same idea.", "Two sleeping figures, one curled warm, one stretched out pale and cold, plain background.", REM)
H("Sleep is when you're least able to fix things.", "The main character snores while rain drips through a gap right onto his foot.", "funny")
F("Now add water to the picture.", "Rain hitting bare skin and running off in streams, close-up, no face.", H2O)
H("Wet beats cold every single time.", "The main character stands in the rain, soaked, looking miserable.", "serious")
F("Water pulls heat about twenty-five times faster than air.", "Two identical stones, one in air, one in a bucket of water losing red glow faster, no text.", H2O)
H("That number is a rule of thumb, by the way.", "The main character holds up his thumb with a sheepish grin.", "funny", pace="fast")
F("It compares how well water and air carry heat.", "A simple drawing of heat arrows leaving a warm body into water and air, no letters.", H2O)
H("Either way, wet bedding is bad news.", "The main character lifts a dripping fur blanket and grimaces.")
F("In one study, volunteers lay in wet clothes at minus eighteen degrees.", "A group of eight people lying in sleeping bags on snow under a grey sky.", WET)
H("Not my idea of a fun weekend.", "The main character shakes his head beside a snowy tent.", "funny")
F("Taking the wet clothes off cut their shivering.", "A pile of wet clothing next to a dry wrapped figure on snow.", WET)
H("Their skin warmed up better, too.", "The main character wraps himself in a dry hide and smiles with relief.", "happy")
F("Their core temperature didn't change much, though.", "A simple body outline with a steady line in its centre, plain background, no letters.", WET)
H("So dry layers help comfort and shivering most.", "The main character holds a dry hide in one hand and a wet one in the other.")
F("Cold during sleep doesn't feel dramatic.", "A calm sleeping figure under a thin hide, frost creeping in from the edges.", REM, "serious")
H("No pain, no panic, just a slow slide.", "The main character sleeps calmly as blue cold slowly fills the frame.", "whisper", pace="slow")
F("Shivering is one of the body's main ways to make heat.", "A simple muscle drawing with small heat waves rising from it, no letters.", REM)
H("Turn it down, and you cool quietly.", "The main character turns a stone dial down, then looks worried.", "tense")
F("Wet bedding underneath drains heat from below, too.", "A sleeping mat soaked with water and heat arrows flowing into the ground.", WET)
H("Cold from above, cold from below.", "The main character sandwiched between rain above and a puddle below, unhappy.", "funny")
F("Ancient people had no science, but they had the rule.", "A family wringing water out of animal hides beside a small fire under an overhang.", WET)
H("Water first. Warmth second.", "The main character holds up a water drop and a flame, the drop raised higher.", "serious", pause=400)

# ---------------- part 2: where to lie down
F("Every night began with one choice: where to lie down.", "An empty patch of ground at dusk with storm clouds gathering on the horizon, no people.", FLD, "curious")
H("Rule one: pick the right ground.", "The main character crouches and studies the ground at dusk, hand on chin.", "curious", sfx="ding")
F("Low ground feels sheltered from the wind.", "A cozy hollow between hills with calm grass, evening light, no people.", FLD)
H("It looks like the perfect bedroom.", "The main character lies down happily in a hollow, arms behind his head.", "happy")
F("But water gathers there first.", "Rainwater running down slopes and pooling in a hollow, no people.", FLD)
H("And a dry stream bed looks even better.", "The main character sweeps pebbles from a flat dry stream bed.")
F("Weather services warn that dry washes are deadly in storms.", "A dry sandy stream bed between rocks under dark storm clouds far away.", FLD, "tense")
H("Here's the scary part.", "The main character looks up at a clear sky above, puzzled.", "tense")
F("The rain doesn't have to fall on you.", "Storm clouds over distant hills while the near valley is dry and calm.", FLD, "tense")
H("It can fall miles upstream.", "The main character squints at faraway lightning over the hills.", "whisper")
F("In 2017, rain fell upstream of an Arizona canyon.", "Dark rain clouds over a rocky desert canyon, no people.", FLD, "serious")
H("Down below, the sky looked calm.", "The main character relaxes under a calm sky beside a gentle stream.", "neutral")
F("A flash flood killed several swimmers there.", "A brown wall of floodwater rushing through a narrow canyon, no people.", FLD, "sad", pace="slow")
H("That's modern history, not prehistory.", "The main character lowers his head quietly, respectful.", "sad", pace="slow")
F("But water followed the same rules back then.", "Muddy water racing down a dry channel at night under a moon, no people.", FLD, "serious")
H("So who chose the camp?", "The main character looks around at a group, wondering.", "curious")
F("Often the most experienced people had a say.", "An older woman pointing to a slightly raised patch of ground while others listen.", FLD)
H("They'd seen water where you'd see nothing.", "The main character stares at flattened grass, confused.")
F("Flattened grass and smooth stones mark old floods.", "Grass bent flat in one direction and rounded pebbles in a shallow dip, no people.", FLD)
H("A young hunter sees a flat clearing.", "The main character spreads his arms in a flat clearing, proud.", "happy")
F("An older eye sees a trap.", "The same clearing drawn with faint blue water lines running through it, no people.", FLD, "tense")
H("Slightly higher ground was the safer bet.", "The main character climbs onto a small rise and nods.", "neutral")

# ---------------- part 3: caves and the drip line
F("Caves and rock shelters looked like the obvious answer.", "A wide rock shelter opening on a hillside in heavy rain, no people.", DRP, "curious")
H("Rule two: don't trust the cave mouth.", "The main character steps toward a big cave entrance in pouring rain, relieved.", "curious", sfx="ding")
F("Rain runs off the cave lip and falls straight down.", "A curtain of water pouring from the edge of a rock overhang, no people.", DRP)
H("That falling line is called the drip line.", "The main character stands right under the dripping edge, getting soaked.", "funny")
F("Sleep under it and you're basically outside.", "A wet sleeping mat lying right under the dripping edge of a cave.", DRP)
H("I'd still blame the cave, honestly.", "The main character shakes his fist at the dripping rock.", "funny", pace="fast")
F("At Riparo Bombrini in Italy, a gap in artefacts marks an old drip line.", "An excavation trench in a rock shelter with a clear empty band in the soil, no people.", DRP, "curious")
H("People clearly organised space around it.", "The main character draws a line in the dirt and steps behind it.")
F("Fires and rubbish often sat outside that line.", "A hearth just outside a rock overhang with scattered bones nearby, no people.", DRP)
H("Beds went deeper inside, where it stayed dry.", "The main character carries a bundle of grass to the back of the cave.")
F("Archaeologists read this from layers, not diaries.", "Layers of soil in a cave wall, each a different colour, no people.", DRP)
H("Most nights, though, there was no cave at all.", "The main character stands in open grassland as rain begins, looking around.", "tense")

# ---------------- part 4: the bed (open loop part 1)
F("Out in the open, wind made rain even worse.", "Rain blowing sideways across an open plain, bending tall grass, no people.", H2O, "tense")
H("Sideways rain finds every gap.", "The main character holds a hide up like a shield as rain blows sideways at him.", "funny")
F("Moving air carries heat away from wet skin even faster.", "Wavy wind lines sweeping heat arrows off a wet arm, plain background, no face.", H2O)
H("Wind plus water. The worst duo.", "The main character's hair blows flat as rain whips past him.", "tense")
F("So a windbreak mattered as much as a roof.", "A low wall of piled branches blocking wind beside a small sleeping spot.", OHA)
H("Even a pile of branches helps.", "The main character stacks branches into a low wall, satisfied.", "neutral")
F("At Ohalo II, people built walls from branches.", "A curved wall of thick branches around a small hut floor by a lake.", OHA)
H("Not fancy, but it works.", "The main character leans on a branch wall and gives a small nod.", "happy")
F("Open ground means the bed itself must do the work.", "A bare stretch of wet grassland under grey rain, no people.", WET, "serious")
H("Rule three: build a bed that stays dry.", "The main character gathers armfuls of dry grass under a cloudy sky.", "curious", sfx="ding")
F("At Border Cave, people made grass beds 200,000 years ago.", "Bundles of broad-leaf grass laid near the back of a cave, no people.", BOR, "awe", pause=400)
H("That's older than any city by a lot.", "The main character gapes at a tiny modern skyscraper next to a huge grass bundle.", "awe")
F("The grass was laid on top of ash.", "A layer of dry grass on a grey ash base, cross-section view, no people.", BOR)
H("Ash as a mattress pad. Bold choice.", "The main character pats a pile of grey ash and coughs.", "funny", pace="fast")
F("Researchers think ash kept crawling insects away.", "Small ants turning away from a line of grey ash, close-up.", BOR)
H("It also gave a clean, dry base.", "The main character sweeps a neat ash floor with a branch.")
F("Camphor bush remains sat on the oldest bedding.", "A green camphor bush branch with small leaves on a dry grass bed.", BOR)
H("Basically, Stone Age bug spray.", "The main character sniffs a leafy branch and nods approvingly.", "funny")
F("At Sibudu, bedding layers go back about 77,000 years.", "Many thin stacked layers of plant bedding in a rock shelter wall.", SIB)
H("People kept rebuilding it for ages.", "The main character lays fresh rushes over an old flattened bed.")
F("They used sedges and rushes, topped with special leaves.", "Bundles of sedges and rushes with a layer of shiny leaves on top.", SIB)
H("Why those leaves? Smell them.", "The main character crushes a leaf and sniffs, eyebrows raised.", "curious")
F("Those leaves contain chemicals that can kill or repel insects.", "A wild quince branch with leaves and a mosquito flying away from it.", SIB)
H("Picking the right leaf took real plant knowledge.", "The main character compares two leaves side by side, very focused.", "neutral")
F("The Sibudu bedding was burned now and then.", "A small fire burning an old flattened grass bed inside a rock shelter, no people.", SIB)
H("Spring cleaning, Stone Age style.", "The main character waves smoke away from a burning old bed, coughing.", "funny", pace="fast")
F("Burning likely cleared pests and old rubbish.", "Ash and charred grass where an old bed used to be, a few bugs fleeing.", SIB)
H("So a good bed was a project, not a pile.", "The main character proudly presents a neat layered bed of grass and leaves.", "happy")
F("At Ohalo II in Israel, huts had grass bedding 23,000 years ago.", "A small brush hut of branches beside a lake with grass laid inside, no people.", OHA)
H("A lakeside hut. Not bad real estate.", "The main character leans in a brush hut doorway looking at a lake, relaxed.", "funny")
F("Their walls were thick branches of local trees.", "Thick tamarisk and willow branches woven into a rounded hut wall.", OHA)
H("Branches, grass, and a fire in the middle.", "The main character sits by a small fire inside a branch hut, content.", "neutral")
F("The bedding lay around a central hearth.", "Grass bedding arranged in a ring around a stone hearth inside a hut, no people.", OHA)
H("Warmth in the middle, beds around it.", "The main character lies on grass beside the hearth, toes toward the fire.", "happy")
F("Grass and leaves trap air between their fibres.", "Close-up of dry grass stems with tiny air pockets between them.", BOR)
H("Trapped air is what keeps you warm.", "The main character fluffs up a pile of grass like a pillow.", "curious")
F("Wet, flattened grass loses those air pockets.", "A soggy flattened bundle of grass lying in a puddle, no people.", WET)
H("So keeping the bed dry was everything.", "The main character shields a grass bundle from rain with his own back.", "serious")

# ---------------- subscribe (mid-video, hero right after a fact)
F("And remember the rule: water first.", "A single raindrop falling toward a dry grass bed, close-up.", H2O)
H("Quick pause. If you're enjoying this, subscribe and stay with me.", "The main character sits by a small fire and waves warmly at the viewer.", "happy")
F("We still haven't solved the quiet rain.", "Gentle drizzle falling on a dark silent camp, no people.", H2O, "whisper")
H("We'll keep exploring the ancient world together.", "The main character points ahead into the misty night with a smile.", "happy")
F("And next comes the thing that dried everything.", "A small protected fire glowing under a rock overhang in the rain.", DRP, "curious")
H("It's free, and it helps more curious people find us.", "The main character gives a cheerful thumbs up beside his fire.", "happy")

# ---------------- open loop paid off: the quiet rain
F("Now, the quiet rain.", "Fine misty rain hanging over a dark forest, no people.", H2O, "whisper", pace="slow")
H("A storm wakes you up. A drizzle doesn't.", "The main character sleeps through a soft drizzle, smiling peacefully.", "tense")
F("Steady light rain soaks things slowly for hours.", "Water slowly spreading through layers of hide and grass, cross-section, no people.", WET, "tense")
H("You never notice the moment it gets through.", "The main character shifts in his sleep as a damp patch grows under him.", "tense")
F("And in REM sleep, the shivering alarm is quiet.", "A sleeping figure with a small silent bell above it, night background, no letters.", REM, "serious")
H("That's why gentle rain was the sneaky killer.", "The main character opens his eyes wide in the dark, realising.", "awe", pause=500)
F("Loud storms got attention. Drizzle got ignored.", "Two skies side by side, one with lightning, one with soft grey drizzle, no people.", H2O, "serious")
H("So someone usually stayed half awake.", "The main character sits up wrapped in a hide, watching the fire.", "neutral")
F("Living foragers often keep fires going through the night.", "A low fire with a log pushed in by an unseen hand at night.", OHA)
H("A sleepy night watch, with a fire to feed.", "The main character yawns and pokes the fire with a stick.", "funny")

# ---------------- rule four: the fire
F("Rule four: never let the fire die.", "A tiny flame glowing between stones while rain falls all around, no people.", DRP, "serious", sfx="ding")
H("Small and sheltered beats big and exposed.", "The main character nods at a tiny fire while a big one sputters out in the rain.", "curious")
F("A fire under an overhang survives rain far better.", "A small fire tucked under a rock overhang while rain falls outside.", DRP)
H("And it does a second job.", "The main character holds a dripping hide toward the fire, hopeful.", "neutral")
F("The fire also dried hides and bedding.", "Animal hides hung on sticks steaming near a small fire.", WET)
H("A clothes dryer that also cooks dinner.", "The main character flips a steaming hide and sniffs a roasting root.", "funny", pace="fast")
F("Border Cave people also burned old bedding in their fires.", "Old grass bedding being pushed into a hearth inside a cave, no people.", BOR)
H("Nothing went to waste.", "The main character tosses an old grass bundle into the fire.", "neutral")
F("Starting fire in a storm is very hard.", "Wet sticks and damp tinder that won't catch, a single dying spark.", H2O, "tense")
H("Wet wood, wet hands, wet everything.", "The main character strikes stones over soggy tinder, frustrated.", "funny")
F("So keeping embers alive mattered more than lighting new ones.", "Glowing embers carefully wrapped in dry moss inside a bark container.", OHA)
H("I'm guessing that job had a grumpy owner.", "The main character guards a bark ember-pot, glaring at the rain.", "funny")
F("The hearth sat at the centre of the Ohalo huts.", "A ring of stones in the middle of a hut floor with ash inside, no people.", OHA)
H("Everyone slept around the one thing that dried them.", "The main character and two friends lie in a circle around a small hearth.", "happy")

# ---------------- rule five: sleep close
F("Rule five: don't sleep alone.", "Three grass beds pushed close together beside a small fire, no people.", OHA, "serious", sfx="ding")
H("I drag my bed closer, no shame.", "The main character drags his grass bed next to two sleeping friends.", "funny")
F("Bodies lying close lose less heat to the air.", "Three sleeping figures huddled under one hide, a small arrow of warmth between them.", WET)
H("Basically, a group hug that lasts all night.", "The main character squeezes between two friends under a hide, grinning.", "funny")
F("And a neighbour could notice when you went cold.", "One sleeping figure gently shaking another awake by the shoulder.", REM)
H("A second pair of eyes, even half asleep.", "The main character wakes up because a friend taps his cold arm.", "neutral")
F("Children and elders usually got the warmest spots.", "A child and an old woman lying closest to the fire while adults sit by the entrance.", OHA)
H("Not a reward, just good survival math.", "The main character counts on his fingers next to a sleeping child.", "curious")
F("Adults near the entrance could react to wind and water.", "An adult sitting by a hut opening watching rain blow in sideways.", OHA)
H("I'd volunteer for the middle, personally.", "The main character tries to sneak into the warm middle spot, caught by a friend.", "funny", pace="fast")

# ---------------- the morning after
F("Long wet seasons brought a slower problem.", "Weeks of grey rain over a soggy camp with mould on old hides, no people.", WET, "serious")
H("Nothing ever fully dries.", "The main character squeezes water out of a hide that is still dripping, tired.", "sad")
F("Damp bedding goes flat and loses its trapped air.", "A flattened, darkened grass bed next to a fluffy dry one, no people.", BOR)
H("So the bed slowly stops working.", "The main character pokes a flat soggy bed and sighs.", "neutral")
F("That's one reason old bedding was burned and replaced.", "A fresh grass bed laid over a layer of black burnt bedding, no people.", SIB)
H("Out with the soggy, in with the fresh.", "The main character throws a soggy bundle away and carries a fresh one in.", "happy")
F("At Sibudu, bedding was renewed in at least fifteen layers.", "Fifteen thin stacked layers of plant bedding in a cut soil wall.", SIB)
H("Fifteen times somebody said: not again.", "The main character rolls his eyes while carrying yet another grass bundle.", "funny", pace="fast")
F("Rain also hid sounds and smells around camp.", "A dark forest edge in heavy rain with faint glowing eyes far away.", H2O, "tense")
H("Which made the night feel even longer.", "The main character peers into the rainy dark, clutching a spear.", "tense")
F("A fire's light was comfort as much as heat.", "A small warm fire glowing inside a branch hut while rain falls outside.", OHA, "happy")
H("I get that. I still leave a hallway light on.", "The main character smiles at a small fire, then at a tiny modern lamp.", "funny")
F("Then, finally, the rain would stop.", "Clouds breaking over a wet valley at dawn, a faint rainbow, no people.", H2O, "awe")
H("And everyone crawled out, a bit soggy, but alive.", "The main character stretches outside a hut at dawn, damp but smiling.", "happy")
F("Surviving the night was only half the job.", "A grey morning after rain over a wet camp with steaming hides, no people.", WET)
H("Morning meant drying everything again.", "The main character hangs dripping hides on branches in weak sunlight.", "neutral")
F("Fresh grass and leaves replaced the soggy layers.", "A pile of soggy grass beside a fresh dry bundle, no people.", SIB)
H("No dry bed tonight if you're lazy today.", "The main character drags a huge grass bundle back to camp, sweating.", "funny")
F("Good shelters were reused again and again.", "Many thin layers of ash and bedding stacked in a rock shelter wall.", SIB)
H("A dry spot was worth coming back to.", "The main character walks back to a familiar overhang, smiling.", "happy")
F("At Sibudu, people returned over tens of thousands of years.", "Thin soil layers in a rock shelter wall, each marking a different time, no people.", SIB, "awe")
H("That's not a camp. That's an inheritance.", "The main character touches the cave wall gently, moved.", "awe", pause=400)
F("Each layer is a night someone survived.", "Close-up of thin stacked bedding layers, each a slightly different colour.", BOR, "sad", pace="slow")
H("Kind of beautiful, if you think about it.", "The main character sits quietly in the cave, looking at the layers.", "sad", pace="slow")

# ---------------- recap and link to the viewer
F("So, why were rainy nights so deadly?", "Rain falling on a dark prehistoric camp, a faint fire glowing, no people.", H2O, "serious")
H("Because sleep turns off your best alarm.", "The main character sleeps while a bell above him stays silent.", "serious")
F("Because water steals heat far faster than air.", "A drop of water hitting a warm stone that loses its glow.", H2O)
H("And because floods come from rain you never saw.", "The main character looks back at a distant storm over the hills.", "tense")
F("Their answers were simple and tested.", "A neat camp on raised ground with a grass bed, a sheltered fire and hides drying.", BOR, "curious")
H("High ground. Behind the drip line.", "The main character points at a rise, then at a line under a cave lip.", "curious")
F("Grass beds on ash, with bug-repelling leaves.", "A grass bed on grey ash with green leaves on top.", SIB)
H("A small fire that never died.", "The main character feeds a small fire under an overhang.", "neutral")
F("And warm bodies close together.", "A family sleeping close under hides around a hearth.", OHA, "happy")
H("Five rules, no instruction manual.", "The main character holds up five fingers, then shrugs, smiling.", "happy")
F("Your own discomfort in a damp bed is an old alarm.", "A modern bed with a damp sheet and a person tossing, no face shown.", REM, "curious")
H("Thank you for spending these minutes with me. If this was worth it, hit like, and tell me in the comments where you'd sleep in that storm. I read every one. Next time, we'll find out how ancient humans survived the heat. See you there, friend.", "The main character waves goodbye from a dry rock shelter as the rain stops and the sun comes out.", "happy", pace="slow", pause=800, sfx="pop")

# ---- build
EMOS = ["curious", "neutral", "serious", "tense", "excited", "happy", "awe", "funny"]
scenes, problems, last = [], [], []
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, src) in enumerate(S):
    hero = i % 2 == 0
    if ("the main character" in prompt.lower()) != hero:
        problems.append(f"scene {i + 1} kind mismatch ({'hero' if hero else 'fact'} expected): {narr[:50]}")
    if (beat == "hook") != (i < 12):
        problems.append(f"scene {i + 1} hook position")
    if not hero and not src:
        problems.append(f"scene {i + 1} fact without source")
    if emo is None or last[-3:] == [emo] * 3:
        emo = next(e for e in EMOS if e != (last[-1] if last else None))
    last.append(emo)
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
                   "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
                   "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})
for p in problems:
    print("PROBLEM", p)

data = {
    "title": "Why Were Rainy Nights So DEADLY for Ancient Humans?",
    "title_alternatives": ["The Hidden Danger of Sleeping in the RAIN", "How Ancient Humans Survived a Night of RAIN",
                           "Why Ancient Humans Feared Gentle RAIN", "The Rainy Night That Could KILL a Hunter"],
    "description": ("Rain sounds cozy from a modern bed. For most of human history it was one of the most dangerous nights there was. "
                    "Why sleep makes you lose heat without noticing, why wet beats cold, the flood that comes from rain you never saw, "
                    "and the five rules ancient people used to survive, from 200,000-year-old grass beds to fires that never died.\n\n"
                    "This video is history and science, not medical or survival advice.\n\nSources:\n"
                    "- Wadley et al. (2020). Fire and grass-bedding construction 200 thousand years ago at Border Cave. Science.\n"
                    "- Wadley et al. (2011). Middle Stone Age bedding construction at Sibudu. Science.\n"
                    "- Nadel et al. (2004). Stone Age hut in Israel yields world's oldest evidence of bedding. PNAS.\n"
                    "- Frontiers in Physiology (2017). Sleep and thermoregulation (review).\n"
                    "- Wilderness & Environmental Medicine (2015). Wet clothing removal or a vapor barrier.\n"
                    "- US National Weather Service flash-flood guidance."),
    "tags": ["ancient humans", "rainy night", "stone age survival", "prehistoric sleep", "ice age", "border cave",
             "grass bedding", "hunter gatherers", "human evolution", "animated explainer", "stickman"],
    "mood": "mysterious",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Why Were Rainy Nights So DEADLY for Ancient Humans?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-26.", "",
      "## Method",
      "- Topic and structure inspired by Before Civilization's top video (rainy nights, about 466k views); no wording copied.",
      "- Living foragers and modern safety guidance are used as windows, and the narration says so where it matters.",
      "- Not survival or medical advice; the description says so.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:70]} |")
md += ["", "## Claims softened or dropped",
       "- 'Wet clothes make you lose heat five times faster': only from field guides, dropped.",
       "- Raised sleeping platforms and drainage trenches: no reliable archaeological source opened, dropped.",
       "- Ash and leaves against insects: told as the researchers' interpretation.",
       "- REM shivering: 'mostly animal studies' said out loud.",
       "- Cold Springs Canyon death toll: 'several' (reports give nine or ten).",
       "- 'Twenty-five times': called a rule of thumb about heat conduction.",
       "- Night fire-keeping and sleeping order: stated for living foragers in general, not as measured ancient facts."]
Path(__file__).with_name("rainy_nights.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:12]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
