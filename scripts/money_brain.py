"""Builds scripts/money_brain.json and scripts/money_brain.factcheck.md
(run: ./venv/Scripts/python scripts/money_brain.py).
Five ancient money traps, ~11 minutes, a new anime picture every ~4 s (import with --minutes 11 --seconds-per-image 4).
P(...) adds one hero scene and one fact scene, so hero/fact always alternate. Concept approved by the owner 2026-11-02.
Education about why brains handle money badly; no financial advice anywhere (YouTube: AI persona + finance guidance)."""
import json
from pathlib import Path

FIN = "Klapper, Lusardi & van Oudheusden (2015). Financial Literacy Around the World: S&P Global FinLit Survey (2014 Gallup data)"
HUB = "Hublin et al. (2017). New fossils from Jebel Irhoud, Morocco and the pan-African origin of Homo sapiens. Nature 546, 289-292"
WOO = "Woodburn, J. (1982). Egalitarian societies. Man 17(3), 431-451"
MCC = "McClure, Laibson, Loewenstein & Cohen (2004). Separate neural systems value immediate and delayed monetary rewards. Science 306, 503-507"
KT = "Kahneman & Tversky (1979). Prospect theory. Econometrica 47; Tversky & Kahneman (1992). Advances in prospect theory. J. Risk and Uncertainty 5"
PS = "Prelec & Simester (2001). Always leave home without it: the credit-card effect on willingness to pay. Marketing Letters 12, 5-12"
LUT = "Luttmer, E. (2005). Neighbors as negatives: relative earnings and well-being. Quarterly Journal of Economics 120, 963-1002"
MES = "Code of Hammurabi (c. 1754 BCE), laws on loans and interest; Mesopotamian loan tablets (silver about 20%, grain about 33%)"
WIE = "Wiessner & Huang (2022). Ju/'hoansi kinship obligations, cash and risk pooling, 1974-2018. PNAS 119, e2213214119"
WAT = "Watts, Duncan & Quan (2018). Revisiting the marshmallow test. Psychological Science 29, 1159-1177"

VERIFY = {
    FIN: ("Searched 2026-11-02; GFLEC presentation and trade-press summaries of the S&P Global FinLit Survey: questions in the Gallup World Poll, "
          "150,000+ adults in 140+ countries, 33% of adults worldwide financially literate (3 of 4 concepts right: interest, compounding, inflation, diversification); US 57%.",
          "'About one in three passed', the test is called 'simple money questions'; the year is not hidden (description says 2014 data)."),
    HUB: ("Searched 2026-11-02 (well-known Nature paper): Jebel Irhoud fossils dated about 300,000 years.", "'About three hundred thousand years'."),
    WOO: ("Searched 2026-11-02; secondary summaries (P2P Foundation, UCL chapter) of Woodburn's immediate-return model based on Hadza fieldwork: "
          "food consumed soon after it is obtained, little storage, demand sharing. A later study found big game sharing favours the hunter's household.",
          "'Anthropologists describe', 'many foragers'; not claimed for every prehistoric group."),
    MCC: ("Searched 2026-11-02; Princeton and ASU records and abstract: fMRI, choices between money now and later; limbic/paralimbic areas more active for immediate rewards, "
          "lateral prefrontal and parietal areas for all choices; more fronto-parietal activity when people chose to wait. Later replications are mixed.",
          "'Brain scans suggest', 'one famous study'; no claim that a single 'impulse centre' exists."),
    KT: ("Searched 2026-11-02; Wikipedia summary and critiques (Jason Collins blog, Yechiam): prospect theory 1979 introduced loss aversion; the about-twice estimate (2 to 2.25) comes from 1992 work; "
         "a 2020 multi-country replication broadly supported the 1979 patterns; strength of loss aversion is debated.",
         "'Roughly twice', 'for many people', and the debate is mentioned."),
    PS: ("Searched 2026-11-02; MIT faculty page, MSU Extension and Psychology Today summaries: MIT MBA students bid on Celtics tickets; those allowed to pay by card bid roughly twice as much as cash-only bidders.",
         "'In one MIT experiment', 'roughly double'; not claimed that cards always double spending."),
    LUT: ("Searched 2026-11-02; NBER working paper w10667 abstract: matched panel data; higher neighbours' earnings associated with lower self-reported happiness, holding own income constant.",
          "'Linked to', 'on average'."),
    MES: ("Searched 2026-11-02; Burr & Forman legal-history article and popular histories: Mesopotamian loans in silver and barley, commonly cited rates about 20% on silver and 33% on grain, "
          "Code of Hammurabi regulated loans (c. 1754 BCE); proto-cuneiform accounting tablets from about 3100 BCE. Weak blog sources ignored.",
          "'About a fifth', 'about a third', 'around'; no exact dates beyond 'nearly four thousand years ago' for Hammurabi and 'over five thousand years' for writing-based accounts."),
    WIE: ("Searched 2026-11-02; PNAS 2022 abstract (PMC9564820), Utah news release and Wiessner's 1977 dissertation title: hxaro gift partners as far as about 200 km; in 1974 about 69% of possessions had come as hxaro gifts; "
          "partnerships fell by about half by 1997 as cash spread.",
          "'Up to about two hundred kilometres', 'in the nineteen seventies', 'about seven in ten'."),
    WAT: ("Searched 2026-11-02; Psychological Science abstract and summaries: about 900 children (NICHD SECCYD), link with later achievement about half the original size and reduced by about two thirds after family background controls.",
          "'Much smaller', 'family background mattered a lot'; willpower not called useless."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source, on_screen)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None, text=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src, text))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None, None))


