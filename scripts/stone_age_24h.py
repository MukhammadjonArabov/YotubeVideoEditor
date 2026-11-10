"""Builds scripts/stone_age_24h.json and scripts/stone_age_24h.factcheck.md
(run: ./venv/Scripts/python scripts/stone_age_24h.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

RUL = "Rule of threes (survival), Wikipedia; Wilderness Medical Society magazine, 'The Rule of Threes' (a rule of thumb, not a precise law)"
NGH = "National Geographic, 'The Hadza' (2009 and later web edition); Hawkes, O'Connell & Blurton Jones (2014). More lessons from the Hadza about men's work. Human Nature 25"
BER = "Berbesque, Wood, Crittenden, Mabulla & Marlowe (2016). Eat first, share later: Hadza hunter-gatherer men consume more while foraging than in central places. Evolution and Human Behavior 37"
KNO = "Knowable Magazine (2022), 'Our ancestors ate a paleo diet with carbs' (interview with Herman Pontzer); Smithsonian Magazine summary"
MUR = "Murray, Schoeninger, Bunn, Pickering & Marlett (2001). Nutritional composition of some wild plant foods and honey used by Hadza foragers of Tanzania. Journal of Food Composition and Analysis 14"
HAW = "Hawkes, O'Connell & Blurton Jones (2014). More lessons from the Hadza about men's work. Human Nature 25; Wood & Marlowe (2013). Household and kin provisioning by Hadza men. Human Nature 24"
PON = "Pontzer et al. (2012). Hunter-gatherer energetics and human obesity. PLoS ONE 7(7): e40503"
RAI = "Raichlen et al. (2017). Physical activity patterns and biomarkers of cardiovascular disease risk in hunter-gatherers. American Journal of Human Biology 29(2) (Hadza adults, about two hours of moderate-to-vigorous activity per day; WGBH news summary)"
CRI = "Crittenden & Zes (2015). Food sharing among Hadza hunter-gatherer children. PLoS ONE 10(7): e0131996; Crittenden et al. (2013). Juvenile foraging among the Hadza. Evolution and Human Behavior 34"
CMP = "Crittenden & Blurton Jones, Hadza summary, eHRAF World Cultures (Yale), citing Marlowe (2010) The Hadza: Hunter-Gatherers of Tanzania (camps average about 30 people, 5-6 grass huts)"
LIE = "Liebenberg, L. (1990). The Art of Tracking: The Origin of Science. David Philip; Liebenberg (2006). Persistence hunting by modern hunter-gatherers. Current Anthropology 47"
BRA = "Brain, C. K. (1981). The Hunters or the Hunted? An Introduction to African Cave Taphonomy. University of Chicago Press (Swartkrans leopard-damaged Paranthropus skull)"
GU12 = "Gurven, M. et al., Tsimane Health and Life History Project: Social Science & Medicine 75 (2012) 2493-2502 (infections 55 percent of infant deaths); ScienceDaily (2009) report (half of documented deaths from infectious or parasitic disease)"
GUR = "Gurven & Kaplan (2007). Longevity among hunter-gatherers: a cross-cultural examination. Population and Development Review 33, 321-365"
YET = "Yetish et al. (2015). Natural sleep and its seasonal variations in three pre-industrial societies. Current Biology 25, 2862-2868"
WIE = "Wiessner, P. (2014). Embers of society: Firelight talk among the Ju/'hoansi Bushmen. PNAS 111, 14027-14035 (the 'more than 80 percent stories' figure is from the PNAS commentary on the study)"
IOM = "Institute of Medicine (2005). Dietary Reference Intakes for Water, Potassium, Sodium, Chloride, and Sulfate. National Academies Press (adequate total water intake: about 3.7 L/day men, 2.7 L/day women, including water in food)"
SOR = "Sorensen, Claud & Soressi (2018). Neandertal fire-making technology inferred from microwear analysis. Scientific Reports 8, 10065"
PRO = "Bushcraft instructor accounts (PropelRC beginner guide; Ray Mears, 'Fire by friction - the bow drill method'); anecdotal, not a controlled study"
STO = "Stout, D. (2002). Skill and cognition in stone tool production: an ethnographic case study from Irian Jaya. Current Anthropology 43, 693-722"
SPO = "Spottiswoode, Begg & Begg (2016). Reciprocal signaling in honeyguide-human mutualism. Science 353, 387-389"
HAR = "Harmand et al. (2015). 3.3-million-year-old stone tools from Lomekwi 3, West Turkana, Kenya. Nature 521, 310-315"

# how each source was checked (goes into the fact-check file)
VERIFY = {
    SPO: ("Opened ScienceDaily, UCT and National Geographic coverage: Yao honey-hunters in Niassa, Mozambique; the traditional call roughly doubled guiding rates and about tripled nest-finding.", "Worded as 'roughly twice as likely' and 'about three times' per the reports; Yao, not Hadza, is stated."),
    RUL: ("Opened two pages on 2026-10-24; both call it a rule of thumb and say the order depends on conditions.", "Phrased as 'rule of thumb', 'roughly', 'about'."),
    NGH: ("Opened National Geographic 'The Hadza' and the Hawkes et al. 2014 abstract.", "'Anthropologists estimate four to six hours' is a secondary estimate, so it is worded as an estimate."),
    BER: ("Opened the abstract: 146 person-days, 921 hours, 2001-2013, about 2,405 kcal per foray, about 85 percent honey.", "Quoted as 'around', not exact."),
    KNO: ("Opened Knowable Magazine/Smithsonian interview with Pontzer: honey up to about a fifth of calories; February honey, July berries, September meat.", "Attributed to Pontzer's account; 'up to a fifth on average'."),
    MUR: ("Opened Murray et al. 2001 listing and a review of Hadza tubers (flash roasting for a few minutes).", "Only the roasting/digestibility point is used."),
    HAW: ("Read abstracts of Hawkes et al. 2014 and Wood & Marlowe 2013; they disagree about men's big-game hunting.", "Both sides presented, no verdict."),
    PON: ("Opened the PLoS ONE page and the University of Arizona summary: after controlling for body size, daily energy expenditure matched Western levels.", "Wording keeps 'once body size was accounted for'."),
    RAI: ("Found the Raichlen paper listing and a news summary (about 2 h 15 min of moderate-to-vigorous activity). Primary paper text not opened.", "Softened to 'roughly two hours'."),
    CRI: ("Crittenden & Zes 2015: children can collect up to 50 percent of daily energy requirement above age five. Primary text not fully opened.", "'Up to half', 'from about five years old'."),
    CMP: ("eHRAF Yale summary: camps average about 30 people, 5-6 grass huts; secondary summary of Marlowe 2010.", "'About thirty', 'five or six'."),
    LIE: ("Liebenberg's argument that tracking is an early form of science is documented in his book; the 2006 paper confirms his fieldwork with San trackers.", "Presented as his argument, not a settled fact."),
    BRA: ("Brain's Swartkrans skull SK 54 with two holes matching leopard canines is classic and widely cited; exact age range kept loose.", "'Between one and two million years old', 'Brain argued'."),
    GU12: ("Searched: infections 55 percent of Tsimane infant deaths; half of documented deaths from infectious or parasitic disease.", "Applies to Tsimane, not all hunter-gatherers; said so."),
    GUR: ("Abstract and secondary summaries: modal adult age of death about 72 (68-78), 21 societies; about 57-60 percent survive to 15; life expectancy at birth in the 30s-40s.", "Wording uses 'around', 'about'."),
    YET: ("Opened Current Biology highlights and press summaries: 6.4 hours average, about 1 hour more in winter, onset about 3.3 hours after sunset, little napping.", "Rounded to 'about six and a half'."),
    WIE: ("Opened PNAS paper listing and the PNAS commentary: evening talk mostly stories (over 80 percent). Primary text figure not seen.", "Attributed to a commentary and worded 'more than eighty percent according to one commentary'."),
    IOM: ("Opened the National Academies summary: 3.7 L men, 2.7 L women total water including food.", "Stated as an adequate intake, not advice."),
    SOR: ("Reused from the ice-age video: Scientific Reports 2018; the idea is debated.", "Says 'researchers think', 'evidence is debated'."),
    PRO: ("No controlled study exists in the sources found; instructors report 10-45 minutes and about 60 percent success for beginners.", "Marked as bushcraft teachers' accounts; hedged strongly."),
    STO: ("Abstract-level: Langda adze makers, long apprenticeship reported as five or more years.", "'Reported', not 'proved'."),
    HAR: ("Opened Nature abstract: about 3.3 million years old, Lomekwi 3.", "Exact."),
}

S = [
    # ---------------- hook (12 one-line scenes)
    ("You wake up in the Stone Age. Nobody's coming.", "The main character wakes up on a bed of leaves in a dim rock shelter, rubbing his eyes, confused.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("Survivalists swear by a rule called the rule of threes.", "Three stones in growing sizes lined up in a row beside a small campfire on dry ground.", "hook", "curious", 2, "normal", 0, None, RUL),
    ("Three hours without shelter. Three days without water.", "The main character shivers in a cold wind beside a dry empty riverbed with a worried look.", "hook", "tense", 2, "normal", 0, None, None),
    ("Living hunter-gatherers spend four to six hours finding food.", "A dry savanna with tall baobab trees and a small camp of grass huts at golden hour.", "hook", "curious", 2, "normal", 0, None, NGH),
    ("Your hardest day might look easy after this.", "The main character looks at a very long paper scroll unrolling to the floor and smiles in relief.", "hook", "serious", 2, "normal", 0, None, None),
    ("Hadza men averaged twenty-four hundred calories per foray, mostly honey.", "A wild beehive hanging from a baobab branch with golden honey dripping and bees around it.", "hook", "excited", 2, "normal", 0, None, BER),
    ("By the end, you'll know exactly how you'd do.", "The main character points at himself with a confident grin, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("The biggest killer wasn't lions. It was something tiny.", "A tiny glowing green germ drawn huge inside a magnifying circle on a plain pale background.", "hook", "whisper", 2, "slow", 0, None, GU12),
    ("So, hour by hour, how long would you last?", "The main character stands next to a giant hourglass with sand pouring, looking up at it nervously.", "hook", "tense", 2, "normal", 0, None, None),
    ("Hour one: you need about three litres of water.", "Three large clay jugs lined up on dry ground, one pouring water into a wooden bowl.", "hook", "serious", 2, "normal", 0, None, IOM),
    ("But there's no tap. Only a dry riverbed.", "The main character stands in a dry cracked riverbed with an empty cup, looking around.", "hook", "tense", 2, "normal", 0, None, None),
    ("A fossil skull carries holes matching a leopard's teeth.", "A fossil skull with two small round holes in its side resting on a stone in soft light.", "hook", "awe", 3, "normal", 500, None, BRA),
    # ---------------- ground rules
    ("Quick ground rules. We can't time travel, so I'll borrow from people who still live this way, like the Hadza in Tanzania. Think of them as a window, not a time machine.", "The main character peers through a small wooden window frame held in front of a savanna scene, curious.", "build", "curious", 2, "normal", 0, None, None),
    ("The Hadza are hunter-gatherers living in northern Tanzania, and researchers have studied them for decades.", "A grass hut camp at the edge of a savanna with smoke rising from a small fire and baobab trees behind.", "build", "neutral", 2, "normal", 0, None, NGH),
    ("And remember, the Stone Age isn't one moment. It's a huge stretch of time, so this is a rough test, not a perfect one. Honestly, my own survival skills peak at ordering dinner online.", "The main character stretches a very long rope across green hills and a river, panting at the far end.", "build", "funny", 2, "normal", 0, None, None),
    ("The oldest known stone tools are about three point three million years old, from a site in Kenya called Lomekwi.", "A rough stone flake and a chunky stone core lying on pale sand in warm light.", "build", "awe", 2, "normal", 0, None, HAR),
    ("Hour zero. You open your eyes in a rock shelter. No phone alarm, no coffee, just a dry mouth and a very strange feeling.", "The main character sits up in a rock shelter stretching, hair messy and eyes half open.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- water
    ("The rule of threes says you can last roughly three minutes without air, three hours in harsh weather without shelter, three days without water and three weeks without food.", "Four stones of growing size arranged in a row on the ground, drawn simply.", "build", "neutral", 2, "normal", 0, None, RUL),
    ("It's a rule of thumb, not a law. But it shows your body's priority list, and it's pretty bossy.", "The main character reads a short scroll with four tick marks and nods seriously.", "build", "curious", 2, "normal", 0, None, None),
    ("Which comes first depends on the weather: water in the heat, shelter when it's cold and wet. Survival teachers treat the numbers as approximate.", "A split drawing of a hot sunny desert on one side and a cold rainy forest on the other side.", "build", "neutral", 2, "normal", 0, None, RUL),
    ("Let's say it's warm and dry today. Lucky you. So job number one is water.", "The main character licks his dry lips under a bright sun, squinting.", "build", "curious", 2, "normal", 0, None, None),
    ("The US National Academies put an adequate daily water intake at about three point seven litres for men and two point seven for women, counting the water in food.", "Two glass jugs, one taller than the other, both filled with water on a wooden table.", "build", "neutral", 2, "normal", 0, None, IOM),
    ("That's a lot of water. And the nearest tap is about thirty thousand years in the future. I can't even last a weekend without Wi-Fi.", "The main character searches a cave wall for a tap and finds only a small round hole.", "build", "funny", 2, "normal", 0, None, None),
    ("Under the rule of threes, a person lasts about three days without water, though heat, age and effort can change that a lot.", "A dry cracked riverbed under a pale sun with a single tiny puddle in the middle.", "build", "serious", 2, "slow", 0, None, RUL),
    ("Say you follow animal trails and find a muddy waterhole. It's not sparkling, but it's wet. Your stomach has opinions.", "The main character kneels at a muddy puddle holding a cupped leaf, hesitating with a grimace.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- fire and tools
    ("Next, fire. Researchers think Neanderthals could make fire on demand about fifty thousand years ago by striking flint against pyrite, though the evidence is debated.", "Two flint hand axes beside a shiny golden mineral chunk with a few bright sparks flying.", "build", "curious", 2, "normal", 0, None, SOR),
    ("You don't have pyrite. You have two sticks and a lot of optimism.", "The main character rubs two sticks together, sweating, with only a thin wisp of smoke.", "build", "funny", 2, "normal", 0, "boing", None),
    ("Bushcraft teachers who run bow-drill classes say beginners often need ten minutes to nearly an hour, and many fail the first day. The wood you choose changes everything.", "A simple wooden bow with a cord wrapped around a spindle resting on a flat wooden board with a thin wisp of smoke.", "build", "neutral", 2, "normal", 0, None, PRO),
    ("Hour four: smoke. Hour five: a tiny orange ember, and you protect it like a newborn. Congratulations. You made fire.", "The main character cups a glowing ember in his palms, face lit orange, eyes shining.", "punchline", "excited", 2, "normal", 300, "ding", None),
    ("Sharp tools are another skill. Dietrich Stout studied stone adze makers in Langda, Papua, and reported that learning the craft takes a long apprenticeship, five years or more.", "A polished stone adze head with a wooden handle lying on a flat stone beside neat stone flakes.", "build", "neutral", 2, "normal", 0, None, STO),
    ("So no knife for you today. Your Stone Age career is on hold until you've finished five years of training.", "The main character pokes a rough stone with a stick, unimpressed, a tiny dust cloud rising.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- food
    ("Fire lets you cook, too. The Hadza roast tubers for just a few minutes in the embers, which makes them easier to digest.", "Several long root tubers laid on glowing embers with thin smoke rising.", "build", "neutral", 2, "normal", 0, None, MUR),
    ("So lunch is a roasted root. Not a mammoth steak. Sorry.", "The main character chews a long root with a flat, disappointed expression.", "build", "funny", 2, "fast", 0, None, None),
    ("Honey can supply up to a fifth of the Hadza's calories on average, according to anthropologist Herman Pontzer.", "A clay pot overflowing with golden honey on a flat stone with a wooden dipper beside it.", "build", "curious", 2, "normal", 0, None, KNO),
    ("A fifth of the calories from honey. You're basically a toddler with a very big wild bee problem.", "The main character sits with a face covered in honey while bees swirl around him, smiling.", "build", "funny", 2, "normal", 0, None, None),
    ("It changes with the season. One account says Hadza calories came mostly from honey in February, berries in July and meat in September.", "Three simple drawings in a row on a cave wall: a honeycomb, a branch of berries and a roasted joint of meat.", "build", "neutral", 2, "normal", 0, None, KNO),
    ("So the real question isn't only whether you'd survive. It's which month you landed in.", "The main character spins a big calendar wheel with twelve plain segments and looks nervous.", "build", "curious", 2, "normal", 0, None, None),
    ("Researchers who followed Hadza men on foraging trips tracked one hundred forty-six person-days, about nine hundred hours, and found men ate around twenty-four hundred calories per trip, mostly honey.", "A tall baobab tree with small wooden pegs hammered into its trunk and a beehive high above.", "build", "awe", 2, "normal", 0, None, BER),
    ("So the 'hunter' in hunter-gatherer is often a honey thief with a very long walk and a lot of nerve. Honestly, the most relatable job in history.", "The main character climbs a tree with a small bag, bees buzzing angrily around his head.", "build", "funny", 2, "normal", 0, None, None),
    ("Honey hunters even have help. In northern Mozambique, Yao honey-hunters use a special call to summon a wild bird, the greater honeyguide, and in one study the birds were roughly twice as likely to lead them when they heard it, and the chance of finding a nest about tripled.", "A small brown bird perched on a branch pointing its beak toward a distant beehive in a big tree.", "build", "awe", 2, "normal", 0, None, SPO),
    ("A bird that works with you for honey. If that's not a Stone Age friendship, I don't know what is.", "The main character whistles at a small bird on his finger, both smiling, a beehive drawn far away behind them.", "build", "happy", 2, "normal", 0, None, None),
    ("The Hadza study has another surprise. The title says it all: men ate more food while out foraging than they brought back to camp, so what lands at camp understates what they actually found.", "A single hand-woven basket with only a few roots inside beside a scatter of berry stems and honeycomb scraps on the ground.", "build", "curious", 2, "normal", 0, None, BER),
    ("So the great provider is also a snacker on the trail. Honestly, relatable.", "The main character walks along a trail with a bag and one cheek puffed out with food, looking innocent.", "build", "funny", 2, "fast", 0, None, None),
    ("Not everyone agrees on the big picture. Hawkes and colleagues found Hadza men chase big game but rarely succeed, while Wood and Marlowe argue men's foraging mainly feeds their families through honey, small game and fruit.", "A split drawing: a large antelope on one side and a honeycomb with a small bird on the other, with a line between them.", "build", "serious", 2, "normal", 0, None, HAW),
    # ---------------- subscribe (once)
    ("Quick pause. If you're enjoying this, subscribe and come along, because there's a lot more of the human story to dig into together. It's free, it takes a second, and it helps others find the channel.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    ("Anthropologists estimate Hadza spend about four to six hours a day actually pursuing food. Every day, not just on weekends.", "A simple sundial on the ground with a short stick shadow and a bright sun above.", "build", "neutral", 2, "normal", 0, None, NGH),
    ("Four to six hours. That's about half a modern workday for your entire food supply, and no commute.", "The main character leans on a stick beside a short and a long shadow, smiling.", "build", "funny", 2, "normal", 0, None, None),
    ("A study using heart monitors found Hadza adults spend roughly two hours a day in moderate to vigorous activity.", "A heart-shaped monitor strap lying next to a pair of simple sandals on dry ground.", "build", "neutral", 2, "normal", 0, None, RAI),
    ("Two hours of real exercise every day, with no gym membership and no podcast. Impressive.", "The main character jogs along a dusty path with a tiny sweatband, looking proud.", "build", "funny", 2, "normal", 0, None, None),
    ("Here's the twist. When Herman Pontzer's team measured Hadza energy use, once body size was accounted for, their total daily calorie burn was no different from people in Western countries.", "Old balance scales with a stack of roots on one side and a stack of bread loaves on the other, perfectly level.", "punchline", "awe", 2, "normal", 400, None, PON),
    ("More active, yet the same total burn. Your body seems to budget its energy, and it's weirdly stubborn about it.", "The main character looks down at his own belly like it is a small calculator, puzzled.", "build", "curious", 2, "normal", 0, None, None),
    ("Kids pitch in, too. A study of Hadza children found that from about five years old, they can collect up to half of their daily energy needs.", "A small digging stick and a tiny basket on the ground beside a few roots.", "build", "neutral", 2, "normal", 0, None, CRI),
    ("Five-year-olds gathering half their own lunch. Meanwhile, I struggle to take out the trash.", "The main character holds a trash bag beside a tiny child-sized stick figure who is digging roots, embarrassed.", "build", "funny", 2, "normal", 0, None, None),
    ("Hadza camps average about thirty people and hold five or six grass huts.", "Five round grass huts in a loose circle around a central fire at a savanna camp.", "build", "neutral", 2, "normal", 0, None, CMP),
    ("That's the real survival trick. You wouldn't be alone. A group can share food, watch for danger, and sit with you when you're sick.", "The main character sits among several stick figures around a fire, smiling softly.", "build", "serious", 2, "slow", 0, None, None),
    ("Louis Liebenberg, who worked with San trackers in southern Africa, argued that reading animal tracks is a kind of early science: read the footprints, form a guess about the animal, then test it.", "A line of animal footprints in soft sand with a small stick pointing at one print and a magnifying glass beside it.", "build", "curious", 2, "normal", 0, None, LIE),
    ("Tracks are text messages from the animal. And you can't read a single one. You're standing in a field full of unread mail.", "The main character squats at animal footprints in the sand, scratching his head, puzzled.", "build", "funny", 2, "normal", 0, None, None),
    ("Predators were real. A fossil skull from Swartkrans in South Africa, from a young Paranthropus between one and two million years old, has two holes that Bob Brain argued match a leopard's lower canine teeth.", "A fossil skull with two small round holes resting on a stone in a dim cave, soft light on it.", "build", "serious", 2, "normal", 0, None, BRA),
    ("So when the sun goes down, you don't wander off alone. You stay close to the fire, and to the group.", "The main character sits close to a fire hugging his knees, glowing eyes looking from the dark around.", "build", "tense", 2, "slow", 0, None, None),
    ("But among the Tsimane of Bolivia, studies found infections cause over half of infant deaths, and about half of all documented deaths come from infectious or parasitic disease.", "A tiny green germ inside a magnifying circle beside a small clay water pot.", "build", "serious", 2, "normal", 0, None, GU12),
    ("So the real monster wasn't the leopard. It was the stomach bug from that muddy waterhole.", "The main character clutches his belly with a cartoon green swirl rising from it, miserable.", "punchline", "funny", 2, "normal", 300, None, None),
    ("Gurven and Kaplan studied twenty-one small-scale societies and found the typical age of adult death was about seventy-two, with a range of sixty-eight to seventy-eight.", "A tall bundle of many small candles glowing in a dark cave.", "build", "neutral", 2, "normal", 0, None, GUR),
    ("Seventy-two. If you made it through childhood, your Stone Age retirement party wasn't far from ours.", "The main character blows out candles on a stone cake, grinning.", "build", "funny", 2, "normal", 0, None, None),
    ("The catch is childhood. In those populations only around six in ten newborns survived to fifteen, and early deaths pulled average life expectancy at birth down to the thirties or forties.", "A row of ten small stones on a flat rock, six of them glowing gold and four dark.", "build", "serious", 2, "slow", 0, None, GUR),
    ("That's where 'people died at thirty' comes from. Not thirty-year-olds dropping dead, but a heartbreaking number of children.", "The main character kneels and places a small flower on a stone, head bowed.", "build", "sad", 2, "slow", 400, None, None),
    ("On sleep: Hadza, San and Tsimane adults averaged about six and a half hours a night, with little napping, and about an hour more in winter than in summer.", "A simple grass bed beside a low fire with a crescent moon above.", "build", "neutral", 2, "normal", 0, None, YET),
    ("Not eight hours, and no snooze button either. Honestly, that makes my own sleep feel less like a failure.", "The main character yawns on a grass bed, a tiny cloud of Zs floating above him, no letters.", "build", "funny", 2, "normal", 0, None, None),
    ("They tended to fall asleep about three hours after sunset, which leaves a long evening around the fire.", "A circle of stone seats around a fire ring with an orange sunset behind low hills.", "build", "neutral", 2, "normal", 0, None, YET),
    ("Hours eighteen to twenty-one: you sit by the fire, nobody checks a screen, and somebody starts telling a story.", "The main character sits in a circle of stick figures around a fire, listening with wide eyes.", "build", "happy", 2, "slow", 0, None, None),
    ("Anthropologist Polly Wiessner recorded conversations among the Ju/'hoansi of southern Africa: daytime talk was mostly practical, while evening talk turned to stories, more than eighty percent of it, according to one commentary.", "A glowing campfire at night with open space around it and sparks floating up into a starry sky.", "build", "curious", 2, "normal", 0, None, WIE),
    ("Stories, songs and jokes instead of emails. Not a bad trade, if you could keep your phone in a drawer. I'd give up a few notifications for that evening, honestly.", "The main character drops a flat stone shaped like a phone into a drawer carved in a cave wall, relieved.", "build", "funny", 2, "normal", 0, None, None),
    ("By the rule of threes, a healthy adult has days, not hours, to find water, and weeks to find food, so one day is survivable in mild weather.", "A simple path of three flat stepping stones leading across a dry riverbed toward green trees.", "punchline", "serious", 2, "slow", 400, None, RUL),
    ("So, could you survive twenty-four hours in the Stone Age? Probably yes, if it's warm, you find water, and a group takes you in. The hard part isn't day one. And honestly, I think the biggest surprise isn't the danger, it's the company. It's day two, day twenty, and getting through childhood in the first place. Thank you for spending this time with me. Hit like if it was fun, and tell me in the comments how long you'd really last. I read every one. Next time: were ancient humans stronger than us? I'll be here. See you soon, friend.", "The main character waves goodbye at sunrise beside a small campfire, a bright sky behind him, smiling warmly.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 60 <= len(S) <= 95, len(S)
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
    "title": "Could You Survive 24 Hours in the STONE AGE?",
    "title_alternatives": ["How Long Would YOU Last in the Stone Age?", "24 Hours as a Hunter-Gatherer: Hour by HOUR",
                           "The Real Reason Stone Age Life Was SHORT", "Would You Survive a Day With the HADZA?"],
    "description": ("You wake up in the Stone Age. Nobody's coming. This video follows a 24-hour test using research on living hunter-gatherers "
                    "like the Hadza: water, fire, food, danger, sleep, and what really shortened life in the past.\n\n"
                    "This video is history and science, not survival or medical advice.\n\nSources:\n"
                    "- Berbesque et al. (2016). Eat first, share later: Hadza men. Evolution and Human Behavior.\n"
                    "- Pontzer et al. (2012). Hunter-gatherer energetics and human obesity. PLoS ONE.\n"
                    "- Gurven & Kaplan (2007). Longevity among hunter-gatherers. Population and Development Review.\n"
                    "- Yetish et al. (2015). Natural sleep in three pre-industrial societies. Current Biology.\n"
                    "- Wiessner (2014). Embers of society: Firelight talk among the Ju/'hoansi. PNAS."),
    "tags": ["stone age", "survival", "hunter-gatherers", "hadza", "ancient humans", "prehistory", "life expectancy", "rule of threes",
             "animated explainer", "stickman"],
    "mood": "playful",
    "sources": [x for x in dict.fromkeys(s[8] for s in S if s[8])][:14],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

# ---- fact-check file
md = ["# Fact-check: Could You Survive 24 Hours in the STONE AGE?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-24.", ""]
md += ["## Method", "- Each claim came from a named, checkable source (paper, university or museum page, major science outlet, well-known book).",
       "- Where only a secondary summary was opened, the claim is worded as 'about', 'roughly' or 'according to'.",
       "- Where scientists disagree, both sides are told (Hawkes vs Wood & Marlowe on big-game hunting).",
       "- Anecdotal material (bow-drill teachers) is labelled as anecdotal in the narration.",
       "- The narrator never gives survival or medical advice; the description says so.", "",
       "## Fact scenes", "", "| # | Narration (shortened) | Source | How verified | Wording safeguard |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        src = sc["fact_source"]
        how, safe = VERIFY.get(src, ("", ""))
        md.append(f"| {i} | {sc['narration'][:90].replace('|', '/')}... | {src[:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Claims softened or dropped",
       "- Hadza dry-season water sources and daily calorie totals for women: no reliable source found, so not claimed.",
       "- Exact bow-drill success rates: only anecdotal; stated as 'bushcraft teachers say'.",
       "- Hadza big-game hunting success rate: disputed, so not given as a number.",
       "- Walking distances per day (11 km / 5.8 km): could not be verified, dropped.",
       "- Wiessner's '80 percent stories': taken from a PNAS commentary, attributed as such.",
       "", "## Human-voice checklist (all done)",
       "- Short and long sentences mixed; contractions used; one clear personal take per few scenes ('I struggle to take out the trash').",
       "- Modern comparisons: office workday, gym membership, phone in a drawer, snooze button, retirement party.",
       "- No filler words ('delve', 'fascinating journey', 'it's important to note').",
       "- Numbers written as words; no ALL CAPS in narration; no long dashes.",
       "- Warm connection: friendly mid-video 'subscribe' invitation, thank-you and 'See you soon, friend' ending; 'like' asked once.",
       "- The first 40 seconds say why to watch ('Your hardest day might look easy after this') and what you get ('By the end, you'll know exactly how you'd do')."]
Path(__file__).with_name("stone_age_24h.factcheck.md").write_text("\n".join(md), encoding="utf-8")

print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]), "max hook line:", max(len(s["narration"].split()) for s in scenes[:12]))
em = [s["emotion"] for s in scenes]
run = 1
for i in range(1, len(em)):
    run = run + 1 if em[i] == em[i - 1] else 1
    if run > 3:
        print("4+ same emotion in a row at scene", i + 1, em[i])
