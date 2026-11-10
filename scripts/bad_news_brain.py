"""Builds scripts/bad_news_brain.json and scripts/bad_news_brain.factcheck.md
(run: ./venv/Scripts/python scripts/bad_news_brain.py).
Psychology video, ~18 minutes, a new picture every ~4 seconds (import with --minutes 18 --seconds-per-image 4).
P(...) adds one hero scene and one fact scene, so hero/fact always alternate. Approved by the owner 2026-10-27."""
import json
from pathlib import Path

UPW = "Robertson et al. (2023). Negativity drives online news consumption. Nature Human Behaviour 7, 812-822"
SOR = "Soroka, Fournier & Nir (2019). Cross-national evidence of a negativity bias in psychophysiological reactions to news. PNAS 116, 18888-18892"
BAU = "Baumeister, Bratslavsky, Finkenauer & Vohs (2001). Bad is stronger than good. Review of General Psychology 5, 323-370"
OHM = "Öhman, Flykt & Esteves (2001). Emotion drives attention: Detecting the snake in the grass. Journal of Experimental Psychology: General 130, 466-478"
NES = "Nesse (2001). The smoke detector principle. Annals of the New York Academy of Sciences 935, 75-85; Nesse (2019), Evolution, Medicine, and Public Health"
ITO = "Ito, Larsen, Smith & Cacioppo (1998). Negative information weighs more heavily on the brain. Journal of Personality and Social Psychology 75, 887-900"
VAI = "Vaish, Grossmann & Woodward (2008). Not all emotions are created equal: the negativity bias in social-emotional development. Psychological Bulletin 134, 383-403"
LOS = "Brown, Imai, Vieider & Camerer (2021/2024), meta-analysis of loss aversion (lambda about 1.8-2.1); Gal & Rucker (2018), The loss of loss aversion, Journal of Consumer Psychology"
MAT = "Mather & Carstensen (2005). Aging and motivated cognition: the positivity effect in attention and memory. Trends in Cognitive Sciences 9, 496-502; Reed & Carstensen (2012), Frontiers in Psychology"
KIS = "Wood & Kisley (2006), Psychology and Aging; Kisley, Wood & Burrows (2007), Psychological Science (older adults show no ERP negativity bias)"

VERIFY = {
    UPW: ("Searched 2026-10-27; LMU press release, Nieman Lab, PsyPost and the paper PDF hosted by LMU: about 105,000 Upworthy headline variants, 22,743 randomised tests, about 5.7 million clicks from more than 370 million impressions; each extra negative word raised click-through by 2.3% for an average-length headline; positive words lowered it; sad words worked more than angry or scary ones.",
          "'About two percent per negative word', 'one big site', not 'all news'."),
    SOR: ("Searched 2026-10-27; PMC full text (PMC6754543), PsyPost: 1,156 people in 17 countries watched BBC World News clips with skin-conductance and pulse sensors; negative stories drew stronger reactions on average; not significant in every country, big differences between individuals; the authors say there is a large audience for positive news.",
          "'On average', 'not in every country', 'people differ a lot' said out loud."),
    BAU: ("Searched 2026-10-27; the paper PDF hosted at UNC (abstract and opening): bad events have stronger effects across everyday events, major life events, close relationships and learning; hardly any exceptions found. The Gottman 5-to-1 link is only from secondary sources.",
          "Called a big review; the 5-to-1 ratio is not used as a number."),
    OHM: ("Searched 2026-10-27; abstract via Universidade Católica record and later reviews: snakes and spiders found faster among flowers and mushrooms than the reverse; search time for threats less affected by the number of distractors; a 2012 review says snakes are detected faster in demanding displays.",
          "'Found faster' only; no millisecond numbers."),
    NES: ("Searched 2026-10-27; University of Michigan Deep Blue record and Nesse's own page: when a defense is cheap and the harm it prevents is large, the best system gives many false alarms (signal detection logic).",
          "Explained as an idea from evolutionary medicine, not a measured fact."),
    ITO: ("Searched 2026-10-27; PubMed 9825526 abstract: late positive potentials larger for negative than positive pictures matched for probability, extremity and arousal. Later ERP studies are mixed (PMC4084413 review).",
          "'In this study', and 'later studies are mixed' is said."),
    VAI: ("Searched 2026-10-27; Birkbeck repository and PMC3652533 abstract: a tendency to attend to, learn from and use negative information more than positive; the paper reviews when it appears in development (infants by about the end of the first year).",
          "Only the review's main claim; no infant percentages."),
    LOS: ("Searched 2026-10-27; Judgment and Decision Making 2022 discussion and Social Science Space: meta-analysis gives lambda about 1.8-2.1 (losses weigh about twice as much); Gal & Rucker argue it is overgeneralised, especially for small stakes; critics do not claim there is no asymmetry.",
          "'About twice, in many studies', the dispute stated."),
    MAT: ("Searched 2026-10-27; Mather & Carstensen 2005 PDF and Reed & Carstensen 2012 (PMC3459016): older adults attend to and remember positive more than negative relative to younger adults; called an 'effect' because it is a relative shift; some studies find no age difference.",
          "'Relative to younger people', 'not every study finds it'."),
    KIS: ("Searched 2026-10-27; summarised in PMC4084413: Wood & Kisley 2006 found the ERP negativity bias in younger but not older adults; Kisley et al. 2007 traced it to smaller responses to negative images with age.",
          "'In brain-wave studies', 'shrinks' rather than 'disappears for everyone'."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None))