# ================= hook (12 short lines)
P("Two out of three adults failed a simple money test.",
  "The main character sits in a cave by a campfire, staring confused at a glowing modern bank card in his hand.",
  "People in over a hundred forty countries took it.",
  "A huge world map made of pebbles on a cave floor lit by torches, most pebbles grey, a few glowing gold.",
  FIN, "tense", "curious", "hook", hsfx="riser", text="2 / 3")
P("And no, it's not because they're stupid.",
  "The main character shrugs with an embarrassed smile, holding a crumpled empty wallet.",
  "Our species is three hundred thousand years old. Money isn't.",
  "An ancient human skull resting on a rock next to a single small silver coin, torchlight.",
  HUB, "serious", "awe", "hook")
P("Today, that ancient brain is holding your bank card.",
  "The main character in his hide tunic stands at a modern shop checkout, tapping a card, looking proud.",
  "And brain scans suggest it still loves right now.",
  "A glowing brain scan image floating above a modern city street at night, warm parts lit orange.",
  MCC, "funny", "curious", "hook", hpace="fast")
P("If your salary vanishes in days, this is about you.",
  "The main character watches banknotes fly out of an open window into the rain, hands on his head.",
  "Losing money hurts about twice as much as winning.",
  "A broken clay bowl with spilled grain on wet ground in the rain, a full bowl beside it.",
  KT, "serious", "excited", "hook", hsfx="whoosh")
P("By the end, you'll spot five ancient money traps.",
  "The main character holds up five fingers in front of five glowing stone traps on a forest path.",
  "In one test, paying by card nearly doubled the offers.",
  "Two hands at an auction table, one holding cash, one holding a card, a big pile of tickets between them.",
  PS, "curious", "whisper", "hook")
P("And one trap is written on five-thousand-year-old clay.",
  "The main character holds a cracked clay tablet covered in wedge marks, eyes wide.",
  "Mesopotamian tablets recorded debts long before coins existed.",
  "Rows of ancient clay tablets with wedge-shaped marks on a dusty shelf, lamp light.",
  MES, "tense", "curious", "hook", fsfx="impact")

# ================= a world without money
P("So let's go back to a world without money.",
  "The main character walks out of a cave at sunrise onto a wide grassy savanna, stretching.",
  "For most of human history, there was nothing to save money in.",
  "A wide savanna at dawn with a small camp of grass huts and smoke rising, no buildings anywhere.",
  HUB, "curious", "neutral")
