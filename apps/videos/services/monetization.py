"""Monetization check for every video (owner, 2026-11-01): runs without Gemini, on rules Claude refreshes weekly.

Rules live in niches/monetization_rules.json (YouTube YPP "inauthentic content" policy: template / mass-produced
content, distressing content, AI personas giving health / legal / financial advice; AI disclosure). Each check returns
findings {category, status pass|warning|fail, message (Uzbek, with a fix)} and is saved to
media/monetization/<kind>_<id>.json so the site and Claude can read the last result.
"""
from __future__ import annotations

import json
import re
from datetime import timedelta
from difflib import SequenceMatcher
from pathlib import Path

from django.conf import settings

from .compliance import worst_status

RULES_PATH = Path(settings.BASE_DIR) / "niches" / "monetization_rules.json"


def rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def _f(category: str, status: str, message: str) -> dict:
    return {"category": category, "status": status, "message": message}


def _hits(text: str, words: list[str]) -> list[str]:
    low = f" {text.lower()} "
    return sorted({w.strip() for w in words if w in low})


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def _common(text: str, r: dict, label: str, body: str = "", music: bool = True) -> list[dict]:
    """Checks shared by both kinds. Promises are looked for in the packaging (title, description, tags); advice and
    distress also in the narration `body`, where history words like "doctor" are fine."""
    out = []
    hard = _hits(text, r["health_claims"])
    soft = _hits(text, r["health_soft"])
    text = f"{text} {body}"
    if hard:
        out.append(_f("Sog'liq va'dalari", "fail", f"{label}da tibbiy va'da bor: {', '.join(hard)}. Olib tashlang: "
                      "'davolaydi', 'melatonin', '100%' kabi so'zlar AI kontentni 'sog'liq maslahati' toifasiga kiritadi."))
    elif soft:
        out.append(_f("Sog'liq va'dalari", "warning", f"{label}da sog'liq mavzusi bor ({', '.join(soft)}). Va'da bermang "
                      "(\"for anxiety\" o'rniga \"for calm nights\" kabi), faqat kayfiyatni ayting."))
    else:
        out.append(_f("Sog'liq va'dalari", "pass", "Tibbiy va'da yo'q."))
    adv = _hits(text, r["advice"])
    out.append(_f("Maslahat (tibbiy/huquqiy/moliyaviy)", "fail" if adv else "pass",
                  f"Maslahat iboralari: {', '.join(adv)}. Olib tashlang." if adv else "Maslahat yo'q."))
    dis = _hits(text, r["distress"])
    out.append(_f("Bezovta qiluvchi kontent", "fail" if dis else "pass",
                  f"Bezovta qiluvchi so'zlar: {', '.join(dis)}." if dis else "Bezovta qiluvchi narsa yo'q."))
    cp = _hits(text, r["style_copy"]) if music else []
    out.append(_f("Boshqa artistdan nusxa", "fail" if cp else "pass",
                  f"Nusxa iboralari: {', '.join(cp)}. Original tasvirlang." if cp else "Nusxa ko'chirish iborasi yo'q."))
    return out