# ================= hook (12 short lines)
P("One sad word in a headline gets more clicks.", "The main character in bed at night stares at a glowing phone, eyes wide, a tiny grey rain cloud above the screen.",
  "Researchers measured it across a hundred thousand headlines.", "A huge wall of small newspaper-style cards with dark storm clouds drawn on some of them, no letters.",
  UPW, "tense", "curious", "hook", hsfx="whoosh")
P("You click, you scroll, you feel worse.", "The main character hunched over a phone on a sofa, shoulders sinking, dark circles under his eyes.",
  "Bad news even changes your skin and pulse.", "A finger wearing a small sensor clip with a jagged heartbeat line beside it, plain background.",
  SOR, "serious", "serious", "hook")
P("Why does this matter to you?", "The main character turns away from his phone and looks straight at the viewer, serious.",
  "Because this pull decides what you fear and remember.", "A small brain drawn with a magnet pulling dark clouds toward it, warm paper background.",
  BAU, "serious", "excited", "hook")
P("By the end, you'll know where it came from.", "The main character holds a lantern up in a dark cave, curious and determined.",
  "And how to notice it without obeying it.", "A small bell alarm on a stone with a calm hand hovering above it, no letters.",
  NES, "curious", "curious", "hook")
P("It started long before phones.", "The main character sits by a campfire at night in the forest, ears perked toward rustling bushes.",
  "Snakes are spotted faster than flowers.", "A snake hidden among bright flowers and mushrooms, top-down view, warm paper background.",
  OHM, "tense", "tense", "hook")
P("But one group barely has this pull at all.", "The main character peeks around a tree trunk, whispering, finger on his lips.",
  "Who? We'll find out later.", "A dim doorway with soft warm light behind it and an old rocking chair half visible, no people.",
  MAT, "whisper", "whisper", "hook", fpace="slow", fpause=500)

# ================= 1. the headline experiment
P("Let's start with that headline thing, because it's a little creepy.", "The main character sits at a wooden table with a cup of tea, frowning at a phone.",
  "The data came from Upworthy, a website that tested headlines on real readers.", "A simple laptop on a desk showing two different coloured boxes side by side, no letters.",
  UPW, "curious")
P("Same story, two different titles. Which one gets the click?", "The main character holds two paper signs, one in each hand, looking from one to the other.",
  "Upworthy ran over twenty-two thousand of these head-to-head tests.", "Two paths splitting from one road, each leading to a small crowd of stick figures, warm paper background.",
  UPW)
P("Researchers later counted the happy and sad words in each version.", "The main character uses a magnifying glass on a long paper scroll, very focused.",
  "Each extra negative word raised clicks by about two percent.", "A small staircase going up with a dark raindrop on each step, no letters.",
  UPW, fe="awe", fpause=400)
P("Two percent sounds tiny. Multiply it by millions of readers.", "The main character stares at a mountain of tiny people stacked like a hill, jaw dropped.",
  "Those tests drew about five point seven million clicks.", "An enormous pile of small computer mouse shapes forming a hill under a cloudy sky.",
  UPW, "funny")
P("And the sneakiest part? Happy words did the opposite.", "The main character holds a smiling sun drawing that slowly droops in his hand.",
  "Positive words actually lowered the click rate.", "A bright sun with a small arrow pointing down beside it, plain background.",
  UPW)
P("So writers aren't evil. They're just reading the scoreboard.", "The main character shrugs beside a scoreboard made of sticks and stones, with dark marks on one side.",
  "Sad words worked even better than angry or scary ones.", "Three small clouds, one crying, one red and angry, one shaking, the crying one biggest.",
  UPW, "neutral")
P("Sad beats angry? I didn't see that coming.", "The main character scratches his head, puzzled, looking at a crying cloud.",
  "That's one big website, not every newspaper on earth.", "A single small house among a huge landscape of many different houses, warm paper background.",
  UPW, "curious")
P("Fair. So let's check bodies, not just clicks.", "The main character rolls up his sleeves and walks into a simple lab tent.",
  "Scientists tested over eleven hundred people in seventeen countries.", "A world map made of soft watercolour patches with seventeen small pins on it, no letters.",
  SOR)
P("They watched real news clips while wearing finger sensors.", "The main character sits in a chair watching a screen, a small clip on his finger.",
  "Negative stories raised skin sweat and changed heart rhythms on average.", "A wavy line that grows taller and spikier from left to right on a paper strip.",
  SOR, fe="serious")
P("Your fingers react before you've even decided how you feel.", "The main character looks at his own sweaty fingertips in surprise.",
  "But the effect wasn't significant in every country.", "Seventeen small flags, most with a bright mark, a few plain, on a long table.",
  SOR, "awe")
P("And people differed wildly. Some barely reacted at all.", "The main character and a calm stick figure side by side, one sweating, one sipping tea.",
  "The authors said there's a big audience for positive news too.", "A small crowd of stick figures gathered around a sunny noticeboard, smiling.",
  SOR, "funny", "happy")
P("So it's a pull, not a rule. Hold on to that.", "The main character grabs a rope that tugs him gently forward, smiling a little.",
  "A pull that shows up on screens and in skin.", "A phone and a hand side by side, both with small storm clouds above them.",
  SOR)

