"""Director marks for project 39 written by Claude (Gemini is off, owner's instruction 2026-10-30).
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/direct_p39.py').read())"
Same output as services/director.py: camera, transition, SFX, music cue, on-screen text; then the code rules and apply."""
from apps.videos.models import Project
from apps.videos.services import director

p = Project.objects.get(pk=39)
scenes = list(p.scenes.order_by("order"))
N = {s.order: s.narration for s in scenes}
import json
SJ = json.load(open("scripts/conversation_mistakes.json", encoding="utf-8"))["scenes"]


def find(text: str) -> int:
    hits = [o for o, n in N.items() if n.startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


SECTIONS = {
    find("You know that replay after a party?"): ("dip_to_black", "whoosh"),
    find("Mistake one sounds friendly."): ("whip", "swoosh"),
    find("Mistake two: you explain"): ("dip_to_black", "riser"),
    find("Mistake three happens inside"): ("whip", "swoosh"),
    find("Quick pause."): ("crossfade", None),
    find("Mistake four: you don't ask"): ("crossfade", "whoosh"),
    find("Mistake five is about the ending."): ("whip", "ding"),
    find("So let's put it together."): ("dip_to_black", None),
    find("Thank you for spending"): ("crossfade", None),
}
MUSIC = {
    find("You know that replay after a party?"): "change_mood",
    find("Again and again") if False else find("Then each person guessed"): "swell",
    find("The tappers expected about half"): "drop_out",
    find("There it is. The open loop"): "swell",
    find("Each person said when they'd secretly"): "drop_out",
    find("So let's put it together."): "change_mood",
    find("Here's my honest take."): "swell",
}
SHAKE = {find("Mistake one sounds friendly."), find("Careful, though. A question storm"), find("Your friend says, I'm so tired")}
PUNCH = {1, 3, 9, find("The tappers expected about half"), find("There it is. The open loop"),
         find("Each person said when they'd secretly"), find("And the silence between turns")}
EXTRA_SFX = {find("Did I talk too much?"): "boing", find("One person tapped a famous song"): "click",
             find("Mistake four: you don't ask"): "impact", find("Ever answered a question nobody"): "pop"}
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