P("No banks. No wallets. No payday.",
  "The main character pats his tunic as if looking for a missing wallet, puzzled.",
  "Anthropologists describe many foragers as eating what they found, often the same day.",
  "Foragers sharing roasted roots around a campfire in the evening, smiling, leaves moving in the wind.",
  WOO, "funny", "neutral", hpace="fast")
P("Honestly, that sounds kind of relaxing.",
  "The main character lies in tall grass under a tree, eating a fruit, very relaxed.",
  "Food spoiled fast in the heat, so hoarding made little sense.",
  "A pile of fruit going brown in the sun next to buzzing flies, hot dry landscape.",
  WOO, "happy", "serious")
P("If you got a big catch, you shared it.",
  "The main character carries a big fish back to camp while children run to meet him.",
  "Sharing meat with the camp was the normal rule, not a kindness.",
  "A group of foragers cutting meat around a large fire at dusk, passing pieces to each other.",
  WOO, "excited", "neutral")
P("Because tomorrow, you might be the one with nothing.",
  "The main character sits alone with an empty spear in the rain, looking at the ground.",
  "Hunting often failed. Many days ended with no meat at all.",
  "An empty hunting trap of sticks and twine in a rainy forest, water dripping from leaves.",
  WOO, "sad", "serious")
P("So your real savings account was other people.",
  "The main character laughs with friends around a campfire, arms around their shoulders.",
  "Help given today was a promise of help coming back.",
  "Two forager families exchanging baskets of food at the edge of a camp at sunset.",
  WIE, "awe", "neutral", hpause=400)
P("Keep that idea in your pocket. We'll need it later.",
  "The main character winks and taps his empty tunic pocket.",
  "Then, about five thousand years ago, things changed.",
  "A green river valley with the first mud-brick town, fields of barley, and people carrying sacks.",
  MES, "funny", "curious")

# ================= trap 1: now vs later
P("Trap number one. Right now beats later.",
  "The main character stands at a fork in a forest path, one sign showing a ripe fruit, one showing a far mountain.",
  "In twenty oh four, scientists scanned people choosing between money now and more money later.",
  "People lying inside large white brain scanners in a quiet hospital room, monitors glowing.",
  MCC, "tense", "curious", beat="punchline", hsfx="ding", text="TRAP 1")
P("Like ten dollars today, or twelve next month.",
  "The main character holds a small fruit in one hand and points at a calendar painted on a rock with the other.",
  "Older, emotional brain areas lit up most for the instant option.",
  "A brain scan with a glowing orange area in the middle and cooler blue areas at the front.",
  MCC, "curious", "neutral")
P("It's like a little caveman inside your head.",
  "The main character looks at a tiny version of himself sitting inside a glass head, banging a drum.",
  "Areas linked to planning got busier when people chose to wait.",
  "The same brain scan with the front area glowing bright blue and the middle area dim.",
  MCC, "funny", "neutral", hpace="fast")
P("Two voices. One shouts now. One whispers later.",
  "The main character stands between a loud drum-beating cave man and a calm old man with a walking stick.",
  "The more the planning areas worked, the more patient the choice.",
  "Two glowing paths inside a clear crystal head, one short and bright, one long and calm.",
  MCC, "whisper", "neutral")
P("Why would evolution build us like this?",
  "The main character scratches his head beside a rotting fruit tree.",
  "In the wild, a later reward was often no reward at all.",
  "A ripe fruit on a branch being snatched by a monkey, the forest wet after rain.",
  WOO, "curious", "serious")
P("A fruit you leave for tomorrow? A monkey eats it.",
  "The main character points angrily at a monkey happily eating his fruit on a branch.",
  "Meat left overnight drew hyenas and went bad by morning.",
  "Hyenas sniffing around a dark camp at night, a small fire flickering, bones on the ground.",
  WOO, "funny", "tense", hpace="fast")
P("So eating it now was usually the smart move.",
  "The main character eats a big fruit in one bite, cheeks full, grinning.",
  "For a forager, waiting could mean losing the reward entirely.",
  "An empty fruit tree at dusk with half-eaten fruit scattered below it.",
  WOO, "happy", "neutral")
