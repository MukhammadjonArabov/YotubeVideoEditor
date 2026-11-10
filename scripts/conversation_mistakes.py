"""Builds scripts/conversation_mistakes.json and scripts/conversation_mistakes.factcheck.md
(run: ./venv/Scripts/python scripts/conversation_mistakes.py).
Five everyday conversation mistakes we don't notice: the liking gap, turning the talk to ourselves, the curse of
knowledge, planning instead of listening, not asking (deep) questions, ending at the wrong time.
~10 minutes, a new anime picture every ~4 s (import with --minutes 10 --seconds-per-image 4).
Concept approved by the owner 2026-11-10. Modern hero, English. No ancient humans, no human-from-apes content,
no therapy or medical advice."""
import json
from pathlib import Path

BOO = "Boothby, Cooney, Sandstrom & Clark (2018). The liking gap in conversations: do people like us more than we think? Psychological Science 29, 1742-1756"
TAM = "Tamir & Mitchell (2012). Disclosing information about the self is intrinsically rewarding. PNAS 109, 8038-8043"
DER = "Derber, C. (1979; 2000). The Pursuit of Attention: Power and Ego in Everyday Life. Oxford University Press"
NEW = "Newton, E. (1990). Stanford PhD dissertation (song-tapping study); described in Heath & Heath (2007), Made to Stick"
STI = "Stivers et al. (2009). Universals and cultural variation in turn-taking in conversation. PNAS 106, 10587-10592"
HUA = "Huang, Yeomans, Brooks, Minson & Gino (2017). It doesn't hurt to ask: question-asking increases liking. JPSP 113, 430-452"
KAR = "Kardas, Kumar & Epley (2022). Overly shallow? Miscalibrated expectations create a barrier to deeper conversation. JPSP 122, 367-398"
MAS = "Mastroianni, Gilbert, Cooney & Wilson (2021). Do conversations end when people want them to? PNAS 118, e2011809118"

VERIFY = {
    BOO: ("Searched 2026-11-10; paper PDF (Wharton copy), Yale News, ScienceDaily: strangers in the lab, first-year dorm mates and the general public "
          "underestimated how much partners liked them; observers watching recordings judged liking accurately; Clark: people are wrapped up in their own worries.",
          "'Probably', 'in these studies', no exact percentage given."),
    TAM: ("Searched 2026-11-10; PMC3361411: paper opens with 'people devote 30-40% of their speech' to their own experiences; self-disclosure activated "
          "mesolimbic dopamine regions; people gave up some money to talk about themselves.",
          "'About a third', 'reward areas', no claim about exact payment amounts (sources differ)."),
    DER: ("Known sociology book; the 'shift response' vs 'support response' terms come from it; widely summarised (e.g. Celeste Headlee, We Need to Talk).",
          "Introduced as 'one sociologist called it', not as a measured study."),
    NEW: ("Searched 2026-11-10; Wikipedia 'Curse of knowledge' and several summaries agree: 120 songs tapped, listeners named 3 (2.5%), tappers predicted about half.",
          "'About half', 'three out of a hundred and twenty'."),
    STI: ("Searched 2026-11-10; PubMed 19553212 abstract: 10 languages, all avoid overlap and keep silences between turns short; averages differ within about 250 ms. "
          "The exact '200 ms' is a secondary summary, so it is not said.",
          "'A fraction of a second', 'researchers think we start planning our reply while the other person is still talking'."),
    HUA: ("Searched 2026-11-10; paper PDF (gwern) and APS summary: more questions, especially follow-up questions, raised liking; speed daters who asked more got more "
          "second-date yeses; people did not predict this; too many or rude questions can backfire; observers of transcripts did not show the effect.",
          "'Follow-up questions', 'in speed-dating data', the caveat about too many questions is said."),
    KAR: ("Searched 2026-11-10; EurekAlert release, Chicago Booth Review: a dozen experiments with over a thousand people; deep talks with strangers were less awkward "
          "and more connecting than predicted; people underestimated others' interest in deep talk.",
          "'Less awkward than people expected', 'with strangers', brief lab conversations noted."),
    MAS: ("Searched 2026-11-10; Mastroianni's research page and press release: 932 conversations; conversations almost never ended when both wanted and rarely when even one did; "
          "the gap between wished and actual length was about half the conversation; people could not tell when partners wanted to stop. '2%' is press wording only.",
          "'Almost never', 'about half', no '2%'."),
}

