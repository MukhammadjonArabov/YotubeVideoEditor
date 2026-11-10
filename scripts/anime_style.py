"""Switches one project to the anime art style and draws its hero reference sheet
(run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/anime_style.py').read()); apply(34)").
The project keeps the niche's voice, montage and rules; only the pictures change."""
from django.core.files.base import ContentFile

from apps.videos.models import Project
from apps.videos.services.image_providers import get_provider

ANIME_STYLE = ("high-quality anime illustration in the style of a modern Japanese animated feature film: clean crisp line art, "
               "cel shading with soft gradients, richly painted detailed backgrounds, cinematic lighting and depth, "
               "vibrant but natural colours, expressive faces and hands, sharp focus, 16:9, no text, no letters, no watermark, "
               "consistent character design across all scenes")
ANIME_HERO = ("the SAME young man in every image: anime style, about twenty-five years old, warm light-brown skin, short messy "
              "dark-brown hair, large expressive dark-brown eyes, friendly face, no beard, slim and athletic, wearing one simple "
              "sleeveless brown animal-hide tunic with a jagged hem and a thin leather cord necklace with a single white tooth pendant, barefoot")
REF_PROMPT = (f"{ANIME_STYLE}. Character reference sheet: {ANIME_HERO}. He stands in a relaxed full-body pose facing the viewer "
              "with a warm smile, plain soft light-grey background, even studio lighting, whole body visible from head to feet.")


def apply(pid: int, seed: int = 4242) -> str:
    p = Project.objects.get(pk=pid)
    png = get_provider().generate(REF_PROMPT, seed=seed)
    p.style_guide = ANIME_STYLE
    p.character_override = ANIME_HERO
    p.character_reference_override.save(f"p{pid}_anime_hero.png", ContentFile(png), save=False)
    p.save(update_fields=["style_guide", "character_override", "character_reference_override"])
    return p.character_reference_override.path
