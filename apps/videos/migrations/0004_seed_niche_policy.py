"""Seed the single niche, the tracked YouTube policy pages and the compliance checklist."""
from django.db import migrations

NICHE = dict(
    name="Qadimgi odamlar va inson tabiati",
    name_en="Ancient humans & the science of everyday human life",
    description=(
        "Qadimgi odamlar qanday yashagani va bugungi oddiy odatlarimiz qayerdan kelgani haqida "
        "qiziqarli, ilmiy asoslangan animatsion explainer videolar (stick-figure uslubida, ingliz tilida)."
    ),
    audience="Curious adults and teens (18-45) who like history, psychology and 'why do we do this?' questions; watch on phone and TV.",
    tone=(
        "Conversational, curious and lightly funny. Short simple sentences. Every claim grounded in "
        "archaeology, anthropology or published studies; uncertain things are said as uncertain. "
        "Advertiser-friendly: violence, drugs and sex are mentioned only briefly and never graphically."
    ),
    title_formula=(
        "A curiosity question that links ancient humans to something everyday: "
        "'What Did Ancient Humans Do When...?', 'How Did Ancient Humans ...?', 'Why Do We ...?'. "
        "Under 60 characters, one surprising word allowed in CAPS."
    ),
    content_pillars="\n".join([
        "Daily life of ancient humans (food, sleep, work, weather, free time)",
        "Origins of everyday things (clothes, cooking, music, counting, money)",
        "Survival: cold, rain, illness, predators, travel",
        "Human body and brain explained through evolution",
        "Other human species and our deep past",
        "Everyday psychology with a historical twist",
    ]),
    avoid_topics="\n".join([
        "Medical, legal or financial advice",
        "Graphic violence, gore, torture details",
        "Drug how-to or glorification",
        "Politics, religion debates, hateful stereotypes about any group",
        "Unverifiable 'secret history' / conspiracy claims",
        "Copying another channel's script, titles or thumbnails",
    ]),
    originality_rules=(
        "Every script needs at least one original angle: a personal-take line from the narrator, a "
        "modern-life comparison, or a 'what would YOU do' moment. Cite 2-3 real sources in the description. "
        "Never re-tell an existing video's structure beat by beat."
    ),
    style_guide=(
        "hand-drawn flat 2D cartoon, simple stick-figure characters with large round white heads, "
        "simple expressive faces, thin black line limbs, clean black outlines, bright flat colors, "
        "natural prehistoric landscapes with soft blue sky, 16:9, no text, no watermark, "
        "consistent character design across all scenes"
    ),
    character_description="a friendly caveman with a big round white head, messy brown hair and a brown fur tunic",
    default_minutes=9,
    default_seconds_per_image=8,
    default_mood="mysterious",
)

POLICY_DOCS = [
    ("YouTube kanal monetizatsiya qoidalari (YPP)", "https://support.google.com/youtube/answer/1311392?hl=en"),
    ("Reklama beruvchilar uchun qulay kontent", "https://support.google.com/youtube/answer/6162278?hl=en"),
    ("YouTube hamjamiyat qoidalari", "https://support.google.com/youtube/answer/9288567?hl=en"),
    ("AI / o'zgartirilgan kontentni oshkor qilish", "https://support.google.com/youtube/answer/14328491?hl=en"),
]

RULES = [
    ("Reklamaga mos kontent",
     "Advertiser-friendly content: flag graphic violence, gore, drug use or glorification, sexual content, hate speech, profanity, or dangerous acts. Brief, non-graphic historical mentions are acceptable."),
    ("Sarlavha va tavsif mosligi",
     "Title/thumbnail truthfulness: does the title and description actually match what the script delivers? Flag bait-and-switch or exaggerated promises."),
    ("Faktlar ehtiyotkorligi",
     "Factual-claim caution: find claims stated as certain fact that the script cannot support. Suggest softer wording such as 'some researchers believe' or 'evidence suggests'."),
    ("O'ziga xoslik (AI kanallar uchun eng muhim)",
     "Originality signal: flag if the script is bare narration of facts with no original commentary, opinion, comparison or added value - YouTube treats this as 'inauthentic / mass-produced' for AI-narrated faceless channels. When flagged, suggest a concrete fix (a personal-take line, a recurring narrator opinion beat, a modern-life comparison, or on-screen source citations)."),
    ("Oldingi videolarga o'xshashlik",
     "Similarity to my own past videos: compare against the list of my previous titles/topics provided and flag if this script is too close to one of them."),
    ("Maslahat berish taqiqi",
     "No professional advice: flag anything that sounds like medical, legal or financial advice aimed at the viewer."),
]


def seed(apps, schema_editor):
    Niche = apps.get_model("videos", "Niche")
    Project = apps.get_model("videos", "Project")
    ChannelSource = apps.get_model("videos", "ChannelSource")
    PolicyDocument = apps.get_model("videos", "PolicyDocument")
    ComplianceRule = apps.get_model("videos", "ComplianceRule")

    niche = Niche.objects.filter(is_active=True).first() or Niche.objects.create(**NICHE)
    Project.objects.filter(niche__isnull=True).update(niche=niche)
    ChannelSource.objects.filter(niche__isnull=True).update(niche=niche)
    if not PolicyDocument.objects.exists():
        for label, url in POLICY_DOCS:
            PolicyDocument.objects.create(label=label, url=url)
    if not ComplianceRule.objects.exists():
        for i, (title, instruction) in enumerate(RULES, start=1):
            ComplianceRule.objects.create(order=i, title=title, instruction=instruction)


class Migration(migrations.Migration):
    dependencies = [("videos", "0003_niche_channels_policy")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
