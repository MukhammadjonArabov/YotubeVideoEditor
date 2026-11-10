"""Builds scripts/first_surgery.json (run: ./venv/Scripts/python scripts/first_surgery.py).
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, fact_source). Even index hero, odd index fact."""
import json
from pathlib import Path

MAL = "Maloney et al. (2022). Surgical amputation of a limb 31,000 years ago in Borneo. Nature 609, 547-551"
MUR = "Murphy, Davis, Tarrant & Balogh (2023). Common orthopaedic trauma may explain 31,000-year-old remains. Nature (Matters Arising)"
BUQ = "Buquet-Marcon, Charlier & Samzun. A possible Early Neolithic amputation at Buthiers-Boulancourt (Seine-et-Marne), France. Antiquity Project Gallery, issue 322; Inrap press release"
ALT = "Alt et al. (1997). Evidence for stone age cranial surgery. Nature 387, 360"
EDW = "Breasted, J. H. (1930). The Edwin Smith Surgical Papyrus. University of Chicago Press"
AUB = "Aubert et al. (2018). Palaeolithic cave art in Borneo. Nature 564, 254-257"
LIS = "Lister, J. (1867). On the antiseptic principle in the practice of surgery. British Medical Journal; Museum of Healthcare, 'Sir Joseph Lister' (amputation death rates of about 40-50 percent in some hospitals)"
SHA = "Trinkaus & Villotte (2017). External auditory exostoses and hearing loss in the Shanidar 1 Neandertal. PLoS ONE"

