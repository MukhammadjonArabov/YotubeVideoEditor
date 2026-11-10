"""Move the single `sfx_cue` into the new `sfx` list and rename transitions to the new names."""
from django.db import migrations

DEFAULT_GAIN_DB = -8.0
TRANSITION_RENAMES = {"fade": "crossfade", "fadewhite": "flash", "fadeblack": "dip_to_black"}


def forwards(apps, schema_editor):
    Scene = apps.get_model("videos", "Scene")
    for s in Scene.objects.exclude(sfx_cue="", transition_in="").iterator():
        if s.sfx_cue and not s.sfx:
            s.sfx = [{"tag": s.sfx_cue, "offset_ms": 0, "gain_db": DEFAULT_GAIN_DB}]
        s.transition_in = TRANSITION_RENAMES.get(s.transition_in, s.transition_in)
        s.save(update_fields=["sfx", "transition_in"])


def backwards(apps, schema_editor):
    Scene = apps.get_model("videos", "Scene")
    back = {v: k for k, v in TRANSITION_RENAMES.items()}
    for s in Scene.objects.all().iterator():
        s.sfx_cue = (s.sfx[0].get("tag", "") if s.sfx else "")[:32]
        s.transition_in = back.get(s.transition_in, s.transition_in)
        s.save(update_fields=["sfx_cue", "transition_in"])


class Migration(migrations.Migration):
    dependencies = [("videos", "0008_scene_direction")]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="scene", name="sfx_cue"),
    ]
