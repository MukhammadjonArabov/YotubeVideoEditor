"""Director marks for project 32 written by Claude (Gemini quota was used up, owner's instruction 2026-10-26).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p32.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=32)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


# section starts: how the scene comes in
SECTIONS = {
    find("Let's start with the flaw"): ("dip_to_black", "whoosh"),
    find("Every night began"): ("crossfade", "whoosh"),
    find("Caves and rock shelters"): ("whip", "swoosh"),
    find("Out in the open, wind"): ("crossfade", "whoosh"),
    find("Rule three:"): ("whip", "swoosh"),
    find("Quick pause."): ("crossfade", None),
    find("Now, the quiet rain."): ("dip_to_black", None),
    find("Rule four:"): ("whip", "whoosh"),
    find("Rule five:"): ("whip", "swoosh"),
    find("Long wet seasons"): ("crossfade", None),
    find("Surviving the night"): ("crossfade", "whoosh"),
    find("So, why were rainy nights"): ("dip_to_black", "riser"),
    find("Thank you for spending"): ("crossfade", None),
}
TEXT = {
    find("Water pulls heat about"): "25X FASTER",
    find("Water first. Warmth second."): "WATER FIRST",
    find("Rule one:"): "RULE 1",
    find("In 2017, rain fell"): "2017",
    find("Rule two:"): "RULE 2",
    find("At Riparo Bombrini"): "DRIP LINE",
    find("Rule three:"): "RULE 3",
    find("At Border Cave, people made"): "200,000 YEARS",
    find("At Sibudu, bedding layers"): "77,000 YEARS",
    find("At Ohalo II in Israel"): "23,000 YEARS",
    find("Rule four:"): "RULE 4",
    find("Rule five:"): "RULE 5",
    find("At Sibudu, bedding was renewed"): "15 LAYERS",
    find("Five rules, no instruction"): "5 RULES",
}
MUSIC = {
    find("Let's start with the flaw"): "change_mood",
    find("Asleep, your body's heating"): "drop_out",
    find("Here's the scary part."): "drop_out",
    find("A flash flood killed"): "stinger",
    find("At Border Cave, people made"): "swell",
    find("That's why gentle rain was the sneaky killer."): "drop_out",
    find("Surviving the night"): "change_mood",
    find("That's not a camp. That's an inheritance."): "swell",
    find("Your own discomfort"): "swell",
}
SHAKE = {find("Weather services warn"), find("A flash flood killed"), find("Fall miles") if False else find("It can fall miles upstream."),
         find("Loud storms got attention.")}
PUNCH = {1, 7, 11, find("Rule one:"), find("Rule two:"), find("Rule three:"), find("Rule four:"), find("Rule five:"),
         find("That's why gentle rain was the sneaky killer."), find("At Border Cave, people made")}
EXTRA_SFX = {find("Ash as a mattress pad."): "boing", find("Basically, Stone Age bug spray."): "pop",
             find("A clothes dryer that also cooks dinner."): "pop", find("I'd volunteer for the middle"): "boing",
             find("Asleep, your body's heating"): "impact", find("At Border Cave, people made"): "ding",
             find("Fifteen times somebody said"): "boing", find("Your own discomfort"): "riser"}

CUES = [x.get("sfx_cue") for x in (p.script_json or {}).get("scenes", [])]
CYCLE = ["slow_zoom_in", "pan_left", "slow_zoom_out", "pan_right"]
dirs = []
for i, s in enumerate(scenes):
    o = s.order
    cam = "punch_zoom" if o in PUNCH else "shake" if o in SHAKE else CYCLE[i % 4]
    trans, tsfx = SECTIONS.get(o, ("cut", None))
    sfx = []
    for tag in (CUES[i] if i < len(CUES) else None, tsfx, EXTRA_SFX.get(o)):
        if tag and tag not in [x["tag"] for x in sfx]:
            sfx.append({"tag": tag, "offset_ms": 0, "gain_db": -10.0 if tag in ("whoosh", "swoosh", "riser") else -8.0})
    dirs.append(director._clean({"emotion": s.emotion, "intensity": s.intensity, "pace": s.pace, "pause_after_ms": s.pause_after_ms,
                                 "camera_move": cam, "transition_in": trans, "sfx": sfx, "music_cue": MUSIC.get(o, "continue"),
                                 "on_screen_text": TEXT.get(o)}, len(s.narration.split())))
dirs = director.enforce_rules(dirs, scenes)
changed = director.apply(p, dirs)
from collections import Counter
print("changed", changed, "| texts", sum(1 for d in dirs if d["on_screen_text"]), "| sfx", sum(len(d["sfx"]) for d in dirs),
      "| music", Counter(d["music_cue"] for d in dirs), "| cams", Counter(d["camera_move"] for d in dirs),
      "| audio kept", p.scenes.exclude(audio="").count())