S = []  # (narration, prompt, beat, emotion, intensity, pace, pause, sfx, source, on_screen)


def P(hero, hero_prompt, fact, fact_prompt, src, he=None, fe=None, beat="build", hpace="normal", fpace="normal",
      hpause=0, fpause=0, hsfx=None, fsfx=None, text=None):
    S.append((hero, hero_prompt, beat, he, 2, hpace, hpause, hsfx, None, None))
    S.append((fact, fact_prompt, beat, fe, 2, fpace, fpause, fsfx, src, text))


def H(narr, prompt, emo=None, pace="normal", pause=0, sfx=None):
    S.append((narr, prompt, "normal", emo, 2, pace, pause, sfx, None, None))


# ================= hook (12 short lines)
P("You walk home sure you sounded boring.",
  "The main character walks home alone at night under street lamps, replaying a conversation, frowning, light rain.",
  "Science says you're probably wrong.",
  "Two strangers laughing together at a cafe table, warm evening light through the window.",
  BOO, "tense", "curious", "hook", fsfx="impact")
P("You replay every awkward word until midnight.",
  "The main character lies awake in bed at midnight staring at the ceiling, phone glowing beside him.",
  "But people liked us more than we guessed.",
  "A friendly group chatting in a park at sunset, smiling warmly at each other.",
  BOO, "curious", "awe", "hook")
P("Because tiny talking mistakes quietly cost friends, dates, even jobs.",
  "The main character sits across from a bored-looking date at a restaurant, talking too much, candle between them.",
  "And almost everyone makes them without noticing.",
  "A busy office kitchen where coworkers chat over coffee, one person looking away politely.",
  TAM, "serious", "serious", "hook")
P("By the end, you'll know five common conversation mistakes.",
  "The main character holds up five fingers in his apartment, eyebrows raised, morning light.",
  "And a simple, tested fix for each one.",
  "Five small keys lying in a row on a wooden table, soft light.",
  HUA, "excited", "curious", "hook")
P("Plus one kind of question that makes people like you.",
  "The main character leans in and whispers behind his hand, eyes wide, in a dim cafe.",
  "Most people never think to ask it.",
  "A closed door with warm light glowing through the keyhole in a dark hallway.",
  HUA, "whisper", "tense", "hook", hsfx="riser")
P("First, what happens after you say goodbye?",
  "The main character waves goodbye to a new friend outside a coffee shop, then looks unsure.",
  "Researchers asked strangers exactly that.",
  "A small research room with two chairs facing each other and a camera on a tripod.",
  BOO, "curious", "neutral", "hook")

# ================= 1. the liking gap
P("You know that replay after a party?",
  "The main character sits on his sofa after a party, hugging a cushion, thinking hard.",
  "Psychologists named it. They call it the liking gap.",
  "Two silhouettes facing each other with a soft glowing gap between them, night sky.",
  BOO, "funny", "curious")
P("Did I talk too much? Was that joke weird?",
  "The main character cringes in front of a bathroom mirror, hand on his forehead.",
  "In one study, strangers chatted, then rated each other.",
  "Pairs of young adults talking in a bright university room, clipboards on a table.",
  BOO, "funny", "neutral")
P("Then each person guessed what the other thought of them.",
  "The main character squints at an imaginary score card, unsure.",
  "Again and again, people underestimated how much they were liked.",
  "A row of empty chairs after a meeting, coffee cups left behind, warm light.",
  BOO, "curious", "awe", fpause=500)
P("Here's the strange part.",
  "The main character raises one finger, intrigued, at his desk.",
  "People watching the recordings could see the liking clearly.",
  "A small screen in a dark room playing a video of two people smiling and talking.",
  BOO, "curious", "neutral")
P("So the signals were there. We just missed them.",
  "The main character stares at his phone while a friend waves at him, unnoticed, across the street.",
  "It showed up with strangers, dorm mates and adults of all ages.",
  "A university dorm hallway with doors open and students chatting, afternoon sun.",
  BOO, "serious", "neutral")
P("Why do we miss them?",
  "The main character scratches his head on a busy sidewalk.",
  "One of the researchers said we're too wrapped up in our own worries.",
  "A tangled ball of red yarn on a table under a lamp.",
  BOO, "curious", "serious")
P("We're busy grading ourselves instead of watching them.",
  "The main character holds a tiny judge's scorecard up at himself in a mirror, laughing.",
  "That worry is behind almost every mistake that follows.",
  "A crowded cafe where people sit in their own thoughts, rain on the window.",
  BOO, "funny", "neutral")