# ================= 2. bad is stronger than good
P("Now a bigger question: is this only about news?", "The main character steps out of a newsroom into a wide open field, curious.",
  "In 2001, Roy Baumeister and colleagues reviewed hundreds of studies.", "A tall stack of old papers tied with string on a wooden desk, a lamp beside it.",
  BAU, "curious", hsfx="whoosh")
P("Their title says it all, honestly.", "The main character holds up a thick book with a cloud on the cover, eyebrows raised.",
  "They called it: bad is stronger than good.", "A balance scale with a small dark stone outweighing a big bright flower.",
  BAU, fe="awe", fpause=500)
P("Think about your own day.", "The main character walks home at dusk, thinking, hands in his pockets.",
  "Bad events had bigger effects in daily life, relationships and learning.", "Three small icons in a row: a house, two holding hands, a book, each with a little dark cloud.",
  BAU)
P("Ten compliments, one insult. Which one do you replay at night?", "The main character lies awake in bed staring at the ceiling, one small dark cloud above him.",
  "The review found hardly any areas where good clearly won.", "A tug of war between a bright team and a dark team, the dark team pulling ahead.",
  BAU, "funny")
P("I still remember a comment from school. Twenty years later.", "The main character as an adult sighs while looking at a faded classroom drawing.",
  "Bad feedback tends to be processed more thoroughly than good feedback.", "A sieve catching dark pebbles while bright pebbles fall through, warm paper background.",
  BAU, "sad")
P("We chew on bad things. Good things, we just swallow.", "The main character chews slowly with a sour face while a sweet berry rolls away.",
  "Bad first impressions were also found to be harder to undo.", "A muddy footprint on a clean white floor and a small broom that can't remove it.",
  BAU, "funny")
P("So one bad day can colour a whole week.", "The main character looks at a calendar with one dark square and grey spreading to the others.",
  "In relationships, harmful acts outweighed kind ones in many studies.", "Two stick figures holding hands, a thorn between them larger than the flowers around them.",
  BAU)
P("That's why one argument can echo louder than a good month.", "The main character covers his ears while a small echo cloud bounces around a room.",
  "The authors argued this pattern could help survival.", "A cave entrance at dusk with a tiny campfire glowing inside and dark woods outside.",
  BAU)
P("Which raises the real question: why would we be built like this?", "The main character stands at a crossroads in the forest, looking back over his shoulder.",
  "To answer that, we need to go back to the campfire.", "A small campfire in a dark prehistoric forest at night, sparks rising.",
  OHM, "curious", fsfx="swoosh")

# ================= 3. the ancient alarm: snakes and smoke detectors
P("Picture a hunter at dusk, walking home through tall grass.", "The main character walks through tall golden grass at dusk carrying a spear, alert.",
  "In 2001, Arne Öhman's team tested how fast people spot danger.", "A grid of small pictures of flowers and mushrooms with one snake among them, top view.",
  OHM, "tense", hsfx="whoosh")
P("Your job in the test: find the odd picture out.", "The main character leans over a table of picture cards, squinting.",
  "People found snakes and spiders faster among flowers than the other way round.", "A snake picture glowing brighter among nine flower pictures, warm paper background.",
  OHM, fe="awe")
P("Your eyes go to the snake before you've even thought 'snake'.", "The main character jumps back from a card with a coiled snake on it, hair standing up.",
  "Adding more harmless pictures barely slowed the threat search down.", "A long row of flower pictures with one spider at the very end still glowing.",
  OHM, "funny", hpace="fast")
P("More clutter, same speed. That's a dedicated alarm.", "The main character points at a big brass bell hanging above his head.",
  "Later reviews found snakes are spotted fastest in hard, busy scenes.", "A dense jungle floor with a snake half hidden among leaves, no people.",
  OHM)
P("Now, why build a brain that jumps at shadows?", "The main character flinches at a curly stick on the path that looks like a snake.",
  "Doctor Randolph Nesse calls it the smoke detector principle.", "A simple round smoke detector on a ceiling with a small puff of toast smoke below it.",
  NES, "curious")
P("Your smoke alarm goes off when you burn toast. Annoying, right?", "The main character waves a towel at a beeping smoke alarm, burnt toast in hand.",
  "But a false alarm costs little. A missed fire costs everything.", "Two scales: one with a tiny burnt toast, one with a whole burning house, much heavier.",
  NES, "funny", hpace="fast")
P("So a good alarm is set to be a bit too jumpy.", "The main character nods, holding the smoke alarm like a treasured pet.",
  "Nesse argues natural selection tunes many defences the same way.", "A row of different alarm bells on a shelf, all small and cheap, warm paper background.",
  NES)
P("Run from a rope that looked like a snake? You lose a few seconds.", "The main character sprints away from a coiled rope, then stops and laughs at himself.",
  "Ignore a real snake once, and that could be the end.", "A real snake coiled on a sunny path beside a single sandal left behind.",
  NES, "funny", "serious")
P("Our ancestors weren't the calm ones. They were the jumpy ones who lived.", "The main character stands proudly in a cave doorway, a little nervous, holding a torch.",
  "Survivors passed on their skills and fears, generation after generation.", "Handprints of different sizes on a cave wall, adults and children, soft firelight.",
  NES, "awe", hpause=400)