P("Now put that brain in a shopping app.",
  "The main character sits on a sofa at night scrolling a phone full of glowing sale buttons.",
  "Today the reward is one tap away, and the cost is weeks away.",
  "A phone screen glowing in a dark bedroom with a big shiny button and a delivery box at the door.",
  MCC, "funny", "serious")
P("Your inner caveman sees fruit. Every single time.",
  "The main character's face glows as a phone shows sneakers that look like ripe fruit.",
  "Studies like this one help explain why spending feels easy and saving feels hard.",
  "A wooden scale with a shiny shopping bag on one side and a small clay jar of coins on the other.",
  MCC, "funny", "neutral")
P("Saving asks the caveman to trust a future he can't see.",
  "The main character squints at a foggy horizon, holding a tiny clay jar.",
  "Scientists still debate how cleanly the brain splits into now and later.",
  "Two scientists arguing politely in front of a whiteboard covered in brain sketches, coffee cups on the table.",
  MCC, "serious", "neutral")
P("Fair. But the pull toward right now? You've felt it.",
  "The main character looks guilty while hiding a new pair of shoes behind his back.",
  "That pull is what researchers call present bias.",
  "A bright glowing fruit in the foreground and a faint mountain far behind, mist between them.",
  MCC, "funny", "neutral")

# ================= trap 2: loss aversion
P("Trap number two. Losing hurts more than winning feels good.",
  "The main character drops a clay pot that shatters on rocky ground, face frozen in shock.",
  "In nineteen seventy-nine, Kahneman and Tversky described this as loss aversion.",
  "Two men in nineteen-seventies clothes at a desk covered in paper sheets and graphs, warm lamp light.",
  KT, "tense", "curious", beat="punchline", hsfx="impact", text="TRAP 2")
P("Find a hundred dollars, you smile for an hour.",
  "The main character finds a banknote on a city sidewalk and smiles.",
  "Later estimates suggest a loss feels roughly twice as strong as the same gain.",
  "A balance scale with one heavy dark stone on one side and two light white stones on the other.",
  KT, "happy", "neutral", text="2x")
P("Lose a hundred dollars, and it ruins your whole day.",
  "The main character sits on a bench in the rain staring at an empty pocket, very grumpy.",
  "The exact size is debated, but the pattern showed up in many countries.",
  "Many small flags of different countries standing on a table around a balance scale.",
  KT, "sad", "neutral")
P("Out there, that fear kept you alive.",
  "The main character guards a small pile of dried meat in a cave during a snowstorm.",
  "For foragers, one lost stash before winter could mean real hunger.",
  "A snowy cave entrance at night with a small fire inside and an empty storage basket.",
  WOO, "serious", "tense")
P("A missed bonus was annoying. A lost stash could kill.",
  "The main character holds an empty basket in the snow, shivering.",
  "So brains that feared losses more had good reasons to.",
  "A wolf circling a frozen camp at night, snow falling, embers glowing.",
  KT, "tense", "neutral")
P("Today, the same fear does strange things with money.",
  "The main character clutches a stock chart printout like a precious stone, sweating.",
  "Loss aversion helps explain why people hold losing bets too long, hoping to break even.",
  "A dark trading screen with a falling red line and a cold cup of coffee beside it.",
  KT, "curious", "serious")
P("We'd rather not look than admit a loss.",
  "The main character covers his eyes while a phone shows a red bank notification.",
  "It also explains why a sale ending tonight feels like losing something.",
  "A shop window with a big clock and a pile of shopping bags under a red glowing light, rain outside.",
  KT, "funny", "neutral")
P("Wait. You lose nothing if you don't buy it.",
  "The main character stops halfway through a shop door, finger raised, realizing something.",
  "Shops know this and frame deals as things you could miss.",
  "Empty shop aisles at night with countdown timers glowing on every shelf.",
  KT, "excited", "neutral")