P("Think about the last time you met someone new.",
  "The main character shakes hands with a new coworker on his first day, nervous smile.",
  "You probably remember your clumsy moments in high detail.",
  "A pile of old instant photos on a desk, one slightly blurry on top.",
  BOO, "neutral", "funny")
P("They probably don't remember them at all.",
  "The main character's coworker walks away humming happily, not thinking about him.",
  "They were too busy worrying about their own clumsy moments.",
  "Two people walking away from a meeting, each lost in their own thoughts, light rain.",
  BOO, "funny", "funny")
P("Honestly? This one changed how I feel after parties.",
  "The main character smiles and relaxes on a balcony at night, city lights below.",
  "The other person probably enjoyed it more than you think.",
  "Two friends walking away from each other after a hug, both smiling, autumn street.",
  BOO, "happy", "happy")

# ================= 2. mistake 1: making it about you
P("Mistake one sounds friendly. It isn't.",
  "The main character sits with a friend at lunch, mouth open, about to interrupt.",
  "People spend about a third of their talk on themselves.",
  "A pie made of three slices on a white plate, one slice glowing gold.",
  TAM, "tense", "neutral", text="30-40%")
P("And it isn't just ego.",
  "The main character shrugs with an innocent grin, holding a coffee cup.",
  "In brain scans, talking about yourself lit up reward areas.",
  "A glowing brain scan image on a lab monitor in a dark room, warm colours in the center.",
  TAM, "funny", "awe")
P("The same kind of areas that react to food or money.",
  "The main character smiles dreamily at a plate of pizza.",
  "Some volunteers even gave up a little money to talk about themselves.",
  "A few coins left on a desk beside a microphone in a quiet lab.",
  TAM, "funny", "curious")
P("So here's how it sneaks in.",
  "The main character listens to a friend who looks tired after a long day at work.",
  "One sociologist called it the shift response.",
  "A railway switch turning a train onto a different track, evening light.",
  DER, "neutral", "serious")
P("Your friend says, I'm so tired this week.",
  "The main character's friend slumps on a sofa with dark circles under her eyes.",
  "And you say, oh, me too, let me tell you about mine.",
  "A spotlight sliding from one chair to another on an empty stage.",
  DER, "neutral", "funny", fpace="fast")
P("You meant to connect. But you took the spotlight.",
  "The main character realises his mistake, hand over his mouth, wincing.",
  "The other option is the support response.",
  "A strong wooden bridge over a calm river at sunrise.",
  DER, "sad", "neutral")
P("Tired how? What happened?",
  "The main character leans forward, listening with full attention, phone face down.",
  "One small question keeps the spotlight on them.",
  "A single warm spotlight on one armchair in a cosy room.",
  DER, "curious", "happy")
P("I do this all the time, by the way.",
  "The main character laughs at himself, rubbing the back of his neck, in a busy cafe.",
  "The shift response usually comes from wanting to relate, not from being selfish.",
  "Two coffee cups touching on a cafe table, steam rising, soft morning light.",
  DER, "funny", "neutral")
P("But the other person doesn't feel related to. They feel interrupted.",
  "The main character's friend looks down at her cup, quietly giving up her story.",
  "Their story gets cut off, and they rarely finish it later.",
  "A half-finished drawing on a sketchpad left on a park bench, a pencil beside it.",
  DER, "sad", "sad")
P("You'll still get your turn. Just not right away.",
  "The main character holds up a patient hand, smiling.",
  "And their story often gets better when you let it run.",
  "A long winding path through a green valley opening to a beautiful view.",
  DER, "funny", "awe")

# ================= 3. mistake 2: the curse of knowledge
P("Mistake two: you explain, they nod, they're lost.",
  "The main character explains something at a whiteboard while two coworkers nod blankly.",
  "In nineteen ninety, a Stanford student ran a simple test.",
  "A university campus with sandstone arches and palm trees in afternoon sun.",
  NEW, "funny", "neutral")
P("One person tapped a famous song on a table.",
  "The main character taps on a table with one finger, humming happily inside his head.",
  "The other person had to guess the song.",
  "A puzzled listener at a table, one hand on chin, a glass of water nearby.",
  NEW, "happy", "curious")
