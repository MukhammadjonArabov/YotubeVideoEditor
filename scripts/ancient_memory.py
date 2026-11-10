"""Builds scripts/ancient_memory.json (run: ./venv/Scripts/python scripts/ancient_memory.py).
Scene tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source)
Odd scenes = hero, even scenes = fact (strict alternation, see CLAUDE.md)."""
import json
from pathlib import Path

DRE = "Dresler et al. (2017). Mnemonic training reshapes brain networks to support superior memory. Neuron"
NUN = "Nunn & Reid (2016). Aboriginal memories of inundation of the Australian coast. Australian Geographer"
MAG = "Maguire et al. (2003). Routes to remembering: the brains behind superior memory. Nature Neuroscience"
SPA = "Sparrow, Liu & Wegner (2011). Google effects on memory. Science"
CIC = "Cicero, De Oratore, Book 2 (the story of Simonides of Ceos)"
QUI = "Quintilian, Institutio Oratoria, Book 11"
KEL = "Kelly, L. (2016). The Memory Code. Allen & Unwin"
CUN = "Earliest writing, cuneiform in Mesopotamia, about 3200 BCE (British Museum)"
HUB = "Hublin et al. (2017). New fossils from Jebel Irhoud, Morocco. Nature"
LOR = "Lord, A. (1960). The Singer of Tales. Harvard University Press"
HOM = "The Iliad, about 15,700 lines; oral-formulaic theory of Milman Parry (Parry, 1930s)"
EBB = "Ebbinghaus (1885), replicated by Murre & Dros (2015), PLOS ONE"
NMA = "Songlines: Tracking the Seven Sisters, National Museum of Australia (2017)"
YAT = "Yates, F. (1966). The Art of Memory. Routledge"

