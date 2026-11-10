"""Director marks for project 35 written by Claude (Gemini is off, owner's instruction 2026-10-30).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p35.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=35)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}
import json
SJ = json.load(open("scripts/money_brain.json", encoding="utf-8"))["scenes"]


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


SECTIONS = {
    find("So let's go back to a world"): ("dip_to_black", "whoosh"),
    find("Trap number one."): ("whip", "swoosh"),
    find("Trap number two."): ("whip", "swoosh"),
    find("Quick pause."): ("crossfade", None),
    find("Trap number three."): ("whip", "swoosh"),
    find("Trap number four."): ("whip", "swoosh"),
    find("Trap number five."): ("dip_to_black", "riser"),
    find("So, did our ancestors"): ("crossfade", "whoosh"),
    find("So is the answer just"): ("crossfade", "whoosh"),
    find("So if your money slips"): ("dip_to_black", None),
    find("Thank you for spending"): ("crossfade", None),
}
MUSIC = {
    find("So let's go back to a world"): "change_mood",
    find("Because tomorrow, you might"): "drop_out",
    find("Trap number one."): "swell",
    find("Trap number two."): "change_mood",
    find("The card group offered"): "drop_out",
    find("Trap number five."): "change_mood",
    find("Their wealth wasn't stuff"): "swell",
    find("So if your money slips"): "drop_out",
    find("But here's the hopeful part"): "swell",
}
SHAKE = {find("Lose a hundred dollars"), find("A missed bonus was annoying"), find("Right now wins. Invisible money")}
PUNCH = {1, 5, 11, find("Twice! For the exact same"), find("Your brain is doing its job"), find("Trap number one."),
         find("Trap number two."), find("Trap number three."), find("Trap number four."), find("Trap number five.")}
EXTRA_SFX = {find("Twice! For the exact same"): "boing", find("A fruit you leave for tomorrow"): "boing",
             find("Your caveman thinks the fruit"): "pop", find("And grain? Even more."): "ding",
             find("Our species is three hundred"): "impact"}
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