P("The tappers expected about half to be guessed.",
  "The main character grins confidently, sure everyone will get it.",
  "Listeners named three songs out of a hundred and twenty.",
  "A big jar of a hundred and twenty marbles with only three bright red ones on top.",
  NEW, "excited", "awe", fpause=600, text="2.5%")
P("The tapper hears the whole melody in their head.",
  "The main character taps with his eyes closed, music notes floating around his head.",
  "The listener hears knock, knock, knock.",
  "A plain wooden table with a single knuckle tapping it in an empty room.",
  NEW, "awe", "funny", fpace="fast")
P("That's the curse of knowledge.",
  "The main character looks surprised at his own hands, as if cursed.",
  "Once you know something, it's hard to imagine not knowing it.",
  "An open book glowing in the dark, light only reaching the first page.",
  NEW, "tense", "serious")
P("It's why directions like 'turn by the old bakery' fail.",
  "The main character gives directions pointing confidently while a tourist looks lost.",
  "The bakery closed years ago. Only you remember it.",
  "An empty shop with covered windows on a quiet street corner.",
  NEW, "funny", "funny")
P("The fix? Give one concrete example.",
  "The main character draws a simple picture on a napkin for a friend in a cafe.",
  "And ask, which part should I explain better?",
  "A notebook with a simple drawing and a question mark shape made of pencils.",
  NEW, "neutral", "curious")
P("Not 'did you understand?' Everyone says yes to that.",
  "The main character laughs as a whole room of people nod automatically.",
  "Nobody wants to look slow in front of others.",
  "A meeting room where people nod politely, one person hiding a confused face behind a cup.",
  NEW, "funny", "neutral")

# ================= 4. mistake 3: planning instead of listening
P("Mistake three happens inside your head.",
  "The main character nods at a friend while gears spin above his head.",
  "Researchers recorded conversations in ten languages around the world.",
  "A world map on a desk with small glowing dots on different continents.",
  STI, "curious", "neutral")
P("From big cities to small villages.",
  "The main character video-calls friends in different countries on his laptop.",
  "Everywhere, people avoided talking over each other.",
  "Villagers chatting in a sunny courtyard while a city cafe chats under rain, side by side.",
  STI, "neutral", "awe")
P("And the silence between turns was usually tiny.",
  "The main character snaps his fingers, surprised.",
  "Often just a fraction of a second.",
  "A stopwatch frozen at a tiny moment, glowing softly on a dark table.",
  STI, "excited", "awe", text="0.2 SEC")
P("That's faster than you could plan a sentence from scratch.",
  "The main character stares at a stopwatch, confused.",
  "So researchers think we often plan our reply while the other person is still talking.",
  "Two speech balloons drawn as overlapping clouds above two coffee cups, no words.",
  STI, "curious", "serious")
P("That's normal. But it has a cost.",
  "The main character nods but his eyes drift away, thinking of his own reply.",
  "The more we rehearse, the less we hear.",
  "A pair of headphones lying unplugged on a table, the cable loose.",
  STI, "tense", "serious")
P("Ever answered a question nobody actually asked?",
  "The main character confidently answers while his friend looks puzzled at a bus stop.",
  "It happens when we answer the words we expected, not the words we heard.",
  "A key that doesn't fit, stuck halfway into the wrong lock.",
  STI, "funny", "neutral")
P("Try this. Let them finish. Then take one breath.",
  "The main character pauses with a calm breath, listening, at a kitchen table.",
  "Then say back what you heard, in a few words.",
  "Two cups on a table and a small echo of ripples moving between them.",
  STI, "neutral", "happy")
P("It feels slow. To them, it feels like respect.",
  "The main character's friend smiles, surprised and grateful.",
  "Being understood is something people remember.",
  "A handshake between two people in warm evening light on a rooftop.",
  BOO, "happy", "awe")
P("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring how people really work, together, one question at a time. It's free, it takes one second, and it helps more curious people find us.",
  "The main character smiles warmly at the viewer, waving him closer, in his cosy lamp-lit apartment.",
  "Now, the question that makes people like you.",
  "A warm doorway opening onto a lively cafe full of friendly faces.",
  HUA, "happy", "curious", hpause=300)

# ================= 5. mistake 4: not asking (the right) questions
P("Mistake four: you don't ask enough.",
  "The main character talks on and on at a dinner while his friend quietly eats.",
  "Harvard researchers studied thousands of chats, including speed dates.",
  "A room of small tables with pairs chatting during a speed-dating event, a bell on the counter.",
  HUA, "serious", "neutral")