P("Your caveman hears: the herd is leaving without you.",
  "The main character runs after a herd of animals across a dusty plain, panicking.",
  "Fear of missing out runs on that same ancient alarm.",
  "A herd of antelope running away across a golden plain, dust rising in the evening light.",
  KT, "funny", "neutral", hpace="fast")

# ================= subscribe (after a fact, mid-video)
P("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring the ancient world together, one question at a time. It's free, it takes one second, and it helps more curious people find us.",
  "The main character waves warmly at the viewer beside a campfire under the stars.",
  "Back to the traps. Number three is invisible.",
  "A clear glass jar on a rock at night, looking empty, faint glowing coins inside.",
  PS, "happy", "whisper", hpace="normal", fpause=300)

# ================= trap 3: invisible money (pays off open loop 1)
P("Trap number three. Money you can't see.",
  "The main character stares at his empty hands, then at a card glowing in the air in front of him.",
  "Remember the card experiment from the start? Here it is.",
  "A college auction room with students raising paddles, tickets for a basketball game on a table.",
  PS, "curious", "curious", beat="punchline", hsfx="ding", text="TRAP 3")
P("Students at MIT bid on basketball tickets.",
  "The main character sits among students in an auction room, raising a paddle with a confused smile.",
  "Half had to pay cash. Half could pay by card.",
  "Two groups of students at two tables, one with paper money, one with plastic cards.",
  PS, "neutral", "neutral")
P("Same tickets. Same game. Just a different way to pay.",
  "The main character holds two identical tickets, one in each hand, comparing them.",
  "The card group offered roughly twice as much.",
  "A tall stack of coins next to a short one on a wooden table, auction paddles behind.",
  PS, "curious", "awe", fpause=600, text="2x")
P("Twice! For the exact same seats.",
  "The main character's jaw drops as a price tag doubles in front of him.",
  "It was one study, but the idea of a pain of paying stuck.",
  "A hand reluctantly handing over paper money, fingers tight, at a market stall.",
  PS, "excited", "neutral")
P("Now think about our ancestors.",
  "The main character holds a heavy armful of firewood and fruit, struggling to carry it.",
  "Everything they owned, they could hold, count and see.",
  "A forager's few belongings on a hide mat: a spear, a basket, a knife, a gourd of water.",
  WOO, "curious", "neutral")
P("Give away food, and the basket gets lighter. You feel it.",
  "The main character hands fruit from his basket to a friend, watching it get lighter.",
  "Cash still works a little like that. You watch it leave.",
  "A wallet with only a few paper notes left, on a kitchen table in the rain-dark evening.",
  PS, "neutral", "neutral")
P("A card? Nothing gets lighter. Nothing leaves your hand.",
  "The main character taps a card on a reader and looks at his hand. It is still full.",
  "No basket, no weight, no warning signal for the brain.",
  "A shiny payment terminal glowing in a dark shop, a tiny beep light flashing green.",
  PS, "whisper", "serious")
P("Your caveman thinks the fruit was free.",
  "The main character walks out of a shop with arms full of bags, whistling happily.",
  "Then the bill arrives weeks later, far from the moment of fun.",
  "An envelope on a doormat under a rainy window, a pile of shopping bags in the corner.",
  MCC, "funny", "tense")
P("That's trap one and trap three teaming up.",
  "The main character high-fives a tiny cave version of himself, both grinning mischievously.",
  "The joy is instant. The cost is delayed and invisible.",
  "A bright party scene in the foreground and a dark storm cloud far in the background.",
  MCC, "funny", "serious")

# ================= trap 4: neighbours
P("Trap number four. The neighbours.",
  "The main character peeks over a hedge at a neighbour washing a shiny new car.",
  "Our ancestors lived in small bands, often a few dozen adults.",
  "A small forager camp of grass huts in a clearing, about thirty people, smoke from cooking fires.",
  WOO, "curious", "neutral", beat="punchline", hsfx="pop", text="TRAP 4")
P("In a band that small, everyone saw everything.",
  "The main character sits by a fire while everyone around it watches him eat.",
  "Your place in the group decided who helped you when things went wrong.",
  "Forager elders talking around a fire at night while a younger man listens respectfully.",
  WIE, "neutral", "serious")
