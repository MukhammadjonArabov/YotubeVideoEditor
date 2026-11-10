"""Replace the seeded, vague main-character description with a precise one (only if unchanged)."""
from django.db import migrations

OLD = "a friendly caveman with a big round white head, messy brown hair and a brown fur tunic"
NEW = ("the SAME stick-figure man in every image: a perfectly round plain white head with two small black dot eyes, "
       "tiny eyebrows and a simple curved mouth, no nose, short spiky dark-brown hair on top of the head, no beard, "
       "thin black stick arms and legs, wearing one short brown fur tunic with a jagged hem, bare feet")
OLD_STYLE_PART = "simple stick-figure characters with large round white heads"
NEW_STYLE_PART = ("stick-figure characters with round plain white heads and dot eyes; other people are plain "
                  "stick figures without the fur tunic")


def forwards(apps, schema_editor):
    Niche = apps.get_model("videos", "Niche")
    for n in Niche.objects.all():
        changed = False
        if n.character_description.strip() == OLD:
            n.character_description = NEW
            changed = True
        if OLD_STYLE_PART in n.style_guide and "dot eyes" not in n.style_guide:
            n.style_guide = n.style_guide.replace(OLD_STYLE_PART, NEW_STYLE_PART)
            changed = True
        if changed:
            n.save(update_fields=["character_description", "style_guide"])


class Migration(migrations.Migration):
    dependencies = [("videos", "0005_character_reference")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