P("People who asked more questions were liked more.",
  "The main character raises his eyebrows, impressed.",
  "Speed daters who asked more got more yeses for a second date.",
  "A small table with two coffee cups and a heart-shaped sugar cube, evening light.",
  HUA, "awe", "happy")
P("But not just any question.",
  "The main character wags a finger playfully.",
  "The strongest effect came from follow-up questions.",
  "A path of stepping stones crossing a calm stream, each one leading further.",
  HUA, "funny", "awe", fpause=500)
P("There it is. The open loop from the start.",
  "The main character points at the viewer with a big grin.",
  "A follow-up builds on what the person just said.",
  "A small stack of building blocks, each new block resting on the last one.",
  HUA, "excited", "neutral")
P("They say, I just got back from Italy.",
  "The main character's friend shows holiday photos on a phone at a cafe.",
  "A switch is, cool, where else have you been?",
  "A train switching tracks away from a sunny station.",
  HUA, "happy", "funny", fpace="fast")
P("A follow-up is, what surprised you most there?",
  "The main character leans in, curious, as his friend lights up and starts telling a story.",
  "It tells them you were actually listening.",
  "A seashell held up to an ear on a quiet beach at sunset.",
  HUA, "curious", "serious")
P("Follow-ups say, I heard you, tell me more.",
  "The main character nods slowly, giving his friend his full attention on a park bench.",
  "Researchers think that feeling of being heard is the real reason it works.",
  "An open window letting warm sunlight into a quiet room with two chairs.",
  HUA, "neutral", "awe")
P("And they're easy. You don't need clever questions.",
  "The main character shrugs with a relaxed smile, hands open.",
  "Just pick one detail they said and ask about it.",
  "A magnifying glass resting on an open notebook beside a cup of tea.",
  HUA, "happy", "neutral")
P("Weirdly, people don't expect this to work.",
  "The main character shrugs, surprised.",
  "In the studies, people didn't predict that questions would make them more liked.",
  "An unopened gift box on a doorstep in soft morning light.",
  HUA, "funny", "neutral")
P("Careful, though. A question storm isn't a conversation.",
  "The main character fires questions like a game-show host while his friend sweats nervously.",
  "Too many, or rude ones, can backfire.",
  "A tiny umbrella under a heavy rain of falling question-shaped raindrops, grey sky.",
  HUA, "funny", "serious")
P("And don't be afraid to go a little deeper.",
  "The main character sits by a lake at dusk with a friend, both thoughtful.",
  "In over a dozen experiments, strangers were given deep questions.",
  "Cards with simple symbols spread on a table between two chairs, no letters.",
  KAR, "serious", "neutral")
P("What are you grateful for? When did you last cry?",
  "The main character looks a little nervous asking a big question.",
  "People expected those talks to be awkward.",
  "Two strangers sitting stiffly on a park bench at first, afternoon light.",
  KAR, "tense", "neutral")
P("They weren't. Not nearly as much as they feared.",
  "The main character relaxes and laughs with the stranger on the bench.",
  "Deep talks felt more connecting than people predicted.",
  "Two people deep in a warm conversation by a fire pit at night, sparks rising.",
  KAR, "happy", "awe")
P("We think others only want small talk.",
  "The main character rolls his eyes while talking about the weather, rain outside.",
  "Most underestimated how much the other person cared to go deeper.",
  "A small boat floating over a lake so clear you can see the deep bottom.",
  KAR, "funny", "awe")
P("So skip one weather question. Ask a real one.",
  "The main character asks a coworker a thoughtful question at a coffee machine, both smiling.",
  "These were short lab talks, but the pattern kept showing up.",
  "A tidy lab room with two empty chairs and a timer on a table.",
  KAR, "excited", "neutral")

# ================= 6. mistake 5: the ending
P("Mistake five is about the ending.",
  "The main character stands at a door, half in and half out, awkwardly smiling.",
  "Researchers studied over nine hundred conversations.",
  "A wall of small photos showing many pairs of people talking in different places.",
  MAS, "curious", "neutral", text="932")
P("Each person said when they'd secretly wanted to stop.",
  "The main character glances at his watch during a long chat, trying to be polite.",
  "Conversations almost never ended when both people wanted.",
  "An hourglass on a cafe table with sand still running, two chairs pulled back.",
  MAS, "funny", "awe", fpause=600)
