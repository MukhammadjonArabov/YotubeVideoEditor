"""Director marks for project 38 written by Claude (Gemini is off, owner's instruction 2026-10-30).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p38.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=38)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}
import json
SJ = json.load(open("scripts/tiny_habits.json", encoding="utf-8"))["scenes"]


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


SECTIONS = {
    find("One percent sounds like nothing."): ("dip_to_black", "whoosh"),
    find("How much of your day is on autopilot?"): ("whip", "swoosh"),
    find("So how long does a new habit take to stick?"): ("dip_to_black", "riser"),
    find("Quick pause."): ("crossfade", None),
    find("You've probably heard willpower is like a battery."): ("whip", "swoosh"),
    find("Researchers pinged two hundred five adults"): ("crossfade", "whoosh"),
    find("One last thing keeps you going."): ("whip", "ding"),
    find("So, how do you actually improve"): ("dip_to_black", None),
    find("Thank you for spending"): ("crossfade", None),
}
MUSIC = {
    find("One percent sounds like nothing."): "change_mood",
    find("You end it about thirty-seven") if False else find("You don't end the year one percent better."): "swell",
    find("And the average time to feel automatic?"): "drop_out",
    find("Now the part that surprised me most."): "swell",
    find("And the willpower battery?"): "drop_out",
    find("Here's the twist. Disciplined people"): "change_mood",
    find("Here's my honest take."): "swell",
}
SHAKE = {find("Now flip it. One percent worse"), find("Resist cookies in the morning"), find("Wake up. Phone. Scroll.")}
PUNCH = {1, 3, 9, find("You don't end the year one percent better."), find("And the average time to feel automatic?"),
         find("And the willpower battery?"), find("Here's the twist. Disciplined people")}
EXTRA_SFX = {find("Quitting at day ten is like leaving"): "boing", find("Every beep, write what"): "ding",
             find("And the willpower battery?"): "impact", find("Not ten habits. Just one."): "pop"}
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
