"""Publish kit for a finished video: 3 title options, 1 description, tags, 3 thumbnail designs and 3 Google Flow prompts.

The owner manages everything through Claude; the site only shows the result. Claude writes the kit with
`manage.py video_kit` and the thumbnails are drawn here with Pillow from the video's own pictures plus the
channel font, so they match the video's look and need no outside tool. Files live in media/projects/p<id>/kit/.
"""
from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
FONT_FILE = Path(settings.BASE_DIR) / "static" / "fonts" / "BebasNeue-Regular.ttf"
YELLOW, WHITE, BLACK, RED = (255, 212, 0), (255, 255, 255), (12, 12, 12), (230, 36, 36)
DESIGNS = ("hero", "object", "split")


# ------------------------------------------------------------------ storage
def kit_dir(project) -> Path:
    return Path(settings.MEDIA_ROOT) / "projects" / f"p{project.pk}" / "kit"


def kit_url(project, name: str) -> str:
    return f"{settings.MEDIA_URL}projects/p{project.pk}/kit/{name}"


def load_kit(project) -> dict:
    """{titles, description, tags, previews:[{file, text, design, url}]}; missing parts are empty."""
    path = kit_dir(project) / "kit.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    tags = data.get("tags") or project.tags or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    previews = [dict(p, url=kit_url(project, p["file"])) for p in data.get("previews", []) if (kit_dir(project) / p["file"]).exists()]
    return {"titles": data.get("titles", []), "description": data.get("description") or project.description or "",
            "tags": tags, "previews": previews, "flow_prompts": data.get("flow_prompts", [])}


def save_kit(project, titles=None, description=None, tags=None, previews=None, flow_prompts=None) -> dict:
    d = kit_dir(project)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "kit.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for key, val in (("titles", titles), ("description", description), ("tags", tags), ("previews", previews),
                     ("flow_prompts", flow_prompts)):
        if val is not None:
            data[key] = val
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


# ------------------------------------------------------------------ drawing helpers
def scene_picture(project, order: int) -> Image.Image:
    scene = project.scenes.get(order=order)
    if not scene.image:
        raise ValueError(f"Sahna {order} da rasm yo'q")
    return Image.open(scene.image.path).convert("RGB")


def cover(img: Image.Image, zoom: float = 1.0, fx: float = 0.5, fy: float = 0.5, ax: float = 0.5, ay: float = 0.5) -> Image.Image:
    """Fill 1280x720 from `img`, zoomed in, with the focus point (fx, fy in 0..1 of the picture) placed at (ax, ay) of the frame
    (the centre by default) as far as the edges allow."""
    base = max(W / img.width, H / img.height) * zoom
    big = img.resize((round(img.width * base), round(img.height * base)), Image.LANCZOS)
    left = min(max(round(fx * big.width - ax * W), 0), big.width - W)
    top = min(max(round(fy * big.height - ay * H), 0), big.height - H)
    return big.crop((left, top, left + W, top + H))


def punch(img: Image.Image) -> Image.Image:
    """More colour and contrast so a small thumbnail still pops."""
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    return ImageEnhance.Sharpness(img).enhance(1.4)


def vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    mask = Image.radial_gradient("L").resize((W, H))  # 0 centre -> 255 edge
    mask = mask.point(lambda v: int(max(0, v - 90) * strength * 1.6))
    return Image.composite(Image.new("RGB", (W, H), BLACK), img, mask)


def side_shade(img: Image.Image, side: str = "right", width: float = 0.55, alpha: int = 215) -> Image.Image:
    """Dark gradient on one side so the title stays readable."""
    ramp = Image.linear_gradient("L").rotate(90).resize((int(W * width), H))  # 255 at left -> 0 at right
    if side == "right":
        ramp = ImageOps.mirror(ramp)
    ramp = ramp.point(lambda v: int(v * alpha / 255))
    mask = Image.new("L", (W, H), 0)
    mask.paste(ramp, (W - ramp.width if side == "right" else 0, 0))
    return Image.composite(Image.new("RGB", (W, H), (8, 10, 26)), img, mask)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_FILE), size)