P("Sometimes one person wanted to leave early.",
  "The main character inches toward the exit while his friend keeps talking happily.",
  "And sometimes one wished it had gone on longer.",
  "A train pulling away from a platform while someone waves, golden evening.",
  MAS, "funny", "sad")
P("On average, the gap was about half the conversation.",
  "The main character holds his hands apart, measuring, amazed.",
  "And people were bad at guessing what the other one wanted.",
  "Two people walking in opposite directions on a foggy bridge at dusk.",
  MAS, "awe", "serious")
P("We're all being polite. Both of us. Silently.",
  "The main character and a friend both smile stiffly at each other, both checking the time.",
  "Most of these chats were between people who'd known each other for years.",
  "Old friends at a kitchen table with tea and an old photo album, soft lamp.",
  MAS, "funny", "neutral")
P("The fix is kind and simple. End it on a high.",
  "The main character laughs with a friend, then stands up, still smiling.",
  "Leaving while it's good is not rude.",
  "A sunset over the sea at its brightest moment, warm orange sky.",
  MAS, "happy", "neutral")
P("Say, I loved this, let's do it again soon.",
  "The main character hugs his friend goodbye at a station, both smiling.",
  "People who wanted more still enjoyed it just as much.",
  "Two coffee cups left with a little coffee still inside, sunlight on the table.",
  MAS, "happy", "happy")
P("Waiting for the other person to end it rarely works.",
  "The main character and his friend stand at a door, both waiting for the other to say goodbye, laughing awkwardly.",
  "The researchers found people couldn't read when their partner wanted to stop.",
  "Two people at a crossroads at dusk, each glancing at the other, street lamps flickering on.",
  MAS, "funny", "serious")
P("So someone has to be brave and kind about it.",
  "The main character gently taps his friend's shoulder and smiles, ready to leave.",
  "A warm, clear goodbye is better than a slow fade.",
  "A sunset fading over a calm lake, the last light on the water.",
  MAS, "happy", "awe")
P("And the next chat starts warmer.",
  "The main character receives a smiling message notification on his phone at home.",
  "A good ending makes people want to come back.",
  "A front door with a welcome mat, light glowing inside, autumn leaves on the steps.",
  MAS, "awe", "neutral")

# ================= 7. the fixes, together
P("So let's put it together.",
  "The main character sits at a desk with a fresh notebook under a warm lamp at night.",
  "One. People probably like you more than you think.",
  "Two friends laughing on a city rooftop at sunset.",
  BOO, "neutral", "happy")
P("Stop grading yourself. Watch them instead.",
  "The main character puts down an imaginary scorecard and looks up, relaxed.",
  "Two. When they share, stay on their story.",
  "A single warm spotlight on one armchair in a quiet room.",
  BOO, "neutral", "serious")
P("Ask, what happened next?",
  "The main character nods along as a friend talks excitedly.",
  "Three. Give an example, and ask what to explain better.",
  "A napkin drawing on a cafe table with a pencil beside it.",
  NEW, "curious", "neutral")
P("Four. Finish listening before you plan.",
  "The main character takes a calm breath while his friend talks at a bus stop, rain falling.",
  "One breath. Then say back what you heard.",
  "Ripples spreading slowly across a calm pond at dawn.",
  STI, "neutral", "awe")
P("Five. Ask one follow-up. Maybe a deep one.",
  "The main character leans in with real curiosity across a dinner table.",
  "Follow-ups were the strongest link to liking in the study.",
  "Stepping stones crossing a stream into a sunny meadow.",
  HUA, "excited", "neutral")
P("And end while it's still good.",
  "The main character waves goodbye with a big smile outside a cafe at dusk.",
  "Almost no conversation ends at the perfect moment anyway.",
  "An hourglass with the last grains of sand falling, warm light.",
  MAS, "happy", "neutral")
P("You don't need to be charming. Just curious.",
  "The main character smiles at the viewer, hands in his pockets, sunny street.",
  "Curiosity looks the same in every language.",
  "People in different countries chatting in markets and cafes, bright morning light.",
  STI, "awe", "awe", hpause=500)
P("Here's my honest take. Nobody is perfect at this.",
  "The main character laughs at himself, covering his face after an awkward joke.",
  "Even the people who study conversation still have awkward ones.",
  "A conference hall coffee break where people chat in small clumsy groups.",
  MAS, "funny", "neutral")