P("Standing out a little was useful. Falling behind was scary.",
  "The main character proudly shows a big fish while others clap.",
  "Today we compare ourselves to far more people than any forager ever met.",
  "A teenager in bed at night scrolling past glowing pictures of yachts and beaches on a phone.",
  LUT, "excited", "serious")
P("And one economist measured what that does to us.",
  "The main character looks over the shoulder of an economist reading charts.",
  "Erzo Luttmer linked people's happiness to their neighbours' earnings.",
  "A quiet suburban street at dusk with similar houses, lights on in the windows.",
  LUT, "curious", "neutral")
P("Same income for you. Neighbours start earning more.",
  "The main character stands in his garden as neighbouring houses grow taller and shinier.",
  "On average, people reported feeling less happy.",
  "A man sitting on his porch looking at a bigger house across the street, rain starting.",
  LUT, "curious", "sad")
P("Nothing changed for you. Except the comparison.",
  "The main character holds the same small basket, looking at bigger baskets around him.",
  "Economists see this as caring about relative income, not only our own.",
  "Two baskets of fruit side by side, one bigger, under a single hanging lamp.",
  LUT, "serious", "neutral")
P("So we buy things to keep up. Not to enjoy them.",
  "The main character drives a too-big car down a narrow street, looking stressed.",
  "Status spending can quietly eat a salary without making anyone happier.",
  "An empty fridge and a brand-new giant television in the same small apartment.",
  LUT, "funny", "serious")
P("Our caveman thinks the whole tribe is watching.",
  "The main character poses for a phone selfie wearing expensive sunglasses with his hide tunic.",
  "Most of them are scrolling too fast to notice.",
  "A crowded city subway car where everyone looks down at their own phone.",
  LUT, "funny", "neutral", hpace="fast")

# ================= trap 5: debt (pays off open loop 2)
P("Trap number five. The oldest one. Debt.",
  "The main character stands before a tall stone gate of an ancient city at sunset, holding a clay tablet.",
  "Remember the clay from the start? This is where it comes from.",
  "A Mesopotamian scribe pressing a reed into wet clay by lamplight, tablets drying nearby.",
  MES, "tense", "curious", beat="punchline", hsfx="riser", text="TRAP 5")
P("Farming changed everything. Now you could store grain.",
  "The main character carries heavy sacks of barley into a mud-brick storehouse.",
  "Early Mesopotamian accounts tracked barley and silver on clay.",
  "Piles of barley sacks and small silver rings on scales in a mud-brick room.",
  MES, "neutral", "neutral")
P("Stored grain meant you could lend it. And borrow it.",
  "The main character hands a sack of grain to a worried farmer while a scribe writes.",
  "Loans of silver often charged about a fifth extra.",
  "A small pile of silver rings on a balance scale next to a clay tablet, oil lamp light.",
  MES, "curious", "neutral", text="20%")
P("And grain? Even more.",
  "The main character's eyebrows shoot up as a scribe adds another sack to the pile.",
  "Grain loans could cost about a third on top.",
  "A farmer looking at a huge pile of barley sacks he must repay, storm clouds over the fields.",
  MES, "funny", "tense", text="33%")
P("Nearly four thousand years ago, the law stepped in.",
  "The main character reads a tall black stone pillar carved with tiny wedge marks.",
  "The Code of Hammurabi set rules for loans and interest.",
  "A tall black stone pillar carved with dense wedge-shaped writing in a temple courtyard, torches burning.",
  MES, "awe", "neutral", hpause=300)
P("Humans needed laws about debt before they had coins.",
  "The main character holds a clay tablet in one hand and a modern credit card in the other.",
  "The same idea lives in every credit card bill today.",
  "A pile of modern bills and envelopes on a table next to an ancient clay tablet.",
  MES, "awe", "serious")
P("And debt mixes all the traps together.",
  "The main character juggles five glowing stones, looking dizzy.",
  "The joy comes now, the payment comes later, and often unseen.",
  "A wrapped gift glowing in the foreground, a long dark road of bills behind it.",
  MCC, "funny", "serious")
