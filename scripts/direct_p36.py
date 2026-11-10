"""Director marks for project 36 written by Claude (Gemini is off, owner's instruction 2026-10-30).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p36.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=36)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}
import json
SJ = json.load(open("scripts/laughter.json", encoding="utf-8"))["scenes"]


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


SECTIONS = {
    find("Imagine being a teacher"): ("dip_to_black", "whoosh"),
    find("So let's find the very first laugh"): ("crossfade", "whoosh"),
    find("But wait. Are we the only"): ("whip", "swoosh"),
    find("Quick test. Try tickling"): ("whip", "swoosh"),
    find("Now picture an ancient camp"): ("dip_to_black", "whoosh"),
    find("Quick pause."): ("crossfade", None),
    find("Robert Provine spent years"): ("whip", "swoosh"),
    find("So when did humour finally"): ("crossfade", "whoosh"),
    find("Here's something you never noticed"): ("whip", "ding"),
    find("And here's where it gets strange"): ("dip_to_black", "riser"),
    find("Remember the clue?"): ("whip", "swoosh"),
    find("This also explains the weird"): ("crossfade", "whoosh"),
    find("So, back to that school"): ("dip_to_black", None),
    find("So why do humans laugh?"): ("crossfade", "whoosh"),
    find("Thank you for spending"): ("crossfade", None),
}
MUSIC = {
    find("So let's find the very first laugh"): "change_mood",
    find("The closer the cousin"): "swell",
    find("Quick test. Try tickling"): "change_mood",
    find("And here's where it gets strange"): "drop_out",
    find("Remember the clue?"): "change_mood",
    find("So, back to that school"): "drop_out",
    find("Here's my take."): "swell",
}
SHAKE = {find("Then it spread to villages"), find("Two young hunters wrestle"), find("Four thousand years, and fart")}
PUNCH = {1, 3, 11, find("Ten million years. Before stone"), find("Thirty times! Alone"), find("And the joke was about"),
         find("Not perfectly. But better"), find("Here's my take.")}
EXTRA_SFX = {find("Nothing. Not even a giggle"): "boing", find("Imagine putting that on your resume"): "pop",
             find("Dad jokes. The worst kind."): "boing", find("A parrot that laughs in the snow"): "pop"}
CYCLE = ["slow_zoom_in", "pan_left", "slow_zoom_out", "pan_right"]
dirs = []
for i, s in enumerate(scenes):
    o = s.order
    cam = "punch_zoom" if o in PUNCH else "shake" if o in SHAKE else CYCLE[i % 4]
    trans, tsfx = SECTIONS.get(o, ("cut", None))
    sfx = []
    for tag in ((SJ[i].get("sfx_cue") if i < len(SJ) else None), tsfx, EXTRA_SFX.get(o)):
        if tag and tag not in [x["tag"] for x in sfx]:
            sfx.append({"tag": tag, "offset_ms": 0, "gain_db": -10.0 if tag in ("whoosh", "swoosh", "riser") else -8.0})
    text = SJ[i].get("on_screen_text") if i < len(SJ) else None
    dirs.append(director._clean({"emotion": s.emotion, "intensity": s.intensity, "pace": s.pace, "pause_after_ms": s.pause_after_ms,
                                 "camera_move": cam, "transition_in": trans, "sfx": sfx, "music_cue": MUSIC.get(o, "continue"),
                                 "on_screen_text": text}, len(s.narration.split())))
dirs = director.enforce_rules(dirs, scenes)
changed = director.apply(p, dirs)
print("director applied", changed, "texts:", sum(1 for s in p.scenes.all() if s.on_screen_text))
