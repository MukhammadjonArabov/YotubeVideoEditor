"""Builds scripts/who_cared_injured.json (run: ./venv/Scripts/python scripts/who_cared_injured.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Odd scenes hero, even fact."""
import json
from pathlib import Path

SHA = "Trinkaus & Villotte (2017). External auditory exostoses and hearing loss in the Shanidar 1 Neandertal. PLoS ONE"
DMA = "Lordkipanidze et al. (2005). The earliest toothless hominin skull. Nature 434"
SIM = "Gracia et al. (2009). Craniosynostosis in the Middle Pleistocene human Cranium 14 from the Sima de los Huesos. PNAS"
SID = "Weyrich et al. (2017). Neanderthal behaviour, diet, and disease inferred from ancient DNA in dental calculus. Nature"
ASP = "History of aspirin: willow bark used as a remedy in ancient Egypt and Greece; acetylsalicylic acid marketed by Bayer in 1897"
MEA = "The 'healed femur' story is widely credited to Margaret Mead; its original source is disputed"
BER = "Berger & Trinkaus (1995). Patterns of trauma among the Neandertals. Journal of Archaeological Science"
TRI = "Trinkaus, E. (2018). An abundance of developmental anomalies and abnormalities in Pleistocene people. PNAS"

S = [
    # ---------------- hook (12 one-line scenes)
    ("This Neanderthal couldn't hear, and half his arm was gone.", "The main character crouches beside a stick-figure Neanderthal sitting alone by a cave wall, looking worried.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("He still lived into his forties, fifty thousand years ago.", "A skeleton resting peacefully in a quiet cave with a small stone beside it, soft light from the entrance.", "hook", "awe", 3, "slow", 300, None, SHA),
    ("Alone, that's impossible. So who kept him alive?", "The main character looks around an empty cave, scratching his head, puzzled.", "hook", "curious", 2, "normal", 0, None, None),
    ("The bones hold a secret about being human.", "Several ancient bones laid out carefully on a cloth, one with a visible healed break.", "hook", "whisper", 2, "slow", 0, None, SHA),
    ("It changes how you'll see every person you meet.", "The main character stands on a hilltop looking at a village of small huts below, thoughtfully.", "hook", "serious", 2, "normal", 0, None, None),
    ("Researchers found care in skeletons older than a million years.", "An ancient jaw bone with almost no teeth sitting on a stone, lit by a single beam of sunlight.", "hook", "awe", 2, "normal", 0, None, DMA),
    ("In a few minutes, you'll meet four of these survivors.", "The main character holds up four fingers proudly with a big friendly smile.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("One of them even ate a natural painkiller.", "A small tooth with a tiny green leaf and a drop of water beside it, on a stone.", "hook", "excited", 2, "normal", 0, None, SID),
    ("And you can spot that same instinct in yourself.", "The main character gently hands a bowl of food to a tired friend by the fire.", "hook", "happy", 2, "normal", 0, None, None),
    ("But first, meet the man from Shanidar Cave.", "A wide dry mountain cave entrance in a rocky Kurdish valley at dawn.", "hook", "curious", 2, "normal", 0, None, SHA),
    ("Nobody expected what the diggers found inside.", "The main character carefully brushes dirt from a skull half buried in a cave floor.", "hook", "tense", 2, "slow", 0, None, None),
    ("It took scientists decades to read his story.", "A long wooden table covered with ancient bones and measuring tools in a quiet museum room.", "hook", "serious", 3, "slow", 500, None, SHA),
    # ---------------- Shanidar 1
    ("Shanidar Cave sits in the mountains of Iraqi Kurdistan, and in nineteen fifty-seven, diggers found a Neanderthal skeleton there.", "The main character walks up a steep rocky path toward a large cave, carrying a small shovel.", "build", "curious", 2, "normal", 0, None, SHA),
    ("Scientists later labelled him Shanidar One. He lived roughly fifty thousand years ago, and his bones tell a rough story.", "A Neanderthal skeleton laid out on a cloth with small numbered stones beside each bone, no letters.", "build", "neutral", 2, "normal", 0, None, SHA),
    ("Let's go through his injuries, one by one. Buckle up, it's a long list.", "The main character clutches a very long wooden list that unrolls all the way to the floor.", "build", "funny", 2, "fast", 0, "boing", None),
    ("His right forearm was missing, the arm bones were withered, and the hand was likely useless.", "A skeleton arm ending at the elbow, the rest of the arm drawn as a faint outline, in soft light.", "build", "serious", 2, "normal", 0, None, SHA),
    ("Imagine losing the use of an arm and still trying to carry water, chop wood, or gather food.", "The main character struggles to carry a heavy bundle of sticks with one arm tucked behind him.", "build", "tense", 2, "normal", 0, None, None),
    ("His leg bones show old damage and a degenerative condition, which probably meant a limp.", "A leg bone with a bumpy healed section drawn next to a small wooden walking stick.", "build", "neutral", 2, "normal", 0, None, SHA),
    ("He had a blow to the face at some point. And here's the bit that surprised researchers.", "The main character winces and rubs his own cheek, eyes closed in sympathy.", "build", "tense", 2, "normal", 0, None, None),
    ("Bony growths blocked his ear canals, which would have left him with serious hearing loss.", "A skull seen from the side with a small round blockage drawn inside the ear opening.", "punchline", "awe", 3, "slow", 500, "ding", SHA),
    ("A deaf hunter who can't hear a lion in the grass. That is not a recipe for old age.", "The main character cups his ear while a big stick-figure lion tiptoes up behind him, comically.", "build", "funny", 3, "normal", 0, None, None),
    ("And yet he reached his forties, which was a long life in the Pleistocene.", "A tall stack of tiny candles, one for each year, glowing in a dark cave.", "build", "awe", 2, "normal", 0, None, SHA),
    ("So who fed him? Who kept watch while he slept? Let's follow the clues.", "The main character peers into a dark cave with one hand shading his eyes, searching for the helpers.", "build", "curious", 2, "normal", 0, None, None),
    ("Researchers who studied his bones argued he almost certainly survived with the help of his group.", "A small group of stick-figure Neanderthals sharing food around a fire with one sitting among them.", "build", "serious", 2, "normal", 0, None, SHA),
    ("Not for a week or two. For years, with injuries that never fully healed.", "The main character counts on his fingers, running out of fingers, looking amazed.", "build", "curious", 2, "normal", 0, None, None),
    ("Somebody shared meat with a man who could not hunt, and kept watch for a man who could not hear.", "A cave at night with a figure resting while another sits awake at the entrance, holding a torch.", "build", "awe", 3, "slow", 300, None, SHA),
    ("That's the heart of it. To a Neanderthal band, one extra mouth was a heavy cost. They paid it anyway.", "The main character lifts one very heavy basket of food, groaning, then smiles and sets it down gently.", "punchline", "serious", 2, "slow", 0, None, None),
    ("And he wasn't a one-off. Researchers have found healed injuries in many Neanderthal skeletons, a sign that people often lived through their wounds.", "Several Neanderthal skulls and rib bones lined up on a stone shelf, each with a small healed mark.", "build", "neutral", 2, "normal", 0, None, BER),
    # ---------------- Dmanisi
    ("Now let's go back much further, almost two million years, to Georgia in the Caucasus.", "The main character spins a large wooden globe and points at a faraway mountain region, grinning.", "build", "excited", 2, "normal", 0, "swoosh", None),
    ("At a site called Dmanisi, researchers found a skull and jaw from a hominin about one point seven seven million years old.", "A hilltop dig site above a green river valley with small tents and wooden ladders, bright morning.", "build", "neutral", 2, "normal", 0, None, DMA),
    ("Here's what stopped them in their tracks. He had lost nearly all of his teeth years before he died.", "The main character stares at a jaw bone with just a single tooth left, mouth wide open in surprise.", "build", "awe", 3, "normal", 0, None, DMA),
    ("The bone where the teeth used to be had shrunk away, which takes time. It means he lived for years that way.", "A close drawing of a jaw bone with smooth rounded gaps where teeth had once been, in soft light.", "build", "neutral", 2, "normal", 0, None, DMA),
    ("So how do you eat tough meat and raw roots when you can't chew anything?", "The main character tries to bite a huge rock-hard piece of dried meat and bounces off it comically.", "build", "funny", 2, "fast", 0, None, None),
    ("The authors suggested someone may have helped by preparing soft food, though that's an inference, not proof.", "A stone slab with a mashed-up soft food and a small wooden spoon next to a campfire.", "build", "serious", 2, "normal", 0, None, DMA),
    ("Another explanation is that he found softer foods himself, like marrow from cracked bones. Science likes keeping its options open.", "The main character cracks a large bone with a rock and scoops out something soft, delighted.", "build", "curious", 2, "normal", 0, None, DMA),
    ("Either way, he survived without teeth in a world with no dentists, and no soup. Respect.", "A cartoonish giant bowl of soup steaming beside a cave fire, comically too modern.", "build", "funny", 2, "normal", 0, "pop", DMA),
    # ---------------- Sima de los Huesos
    ("Next stop: Spain, a cave called Sima de los Huesos, the Pit of Bones, about four hundred thirty thousand years old.", "The main character peers over the edge of a deep dark pit in the ground, holding a torch.", "build", "curious", 2, "normal", 0, None, SIM),
    ("Among hundreds of bones, researchers found a child's skull known as Cranium fourteen.", "A small child-sized skull resting alone on a soft cloth in a pool of warm light.", "build", "awe", 2, "slow", 0, None, SIM),
    ("The child had a condition where the skull bones fuse too early, which can cause pain, problems with development, and more.", "The main character looks sadly at a small skull drawn with a visible fused seam across the top.", "build", "sad", 2, "slow", 0, None, SIM),
    ("The researchers estimated the child lived for several years, probably between five and ten.", "A row of small seashells arranged in a line, five or six of them, on a stone shelf.", "build", "neutral", 2, "normal", 0, None, SIM),
    ("A sick, struggling child survived, and the simplest explanation is that adults kept bothering to help.", "The main character sits by a fire holding a tiny blanket, humming gently to someone off-screen.", "build", "serious", 2, "slow", 0, None, None),
    ("Parents have always been parents. That instinct is old, much older than our species.", "A big warm campfire with several small stick-figure sleeping shapes tucked together near it.", "build", "awe", 2, "slow", 0, None, SIM),
    # ---------------- subscribe (mid)
    ("Quick pause. If you're enjoying this, tap subscribe, because a new ancient mystery lands every week. It's free, it takes one second, and it tells YouTube that stories like this are worth showing to more curious people.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    # ---------------- El Sidron
    ("El Sidrón is a cave in northern Spain where researchers recovered the remains of about a dozen Neanderthals.", "A narrow cave mouth in a green hillside with ferns around the entrance, early morning mist.", "build", "neutral", 2, "normal", 0, None, SID),
    ("Okay. Back to the survivors. Now the strangest one. One of those Neanderthals had a very painful problem.", "The main character climbs into a narrow dim cave tunnel with a torch, whispering to himself.", "build", "curious", 2, "normal", 0, None, SID),
    ("Researchers studied the tartar on his teeth, the hardened plaque, and read the DNA trapped inside it.", "A single worn tooth shown huge in the center with tiny floating specks around it.", "build", "neutral", 2, "normal", 0, None, SID),
    ("Scientists found he had a painful tooth abscess, and a parasite likely causing stomach trouble.", "The main character holds his swollen cheek with a wince, sitting hunched near a cave wall.", "build", "tense", 2, "normal", 0, None, SID),
    ("Then they found something odd in the plaque: DNA from poplar, a tree whose bark contains salicylic acid.", "A tall poplar tree with silvery leaves swaying on a hillside beside a small stream.", "build", "awe", 2, "normal", 0, None, SID),
    ("Salicylic acid is the natural painkiller behind aspirin, which was developed from compounds in willow bark.", "The main character chews a small strip of tree bark with a thoughtful face.", "build", "curious", 2, "normal", 0, None, ASP),
    ("They also found traces of a mould called Penicillium, the same kind of mould that gave us penicillin.", "A small slice of old bread with green fuzzy patches in the dim light of a cave.", "build", "awe", 3, "normal", 0, None, SID),
    ("Nobody else's plaque in that group showed the mould. Only the man with the abscess had it.", "The main character compares four clean teeth drawn on a stone with one fuzzy green tooth, spotting the difference.", "punchline", "excited", 2, "normal", 400, "ding", SID),
    ("Now, a big warning. The researchers said they can't prove he was treating himself on purpose.", "A raised hand drawn in a stop gesture over a small plant, in soft light.", "build", "serious", 2, "slow", 0, None, SID),
    ("Poplar isn't a regular food. But eating it by accident is an awkward explanation too.", "The main character shrugs with both hands raised, head tilted, standing in a grove of poplar trees.", "build", "funny", 2, "normal", 0, None, SID),
    ("So treat it as a fascinating possibility: a person in pain, reaching for the right plant.", "A path leading to a single plant with golden light shining on it in a quiet forest.", "build", "curious", 2, "slow", 0, None, SID),
    ("Whatever it was, it hints at something we also do. Look around, find something that helps, and share the trick.", "The main character offers a leaf to a friend holding his jaw, both sitting on logs.", "build", "happy", 2, "normal", 0, None, None),
    ("People kept doing it for thousands of years. Ancient Egyptians and Greeks used willow bark for pain, long before anyone made aspirin.", "A willow tree beside a slow river with a few strips of bark laid on a flat stone, golden afternoon light.", "build", "curious", 2, "normal", 0, None, ASP),
    # ---------------- the myth
    ("You may have heard a famous story: the first sign of civilization is a healed thighbone, because it proves someone cared.", "The main character holds up a long femur bone like a trophy in front of a crowd, proudly.", "build", "curious", 2, "normal", 0, None, MEA),
    ("It's often credited to Margaret Mead. But the original source is disputed, so take that attribution with a grain of salt.", "A scholar with round glasses squints at an old notebook with a puzzled expression, pages blank.", "build", "serious", 2, "normal", 0, None, MEA),
    ("The idea behind it still holds up, because bones really do show healing. A healed bone means someone lived long enough for it to mend, and that usually takes weeks.", "The main character rests on a flat bed of leaves with a splinted leg while someone brings water.", "build", "serious", 2, "slow", 0, None, None),
    # ---------------- why it matters
    ("So what does all this add up to? Four different species, up to nearly two million years, one repeating pattern.", "Four skulls of different shapes lined up on a shelf with a long glowing line connecting them.", "punchline", "awe", 2, "slow", 300, None, DMA + "; " + SHA + "; " + SIM),
    ("Our ancestors were not only tough survivors. They were people who stayed with the ones who couldn't keep up.", "The main character walks slowly beside a limping friend, adjusting his pace to match.", "build", "serious", 2, "slow", 0, None, None),
    ("Researchers who study these skeletons have argued that care could be a very old human trait, not a modern invention.", "A big stone circle of ancient people with small arrows pointing inward to the center, in warm light.", "build", "neutral", 2, "normal", 0, None, TRI),
    ("And in a world of danger, caring was practical. A band that looks after its members keeps its knowledge and skills.", "The main character teaches a young stick figure how to light a fire while an older figure sits watching.", "build", "curious", 2, "normal", 0, None, None),
    ("The deaf man from Shanidar probably knew things nobody else did. Where the best berries grew. What every sound in the valley meant.", "An old Neanderthal figure sits on a rock pointing at distant hills while younger ones listen closely.", "build", "awe", 2, "slow", 0, None, SHA),
    ("So when we look after someone, we're not breaking nature's rules. We're following a very old one.", "The main character holds a wooden cup toward someone sitting weak and thin, gently.", "punchline", "serious", 2, "slow", 400, None, None),
    ("Think about the last time someone helped you when you were sick or stuck. Ancient people gave that same help. Researchers have catalogued many Pleistocene individuals with severe conditions who still grew up.", "A row of ancient skeletons of different sizes lying peacefully by a warm fire glow, one with a slightly curved spine.", "build", "happy", 2, "slow", 0, None, TRI),
    ("And maybe it's also about the next time. Because the oldest, most human thing we do is to notice somebody falling behind.", "The main character stops walking and turns back, extending a hand toward a distant figure.", "build", "serious", 2, "slow", 0, None, None),
    # ---------------- end + subscribe
    ("Four survivors, four different eras, and one thread that connects us all.", "Four small candles glowing in a row, each in front of a different ancient skull, in a dark cave.", "punchline", "awe", 2, "slow", 300, None, DMA + "; " + SHA + "; " + SIM + "; " + SID),
    ("If this made you see the past differently, subscribe, hit like, and tell me in the comments who you would have helped. Next time, we find out how ancient humans survived the cold. See you there, and look after each other.", "The main character smiles warmly at the viewer, pointing at a glowing like button, with snowy mountains and a small orange glowing cave behind him.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 60 <= len(S) <= 130, len(S)
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
    "title": "Who Cared for the INJURED 50,000 Years Ago?",
    "title_alternatives": ["Did Neanderthals Take Care of the SICK?", "The Neanderthal Who Should Not Have Survived",
                           "Ancient Humans Who Lived Without TEETH", "What Bones Reveal About Ancient KINDNESS"],
    "description": ("A Neanderthal who couldn't hear and had lost part of an arm lived into his forties. A toothless hominin survived for "
                    "years. A sick child grew up. And one Neanderthal may have chewed a natural painkiller. This video follows the "
                    "skeletons that suggest ancient humans cared for the injured, and what that says about us.\n\nSources:\n"
                    "- Trinkaus & Villotte (2017). Shanidar 1 Neandertal ear exostoses. PLoS ONE.\n"
                    "- Lordkipanidze et al. (2005). The earliest toothless hominin skull. Nature.\n"
                    "- Gracia et al. (2009). Cranium 14, Sima de los Huesos. PNAS.\n"
                    "- Weyrich et al. (2017). Neanderthal dental calculus DNA. Nature.\n- Trinkaus (2018). PNAS."),
    "tags": ["neanderthals", "ancient humans", "shanidar", "stone age", "caring for the sick", "archaeology", "prehistory",
             "human evolution", "ancient medicine", "animated explainer", "stickman"],
    "mood": "wholesome",
    "sources": [
        "Trinkaus, E. & Villotte, S. (2017). External auditory exostoses and hearing loss in the Shanidar 1 Neandertal. PLoS ONE.",
        "Lordkipanidze, D. et al. (2005). The earliest toothless hominin skull. Nature 434, 717-718.",
        "Gracia, A. et al. (2009). Craniosynostosis in the Middle Pleistocene human Cranium 14 from the Sima de los Huesos, Atapuerca, Spain. PNAS.",
        "Weyrich, L. S. et al. (2017). Neanderthal behaviour, diet, and disease inferred from ancient DNA in dental calculus. Nature.",
        "Trinkaus, E. (2018). An abundance of developmental anomalies and abnormalities in Pleistocene people. PNAS.",
    ],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(out, len(scenes), "scenes,", sum(len(s["narration"].split()) for s in scenes), "words,",
      "hook words:", sum(len(s["narration"].split()) for s in scenes[:12]))