P("Right now wins. Invisible money. Keeping up. All at once.",
  "The main character stands in a mall holding bags, a card and a phone, overwhelmed.",
  "Interest keeps growing quietly, like weeds after rain.",
  "Weeds spreading fast across a small garden plot after heavy rain, water pooling.",
  MES, "tense", "neutral")

# ================= ancient insurance (pays off "savings account was other people")
P("So, did our ancestors have no safety net at all?",
  "The main character sits by a fire in the rain, holding his knees, thinking.",
  "They did. Remember: their savings account was other people.",
  "A wide desert at dusk with tiny camps far apart, connected by faint footpaths.",
  WIE, "curious", "awe")
P("The Ju/'hoansi of the Kalahari called it hxaro.",
  "The main character receives a beaded necklace from a smiling friend at a desert camp.",
  "Hxaro partners traded gifts across distances of up to about two hundred kilometres.",
  "Two forager women exchanging ostrich-shell bead necklaces in a desert camp at sunset.",
  WIE, "neutral", "neutral")
P("When rain failed in one place, you walked to a friend.",
  "The main character walks across a dry cracked land toward a distant green camp.",
  "In the nineteen seventies, about seven in ten of their belongings were hxaro gifts.",
  "A small hut interior with beaded bags, blankets and tools hanging, warm firelight.",
  WIE, "serious", "awe", text="69%")
P("Their wealth wasn't stuff. It was friendships.",
  "The main character sits among many friends laughing around a big fire.",
  "As cash spread, those partnerships fell by about half.",
  "A desert camp with fewer people, a small shop with metal roof in the distance.",
  WIE, "awe", "sad")
P("I find that a little sad, honestly.",
  "The main character looks at an empty spot by the fire where a friend used to sit.",
  "Researchers saw money replace some of what people once did for each other.",
  "A single lantern on a table between two empty chairs on a rainy evening.",
  WIE, "sad", "neutral")

# ================= the willpower myth
P("So is the answer just more willpower?",
  "The main character clenches his fists and stares hard at a cake on a table.",
  "The famous marshmallow test suggested patient kids did better later.",
  "A small child at a table staring at one marshmallow on a plate, a bell beside it.",
  WAT, "curious", "neutral")
P("Wait for two treats instead of one, and you'd succeed in life.",
  "The main character sits at a tiny table staring at a marshmallow, sweating.",
  "But a much bigger study in twenty eighteen found the link was far smaller.",
  "Hundreds of children's drawings pinned to a big board in a research office.",
  WAT, "funny", "serious")
P("So what mattered more?",
  "The main character raises an eyebrow at the marshmallow, suspicious.",
  "Family background and home life explained a big part of it.",
  "A warm family kitchen in the evening with children doing homework at the table, rain on the window.",
  WAT, "curious", "awe", fpause=500)
P("That's the part nobody tells you.",
  "The main character sits down, thoughtful, the marshmallow forgotten.",
  "Environment shaped choices as much as willpower did.",
  "A tidy room with a clear plan pinned to the wall, a calm morning light.",
  WAT, "serious", "neutral")

# ================= ending
P("So if your money slips away, it isn't all your fault.",
  "The main character looks straight at the viewer, calm and kind.",
  "Every trap was once a survival skill.",
  "Five glowing stones in a circle around a campfire at night, sparks rising.",
  WOO, "serious", "awe")
P("Your brain is doing its job. Just for the wrong century.",
  "The main character stands in a modern city at night, looking up at bright billboards.",
  "Most people worldwide never learned the basic money ideas.",
  "A night classroom with empty desks and simple drawings of coins and jars on a chalkboard.",
  FIN, "funny", "neutral")
P("But here's the hopeful part. A trap you can see is weaker.",
  "The main character steps around a glowing trap on the path, smiling.",
  "Researchers found that knowing a bias is the first step to noticing it.",
  "A person pausing at a shop door, looking at a price tag thoughtfully, rain outside.",
  KT, "excited", "neutral")