P("So that pull toward bad news? It's an old alarm with a new speaker.", "The main character holds a phone up to his ear like a seashell, listening.",
  "Reviews describe the negativity bias across many areas of life.", "A tree with many branches, each holding a small dark cloud, warm paper background.",
  BAU, "awe")
P("In the forest, bad news meant a lion nearby. Useful!", "The main character crouches behind a bush as a lion's tail passes in the distance.",
  "Warnings about danger were worth paying attention to fast.", "Paw prints in mud leading toward a camp, early morning mist.",
  NES, "tense")
P("On your phone, bad news means a disaster far away. Still you react.", "The main character gasps at his phone in a cosy living room, totally safe.",
  "The same physical stress responses showed up while watching news clips.", "A small heart beating fast drawn next to a television set, no letters.",
  SOR)
P("Your body can't tell 'far away' from 'right here' very well.", "The main character hides behind a sofa cushion while watching TV.",
  "In the lab, people watched calm rooms and still reacted to stories.", "A quiet room with a chair, a lamp and a small screen glowing blue.",
  SOR, "funny")
P("Funny, until it's three in the morning and you're still scrolling.", "The main character in bed at three in the morning, phone light on his face, yawning.",
  "Online, negative headlines kept drawing clicks across years of tests.", "A tall pile of calendar pages with small rain clouds on each page.",
  UPW, "sad")

# ================= 4. the brain's extra attention
P("Let's look inside the head for a second.", "The main character opens a small door in the side of a giant cartoon head, peeking in.",
  "In 1998, Tiffany Ito and John Cacioppo recorded brain waves.", "A simple cap with wires on a dummy head, beside a wavy paper printout.",
  ITO, "curious", hsfx="swoosh")
P("People looked at good, bad and neutral pictures.", "The main character watches a slideshow: a puppy, a broken plate, a plain chair.",
  "Bad pictures produced bigger brain responses than good ones.", "Two wave lines on paper, one much taller and darker than the other.",
  ITO, fe="awe", fpause=400)
P("Even when the pictures were matched for how exciting they were.", "The main character holds a ruler between two pictures, measuring carefully.",
  "The authors called it a physiological sign of the negativity bias.", "A small brain with a bright spot lighting up beside a broken plate.",
  ITO)
P("To be fair, brain-wave studies since then are a bit mixed.", "The main character shrugs with a 'well, kind of' face, palms up.",
  "Later work found the effect isn't the same for everyone.", "A row of different wave lines, some tall, some flat, on a paper strip.",
  KIS, "neutral")
P("Who's 'everyone'? Remember our mystery group. Hold that thought.", "The main character taps his temple with a knowing smile, winking.",
  "First, the alarm seems to switch on early in life.", "A baby's small rattle and a soft blanket on a wooden floor, morning light.",
  VAI, "whisper")
P("Babies, it turns out, notice frowns.", "The main character waves at a baby in a crib, then frowns, and the baby stares at him.",
  "A 2008 review found infants learn more from negative signals than positive ones.", "A baby crawling toward a toy, then stopping beside a worried adult face, warm light.",
  VAI, "funny")
P("A mum's worried face beats a mum's smile, for learning anyway.", "The main character as a parent makes a worried face, a toddler freezes mid-step.",
  "The review traces this bias to around the end of the first year.", "A tiny birthday cake with one candle beside a small toy wooden block.",
  VAI)
P("So before you could walk, you were already listening for danger.", "The main character holds a tiny version of himself, both looking around nervously.",
  "Negative information is attended to, learned from and used more.", "Three small icons: an eye, an open book, a hand, each with a dark dot.",
  VAI, "awe")

# ================= 5. an old alarm in a new world (+ subscribe)
P("Now put that baby brain into a world of screens.", "The main character as a grown man stands in a city street surrounded by glowing billboards, blinking.",
  "The headline study showed sad words drew the most extra clicks.", "A small crying cloud sitting on top of a tall stack of newspapers.",
  UPW, "curious", hsfx="whoosh")
P("Every app is basically a lab running that test on you, all day.", "The main character sits inside a giant glass jar, tapping on a phone, while tiny scientists take notes outside.",
  "Upworthy's tests ran on hundreds of millions of headline views.", "A huge crowd of tiny eyes drawn in rows like a stadium, warm paper background.",
  UPW, "funny")
P("Hundreds of millions. That's not a study. That's a planet.", "The main character holds a small globe in his hands, eyebrows raised.",
  "In the body study, negative clips raised arousal on average.", "A small thermometer next to a TV screen with its red line rising.",
  SOR, "awe")
P("And arousal feels like importance. It isn't always.", "The main character points at a flashing red light on a toy car, unimpressed.",
  "The 2001 review found bad events also stick longer in memory.", "A wooden box of memories with one dark stone at the top, clearly visible.",
  BAU, "serious")
P("Which explains why your brain keeps a highlight reel of cringe.", "The main character watches a tiny cinema screen inside his own head showing himself tripping.",
  "Bad information gets more processing, so it leaves deeper traces.", "A footprint pressed deeply into wet clay next to a faint one, warm paper background.",
  BAU, "funny", hpace="fast")