def split_lines(text: str, max_lines: int = 3, min_lines: int = 1) -> list[str]:
    """Break a short title into balanced lines (by words)."""
    words = text.upper().split()
    if len(words) <= 1 or max_lines <= 1:
        return [" ".join(words)]
    best, best_cost = [" ".join(words)], float("inf")
    for n in range(min(min_lines, len(words)), min(max_lines, len(words)) + 1):
        size = -(-len(words) // n)
        lines = [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
        cost = max(len(x) for x in lines) + 4 * (n - 1)
        if cost < best_cost:
            best, best_cost = lines, cost
    return best


def title_block(img: Image.Image, text: str, box: tuple[int, int, int, int], fill=YELLOW, align: str = "left",
                max_lines: int = 3, min_lines: int = 1) -> Image.Image:
    """Draw big outlined title text as large as fits `box` (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    lines = split_lines(text, max_lines, min_lines)
    size = 260
    while size > 40:
        font = _font(size)
        stroke = max(4, size // 11)
        widths = [font.getlength(line) for line in lines]
        line_h = size * 0.98
        if max(widths) + 2 * stroke <= x1 - x0 and line_h * len(lines) + stroke <= y1 - y0:
            break
        size -= 4
    draw = ImageDraw.Draw(img)
    total_h = line_h * len(lines)
    y = y0 + (y1 - y0 - total_h) / 2
    for line, w in zip(lines, widths):
        x = x0 if align == "left" else x0 + (x1 - x0 - w) / 2
        draw.text((x + stroke * 0.5, y + stroke * 0.7), line, font=font, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=fill, stroke_width=stroke, stroke_fill=BLACK)
        y += line_h
    return img


def badge(img: Image.Image, text: str, xy: tuple[int, int]) -> Image.Image:
    font = _font(64)
    w = int(font.getlength(text.upper())) + 56
    box = (xy[0], xy[1], xy[0] + w, xy[1] + 96)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=18, fill=RED, outline=WHITE, width=5)
    draw.text((xy[0] + 28, xy[1] + 8), text.upper(), font=font, fill=WHITE)
    return img


# ------------------------------------------------------------------ the three designs
def find_character(img: Image.Image) -> tuple[float, float]:
    """Where the main character is (x, y in 0..1), found from the colour of his brown fur tunic; centre if not found."""
    small = img.resize((192, 108))
    px = small.load()
    xs, ys = [], []
    for y in range(108):
        for x in range(192):
            r, g, b = px[x, y]
            if 95 <= r <= 165 and 55 <= g <= 105 and 20 <= b <= 70 and r - g >= 25 and g - b >= 15:
                xs.append(x)
                ys.append(y)
    if len(xs) < 40:
        return 0.5, 0.5
    xs.sort()
    ys.sort()
    return xs[len(xs) // 2] / 192, ys[len(ys) // 2] / 108


def design_hero(project, spec: dict) -> Image.Image:
    """The character big on the left, a dark panel and a huge yellow title on the right."""
    src = scene_picture(project, spec["hero"])
    fx, fy = (spec.get("fx"), spec.get("fy"))
    if fx is None or fy is None:
        cx, cy = find_character(src)
        fx, fy = (cx if fx is None else fx), (0.5 if fy is None else fy)
    big = punch(cover(src, spec.get("zoom", 1.12), fx, fy))
    bg = Image.new("RGB", (W, H), (10, 12, 30))  # dark panel the title sits on
    shift = int(W * spec.get("shift", 0.22))
    start, end = int(W * 0.40) + shift, int(W * 0.56) + shift  # fade the picture out (in its own coordinates) before the title panel
    feather = Image.new("L", (W, H), 255)
    fd = ImageDraw.Draw(feather)
    for x in range(start, min(end, W)):
        fd.line([(x, 0), (x, H)], fill=int(255 * (1 - (x - start) / (end - start))))
    if end < W:
        fd.rectangle((end, 0, W, H), fill=0)
    img = bg.copy()
    img.paste(big, (-shift, 0), feather)
    img = side_shade(img, "right", 0.46, 240)
    img = title_block(img, spec["text"], (int(W * 0.53), 70, W - 50, H - 70), min_lines=2)
    ImageDraw.Draw(img).rectangle((int(W * 0.53), H - 78, W - 50, H - 66), fill=RED)
    return img


def design_object(project, spec: dict) -> Image.Image:
    """The evidence (an object, a skeleton, a place) filling the frame, the title on a banner across the top."""
    img = cover(scene_picture(project, spec["fact"]), spec.get("zoom", 1.2), spec.get("fx", 0.5), spec.get("fy", 0.55))
    img = vignette(punch(img), 0.6)
    top = Image.linear_gradient("L").resize((W, 330)).transpose(Image.FLIP_TOP_BOTTOM).point(lambda v: int(v * 0.88))
    img.paste(Image.new("RGB", (W, 330), (6, 8, 20)), (0, 0), top)
    img = title_block(img, spec["text"], (50, 20, W - 50, 300), fill=WHITE, align="center", max_lines=2)
    if spec.get("badge"):
        img = badge(img, spec["badge"], (50, H - 140))
    ImageDraw.Draw(img).rectangle((0, 0, W - 1, H - 1), outline=YELLOW, width=10)
    return img


def design_split(project, spec: dict) -> Image.Image:
    """The character on one side, the evidence on the other, split by a bright diagonal, title in a ribbon below."""
    hero = scene_picture(project, spec["hero"])
    cx, cy = find_character(hero)
    left = punch(cover(hero, 1.12, spec.get("fx", cx), spec.get("fy", 0.5), ax=0.25))
    right = punch(cover(scene_picture(project, spec["fact"]), 1.15, spec.get("fx2", 0.5), 0.55))
    img = right.copy()
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(0, 0), (int(W * 0.56), 0), (int(W * 0.44), H), (0, H)], fill=255)
    img.paste(left, (0, 0), mask)
    draw = ImageDraw.Draw(img)
    draw.line([(int(W * 0.56), 0), (int(W * 0.44), H)], fill=YELLOW, width=14)
    ribbon = Image.new("RGBA", (W, 190), (8, 10, 26, 225))
    img = img.convert("RGBA")
    img.alpha_composite(ribbon, (0, H - 190))
    img = img.convert("RGB")
    return title_block(img, spec["text"], (60, H - 185, W - 60, H - 5), fill=YELLOW, align="center", max_lines=1)


BUILDERS = {"hero": design_hero, "object": design_object, "split": design_split}


def build_previews(project, specs: list[dict]) -> list[dict]:
    """Draw one 1280x720 JPEG per spec: {"design": hero|object|split, "text", "hero": order, "fact": order, ...}."""
    d = kit_dir(project)
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("preview_*.jpg"):
        old.unlink()
    out = []
    for i, spec in enumerate(specs, start=1):
        design = spec.get("design", DESIGNS[(i - 1) % 3])
        img = BUILDERS[design](project, spec)
        name = f"preview_{i}.jpg"
        img.convert("RGB").save(d / name, "JPEG", quality=92, subsampling=0)
        out.append({"file": name, "text": spec["text"], "design": design})
    save_kit(project, previews=out)
    return out