def check_music(mv) -> dict:
    from ..models import MusicVideo

    r = rules()
    kit = mv.kit or {}
    titles = kit.get("titles") or [mv.title]
    desc = kit.get("description", "")
    tags = ", ".join(kit.get("tags", []))
    flows = " ".join(f.get("prompt", "") for f in (mv.flow_prompts or []))
    text = " ".join([*titles, desc, tags, mv.music_prompt or ""])
    out = _common(text, r, "Sarlavha/tavsif/prompt")

    low = desc.lower()
    out.append(_f("AI oshkor qilish", "pass" if any(w in low for w in r["ai_disclosure_words"]) else "fail",
                  "Tavsifda AI ishlatilgani yozilgan. Yuklashda Studio'da 'Altered or synthetic content: Yes' belgilang."
                  if any(w in low for w in r["ai_disclosure_words"]) else
                  "Tavsifda AI (ElevenLabs, Google Flow) ishlatilgani yozilmagan. Qo'shing va Studio'da belgini qo'ying."))

    others = MusicVideo.objects.exclude(pk=mv.pk)
    worst, who = 0.0, ""
    for o in others:
        s = max(_similar(mv.title, o.title), _similar(mv.music_prompt, o.music_prompt),
                _similar(flows, " ".join(f.get("prompt", "") for f in (o.flow_prompts or []))))
        if s > worst:
            worst, who = s, o.title
    st = "fail" if worst >= r["similarity_fail"] else "warning" if worst >= r["similarity_warn"] else "pass"
    out.append(_f("Takroriy/shablon emasligi", st, f"Eng o'xshash video: \"{who}\" ({worst:.0%}). " +
                  ("Mavzu, sahna va musiqani ancha o'zgartiring." if st != "pass" else "Yetarlicha farq qiladi.")))

    since = (mv.created_at or mv.updated_at) - timedelta(days=7)
    week = MusicVideo.objects.filter(created_at__gte=since, created_at__lte=mv.created_at).count()
    out.append(_f("Yuklash tezligi", "warning" if week > r["music_max_per_week"] else "pass",
                  f"7 kunda {week} ta musiqa video. " + ("Ommaviy ishlab chiqarishdek ko'rinmasligi uchun haftasiga "
                  f"{r['music_max_per_week']} tadan oshirmang." if week > r["music_max_per_week"] else "Me'yorda.")))

    n = mv.clips.count()
    out.append(_f("Vizual xilma-xillik", "pass" if n >= r["min_clips"] else "warning",
                  f"{n} ta klip." + ("" if n >= r["min_clips"] else f" Kamida {r['min_clips']} ta har xil klip qo'ying.")))
    out.append(_f("Ijodiy hissa", "pass" if mv.flow_prompts and len(mv.music_prompt or "") > 200 else "warning",
                  "Har bir video o'z g'oyasi, prompti va sahnalari bilan." if mv.flow_prompts else "Prompt va sahnalar yozilmagan."))
    bad_t = [t for t in titles if len(t) >= 100]
    out.append(_f("Metadata", "warning" if bad_t or len(tags) > 500 else "pass",
                  "Sarlavha 100 yoki teglar 500 belgidan oshmasin." if bad_t or len(tags) > 500 else "Sarlavha va teglar me'yorda."))
    return _save("music", mv.pk, mv.title, out, r)


def _factcheck_for(title: str) -> Path | None:
    for p in (Path(settings.BASE_DIR) / "scripts").glob("*.factcheck.md"):
        head = p.read_text(encoding="utf-8", errors="ignore")[:400]
        if title and _similar(title, re.sub(r"^#\s*Fact-check:\s*", "", head.splitlines()[0] if head else "")) > 0.8:
            return p
    return None


def check_project(project) -> dict:
    from ..models import Project

    r = rules()
    narration = " ".join(s.narration for s in project.scenes.all())
    title = project.title or project.topic
    out = _common(" ".join([title, project.description or ""]), r, "Sarlavha/tavsif", body=narration, music=False)

    script = project.script_json or {}
    src = script.get("sources") or []
    fc = _factcheck_for(title)
    out.append(_f("Faktlar manbasi", "pass" if src and fc else "warning",
                  f"{len(src)} ta manba" + (f", fact-check: {fc.name}." if fc else "; fact-check fayli topilmadi.")))
    minutes = (project.actual_duration_sec or project.target_duration_sec or 0) / 60
    out.append(_f("Uzunlik va chuqurlik", "pass" if minutes >= r["explainer_min_minutes"] else "warning",
                  f"{minutes:.1f} daqiqa."))
    worst, who = 0.0, ""
    for o in Project.objects.exclude(pk=project.pk).only("title", "topic"):
        s = _similar(title, o.title or o.topic)
        if s > worst:
            worst, who = s, o.title or o.topic
    st = "fail" if worst >= r["similarity_fail"] else "warning" if worst >= r["similarity_warn"] else "pass"
    out.append(_f("Takroriy/shablon emasligi", st, f"Eng o'xshash sarlavha: \"{who}\" ({worst:.0%})."))
    hook = " ".join(s.narration for s in project.scenes.all()[:3]).lower()
    out.append(_f("Hook xilma-xilligi", "warning" if hook.startswith(("imagine", "have you ever")) else "pass",
                  "Hook 'Imagine/Have you ever' bilan boshlanadi: shablon ko'rinadi." if hook.startswith(("imagine", "have you ever"))
                  else "Hook o'ziga xos."))
    subs = narration.lower().count("subscribe")
    out.append(_f("CTA me'yori", "pass" if subs <= 2 else "warning", f"'subscribe' {subs} marta."))
    return _save("project", project.pk, title, out, r)


def _save(kind: str, pk: int, title: str, findings: list[dict], r: dict) -> dict:
    report = {"kind": kind, "id": pk, "title": title, "rules_updated": r["updated"],
              "status": worst_status(f["status"] for f in findings), "findings": findings}
    folder = Path(settings.MEDIA_ROOT) / "monetization"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{kind}_{pk}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def last_report(kind: str, pk: int) -> dict | None:
    p = Path(settings.MEDIA_ROOT) / "monetization" / f"{kind}_{pk}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