P("I once waved back at someone who wasn't waving at me. Never forgot it.", "The main character waves at a stranger who is actually waving at someone behind him, embarrassed.",
  "Negative social signals were among the strongest in the review.", "Two stick figures, one turning its back on the other, a small cold wind between them.",
  BAU, "funny")
P("For a hunter, being pushed out of the group was dangerous.", "The main character stands alone outside a circle of figures around a fire, at night.",
  "Infants already react strongly to adults' fearful expressions, the review notes.", "A toddler stopping at the edge of a rug while an adult face shows fear, warm light.",
  VAI, "serious")
P("So our alarm cares a lot about danger and about rejection.", "The main character holds a small bell in one hand and a broken heart in the other.",
  "These are the areas where negativity bias shows up most often.", "A simple chart drawn with stones: a tall pile for danger, a tall pile for people.",
  BAU)
P("Okay. I promised you an answer about who escapes it.", "The main character opens a heavy wooden door with a small creak, curious.",
  "Researchers found it in brain waves of some people, but not others.", "Two brain-wave lines on paper, one spiky and tall, one smooth and calm.",
  KIS, "curious")
P("We'll get there. First, a short break.", "The main character sits down on a log beside a cosy fire and takes a breath.",
  "Older brains turned out to be one of the surprises.", "An old wooden walking stick leaning on a sunny bench, no people.",
  KIS)
P("Quick pause. If you're enjoying this, subscribe and stay with me.", "The main character smiles and waves warmly at the viewer from beside the campfire.",
  "There's still the loss experiment and the big reveal ahead.", "A winding path through a watercolour forest leading toward a bright clearing.",
  LOS, "happy")
P("We'll keep exploring the human mind together, one question at a time.", "The main character walks along a forest path with a lantern, looking back with a friendly smile.",
  "Next comes the famous claim that losses hurt twice as much.", "Two coins on a table, one cracked and dark, one shiny, the cracked one looks heavier.",
  LOS, "happy")
P("It's free, it takes one second, and it helps more curious people find us.", "The main character gives a big thumbs up, grinning, in warm firelight.",
  "Here's how that research began.", "An old wooden desk with two coins, a notebook and a candle, no people.",
  LOS, "happy")

# ================= 6. losses loom larger
P("Imagine I hand you ten dollars, then take ten dollars away.", "The main character receives a coin, smiles, then a hand takes it back and he frowns.",
  "Kahneman and Tversky argued that losses loom larger than gains.", "A see-saw with a small dark coin on one side lifting a bigger shiny coin.",
  LOS, "curious", hsfx="ding")
P("You're back where you started. So why do you feel worse?", "The main character stares at his empty hands, confused and a little grumpy.",
  "A big meta-analysis estimated losses weigh about twice as much as gains.", "A balance scale with one dark coin on one side and two bright coins on the other, level.",
  LOS, "funny", fe="awe", fpause=400)
P("Twice! That's like a refund that only counts half.", "The main character looks at a receipt and counts half a coin, baffled.",
  "That estimate landed between about one point eight and two point one.", "A small ruler with a narrow coloured band near the number two, no letters.",
  LOS, "funny")
P("But here's where it gets spicy. Not everyone agrees.", "The main character holds up a red chilli pepper with a mischievous look.",
  "Gal and Rucker argued loss aversion has been overgeneralised.", "Two professors' chairs facing each other with papers flying between them.",
  LOS, "excited")
P("In some tests, people valued a mug the same, buying or selling.", "The main character holds a mug up to a stick figure buyer, both shrugging.",
  "For small stakes, some studies find little or no loss aversion.", "A tiny coin on a big scale that stays perfectly level.",
  LOS)
P("So small losses, like a coffee, might not sting double.", "The main character drops a coin into a coffee cup, shrugs and sips happily.",
  "Critics still agree that some asymmetry between losses and gains exists.", "A slightly tilted balance scale, the dark side just a little lower.",
  LOS, "funny")
P("Science fights are healthy. This is how we get closer to true.", "The main character referees two stick figures arguing politely, holding a whistle.",
  "Big losses still tend to weigh more in many studies.", "A large cracked pot next to a small shiny bead, the pot casting a long shadow.",
  LOS, "neutral")
P("Losing your phone ruins a day. Finding a coin barely makes one.", "The main character searches frantically under a sofa, then ignores a coin on the floor.",
  "Researchers link this pull to the wider negativity bias.", "Two trees from one root, one labelled with a dark cloud, the other with a coin, no letters.",
  BAU)
P("For a hunter, losing a day's food mattered more than finding a bonus berry.", "The main character clutches an empty basket while a single berry rolls away.",
  "When harm is large and protection cheap, alarms should fire often.", "A small cheap bell beside a huge rockfall in the mountains.",
  NES)
P("Protecting what you had was a life-or-death habit.", "The main character guards a small food pile by the fire, watchful.",
  "Many defensive responses look over-tuned for exactly this reason.", "A turtle pulling into its shell at a falling leaf, warm paper background.",
  NES, "serious")

# ================= 7. the mystery group: older adults
P("Okay. Remember the group that barely has this pull?", "The main character leans in close to the viewer, whispering, a candle in hand.",
  "It's older adults.", "An elderly stick figure with a cane smiling on a sunny park bench, birds nearby.",
  KIS, "whisper", "awe", hpace="slow", fpause=600, fsfx="ding")