P("Next time you tap that card, listen for the caveman.",
  "The main character pauses with a card above a payment terminal, listening.",
  "Five traps. Right now, losses, invisible money, neighbours, and debt.",
  "Five carved stones in a row on a beach at sunset, each glowing softly.",
  PS, "whisper", "curious")
H("Thank you for spending these minutes with me. If it helped you see your own habits a little clearer, hit like, and tell me in the comments which trap catches you most. I read every one. Next time, we'll find out how the first coins changed the ancient world. See you there, friend.",
  "The main character waves goodbye by a campfire at dusk, a clay tablet and a bank card resting on a rock beside him.",
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
    "title": "Why Is Saving MONEY So Hard for Humans?",
    "title_alternatives": ["Ancient Humans Had No Money. Why Are We So BAD at It?", "Your Stone Age Brain Is Why You Can't Keep MONEY",
                           "The 5 Ancient Traps Your Brain Uses Against Your MONEY", "Why Your Salary Disappears: The Stone Age ANSWER",
                           "Your Brain Is Older Than MONEY"],
    "description": ("Two out of three adults failed a simple money test. Not because they're stupid, but because the human brain is far older than money. "
                    "Five ancient traps, from 'right now beats later' to five-thousand-year-old debt, and why they made sense for our ancestors.\n\n"
                    "This video is history and psychology for education. It is not financial advice.\n\nSources:\n"
                    "- Klapper, Lusardi & van Oudheusden (2015). S&P Global FinLit Survey (2014 data).\n"
                    "- Hublin et al. (2017). Jebel Irhoud and the origin of Homo sapiens. Nature.\n"
                    "- Woodburn (1982). Egalitarian societies. Man.\n"
                    "- McClure et al. (2004). Separate neural systems value immediate and delayed monetary rewards. Science.\n"
                    "- Kahneman & Tversky (1979); Tversky & Kahneman (1992). Prospect theory.\n"
                    "- Prelec & Simester (2001). The credit-card effect on willingness to pay. Marketing Letters.\n"
                    "- Luttmer (2005). Neighbors as negatives. Quarterly Journal of Economics.\n"
                    "- Code of Hammurabi (c. 1754 BCE) and Mesopotamian loan tablets.\n"
                    "- Wiessner & Huang (2022). Ju/'hoansi kinship, cash and risk pooling. PNAS.\n"
                    "- Watts, Duncan & Quan (2018). Revisiting the marshmallow test. Psychological Science."),
    "tags": ["money psychology", "why is saving money hard", "ancient humans", "stone age brain", "behavioral economics",
             "loss aversion", "present bias", "hunter gatherers", "history of money", "mesopotamia debt", "financial literacy", "animated explainer"],
    "mood": "playful",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Why Is Saving MONEY So Hard for Humans?", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-11-02.", "",
      "## Method",
      "- Every study was found online and its abstract, record or a reliable summary opened; contested points are told as such.",
      "- No financial advice: the video explains why brains struggle with money and never tells viewers what to buy, save or invest.",
      "- Modern foragers are not treated as living ancestors; 'many foragers' and 'anthropologists describe' are used.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- 'Losses hurt exactly 2x': the factor comes from later estimates and is debated; said as 'roughly twice', debate mentioned.",
       "- FinLit 33% is 2014 data; said as 'about one in three passed', year in the description.",
       "- Mesopotamian interest rates come from legal-history summaries; said as 'about a fifth' and 'about a third'.",
       "- Woodburn's immediate-return model rests on Hadza fieldwork; a later study found big game sharing favours the hunter's household; 'many foragers' used.",
       "- McClure 2004 limbic finding: later replications mixed; 'brain scans suggest' and the debate line used.",
       "- Prelec & Simester: one MIT experiment; 'in one experiment' said, no general claim that cards double spending.",
       "- 'Knowing a bias is the first step to noticing it' is a general framing, not a cited effect size.",
       "- Dropped: the claim that lottery winners usually go broke (no solid source found)."]
Path(__file__).with_name("money_brain.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
