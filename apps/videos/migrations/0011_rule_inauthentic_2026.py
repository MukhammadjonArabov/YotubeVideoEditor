"""Add the YouTube July 2026 "inauthentic content" clarification to the compliance checklist."""
from django.db import migrations

TITLE = "YouTube 2026: inauthentic content"
INSTRUCTION = (
    "YouTube (July 2026) does not monetize three kinds of 'inauthentic content': (1) generic, repetitive or "
    "template-based videos with no real narrative arc or visible creativity; (2) off-putting or distressing content "
    "built to chase engagement, e.g. emotionally manipulative suffering; (3) AI personas giving health, medical, "
    "legal or financial guidance. Check that this script has a clear narrative arc with a beginning, tension and "
    "payoff, a distinct angle of its own rather than a reusable template with the topic swapped in, no manipulative "
    "or graphic distress, and that no narrator or character presents itself as giving health, legal or money advice. "
    "Warn on any risk; fail if the script would plainly fall into one of the three kinds."
)


def forwards(apps, schema_editor):
    ComplianceRule = apps.get_model("videos", "ComplianceRule")
    if ComplianceRule.objects.filter(title=TITLE).exists():
        return
    last = ComplianceRule.objects.order_by("-order").values_list("order", flat=True).first() or 0
    ComplianceRule.objects.create(order=last + 1, title=TITLE, instruction=INSTRUCTION, enabled=True)


def backwards(apps, schema_editor):
    apps.get_model("videos", "ComplianceRule").objects.filter(title=TITLE).delete()


class Migration(migrations.Migration):
    dependencies = [("videos", "0010_claude_workflow")]
    operations = [migrations.RunPython(forwards, backwards)]