P("Yes, grandma might be winning this one.", "The main character bows playfully to an elderly stick figure who laughs.",
  "In brain-wave studies, younger adults showed the bias, older adults didn't.", "Two brain-wave lines: a young one spiky, an old one smooth, on paper.",
  KIS, "funny")
P("Not because they stopped caring. Something shifted.", "The main character sits beside the elder on a bench, both looking at a sunset.",
  "Their responses to negative pictures got smaller with age.", "A large dark picture frame shrinking into a smaller one, beside a bright frame staying the same size.",
  KIS)
P("Psychologists Mara Mather and Laura Carstensen called this the positivity effect.", "The main character opens a book with a sun on the cover, curious.",
  "Older adults tend to notice and remember positive things more, relative to younger people.", "A photo album open on a table, bright pictures larger than grey ones.",
  MAT, fe="awe")
P("They chose the word 'effect', not 'bias', on purpose.", "The main character holds up two cards and puts one down carefully.",
  "Younger adults often lean toward the negative, so it's a relative shift.", "Two arrows, one tilting toward a cloud, one toward a sun, side by side.",
  MAT)
P("One idea: when time feels shorter, you care more about feeling good now.", "The main character looks at a small hourglass, then smiles at a flower.",
  "The researchers link it to a greater focus on regulating emotions.", "A calm lake reflecting a sunrise, soft colours, no people.",
  MAT, "serious")
P("So the alarm can be turned down. Life experience does it somehow.", "The main character turns a big brass dial slowly to the left, relieved.",
  "Not every study finds the age difference, though.", "Several small scales, most tipped, a couple perfectly level.",
  MAT, "awe")
P("Honest science: it's a tendency, not a superpower.", "The main character shrugs with a smile, holding a small trophy that says nothing.",
  "Over a hundred studies had tested the idea by twenty twelve.", "A tall shelf full of thin research journals, warm lamp light.",
  MAT, "neutral")
P("Which means you don't need to wait till eighty to notice it.", "The main character winks and points at his own forehead.",
  "People in the news study also differed a lot from one another.", "A row of stick figures, some sweating, some calm, watching the same screen.",
  SOR, "happy")
P("Some people are calm by nature. Some are smoke alarms with legs.", "The main character jumps at a leaf while his calm friend sips tea, unbothered.",
  "The negativity bias is an average across people, not a fixed law.", "A crowd of stick figures with a soft curve drawn over them like a hill.",
  BAU, "funny")

# ================= 8. hearing the alarm without obeying it
P("So how do you live with an ancient alarm in a modern pocket?", "The main character holds his phone and a small stone hand-axe, comparing them.",
  "This isn't advice, just what the research describes.", "A plain notebook and a pencil on a table, a cup of tea nearby, no people.",
  NES, "curious", hsfx="whoosh")
P("The research points to something simple: the pull can be noticed. 'Oh, there's my alarm again.'", "The main character points at a tiny bell ringing above his own head, smiling.",
  "Defences fire often because a false alarm used to be cheap.", "The smoke detector again, beeping at a slice of toast, no people.",
  NES, "happy")
P("Naming it doesn't switch it off. But it puts you back in the driver's seat.", "The main character sits behind a steering wheel made of a branch, steady.",
  "The 2023 authors noted sad and angry words spread differently.", "Two clouds, one crying, one red, drifting in different directions.",
  UPW, "neutral")
P("It also helps to remember: clicks are a business, not the whole world.", "The main character pulls back a curtain to reveal a tiny machine counting clicks.",
  "Each negative word was worth about two percent more clicks.", "A coin slot in a wooden box with a small dark cloud above it.",
  UPW, "serious")
P("The world on your screen is the world that got clicked.", "The main character looks through a small window frame at a stormy scene, while sunshine is behind him.",
  "Researchers found a real audience for positive news, too.", "A small crowd gathered around a sunny noticeboard in a village square.",
  SOR, "awe")
P("And studies suggest good things need a little extra time to land.", "The main character sits and watches a sunset slowly, holding a warm cup.",
  "Good events seem to need more attention to match a bad one's impact.", "A balance scale with several bright flowers balancing one dark stone.",
  BAU, "happy")
P("Like watering a plant while weeds grow on their own.", "The main character waters a small flower while weeds sprout around it, determined.",
  "The review described good as weaker but more common in daily life.", "A field full of many small flowers and only a few thorny weeds.",
  BAU, "funny")
P("And that's the hopeful part. Good things are everywhere. They're just quieter.", "The main character walks through a meadow full of small flowers, smiling.",
  "Older adults, the research suggests, learn to tune into them.", "An elderly stick figure feeding birds in a sunny park.",
  MAT, "happy")

# ================= 9. one day with your alarm (story walk-through)
P("Let's follow the alarm through one ordinary day. Yours, probably.", "The main character wakes up in a modern bedroom at sunrise, stretching, sleepy.",
  "Negative information grabs attention faster, the reviews agree.", "A sunrise window with one small dark cloud that somehow looks bigger than the sun.",
  BAU, "curious", hsfx="swoosh")
P("Seven a.m. You check your phone before your eyes are fully open.", "The main character squints at a bright phone in bed, hair messy.",
  "In the tests, headlines with more negative words got more clicks.", "A phone screen showing three coloured boxes, one with a storm cloud glowing.",
  UPW, "funny")