S = [
    # ---------------- hook (12 one-line scenes)
    ("Quick: what did you eat three days ago?", "The main character scratches his head, staring at an empty wooden bowl, completely puzzled.", "hook", "curious", 2, "normal", 0, None, None),
    ("Humans lived without writing for nearly three hundred thousand years.", "A long line of ancient people walking across a vast plain at sunset, carrying spears and baskets.", "hook", "awe", 2, "normal", 0, None, HUB + "; " + CUN),
    ("No notes, no phone, no cloud backup.", "The main character pats his empty fur tunic pockets, looking around in mild panic.", "hook", "funny", 2, "fast", 0, "pop", None),
    ("Yet some stories may have survived seven thousand years.", "An elder telling a story to a circle of listeners around a campfire under a starry sky.", "hook", "awe", 3, "slow", 300, None, NUN),
    ("Meanwhile, your phone remembers everything, so you don't.", "The main character stares at a glowing flat stone in his hand like a phone, eyes glazed.", "hook", "serious", 2, "normal", 0, None, None),
    ("Expecting to look things up, people remember them less.", "A modern person scrolling a phone while a thought bubble above them fades into nothing.", "hook", "serious", 2, "normal", 0, None, SPA),
    ("Today you'll learn their memory trick, step by step.", "The main character points proudly at his own head with a big confident grin.", "hook", "curious", 3, "normal", 0, None, None),
    ("In one study, it more than doubled word recall.", "A simple bar chart drawn on a cave wall, one short bar and one bar twice as tall.", "hook", "excited", 2, "normal", 0, "ding", DRE),
    ("And you can start using it tonight.", "The main character rubs his hands together excitedly next to a cozy cave fire.", "hook", "excited", 2, "fast", 0, None, None),
    ("But first, a disaster in ancient Greece started everything.", "A grand ancient Greek banquet hall with columns and long tables, lit by oil lamps.", "hook", "tense", 2, "normal", 0, None, CIC),
    ("A roof collapsed, and one survivor remembered every guest.", "The main character stands outside a dusty ruined hall, staring at the rubble in shock.", "hook", "whisper", 2, "slow", 300, "impact", None),
    ("How he did it changed memory forever.", "Broken stone columns and fallen roof tiles in a cloud of settling dust.", "hook", "tense", 3, "slow", 500, None, CIC),
    # ---------------- a world without writing
    ("Let's rewind. Picture every recipe, every map, every family rule, all of it stored in one place: your head.", "The main character sits by a fire with dozens of tiny floating pictures circling his head.", "build", "curious", 2, "normal", 0, None, None),
    ("The oldest known writing, Mesopotamian cuneiform, appeared only about five thousand two hundred years ago.", "A clay tablet covered in small wedge-shaped marks resting on a wooden table.", "build", "neutral", 2, "normal", 0, None, CUN),
    ("That's a blink. For almost all of human history, nothing was written down. Not once.", "The main character holds a tiny pebble up to a giant boulder, comparing their sizes.", "build", "serious", 2, "slow", 0, None, None),
    ("Our species is at least three hundred thousand years old, based on fossils from Jebel Irhoud in Morocco.", "Ancient skull fossils half buried in red desert rock under bright sun.", "build", "awe", 2, "normal", 0, None, HUB),
    ("So for about ninety eight percent of that time, if you forgot something important, it was simply gone.", "The main character drops a basket of berries and watches them roll away across the ground.", "build", "sad", 2, "normal", 0, None, None),
    ("And forgetting is fast. Ebbinghaus found that memories of new material fade quickest in the very first hours.", "A curved line drawn in the sand dropping steeply at first and then flattening out.", "build", "neutral", 2, "normal", 0, None, EBB),
    ("Which sounds like a death sentence for knowledge. Which plant heals, which one kills, where the water hides in a drought.", "The main character looks nervously between two nearly identical plants, one in each hand.", "build", "tense", 2, "normal", 0, None, None),
    ("Researcher Lynne Kelly argues that oral cultures still held huge amounts of practical knowledge about plants, animals and land.", "A wide valley full of different plants, birds and animals, each one clearly visible.", "build", "curious", 2, "normal", 0, None, KEL),
    ("So they weren't forgetting. They were remembering on a scale that would melt our brains.", "The main character's eyes grow wide as the night sky fills with glowing constellations.", "punchline", "awe", 3, "slow", 400, None, None),
    ("Here's the plot twist: they didn't have better brains than ours. They had better methods.", "Two identical brains drawn side by side on a cave wall, one with a winding path drawn through it.", "punchline", "excited", 2, "normal", 0, "whoosh", MAG),
    # ---------------- why we forget now
    ("Now, before we get smug about the past, let's talk about you.", "The main character sits on a log and looks straight ahead with a teasing smile.", "build", "funny", 2, "normal", 0, None, None),
    ("In a two thousand eleven study, people who expected to look trivia up later remembered it less well.", "A modern laptop on a desk next to a sticky note that is fading away.", "build", "neutral", 2, "normal", 0, None, SPA),
    ("Basically, your brain thinks: why carry it, if the phone carries it for me?", "The main character hands a heavy rock to a small helper creature and walks away relaxed.", "build", "funny", 2, "fast", 0, "boing", None),
    ("The researchers also found people often remembered where the information was saved, instead of the information itself.", "A cartoon filing cabinet with one open drawer and an arrow pointing at it.", "build", "neutral", 2, "normal", 0, None, SPA),
    ("And honestly? That's not stupid. It's efficient. Our ancestors had no such luxury.", "The main character shrugs, holding a flat stone tablet with nothing on it.", "build", "serious", 2, "normal", 0, None, None),
    ("For them, the only cloud storage was other people and the land itself.", "A small village of huts beside a river, people talking in groups between the huts.", "build", "curious", 2, "normal", 0, None, KEL),
    ("Which brings us to one of the most impressive memory systems ever built.", "The main character walks toward a red desert landscape that stretches to the horizon.", "build", "excited", 2, "normal", 0, None, None),
    ("In Aboriginal Australia, knowledge was woven into songlines: songs that follow paths across the land.", "A winding dotted path crossing a red desert, passing rocks, a waterhole and a hill.", "build", "awe", 2, "slow", 0, "swoosh", NMA),
    # ---------------- songlines
    ("Imagine a song where every verse is a place. Sing the verse, and you know where the next waterhole is.", "The main character walks along a dusty path, mouth open in song, a waterhole ahead.", "build", "curious", 2, "normal", 0, None, None),
    ("Songlines can stretch across huge distances, linking landmarks, stories, laws and navigation in a single path.", "A large map-like landscape seen from above with a long glowing path linking rocks and rivers.", "build", "awe", 2, "normal", 0, None, NMA),
    ("It's a map, an encyclopedia, and a playlist. All at once. Try doing that with your phone.", "The main character holds a stone in one hand and a stick in the other, pretending to play music.", "build", "funny", 2, "fast", 0, "pop", None),
    ("And the land helps. Each rock or hill becomes a hook that a memory hangs on.", "A distinctive rock shaped like a sleeping animal standing alone in the desert.", "build", "neutral", 2, "normal", 0, None, KEL),
    ("Here's where it gets wild. Some of these stories describe the sea swallowing land.", "The main character stands on a beach watching the waves creep closer to his feet.", "build", "tense", 2, "slow", 0, None, None),
    ("Researchers collected stories from twenty one places around Australia's coast describing land lost to rising seas.", "A coastline with shallow water covering old trees and hills, seen from a cliff.", "build", "awe", 2, "normal", 0, None, NUN),
    ("So how do you check a story that old? You compare it with the sea itself.", "The main character squints at the waves, holding a long measuring stick in the water.", "build", "curious", 2, "normal", 0, None, None),
    ("When they compared the stories to sea level records, the flooding matched a time over seven thousand years ago.", "Layers of sea water rising up a hillside, drawn as simple steps of blue.", "punchline", "awe", 3, "slow", 500, "ding", NUN),
    ("Seven thousand years. That's older than the pyramids. Passed down by voice, person to person.", "The main character whispers into another person's ear, who whispers to the next, in a long line.", "build", "whisper", 2, "slow", 300, None, None),
    ("To be fair, this is debated. Some experts think oral history only stays accurate for centuries, not millennia.", "Two scholars in robes pointing at different scrolls with crossed arms.", "build", "serious", 2, "normal", 0, None, NUN),
    ("But even if it's only half right, it's still the longest game of telephone humans have ever won.", "The main character raises a trophy made of carved wood, beaming with pride.", "build", "funny", 2, "normal", 0, None, None),
    ("The trick in songlines is simple to name: tie every fact to a place, and walk the places in order.", "A simple drawing of a footpath with small pictures placed at each turn of the path.", "build", "neutral", 2, "normal", 0, None, KEL),
    ("Remember that. Places in order. It's about to show up on the other side of the world.", "The main character taps his temple knowingly and winks.", "build", "curious", 2, "normal", 0, None, None),
    # ---------------- Simonides
    ("Back to Greece. The poet Simonides of Ceos was performing at a feast when he was called outside.", "A crowded ancient Greek feast hall with a poet standing by the door.", "build", "neutral", 2, "normal", 0, None, CIC),
    ("Seconds later, the roof came down. Everyone inside was crushed, too damaged to recognize.", "The main character covers his ears as dust bursts from the doorway of a collapsing hall.", "build", "tense", 3, "fast", 0, "impact", None),
    ("According to Cicero, Simonides identified every guest by remembering exactly where each one had been sitting.", "A long banquet table seen from above with empty seats in a neat row.", "punchline", "awe", 2, "slow", 400, None, CIC),
    ("Seat one, the merchant. Seat two, the athlete. Place by place, he walked the table in his mind.", "The main character walks slowly along a row of chairs, pointing at each one in turn.", "build", "curious", 2, "normal", 0, None, None),
    ("That story became the origin legend of the method of loci, loci simply meaning places in Latin.", "An old scroll lying open on a marble bench beside a small oil lamp.", "build", "neutral", 2, "normal", 0, None, CIC + "; " + YAT),
    ("Sounds familiar? It's the songline trick again. Places in order. Two cultures, same discovery.", "The main character holds a Greek column in one hand and a desert rock in the other, comparing them.", "punchline", "excited", 2, "normal", 0, "whoosh", None),
    ("Roman teachers trained speakers to place each part of a speech in rooms of an imagined building.", "A Roman house drawn in cross section, each room holding one simple object.", "build", "neutral", 2, "normal", 0, None, QUI),
    ("So a two hour speech was really just a walk through a house you knew by heart.", "The main character strolls through a big imaginary house, waving at objects in each room.", "build", "happy", 2, "normal", 0, None, None),
    ("For centuries, this art of memory was taught as a serious skill, long after writing existed.", "A medieval monk at a desk surrounded by drawings of rooms and arches.", "build", "neutral", 2, "normal", 0, None, YAT),
    ("Then printing arrived, books got cheap, and the skill slowly faded. A bit like your phone did to phone numbers.", "The main character looks sadly at a pile of books stacked high next to his cave.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- oral epics
    ("But the best proof that memory can be trained comes from poetry.", "A storyteller standing on a stone stage, arms spread wide, in front of a large crowd.", "build", "curious", 2, "normal", 0, None, HOM),
    ("The Iliad runs to about fifteen thousand seven hundred lines. Many scholars think it grew out of an oral tradition.", "The main character stares up at an impossibly tall scroll unrolling down a hillside.", "build", "awe", 2, "normal", 0, None, None),
    ("Milman Parry noticed the poem repeats ready-made phrases, like swift-footed Achilles, which fit the rhythm perfectly.", "Small identical building blocks stacked into a tall tower, each block the same shape.", "build", "neutral", 2, "normal", 0, None, HOM),
    ("Those phrases are like Lego bricks for storytellers. Grab one, click it in, keep going.", "The main character stacks wooden blocks into a tower, grinning with each new block.", "build", "funny", 2, "fast", 0, "click", None),
    ("In the nineteen thirties, Parry and Albert Lord recorded singers in the Balkans performing epics with no written text.", "A singer with a simple stringed instrument performing to villagers in a stone courtyard.", "build", "neutral", 2, "normal", 0, None, LOR),
    ("One singer reportedly sang a single epic of around twelve thousand lines, over several days.", "The main character sits in an audience, yawning and then snapping awake, amazed.", "build", "awe", 2, "normal", 0, None, None),
    ("Lord found the singers weren't reciting word for word. They rebuilt each story from patterns every time.", "A path of stepping stones across a river, each stone a slightly different shape.", "build", "curious", 2, "normal", 0, None, LOR),
    ("So their memory wasn't a recording. It was a skill. And skills can be learned.", "The main character flexes his skinny arm like a bodybuilder, proudly.", "punchline", "excited", 2, "normal", 300, None, None),
    ("Which raises the obvious question: could you learn it? Science has actually tested this.", "A modern laboratory with a brain scanner and a desk of word lists.", "build", "curious", 2, "normal", 0, "riser", DRE),
    ("Spoiler: yes. And you won't believe how fast.", "The main character leans forward with wide eyes, hanging on every word.", "build", "excited", 3, "fast", 0, None, None),
    # ---------------- memory athletes
    ("First, the memory champions. People who memorize a deck of cards in under a minute.", "A shuffled deck of cards spread across a table under bright competition lights.", "build", "neutral", 2, "normal", 0, None, MAG),
    ("Surely they have giant, special brains, right?", "The main character pictures a huge glowing brain floating above a stage, eyes wide.", "build", "funny", 2, "normal", 0, None, None),
    ("In two thousand three, scientists scanned superior memorizers and found no clear structural differences from ordinary brains.", "Two brain scans side by side on a light box, looking almost identical.", "punchline", "awe", 2, "slow", 400, None, MAG),
    ("What they did share was a strategy. Most of them used the method of loci. Places in order.", "The main character walks through his cave, placing small objects at each corner.", "build", "excited", 2, "normal", 0, "ding", None),
    ("Then in two thousand seventeen, a team trained ordinary people in the method of loci for six weeks.", "A group of ordinary people at computers wearing headphones, practicing quietly.", "build", "neutral", 2, "normal", 0, None, DRE),
    ("Thirty minutes a day. Not monks, not geniuses. Regular folks with regular schedules.", "The main character sits cross-legged with his eyes closed, timing himself with a sundial.", "build", "neutral", 2, "normal", 0, None, None),
    ("Before training, they could recall around twenty six to thirty words from a list of seventy two.", "A long list of simple pictures on a wall, with only a few of them circled.", "build", "neutral", 2, "normal", 0, None, DRE),
    ("Now guess how many they remembered after six weeks. Go on, guess.", "The main character bites his nails nervously, staring at a closed wooden box.", "build", "tense", 2, "normal", 0, None, None),
    ("After six weeks, the method of loci group recalled about thirty five more words on average.", "The same wall of pictures with most of them now circled, bright and clear.", "punchline", "excited", 3, "normal", 500, "ding", DRE),
    ("That's more than double. In six weeks. With a trick older than writing.", "The main character jumps in the air with both fists raised in triumph.", "punchline", "excited", 3, "fast", 0, None, None),
    ("Four months later, they still remembered over twenty two more words than before training.", "A calendar drawn as stone tablets, four of them, with a happy brain drawn on the last.", "build", "happy", 2, "normal", 0, None, DRE),
    ("So it wasn't a quick sugar rush. The skill actually stuck.", "The main character proudly holds up a carved stone with a brain drawn on it, smiling.", "build", "happy", 2, "normal", 0, None, None),
    ("Their brain scans even started to look more like the champions' brains, in how regions talked to each other.", "Two brain drawings connected by glowing lines that slowly match each other.", "build", "awe", 2, "normal", 0, None, DRE),
    ("Okay. Enough history. Let's build your first memory palace. Right now.", "The main character rolls up his sleeves and grabs a stick to draw on the ground.", "build", "excited", 2, "normal", 0, "whoosh", None),
    # ---------------- build your memory palace (practical part)
    ("Step one: pick a place you know perfectly. Your home works great.", "A simple cozy house with a front door, a hallway, a kitchen and a bedroom.", "build", "curious", 2, "normal", 0, None, QUI),
    ("Not a fancy palace. The place where you could find the fridge in the dark at three in the morning.", "The main character tiptoes through a dark kitchen toward a glowing food storage box.", "build", "funny", 2, "normal", 0, None, None),
    ("Step two: choose a route. Front door, hallway, kitchen, sofa, bed. Always the same order.", "A dotted path drawn through a house floor plan, from the door to the bed.", "build", "neutral", 2, "normal", 0, None, QUI),
    ("Order matters because it's the songline idea again. The path keeps the memories in line.", "The main character walks a winding path, touching each tree along the way.", "build", "curious", 2, "normal", 0, None, None),
    ("Step three: turn what you need to remember into a picture. Ancient teachers said striking images stick best.", "A giant strange fish wearing a crown sitting on a doormat.", "build", "neutral", 2, "normal", 0, None, YAT),
    ("Let's try a shopping list: eggs, milk, bread, bananas, and batteries.", "The main character holds a long strip of bark with five simple drawings on it.", "build", "happy", 2, "normal", 0, None, None),
    ("Step four: place each picture along your route, and make it ridiculous.", "A front door with a giant cracked egg oozing over the handle.", "build", "funny", 2, "normal", 0, None, YAT),
    ("A giant egg cracking all over your front door. Gross. Memorable.", "The main character jumps back from a door dripping with egg yolk, disgusted.", "build", "funny", 3, "fast", 0, "boing", None),
    ("A river of milk flooding the hallway. Bread slices as kitchen tiles.", "A hallway flooded with white milk and a kitchen floor tiled with bread slices.", "build", "excited", 2, "normal", 0, None, YAT),
    ("A banana lounging on your sofa like it owns the place.", "The main character stares at a banana relaxing on a couch with sunglasses.", "build", "funny", 2, "fast", 0, None, None),
    ("And batteries buzzing under your pillow, keeping you awake.", "A bed with a pillow lifted up and batteries sparking underneath it.", "build", "curious", 2, "normal", 0, None, YAT),
    ("Step five: walk the route in your head. Door, hallway, kitchen, sofa, bed.", "The main character closes his eyes and walks slowly, a dream bubble showing the house.", "build", "curious", 2, "slow", 0, None, None),
    ("Each place hands you its picture back. That's exactly what the method of loci trains.", "The same house floor plan with a small glowing picture at each stop along the path.", "build", "neutral", 2, "normal", 0, None, DRE),
    ("Go ahead, try it. Without looking. Door?", "The main character points at a door with a raised eyebrow, waiting.", "build", "curious", 2, "slow", 600, None, None),
    ("Egg. Hallway? Milk. Kitchen? Bread. That's how the method works, and it gets faster with practice.", "A row of five simple pictures lighting up one after another.", "build", "excited", 2, "fast", 0, "ding", DRE),
    ("The first time feels silly. The fifth time feels like a superpower. I'm not even exaggerating.", "The main character stands like a superhero on a rock with his tunic blowing in the wind.", "build", "happy", 2, "normal", 0, None, None),
    ("And you can reuse the same route again and again, just like singers reused paths and phrases.", "A worn footpath through grass, clearly used many times.", "build", "neutral", 2, "normal", 0, None, LOR),
    ("Use it for speeches, exam lists, names at a party. Anything that comes in a list.", "The main character waves at a group of people, each with a small picture above their head.", "build", "happy", 2, "normal", 0, None, None),
    # ---------------- monuments as memory (hypothesis)
    ("Some researchers think ancient monuments may have worked as memory palaces too.", "Large standing stones in a circle on a green plain under clouds.", "build", "curious", 2, "normal", 0, "swoosh", KEL),
    ("Imagine a circle of stones where every stone holds a story. Walk the circle, recall the knowledge.", "The main character walks slowly around a circle of tall stones, touching each one.", "build", "awe", 2, "slow", 0, None, None),
    ("Lynne Kelly argues sites like Stonehenge could have served this role. It's a fascinating idea, but still a hypothesis.", "A ring of huge stone pillars with lintels at sunrise, mist around the base.", "build", "serious", 2, "normal", 0, None, KEL),
    ("Either way, the logic is the same one you just used for bananas and batteries.", "The main character balances a banana on top of a tall standing stone and grins.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- ending
    ("So, how did ancient humans remember everything without writing? They turned the world into a map of memories.", "A wide landscape at dusk where small glowing pictures float above rocks, trees and rivers.", "punchline", "awe", 2, "slow", 400, None, NMA + "; " + KEL),
    ("Places in order. Vivid pictures. Walk, and remember. The same trick from a desert song to a Greek feast.", "The main character walks along a path, glowing pictures appearing beside him as he passes.", "build", "serious", 2, "slow", 0, None, None),
    ("And modern science agrees: six weeks of practice changed how ordinary people's brains worked together.", "Two simple brain drawings with lines of light linking their parts.", "build", "neutral", 2, "normal", 0, None, DRE),
    ("Your phone is great. Keep it. But your brain is still the oldest storage device you own.", "The main character sets a flat stone phone down on a rock and taps his head with a smile.", "build", "happy", 2, "normal", 0, None, None),
    ("Our ancestors carried whole libraries in their heads for three hundred thousand years.", "A huge starry night sky over a small campfire where a few people sit together.", "build", "awe", 2, "slow", 0, None, HUB),
    ("Tonight, try a five-item palace. You might be surprised who's living in your head.", "The main character waves goodnight from the doorway of his cozy cave, firelight behind him.", "punchline", "happy", 2, "slow", 800, None, None),
]

# Extra sentences (narration start -> appended text): the video must reach ~13 minutes (~1950 words).
ADD = {
    "Let's rewind.": " No sticky notes, no calendar reminders, no search bar.",
    "The oldest known writing": " Before that, every single thing a community knew had to live inside living people.",
    "That's a blink.": " If human history were one day, writing showed up in the last half hour.",
    "Our species is at least": " Hundreds of thousands of years of experience, passed on without a single page.",
    "So for about ninety eight": " Or rather, it was gone unless somebody else still carried it.",
    "And forgetting is fast.": " Your brain is not a hard drive. It's more like a garden that gets weedy fast.",
    "Which sounds like a death": " Forget the wrong detail, and the whole group pays for it.",
    "Researcher Lynne Kelly argues": " Think thousands of species, seasons, routes and rules, all held in memory.",
    "So they weren't forgetting.": " And they did it every day, without ever calling it a skill.",
    "Here's the plot twist": " And methods can be copied. Including by you.",
    "Now, before we get smug": " Because modern life does something sneaky to memory.",
    "In a two thousand eleven study": " The idea of saving it somewhere was enough to make the brain relax.",
    "Basically, your brain thinks": " Very relatable. Very lazy. Very human.",
    "And honestly? That's not stupid.": " If the information is always one tap away, why spend the energy?",
    "For them, the only cloud": " Elders, songs, ceremonies and landmarks were the backup drives.",
    "In Aboriginal Australia": " Some of them are described as crossing a large part of the continent.",
    "Imagine a song where": " Forget the next verse, and you might walk past the water.",
    "Songlines can stretch": " Knowledge isn't stored in a book. It's stored in a route.",
    "And the land helps.": " The landscape itself becomes the bookshelf.",
    "Researchers collected stories": " The stories talk about islands that used to be joined to the mainland.",
    "Seven thousand years.": " No ink. No paper. Just people who cared enough to get it right.",
    "To be fair, this is debated.": " That disagreement is healthy. It's how science checks a big claim.",
    "The trick in songlines": " Your memory loves places far more than it loves lists.",
    "Back to Greece.": " The story comes to us through the Roman writer Cicero, centuries later.",
    "According to Cicero": " The families could finally identify and bury their relatives.",
    "That story became": " The name sounds fancy, but the idea fits in one sentence.",
    "Roman teachers trained speakers": " The teacher Quintilian described this as a standard part of training a speaker.",
    "For centuries, this art": " Historian Frances Yates traced it through the ancient world and the Middle Ages.",
    "The Iliad runs to": " That's more lines than many modern novels have sentences.",
    "Milman Parry noticed": " The repeated phrases gave the singer a moment to think about the next line.",
    "In the nineteen thirties": " They were watching an oral tradition that was still alive.",
    "Lord found the singers": " The plot stayed the same. The exact words could shift a little.",
    "Which raises the obvious": " Not in theory, in an actual lab with actual brain scans.",
    "First, the memory champions.": " They also memorize long strings of numbers, faces and names.",
    "In two thousand three": " Their brains looked normal. Their methods didn't.",
    "Then in two thousand seventeen": " The study compared them with groups that did different training, or none.",
    "Before training, they could recall": " That's a pretty normal score. Most of us would land in the same range.",
    "Four months later": " The other groups did not keep anything close to that boost.",
    "Their brain scans even started": " Practice didn't just add a trick. It rewired the teamwork.",
    "Step one: pick a place": " The better you know it, the stronger your palace.",
    "Step two: choose a route.": " Never jump around. The order is your index.",
    "Step three: turn what you need": " Boring images vanish. Weird, funny or gross ones stay.",
    "Step four: place each picture": " The sillier the scene, the better it sticks.",
    "Each place hands you": " You're not memorizing a list. You're taking a walk.",
    "And you can reuse the same route": " Some people build several palaces for different subjects.",
    "Some researchers think ancient": " Big, permanent, impossible to lose. The perfect hook for memories.",
    "Lynne Kelly argues sites like": " Nobody can prove it yet, so treat it as an idea, not a fact.",
    "So, how did ancient humans": " Every hill, song and story was part of the library.",
    "And modern science agrees": " The ancient trick isn't folklore. It's measurable.",
    "Our ancestors carried whole": " And the same tool is sitting on your shoulders right now.",
}
for start, extra in ADD.items():
    hits = [k for k, t in enumerate(S) if t[0].startswith(start)]
    assert len(hits) == 1, start
    t = list(S[hits[0]])
    t[0] += extra
    S[hits[0]] = tuple(t)

assert 90 <= len(S) <= 121, len(S)
scenes = []
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, src) in enumerate(S):
    hero = i % 2 == 0
    assert ("the main character" in prompt.lower()) == hero, (i + 1, prompt)
    assert (beat == "hook") == (i < 12), i + 1
    assert src or hero, (i + 1, "fact scene needs a source")
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx,
                   "scene_kind": "hero" if hero else "fact", "fact_source": None if hero else src,
                   "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})

data = {
    "title": "How Did Ancient Humans Remember EVERYTHING Without Writing?",
    "title_alternatives": ["The Ancient MEMORY Trick That Doubles Your Recall", "How Ancient People Stored KNOWLEDGE Without Books",
                           "Why Your Brain Is Better Than You THINK", "The 7,000 Year Old STORIES Nobody Wrote Down"],
    "description": ("For almost all of human history there was no writing, yet people carried maps, laws, stories and survival "
                    "knowledge in their heads. This video follows how: Aboriginal songlines, the Greek poet Simonides, oral epics, "
                    "and what modern brain science says about the memory trick they shared. Then you build your own memory palace "
                    "in under a minute.\n\nSources:\n"
                    "- Dresler et al. (2017). Mnemonic training reshapes brain networks to support superior memory. Neuron.\n"
                    "- Maguire et al. (2003). Routes to remembering: the brains behind superior memory. Nature Neuroscience.\n"
                    "- Nunn & Reid (2016). Aboriginal memories of inundation of the Australian coast. Australian Geographer.\n"
                    "- Sparrow, Liu & Wegner (2011). Google effects on memory. Science.\n"
                    "- Kelly, L. (2016). The Memory Code.\n- Lord, A. (1960). The Singer of Tales.\n- Yates, F. (1966). The Art of Memory.\n"
                    "- Cicero, De Oratore; Quintilian, Institutio Oratoria."),
    "tags": ["ancient humans", "memory palace", "method of loci", "how to remember", "songlines", "ancient history",
             "memory techniques", "oral tradition", "brain science", "animated explainer", "stickman"],
    "mood": "mysterious",
    "sources": [
        "Dresler, M. et al. (2017). Mnemonic training reshapes brain networks to support superior memory. Neuron.",
        "Maguire, E. A. et al. (2003). Routes to remembering: the brains behind superior memory. Nature Neuroscience.",
        "Nunn, P. D. & Reid, N. J. (2016). Aboriginal memories of inundation of the Australian coast dating from more than 7000 years ago. Australian Geographer.",
        "Sparrow, B., Liu, J. & Wegner, D. M. (2011). Google effects on memory. Science.",
        "Kelly, L. (2016). The Memory Code. Allen & Unwin.",
        "Lord, A. B. (1960). The Singer of Tales. Harvard University Press.",
        "Yates, F. A. (1966). The Art of Memory. Routledge.",
        "Hublin, J.-J. et al. (2017). New fossils from Jebel Irhoud, Morocco. Nature.",
        "Murre, J. M. J. & Dros, J. (2015). Replication and analysis of Ebbinghaus' forgetting curve. PLOS ONE.",
    ],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]))
