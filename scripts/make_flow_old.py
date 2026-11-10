"""Writes scripts/kits/p<id>.flow.json (3 Google Flow image prompts each) for the older videos and saves them into the kits.
Run: ./venv/Scripts/python scripts/make_flow_old.py"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()
from apps.videos.models import Project  # noqa: E402
from apps.videos.services import kit  # noqa: E402

MAN = ("the SAME stick-figure man (round plain white head, dot eyes, short spiky dark-brown hair, short brown fur tunic with a jagged hem, "
       "thin black stick arms and legs)")
STYLE = "Hand-drawn flat 2D cartoon, stick-figure style, 16:9. "
END = "Thick black outlines, saturated flat colors, very high contrast, no watermark."
DIV = "A bright white lightning-shaped divider between them."


def title_clause(text: str, color: str) -> str:
    words = text.split()
    if len(words) >= 3:
        half = (len(words) + 1) // 2
        l1, l2 = " ".join(words[:half]), " ".join(words[half:])
        lines = f'exactly {len(words)} words on two lines: "{l1}" on the first line and "{l2}" on the second line'
    elif len(words) == 2:
        lines = f'exactly two words on two lines: "{words[0]}" on the first line and "{words[1]}" on the second line'
    else:
        lines = f'exactly one word: "{text}"'
    return (f"Big bold title text across the top of the frame, {lines}, huge thick {color} block capital letters with a thick black outline "
            f"and a soft shadow, perfectly spelled, easy to read, no other text anywhere. ")


def P(text, scene, color="yellow"):
    scene = scene.replace("MAN", MAN).replace("DIVIDER", DIV)
    if scene.startswith("the SAME"):
        scene = "The" + scene[3:]
    return {"text": text, "prompt": STYLE + scene + " " + title_clause(text, color) + END}


V = {
    3: [P("STILL HAUNTED?", "MAN sits up in a modern bed at night with huge scared eyes and sweat drops, a giant shadow of a sabertooth cat with glowing eyes on the bedroom wall behind him, moonlight through the window."),
        P("DREAMS OF DANGER", "A giant sabertooth cat silhouette looming over a small sleeping stick figure on a cozy bed, deep blue night, glowing yellow eyes, a crescent moon.", "white"),
        P("ANCIENT NIGHTMARES", "Split frame. Left half: MAN sleeping peacefully in a modern bed. Right half: a roaring sabertooth cat charging out of a dark savanna. DIVIDER")],
    4: [P("BUG ATTACK!", "MAN swats wildly at a cloud of big cartoon mosquitoes around a campfire at dusk in front of a cave, miserable face, buzzing swirls."),
        P("ANCIENT BUG SPRAY?", "A giant mosquito hovering over a small smoky fire with green leaves and a bundle of herbs beside it, MAN grinning in the smoke holding a leafy branch, warm orange dusk light.", "white"),
        P("SMOKE VS BUGS", "Split frame. Left half: a swarm of mosquitoes biting MAN, who looks miserable. Right half: MAN relaxed in thick herb smoke while the mosquitoes flee. DIVIDER")],
    5: [P("BARE FEET?", "MAN stands on hot rocky ground with one bare foot raised and a pained face, a pair of simple sandals lying in front of him, desert sun."),
        P("WHY WEAR SHOES?", "A single big bare foot with a thick sole next to a modern sneaker on a pale sandy background, MAN peering between them with a magnifying glass.", "white"),
        P("SHOE OR NO SHOE?", "Split frame. Left half: MAN walking happily barefoot on soft grass. Right half: MAN limping on sharp stones in thin sandals. DIVIDER")],
    6: [P("THE FIRE WENT OUT!", "MAN stares in panic at a cold pile of grey ash and black sticks outside a dark cave at night, hands on his cheeks, a few friends behind him looking worried."),
        P("KEEP THE FIRE", "A single glowing ember carried inside a small clay pot with a thin wisp of smoke, MAN cupping it protectively in the dark with an orange glow on his face.", "white"),
        P("FIRE OR DARKNESS?", "Split frame. Left half: a cold dark cave with MAN shivering. Right half: a bright warm campfire with MAN smiling. DIVIDER")],
    8: [P("ANCIENT TOOTHPASTE?", "MAN happily chews the end of a frayed twig like a toothbrush and shows a huge sparkling smile with shiny teeth, a few bright stars around his mouth."),
        P("NO TOOTHBRUSH?", "A frayed chewing stick lying next to an ancient skull with a few worn teeth on a flat stone, MAN leaning over it with a magnifying glass.", "white"),
        P("CLEAN TEETH, NO BRUSH", "Split frame. Left half: MAN scrubbing his teeth with a twig. Right half: a modern toothbrush and a tube of paste. DIVIDER")],
    9: [P("WHO MADE PANTS?", "MAN shivers in a snowy landscape wrapped in a pile of rough furs with one fur tied around his legs, proud and cold, icy wind lines."),
        P("THE FIRST CLOTHES", "A small bone needle threaded with sinew beside a stretched animal hide and a stone scraper on a flat rock, warm golden light.", "white"),
        P("COLD OR COZY?", "Split frame. Left half: MAN shivering with no clothes in a snowstorm. Right half: MAN cozy in furs by a warm fire. DIVIDER")],
    10: [P("WHY PAINT CAVES?", "MAN holds a flickering torch in a dark cave and paints a big red bison on the wall with his hand, glowing orange light, deep blue shadows."),
         P("HANDS ON THE WALL", "A red-ochre handprint stencil on a rough cave wall with a few painted animals, torchlight glow, a tiny stick figure looking up at it.", "white"),
         P("ART OR MAGIC?", "Split frame. Left half: a dark empty cave wall. Right half: the same wall covered with glowing painted bison and horses. DIVIDER")],
    11: [P("NO WORDS?", "MAN waves his arms and points wildly at an animal while two friends stare at him confused, a savanna behind them, comic gesture lines."),
         P("BEFORE LANGUAGE", "Three stick figures communicating only with gestures, pointing hands, a drawn sound-wave swirl and a small drum, warm sunset light, no letters anywhere except the title.", "white"),
         P("TALK WITHOUT WORDS", "Split frame. Left half: MAN grunting and pointing. Right half: two friends smiling and understanding, with a glowing heart-shaped swirl between them. DIVIDER")],
    12: [P("NO MAPS!", "MAN stands lost in a huge empty valley holding a long stick and looking at the night sky full of stars, sweat drop, a faint trail behind him."),
         P("FIND YOUR WAY", "A starry night sky over a wide savanna with a glowing path of footprints and a tall landmark tree, MAN tiny at the bottom looking up.", "white"),
         P("GPS OR STARS?", "Split frame. Left half: MAN staring at a glowing phone map. Right half: MAN confidently pointing at the stars. DIVIDER")],
    13: [P("TASTE DEATH?", "MAN holds a bright red berry close to his mouth with a worried sweaty face, a friend behind him shaking his head, a green forest around them."),
         P("POISON OR FOOD?", "A pile of red berries and a spotted mushroom side by side on a leaf with a big glowing question mark between them, MAN peeking nervously from behind a bush.", "white"),
         P("EAT IT OR NOT?", "Split frame. Left half: MAN smiling and eating a plump safe-looking fruit. Right half: MAN green-faced and dizzy after a bad berry, swirly eyes. DIVIDER")],
    14: [P("HALF YOUR LIFE IN THE DARK", "MAN sits by a tiny campfire in the middle of a huge dark night with only a thin crescent moon and many stars above, small glowing circle of light around him, cold blue shadows."),
         P("12 HOURS OF DARK", "A dark savanna camp under a huge starry sky with one tiny fire and a few sleeping stick figures, eyes of animals glowing far away in the dark.", "white"),
         P("DARK OR LIGHT?", "Split frame. Left half: a dark camp at night with MAN huddled by a small fire. Right half: a bright modern bedroom with a glowing lamp and MAN scrolling a phone. DIVIDER")],
    17: [P("STONE AGE OR WOOD AGE?", "MAN proudly holds a long wooden spear in one hand and a small stone axe in the other, a pile of logs and sticks next to him, forest background."),
         P("WOOD, NOT STONE?", "A wooden spear, a digging stick and a wooden bowl next to one small stone axe on a flat rock, warm golden forest light.", "white"),
         P("WHAT WAS IT MADE OF?", "Split frame. Left half: a small pile of stone tools. Right half: a much bigger pile of wooden tools and sticks, with MAN scratching his head between them. DIVIDER")],
    18: [P("NO NOTES. NO PHONE.", "MAN stands calmly on a hill and points to his own head with a confident grin, glowing swirling trail lines of memory floating above it, a savanna with distant landmarks behind him.", "white"),
         P("YOU VS THEM", "Split frame. Left half: MAN scrolling a phone with a blank, forgetful look. Right half: an ancient storyteller by a fire with a glowing head full of tiny pictures. DIVIDER"),
         P("THE MAP IN THEIR HEAD", "A big round head outline filled with a glowing map of rivers, hills, trees and animal trails, MAN looking up at it amazed.", "white")],
    19: [P("WHO HELPED HIM?", "A lone injured stick figure with a bandaged arm and a cane sitting at a cave mouth at sunset, MAN kneeling beside him offering a bowl of food, warm golden light.", "white"),
         P("NOT ALONE", "Split frame. Left half: a wounded figure lying alone looking sad. Right half: the same figure surrounded by friends giving him food and water. DIVIDER"),
         P("WHO WAS HE?", "An ancient skeleton resting on a cloth in a dim cave with a bright spotlight, a healed broken bone glowing softly, MAN leaning in with a magnifying glass, eyes huge.", "white")],
    21: [P("NO FRIDGE?", "MAN stares at a huge piece of rotting meat with green flies buzzing around it and holds his nose, a sunny savanna behind him.", "white"),
         P("STILL CHEESE", "A small clay jar of ancient cheese buried in sand with a few golden crumbs beside a trowel, MAN peering at it in amazement, warm desert light."),
         P("500 YEARS OLD", "A tiny wrinkled potato resting on a stone slab in a dusty ancient storehouse, MAN holding it up with a huge surprised face, golden light.", "white")],
    22: [P("WHO DRANK FIRST?", "MAN sniffs a bubbling clay pot of fruit juice with a puzzled face while a chimpanzee in the background drinks from a bowl of palm tree sap, savanna sunset."),
         P("BEER OR BREAD?", "Split frame. Left half: a loaf of rough bread on a stone table. Right half: a clay jar of foamy ancient beer with a straw. MAN stands between them with hands on hips, unable to choose. DIVIDER", "white"),
         P("DRUNK CHIMPS?", "A chimpanzee sitting happily under a palm tree holding a coconut shell cup, swirling stars around its head, MAN looking at it in disbelief, jungle background.")],
}

for pid, items in V.items():
    assert len(items) == 3
    path = ROOT / "scripts" / "kits" / f"p{pid}.flow.json"
    path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    kit.save_kit(Project.objects.get(pk=pid), flow_prompts=items)
    print("saved", pid)