P("Guess which headline you tap. Yep. The scary one.", "The main character taps the stormy box on the phone, eyes wide.",
  "Readers didn't plan it. The pattern only showed up in the numbers.", "A long paper strip of tally marks, most of them dark, on a desk.",
  UPW)
P("Eight a.m. Your heart is already a little faster. Over a story far away.", "The main character eats breakfast with a tense face, phone propped against the cereal box.",
  "Negative clips raised skin conductance, a sign of arousal.", "A small drop of sweat on a fingertip next to a small TV screen.",
  SOR, "serious")
P("Nine a.m. Your boss says 'good work', then 'one small thing'.", "The main character in an office hears a stick-figure boss speak, smile fading.",
  "Bad feedback had stronger effects than good feedback in many studies.", "A sticky note with a frown next to a gold star, the note much bigger.",
  BAU, "funny")
P("Guess which part you'll think about at lunch.", "The main character eats a sandwich alone, staring into space, one small cloud above.",
  "Bad events were also found to be thought about longer.", "A clock with a dark cloud circling around it many times.",
  BAU, "funny")
P("Noon. A friend doesn't reply for three hours. Panic.", "The main character stares at a phone with no messages, sweating, imagining disasters.",
  "Social rejection is one of the strongest bad signals in the research.", "A small stick figure standing outside a closed door, a cold breeze around it.",
  BAU, "tense")
P("Turns out their phone died. Of course it did.", "The main character facepalms as his friend waves a dead phone, laughing.",
  "Cheap false alarms are exactly what the smoke detector logic predicts.", "Burnt toast and a beeping smoke detector, a cat looking unimpressed.",
  NES, "funny", hpace="fast")
P("Three p.m. A rope on the path. You jump. It's a garden hose.", "The main character leaps sideways from a coiled green garden hose on a path.",
  "Snake-like shapes catch the eye quickly in visual search tests.", "A coiled garden hose in grass that looks a bit like a snake, no people.",
  OHM, "funny")
P("Your great-great-great-grandparents would be proud of that jump.", "The main character bows to a row of cave-dwelling ancestors who clap politely.",
  "Fast threat detection makes sense where real snakes lived.", "A rocky savanna path at dusk with a real snake sunning itself on a stone.",
  OHM, "happy")
P("Six p.m. You lose ten dollars and it bugs you all evening.", "The main character searches his pockets on a bus, frowning.",
  "In many experiments, losses weighed more than equal gains.", "A balance scale with one dark coin outweighing a bright coin.",
  LOS)
P("You found twenty last month. Forgot about it in a day.", "The main character finds a banknote on the pavement, shrugs and walks on.",
  "Though for small amounts, some researchers find no difference at all.", "A tiny coin on a perfectly level small scale, warm paper background.",
  LOS, "funny")
P("Ten p.m. Bed. Your brain plays the day's worst moments, in HD.", "The main character lies in bed while a tiny projector in his head shows embarrassing scenes.",
  "Bad memories tend to be more vivid and better processed, the review says.", "A dim bedroom with a bright little film strip floating above the pillow.",
  BAU, "sad")
P("Not one of those moments was a lion. Your alarm doesn't know that.", "The main character pulls the blanket over his head while a cartoon lion shadow appears on the wall.",
  "The alarm was tuned for a world of real predators.", "A lion silhouette on a hill under the moon, prehistoric savanna.",
  NES, "awe", hpause=400)
P("That's not a flaw in you. It's a very old feature, slightly out of date.", "The main character holds an old stone tool and a modern phone, smiling kindly.",
  "Natural selection shapes defences for past dangers, not present ones.", "A worn stone axe resting on top of a modern keyboard, warm paper background.",
  NES, "happy")
P("Like a smoke alarm installed in a cave, now hanging in your kitchen.", "The main character looks up at a smoke alarm nailed to a rock ceiling in a modern kitchen.",
  "Mismatch between old adaptations and new worlds is a classic idea in evolutionary medicine.", "A cave wall with a modern smoke detector bolted onto the stone.",
  NES, "funny")
P("And remember, people really differ. You might be one of the calm ones.", "The main character meets a calm friend meditating peacefully while birds land on him.",
  "In the news study, individual reactions varied a lot.", "A row of different coloured hearts, some racing, some steady, warm paper background.",
  SOR, "happy")
P("Or you might be like me: smoke alarm with legs.", "The main character jumps at a leaf falling, then laughs at himself.",
  "Averages hide big differences between people.", "A tall bell curve drawn with pebbles on sand, no letters.",
  SOR, "funny")
P("Either way, the alarm is loud for a reason. And it's yours.", "The main character gently pats a small bell hanging from his belt, at peace.",
  "Attending to danger helped ancestors survive long enough to have children.", "A family of stick figures by a campfire, children sleeping, adults watchful.",
  VAI, "serious")

# ================= 10. recap and ending
P("So, why is your brain addicted to bad news?", "The main character sits by a campfire at dusk, thinking, chin in hand.",
  "Bad information gets more attention, more processing and more memory.", "Three stones in a row, each a little darker and heavier, on warm paper.",
  BAU, "serious", hsfx="riser")
P("Because for most of history, bad news was the news that kept you alive.", "The main character points to a distant lion on a hill while his tribe looks.",
  "Threats like snakes are spotted remarkably fast.", "A snake among flowers with a soft glow around it, top view.",
  OHM, "awe")
