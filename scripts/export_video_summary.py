"""Writes VIDEOS_SUMMARY.txt at the repo root: every video made so far (explainer projects + music videos), so new videos
don't repeat old ones even on a fresh install where the database is empty.
Run: ./venv/Scripts/python manage.py shell -c "exec(open('scripts/export_video_summary.py', encoding='utf-8').read())"
"""
from pathlib import Path

from django.conf import settings

from apps.videos.models import MusicVideo, Project
from apps.videos.services import history, kit

L = ["VIDEOLAR XULOSASI (YotubeVideo)", "=" * 60,
     "Har bir yaratilgan video haqida qisqa ma'lumot. Yangi video oldingisiga o'xshab qolmasligi uchun shu fayl bilan solishtiring:",
     "mavzu, hook'ning birinchi gapi, bo'limlar, ishlatilgan ilmiy manbalar va kalit so'zlar.", ""]
done = {e["id"]: e for e in history.write_history()}
L += ["", "1. TUSHUNTIRUVCHI VIDEOLAR (ingliz / o'zbek)", "-" * 60]
for p in Project.objects.order_by("pk"):
    e = done.get(p.pk)
    k = kit.load_kit(p)
    niche = p.niche.name if p.niche else "-"
    L.append(f"\n#{p.pk} {p.title or p.topic}")
    L.append(f"  Nisha: {niche} | Holat: {p.status} | Yaratilgan: {p.created_at:%Y-%m-%d}"
             + (f" | Davomiyligi: {int(p.actual_duration_sec // 60)}:{int(p.actual_duration_sec % 60):02d}" if p.actual_duration_sec else ""))
    if k.get("titles"):
        L.append("  Sarlavhalar: " + " | ".join(k["titles"]))
    if e:
        if e["summary"]:
            L.append("  Mazmuni: " + e["summary"])
        if e["chapters"]:
            L.append("  Bo'limlar: " + "; ".join(e["chapters"]))
        if e["hook"]:
            L.append("  Hook: " + " / ".join(e["hook"]))
        if e["source_keys"]:
            L.append("  Manbalar: " + ", ".join(e["source_keys"]))
        L.append("  Kalit so'zlar: " + ", ".join(e["keywords"][:15]))
    else:
        first = p.scenes.order_by("order").first()
        if first:
            L.append("  Hook: " + first.narration)
    if k.get("tags"):
        L.append("  Teglar: " + ", ".join(k["tags"]))
L += ["", "", "2. MUSIQA VIDEOLARI (Calm Hours)", "-" * 60]
for m in MusicVideo.objects.order_by("pk"):
    mk = m.kit or {}
    L.append(f"\n#{m.pk} {m.title}")
    L.append(f"  Holat: {m.status} | Yaratilgan: {m.created_at:%Y-%m-%d}"
             + (f" | Davomiyligi: {int(m.actual_duration_sec // 60)} daq" if m.actual_duration_sec else "")
             + f" | Vokal: {m.vocals}")
    if mk.get("titles"):
        L.append("  Sarlavhalar: " + " | ".join(mk["titles"]))
    if m.music_prompt:
        L.append("  Musiqa prompti: " + " ".join(m.music_prompt.split())[:400])
    if m.flow_prompts:
        scenes = [(f.get("prompt") if isinstance(f, dict) else str(f)) for f in m.flow_prompts]
        L.append(f"  Klip sahnalari ({len(scenes)}): " + " || ".join(" ".join(s.split())[:160] for s in scenes))
    if mk.get("tags"):
        L.append("  Teglar: " + ", ".join(mk["tags"]) if isinstance(mk["tags"], list) else "  Teglar: " + str(mk["tags"]))
out = Path(settings.BASE_DIR) / "VIDEOS_SUMMARY.txt"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("yozildi:", out, len(L), "qator")
