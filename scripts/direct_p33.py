"""Director marks for project 33 written by Claude (Gemini quota was used up, owner's instruction 2026-10-26).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p32.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=33)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


# section starts: how the scene comes in
SECTIONS = {
    find("Let's start with that headline"): ("dip_to_black", "whoosh"),
    find("Now a bigger question"): ("crossfade", "whoosh"),
    find("Picture a hunter at dusk"): ("dip_to_black", "whoosh"),
    find("Let's look inside the head"): ("whip", "swoosh"),
    find("Now put that baby brain"): ("crossfade", "whoosh"),
    find("Quick pause."): ("crossfade", None),
    find("Imagine I hand you ten dollars"): ("whip", "ding"),
    find("Okay. Remember the group"): ("dip_to_black", None),
    find("So how do you live with"): ("crossfade", "whoosh"),
    find("Let's follow the alarm"): ("whip", "swoosh"),
    find("So, why is your brain addicted"): ("dip_to_black", "riser"),
    find("Thank you for spending"): ("crossfade", None),
}
TEXT = {
    find("Researchers measured it across"): "105,000 HEADLINES",
    find("Each extra negative word raised"): "+2% CLICKS",
    find("Scientists tested over eleven hundred"): "17 COUNTRIES",
    find("They called it: bad is stronger"): "BAD > GOOD",
    find("People found snakes and spiders faster"): "SNAKE FIRST",
    find("Doctor Randolph Nesse calls it"): "SMOKE DETECTOR",
    find("Bad pictures produced bigger brain"): "1998",
    find("A big meta-analysis estimated"): "2X?",
    find("It's older adults."): "OLDER ADULTS",
    find("Over a hundred studies had tested"): "100+ STUDIES",
    find("Seven a.m."): "7 A.M.",
    find("Ten p.m. Bed."): "10 P.M.",
}
MUSIC = {
    find("Let's start with that headline"): "change_mood",
    find("Each extra negative word raised"): "drop_out",
    find("They called it: bad is stronger"): "swell",
    find("Ignore a real snake once"): "drop_out",
    find("Okay. Remember the group"): "drop_out",
    find("It's older adults."): "swell",
    find("Let's follow the alarm"): "change_mood",
    find("Next time the alarm rings"): "swell",
}
SHAKE = {find("Your eyes go to the snake"), find("Three p.m. A rope on the path."), find("Noon. A friend doesn't reply")}
PUNCH = {1, 5, 9, find("Twice! That's like a refund"), find("Yes, grandma might be winning"), find("So that pull toward bad news?"),
         find("The research points to something simple"), find("Because for most of history")}
EXTRA_SFX = {find("Your smoke alarm goes off"): "boing", find("Twice! That's like a refund"): "pop",
             find("Yes, grandma might be winning"): "pop", find("Turns out their phone died."): "boing",
             find("Or you might be like me"): "boing", find("It's older adults."): "ding",
             find("Bad pictures produced bigger brain"): "impact", find("Here's the part") if False else find("But here's where it gets spicy."): "riser"}

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