P("Because a false alarm cost a little, and a missed one cost everything.", "The main character holds burnt toast in one hand and points to a burning hut far away.",
  "That's the smoke detector principle.", "A smoke detector on a cave ceiling, a small campfire below.",
  NES)
P("Because the alarm switches on before we can even walk.", "The main character holds a baby who stares at a frowning face, curious.",
  "Infants already weight negative signals more heavily.", "A baby's hand resting on a wooden block, soft morning light.",
  VAI)
P("And because modern headlines learned to ring it on purpose.", "The main character looks at a giant phone with a bell attached to it, raising an eyebrow.",
  "Each negative word nudged clicks up by about two percent.", "A small staircase of raindrops going up, warm paper background.",
  UPW)
P("But the alarm isn't destiny.", "The main character turns the brass dial down again, calm and smiling.",
  "Older adults show a relative shift toward positive information.", "An elderly couple of stick figures watching birds on a park bench.",
  MAT, "happy")
P("And plenty of people want good news too. Maybe more than editors think.", "The main character hands out sunny newspapers to a small smiling crowd.",
  "The authors of the body study said exactly that.", "A small village noticeboard covered in sunny drawings, people gathered round.",
  SOR, "happy")
P("Me? I still jump at garden hoses. I've made peace with it.", "The main character jumps at a hose, then laughs and gives the hose a little bow.",
  "Some false alarms are just the price of a careful brain.", "A smoke detector, a slice of toast and a smiling cat, warm light.",
  NES, "funny")
P("Next time the alarm rings at three a.m., you'll know who installed it.", "The main character lies in bed at night, looking at a tiny caveman on his pillow, smiling.",
  "It was built by thousands of generations of careful survivors.", "A long line of footprints from a cave into a modern city, watercolour.",
  NES, "awe", fpace="slow", fpause=600)
H("Thank you for spending these minutes with me. If this was worth it, hit like, and tell me in the comments the bad headline you still remember. I read every one. Next time, we'll find out why your brain loves gossip so much. See you there, friend.",
  "The main character waves goodbye from a cosy campfire at sunset, a phone face-down beside him, smiling warmly.", "happy", pace="slow", pause=800, sfx="pop")

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
    if emo is None or last[-3:] == [emo] * 3:
        emo = next(e for e in EMOS if e != (last[-1] if last else None) and last[-2:].count(e) < 2)
    last.append(emo)
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
                   "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
                   "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})
for p in problems:
    print("PROBLEM", p)

data = {
    "title": "Why Is Your Brain Addicted to BAD News?",
    "title_alternatives": ["Why Your Brain Remembers the BAD Things", "Why One Insult Beats Ten COMPLIMENTS",
                           "The Ancient Alarm Inside Your HEAD", "Why Negativity Is So ADDICTIVE"],
    "description": ("One sad word in a headline gets more clicks. Your skin reacts to bad news before you've decided how you feel. "
                    "Where does this pull come from, why did it keep our ancestors alive, and who barely has it at all? "
                    "A tour through the psychology of the negativity bias, from snakes in the grass to the smoke detector principle.\n\n"
                    "This video is psychology and history, not medical or mental-health advice.\n\nSources:\n"
                    "- Robertson et al. (2023). Negativity drives online news consumption. Nature Human Behaviour.\n"
                    "- Soroka, Fournier & Nir (2019). Cross-national evidence of a negativity bias in psychophysiological reactions to news. PNAS.\n"
                    "- Baumeister et al. (2001). Bad is stronger than good. Review of General Psychology.\n"
                    "- Öhman, Flykt & Esteves (2001). Emotion drives attention: Detecting the snake in the grass. JEP: General.\n"
                    "- Nesse (2001). The smoke detector principle. Annals of the New York Academy of Sciences.\n"
                    "- Ito et al. (1998). Negative information weighs more heavily on the brain. JPSP.\n"
                    "- Vaish, Grossmann & Woodward (2008). Not all emotions are created equal. Psychological Bulletin.\n"
                    "- Mather & Carstensen (2005). Aging and motivated cognition: the positivity effect. Trends in Cognitive Sciences."),
    "tags": ["negativity bias", "psychology", "bad news", "doomscrolling", "human brain", "evolutionary psychology",
             "why we focus on the negative", "loss aversion", "smoke detector principle", "ancient humans", "stickman", "animated explainer"],
    "mood": "mysterious",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Why Is Your Brain Addicted to BAD News?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-10-27.", "",
      "## Method",
      "- Every study was found and its abstract or a reliable summary opened; contested findings are told as contested.",
      "- No mental-health advice: the 'what to do' part only describes what studies report, and says 'this isn't advice'.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- Gottman's '5 to 1' ratio: only in secondary sources, dropped.",
       "- Hamlin et al. (2007) infant helper/hinderer study: replication failures (ManyBabies), dropped.",
       "- 'Losses hurt exactly twice as much': told as 'about twice in many studies', with Gal & Rucker's critique.",
       "- Brain-wave negativity bias: 'in this study', 'later studies are mixed'.",
       "- Positivity effect: 'relative to younger people', 'not every study finds it'.",
       "- Nesse 2005 Evolution and Human Behavior citation could not be confirmed; the 2001 Annals paper is cited instead."]
Path(__file__).with_name("bad_news_brain.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
