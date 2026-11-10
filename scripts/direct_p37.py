"""Director marks for project 37 written by Claude (Gemini is off, owner's instruction 2026-10-30).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p37.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=37)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}
import json
SJ = json.load(open("scripts/broken_plans.json", encoding="utf-8"))["scenes"]


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


SECTIONS = {
    find("So let's start with the biggest lie"): ("dip_to_black", "whoosh"),
    find("And it's not just students"): ("crossfade", "whoosh"),
    find("Okay. But what if we just want it more?"): ("whip", "swoosh"),
    find("Remember the stranger in the brain scanner?"): ("dip_to_black", "riser"),
    find("Quick pause."): ("crossfade", None),
    find("Procrastination. The art of tomorrow."): ("whip", "swoosh"),
    find("January first. New year, new me."): ("crossfade", "whoosh"),
    find("So what actually works?"): ("dip_to_black", "riser"),
    find("So, why do we make plans we never keep?"): ("crossfade", "whoosh"),
    find("Thank you for spending"): ("crossfade", None),
}
MUSIC = {
    find("So let's start with the biggest lie"): "change_mood",
    find("And the final bill?"): "drop_out",
    find("Remember the stranger in the brain scanner?"): "change_mood",
    find("Guess which one future you looked like?"): "drop_out",
    find("January first. New year, new me."): "swell",
    find("So what actually works?"): "change_mood",
    find("Ninety-one percent said they actually did it."): "swell",
    find("None of that makes you lazy."): "swell",
}
SHAKE = {find("By Wednesday, the plan is gone."), find("Three extra weeks. On their own project."), find("Monday. Then next Monday.")}
PUNCH = {1, 5, 11, find("Sounds reasonable. Very confident."), find("And the actual behaviour?"), find("Your brain treats future you like a stranger."),
         find("Six months later, how many were still going?"), find("Ninety-one percent said they actually did it.")}
EXTRA_SFX = {find("Sounds reasonable. Very confident."): "boing", find("Of course you skip the gym."): "pop",
             find("I once cleaned my whole room"): "boing", find("And the final bill?"): "impact", find("Ninety-one percent said"): "ding"}
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