S = [
    # ---------------- hook (12 one-line scenes)
    ("Thirty-one thousand years ago, someone amputated a child's leg.", "The main character stands wide-eyed in a dim cave beside a small wooden crutch leaning on the wall.", "hook", "tense", 2, "normal", 0, "impact", None),
    ("The child did not die. The child lived for years.", "A young person's skeleton resting in a shallow grave with limestone rocks over the head, soft light from above.", "hook", "awe", 3, "normal", 400, None, MAL),
    ("No hospital. No antibiotics. No anesthesia we know of.", "The main character shakes his head slowly in front of a cave entrance with only a bundle of leaves on the ground.", "hook", "serious", 2, "normal", 0, None, None),
    ("The authors say the wound healed cleanly, without infection.", "Two bones of a lower leg with a smooth rounded end, resting side by side on a cloth.", "hook", "curious", 2, "normal", 0, None, MAL),
    ("If you've ever trusted a surgeon, this is for you.", "The main character holds a tiny stone blade up to the light with a puzzled face.", "hook", "serious", 2, "normal", 0, None, None),
    ("The previous record was only seven thousand years old.", "A single old arm bone resting on a stone with a small clay lamp beside it.", "hook", "awe", 2, "normal", 0, None, BUQ),
    ("By the end, you'll know how it was possible.", "The main character points at his own head with a confident grin, one eyebrow raised.", "hook", "curious", 3, "normal", 0, "pop", None),
    ("But another team says it wasn't surgery at all.", "Two question mark shapes made of stones standing on a cave floor in dim light.", "hook", "tense", 2, "normal", 0, None, MUR),
    ("Who is right? The bones hold the clues.", "The main character leans over a long stone table covered with bones, peering through a magnifying glass.", "hook", "whisper", 2, "slow", 0, None, None),
    ("The grave held red ochre, left near the jaw.", "A small red ochre lump resting on the ground beside a jaw bone, soft golden light.", "hook", "awe", 2, "slow", 0, None, MAL),
    ("But first, meet the cave in Borneo.", "The main character pushes aside giant jungle leaves and peeks out, a small torch in his hand.", "hook", "curious", 2, "normal", 0, None, None),
    ("Liang Tebo sits in a jungle of limestone cliffs.", "A wide dark cave mouth at the foot of tall limestone cliffs covered in green jungle under a misty sky.", "hook", "awe", 3, "normal", 500, None, MAL),
    # ---------------- the place and the grave
    ("Let's start with the place. Borneo, an island of rainforest, rivers and caves.", "The main character walks along a jungle trail with a small torch, tall tropical trees around him.", "build", "curious", 2, "normal", 0, None, None),
    ("The same limestone region in East Kalimantan holds some of the oldest cave paintings on Earth, with one animal painting at least forty thousand years old.", "A red-orange painted animal shape on a pale limestone cave wall with a hand stencil beside it, warm torch light.", "build", "awe", 2, "normal", 0, None, AUB),
    ("So people here were artists and thinkers long before farming existed. Hold onto that, because it matters later.", "The main character admires a cave wall painting with his head tilted, torch raised.", "build", "curious", 2, "normal", 0, None, None),
    ("In twenty twenty, archaeologists dug a small trench in Liang Tebo and found a grave.", "A small square excavation trench in a cave floor with measuring ropes, brushes and a bucket beside it.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("A grave, dug on purpose. Someone laid this person to rest with real care.", "The main character gently places a flat stone beside a small grave in a cave, head bowed.", "build", "serious", 2, "slow", 0, None, None),
    ("The body lay on its back with the legs bent, limestone rocks placed over the head and arms, and a lump of red ochre near the jaw.", "A shallow grave in a cave floor with several flat limestone rocks arranged around a resting skeleton.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("Red ochre was precious. Someone chose to leave it here, and that tells us this person mattered.", "The main character holds a small red ochre lump in his open palm, looking at it with respect.", "build", "serious", 2, "slow", 0, None, None),
    ("Radiocarbon dating of charcoal around the grave, plus a method called electron spin resonance on a tooth, put the burial at about thirty-one thousand years ago.", "A tiny pile of black charcoal beside a single tooth on a flat stone, a thin beam of light falling on them.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("Thirty-one thousand years. No metal, no farms, no writing, just hunter-gatherers and their knowledge.", "The main character holds a stone spear point and a wooden digging stick, standing in a rainforest clearing.", "build", "awe", 2, "slow", 0, None, None),
    # ---------------- the skeleton
    ("The skeleton belonged to a young adult, about nineteen or twenty when they died. The researchers couldn't tell the sex.", "A complete skeleton lying peacefully on its back in the soft light of a cave, the head resting on a flat stone.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("Then the team looked at the legs, and they noticed something strange.", "The main character crouches and points at the lower legs of a skeleton, one eyebrow raised.", "build", "tense", 2, "normal", 0, None, None),
    ("The left foot was missing, and the lower left leg ended in a smooth, rounded tip. All twenty-six bones of the right foot were there.", "A skeleton's right foot bones neatly arranged in a row beside a leg bone with a smooth rounded end.", "build", "serious", 2, "normal", 300, None, MAL),
    ("That suggests the foot was removed long before the burial, while the person was alive.", "The main character looks at an empty space where a foot bone should be, head tilted in thought.", "build", "serious", 2, "slow", 0, None, None),
    ("The left leg bones were also smaller and thinner than the right, which suggests the damage happened in childhood.", "Two lower leg bones lying next to each other, the left one visibly thinner and shorter than the right.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("Imagine being a child in a rainforest, with climbing and foraging all around you, and losing your foot.", "The main character stands at the foot of a huge rainforest tree looking up at its branches, a small crutch under one arm.", "build", "sad", 2, "slow", 0, None, None),
    ("The end of the bone shows a clean, angled cut, which the authors say looks unlike an accident or an animal attack.", "A close drawing of a leg bone with a smooth angled end, lit by a soft beam of light on a plain cloth.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("A clean cut. That's the first big clue.", "The main character holds a magnifying glass up to a smooth angled bone, looking impressed.", "build", "curious", 2, "normal", 0, None, None),
    ("New bone had grown over the cut ends, which is a sign of healing, and the authors found no sign of infection in the left leg.", "A leg bone with a smooth rounded healed end shown beside a small glowing check mark made of light.", "punchline", "awe", 2, "slow", 400, "ding", MAL),
    ("No infection. Before antibiotics, that's a huge deal.", "The main character wipes his forehead in relief and looks at a tiny cartoon germ marching away.", "build", "excited", 2, "normal", 0, None, None),
    ("As late as the eighteen sixties, roughly four in ten amputation patients in some hospitals died of infection, until Joseph Lister introduced antiseptic methods.", "A plain old hospital bed with a folded white sheet and a small brown glass bottle on a wooden bedside table.", "build", "serious", 2, "normal", 0, None, LIS),
    # ---------------- subscribe (once)
    ("Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring the ancient world together, one question at a time. It's free, it takes one second, and it helps more curious people find us.", "The main character points happily at the viewer with a thumbs up, standing beside a glowing red button drawn on a cave wall.", "normal", "happy", 2, "normal", 0, "pop", None),
    ("The healed bone also shows the person lived another six to nine years after the amputation.", "A simple wall of six to nine small charcoal tally marks drawn on a pale limestone cave wall.", "build", "awe", 2, "normal", 0, None, MAL),
    ("Six to nine years. They grew up, grew strong, and reached adulthood.", "The main character stands tall with a small crutch beside him, smiling, a young sapling growing next to him.", "build", "happy", 2, "slow", 0, None, None),
    ("They carried other health problems too, including a healed break in the neck and signs of infection in the right thigh bone. So someone kept caring for them.", "Two bones, a neck bone and a thigh bone, lying on a cloth beside a small bundle of green leaves.", "build", "serious", 2, "normal", 0, None, MAL),
    ("That is a lot to live with. Someone must have fed them, carried them and kept them clean.", "The main character carefully carries a bowl of food and a bundle of leaves toward a cave, with a gentle look.", "build", "serious", 2, "slow", 0, None, None),
    ("The authors say the operation needed knowledge of muscles and blood vessels to prevent deadly bleeding, plus cleaning and dressing the wound afterwards.", "An anatomy-style drawing of leg muscles and thin red lines for blood vessels on a cave wall, no letters.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("In plain words: a skilled healer with steady hands, and a very brave child.", "The main character holds a small stone blade steady in one hand and a leaf bandage in the other, very focused.", "build", "serious", 2, "normal", 0, None, None),
    ("The authors suggest local plants with medicinal properties may have been used, but there is no direct evidence of which plants.", "A rainforest floor with several different leafy plants and a small mortar bowl for grinding beside them.", "build", "curious", 2, "normal", 0, None, MAL),
    ("So we don't know the name. We don't know the plant. But we know someone knew what to do.", "The main character sits by a small fire, quietly stirring a bowl of green paste, with a thoughtful face.", "punchline", "serious", 2, "slow", 400, None, None),
    ("Until this find, the oldest known amputation came from a farmer in France, about six thousand nine hundred years ago, described as a possible amputation of the left arm.", "A single old arm bone resting on a stone in soft light, with a small farm field drawn in the far background.", "build", "neutral", 2, "normal", 0, None, BUQ),
    ("That makes Borneo's case about twenty-four thousand years older. Your history textbook just got a lot longer.", "The main character stretches a very long paper scroll across the floor of a cave, with a big smile.", "build", "excited", 2, "normal", 0, None, None),
    ("Neolithic farmers also opened skulls. A man at Ensisheim in France, about seven thousand years ago, had two skull openings that had healed, one of them fully.", "A skull with a neat round healed hole resting on a flat stone in warm light.", "build", "curious", 2, "normal", 0, None, ALT),
    ("So surgery before writing is real. But writing arrives much later.", "The main character holds a clay tablet in one hand and a stone blade in the other, looking from one to the other.", "build", "curious", 2, "normal", 0, None, None),
    ("The Edwin Smith papyrus, a copy from about sixteen hundred BCE probably made from older texts, lists forty-eight injury cases with notes on how to examine them.", "An old unrolled papyrus scroll with rows of tiny pictures of bones and no readable letters on a wooden table.", "build", "neutral", 2, "normal", 0, None, EDW),
    ("Think of that as a doctor's notebook from three and a half thousand years ago. The first written medicine.", "The main character wears a tiny round pair of glasses and carefully writes in a big notebook, very serious.", "build", "funny", 2, "normal", 0, None, None),
    # ---------------- the challenge
    ("Now the big challenge. In twenty twenty-three, a team of doctors argued in Nature that the leg could have been an open fracture of the growth plate that became infected, and was later lost.", "A drawing of a broken lower leg bone with a small flame-shaped infection symbol beside it on a plain cloth.", "build", "serious", 2, "normal", 0, None, MUR),
    ("So maybe it wasn't a planned operation. Maybe it was an accident, followed by a slow, long infection.", "The main character gets up from a rock holding his ankle, looking worried, a tiny cloud of dust behind him.", "build", "tense", 2, "slow", 0, None, None),
    ("They also say cutting through thick shin bone without metal tools would be highly improbable.", "A flint blade and a thick shin bone side by side on a stone, the blade tiny next to the bone.", "build", "neutral", 2, "normal", 0, None, MUR),
    ("Fair point. Flint is sharp, but bone is tough.", "The main character tries to saw a thick bone with a flint blade, sweating, the bone barely scratched.", "build", "funny", 2, "fast", 0, None, None),
    ("The original authors point to the clean, angled cut and the lack of infection signs as evidence for a deliberate operation.", "A leg bone with a smooth angled end shown beside a plain healed bone end, both on a clean cloth.", "build", "neutral", 2, "normal", 0, None, MAL),
    ("Two teams, one skeleton. That's science: more checking, less certainty.", "The main character stands between two giant stone question marks, shrugging and smiling.", "build", "funny", 2, "normal", 0, None, None),
    ("Either way, the skeleton shows long survival with serious injuries, and that suggests care.", "A skeleton resting on its back inside a cave with a small cluster of glowing candles around it.", "punchline", "awe", 2, "slow", 400, None, MAL),
    ("That's the part I find hardest to argue with. Care. Honestly, it moves me more than the surgery itself.", "The main character sits by a fire with a hand over his heart, looking into the flames softly.", "build", "serious", 2, "slow", 0, None, None),
    ("Stone Age skeletons keep showing the same pattern: people surviving serious injuries for years.", "A Neanderthal skeleton lying peacefully in a cave beside a small stone, soft light from the entrance.", "build", "neutral", 2, "normal", 0, None, SHA),
    ("So who performed the world's first surgery? Maybe nobody we'll ever name. A healer in a rainforest, thirty-one thousand years ago, who may have given a child a future. Thank you for staying with me to the very end. If this made you think, hit like and tell me in the comments which side you believe. I read every one. Next time: when did dogs join the camp? I'll be here, and I hope you'll be too. See you there, friend.", "The main character smiles warmly at the viewer, a small crutch beside him and a rainforest cave behind him.", "normal", "happy", 2, "slow", 800, "pop", None),
]

assert 50 <= len(S) <= 80, len(S)
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
    "title": "Who Performed the World's First SURGERY?",
    "title_alternatives": ["A Child Lost a Leg 31,000 Years Ago. Then LIVED.", "Was This the Oldest SURGERY? Scientists Disagree",
                           "The Borneo Skeleton That Rewrote MEDICINE", "How Did Stone Age Healers Beat INFECTION?"],
    "description": ("Thirty-one thousand years ago, someone amputated a child's leg. The child did not die. This video follows the Borneo "
                    "skeleton from Liang Tebo cave, the evidence that the wound healed, the earlier record from France, early skull surgery, "
                    "and the scientists who argue it was not surgery at all.\n\nThis video is history and science, not medical advice.\n\n"
                    "Sources:\n"
                    "- Maloney et al. (2022). Surgical amputation of a limb 31,000 years ago in Borneo. Nature.\n"
                    "- Murphy et al. (2023). Common orthopaedic trauma may explain 31,000-year-old remains. Nature (Matters Arising).\n"
                    "- Aubert et al. (2018). Palaeolithic cave art in Borneo. Nature.\n"
                    "- Buquet-Marcon, Charlier & Samzun. A possible Early Neolithic amputation at Buthiers-Boulancourt. Antiquity.\n"
                    "- Alt et al. (1997). Evidence for stone age cranial surgery. Nature.\n"
                    "- Breasted (1930). The Edwin Smith Surgical Papyrus.\n"
                    "- Lister (1867). On the antiseptic principle in the practice of surgery."),
    "tags": ["first surgery", "oldest amputation", "borneo skeleton", "liang tebo", "stone age surgery", "ancient medicine",
             "ancient humans", "archaeology", "history of medicine", "prehistory", "animated history", "stickman"],
    "mood": "mysterious",
    "sources": [
        "Maloney, T. R. et al. (2022). Surgical amputation of a limb 31,000 years ago in Borneo. Nature 609, 547-551.",
        "Murphy, N. J., Davis, J. S., Tarrant, S. M. & Balogh, Z. J. (2023). Common orthopaedic trauma may explain 31,000-year-old remains. Nature (Matters Arising).",
        "Aubert, M. et al. (2018). Palaeolithic cave art in Borneo. Nature 564, 254-257.",
        "Buquet-Marcon, C., Charlier, P. & Samzun, A. A possible Early Neolithic amputation at Buthiers-Boulancourt (Seine-et-Marne), France. Antiquity (Project Gallery).",
        "Alt, K. W. et al. (1997). Evidence for stone age cranial surgery. Nature 387, 360.",
        "Breasted, J. H. (1930). The Edwin Smith Surgical Papyrus. University of Chicago Press.",
        "Lister, J. (1867). On the antiseptic principle in the practice of surgery. British Medical Journal.",
        "Trinkaus, E. & Villotte, S. (2017). External auditory exostoses and hearing loss in the Shanidar 1 Neandertal. PLoS ONE.",
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