P("Try just one thing this week.",
  "The main character writes one small note and sticks it on his fridge.",
  "Small changes in how we listen can change how people feel around us.",
  "A circle of friends around a table, everyone leaning in, warm string lights.",
  HUA, "excited", "happy")
H("Thank you for spending these minutes with me. If this helped, hit like, and tell me in the comments which mistake you catch yourself making. I read every one. Next time, we'll find out why saying no feels so hard. See you there, friend.",
  "The main character waves goodbye from his sunny balcony, a coffee cup in hand and city rooftops behind him.",
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
    "title": "Conversation Mistakes You Don't Know You're MAKING",
    "title_alternatives": ["Why People Stop LISTENING When You Talk", "The Hidden Mistakes That Make Conversations AWKWARD",
                           "People Like You More Than You THINK", "The Question That Makes People LIKE You",
                           "5 Conversation Mistakes Almost EVERYONE Makes"],
    "description": ("You leave a conversation sure you sounded boring. Research says people probably liked you more than you think. "
                    "Five everyday conversation mistakes, what the studies found, and the simple fix for each, including the one kind of question that makes people like you.\n\n"
                    "This video is psychology for education, not professional advice.\n\nSources:\n"
                    "- Boothby et al. (2018). The liking gap in conversations. Psychological Science.\n"
                    "- Tamir & Mitchell (2012). Disclosing information about the self is intrinsically rewarding. PNAS.\n"
                    "- Derber (1979/2000). The Pursuit of Attention.\n"
                    "- Newton (1990). Song-tapping study, Stanford; Heath & Heath, Made to Stick.\n"
                    "- Stivers et al. (2009). Universals and cultural variation in turn-taking in conversation. PNAS.\n"
                    "- Huang et al. (2017). It doesn't hurt to ask: question-asking increases liking. JPSP.\n"
                    "- Kardas, Kumar & Epley (2022). Overly shallow? JPSP.\n"
                    "- Mastroianni et al. (2021). Do conversations end when people want them to? PNAS."),
    "tags": ["conversation mistakes", "how to talk to people", "conversation skills", "social skills", "liking gap",
             "follow-up questions", "how to be a better listener", "curse of knowledge", "psychology of conversation",
             "communication skills", "how to be more likable", "animated explainer"],
    "mood": "wholesome",
    "sources": list(dict.fromkeys(s[8] for s in S if s[8])),
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Conversation Mistakes You Don't Know You're MAKING", "",
      "Every fact scene, its source, how it was checked and how the wording was kept honest. Checked 2026-11-10.", "",
      "## Method",
      "- Every study was found online and its abstract, record or a reliable summary opened; limits are said out loud.",
      "- No therapy or professional advice: everyday conversation habits only.", "",
      "## Sources and checks", ""]
for src, (how, safe) in VERIFY.items():
    md += [f"### {src}", f"- How verified: {how}", f"- Wording safeguard: {safe}", ""]
md += ["## Fact scenes", "", "| # | Narration | Source |", "|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        md.append(f"| {i} | {sc['narration'].replace('|', '/')} | {sc['fact_source'][:60]} |")
md += ["", "## Claims softened or dropped",
       "- '2% of conversations end when both want': press wording, not in the paper; 'almost never' used.",
       "- '200 ms between turns': secondary summary; narration says 'a fraction of a second' (the on-screen 0.2 SEC is a rough picture of that).",
       "- 'Planning the reply while listening': researchers' interpretation, said as 'researchers think'.",
       "- Tamir & Mitchell: payment amounts differ across sources, so only 'a little money' is said; '80% online' interview claim dropped.",
       "- Newton (1990): dissertation not opened directly; figures agree across multiple summaries; Stanford setting kept, 'student' used.",
       "- Huang (2017): observers of transcripts did not show the effect; 'too many or rude questions can backfire' is said.",
       "- Kardas (2022): brief lab talks with strangers; this limit is said in the narration.",
       "- Derber: 'shift/support response' is a sociologist's concept, not a measured result; said as 'one sociologist called it'."]
Path(__file__).with_name("conversation_mistakes.factcheck.md").write_text("\n".join(md), encoding="utf-8")
words = sum(len(s["narration"].split()) for s in scenes)
print(len(scenes), "scenes,", words, "words, hook words:", sum(len(s["narration"].split()) for s in scenes[:hook_n]),
      "subscribe at:", [i + 1 for i, s in enumerate(scenes) if "subscribe" in s["narration"].lower()])
