"""Draws 6 autumn anime pictures for music project 6 and turns each into a 20 s clip:
living loop (leaves/grass sway) + slow camera push + rain or snow particles.
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/music/make_m6_clips.py').read())"
Writes media/music/m6/gen/ (pictures and clips); a second step attaches the clips to the project."""
import subprocess
from pathlib import Path

from django.conf import settings

from apps.videos.services import atmosphere, living
from apps.videos.services.image_providers import get_provider
from apps.videos.services.images import normalize_to_1080p
from apps.videos.services.render import ffmpeg_exe

STYLE = ("high-quality anime illustration in the style of a modern Japanese animated feature film: clean crisp line art, "
         "cel shading with soft gradients, richly painted detailed backgrounds, cinematic lighting and depth, melancholic "
         "autumn night colours, deep blue and warm orange, sharp focus, 16:9, no text, no letters, no watermark")
SHOTS = [
    ("rain", "A young anime girl with short brown hair, a beige coat and a red scarf walks alone under a transparent umbrella "
             "along a quiet Japanese street at night in the rain, orange maple leaves on the wet road, warm shop lights reflecting in puddles."),
    ("rain", "A young anime man in a long grey coat stands alone on an open-air train platform at night in the rain, orange maple "
             "trees behind the tracks, a single lamp glowing, fallen leaves floating in puddles."),
    ("rain", "An empty wooden park bench under a large red maple tree at night in the rain, a forgotten transparent umbrella "
             "leaning on it, fallen leaves in puddles, a warm street lamp glowing, no people."),
    ("snow", "A young anime girl with long dark hair, a cream coat and a red scarf waits at a small country bus stop at night as "
             "the first snow falls on red and orange autumn leaves, a street lamp glowing above her."),
    ("rain", "A young anime man in a dark jacket walks slowly under a black umbrella along a street lined with golden ginkgo trees "
             "at dusk in the rain, yellow leaves on the wet pavement, shop windows glowing warmly."),
    ("snow", "A small wooden house among autumn maple trees at night as the first snow begins to fall, one warm window glowing, "
             "orange leaves under a thin layer of snow, a quiet path leading to the door, no people."),
]
CLIP_SEC = 20
out_dir = Path(settings.MEDIA_ROOT) / "music" / "m6" / "gen"
out_dir.mkdir(parents=True, exist_ok=True)
provider = get_provider()
exe = ffmpeg_exe()
for i, (effect, scene) in enumerate(SHOTS, start=1):
    img = out_dir / f"shot_{i:02d}.png"
    if not img.exists():
        png = provider.generate(f"{STYLE}. Scene: {scene}", seed=6100 + i)
        img.write_bytes(normalize_to_1080p(png))
    loop = living._make(img, out_dir / f"living_{i:02d}.mp4", out_dir / f"living_{i:02d}.none") or img
    fx = atmosphere.overlay_path(effect)
    clip = out_dir / f"clip_{i:02d}.mp4"
    src = ["-stream_loop", "-1", "-i", str(loop)] if loop != img else ["-loop", "1", "-i", str(img)]
    frames = CLIP_SEC * 24
    vf = (f"[0:v]fps=24,scale=2112:1188,zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d=1:s=1920x1080:fps=24,setsar=1[bg];[1:v]format=rgba,colorchannelmixer=aa=0.75[fx];"
          f"[bg][fx]overlay=0:0:shortest=0,format=yuv420p[v]")
    subprocess.run([exe, "-y", "-loglevel", "error", *src, "-stream_loop", "-1", "-i", str(fx), "-filter_complex", vf,
                    "-map", "[v]", "-t", str(CLIP_SEC), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(clip)],
                   check=True)
    print("clip", i, effect, "living" if loop != img else "still")
