"""Compliance rule: the first 30-40 s must tell the viewer why to watch and what they will get."""
from django.db import migrations

TITLE = "Hook: nega ko'rish kerak va nima oladi"
INSTRUCTION = (
    "Look only at the hook scenes (beat_type 'hook', the first 30-40 seconds). They must (1) grab attention in the "
    "very first sentence without a greeting or 'in this video', (2) say why this matters to the viewer personally "
    "right now, (3) promise clearly and specifically what the viewer will know or understand by the end, and "
    "(4) leave one open question that the rest of the script really answers. Check that the promise is kept later in "
    "the script and that the hook is honest (no clickbait the video doesn't deliver). Warn if any of the four is "
    "weak or vague; fail if there is no reason to watch or no promise at all, or if the promise is not kept."
)


def forwards(apps, schema_editor):
    Rule = apps.get_model("videos", "ComplianceRule")
    if not Rule.objects.filter(title=TITLE).exists():
        last = Rule.objects.order_by("-order").values_list("order", flat=True).first() or 0
        Rule.objects.create(order=last + 1, title=TITLE, instruction=INSTRUCTION, enabled=True)


def backwards(apps, schema_editor):
    apps.get_model("videos", "ComplianceRule").objects.filter(title=TITLE).delete()


class Migration(migrations.Migration):
    dependencies = [("videos", "0011_rule_inauthentic_2026")]
    operations = [migrations.RunPython(forwards, backwards)]
