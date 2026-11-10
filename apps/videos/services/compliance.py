"""Per-video compliance check (prompt 5.10). Runs after script generation (phase 2)."""
from __future__ import annotations

import logging
from typing import Iterable, Literal

from pydantic import BaseModel, Field

from . import gemini_client

logger = logging.getLogger(__name__)

ORDER = {"pass": 0, "warning": 1, "fail": 2}


def worst_status(statuses: Iterable[str]) -> str:
    """Overall status = the worst item ('fail' > 'warning' > 'pass'); empty -> 'pass'."""
    worst = "pass"
    for s in statuses:
        s = (s or "pass").lower()
        if ORDER.get(s, 1) > ORDER[worst]:
            worst = s if s in ORDER else "warning"
    return worst


def can_auto_approve(status: str) -> bool:
    """auto-approve may skip the manual stop only for pass/warning - a fail always stops."""
    return status in ("pass", "warning")


class Finding(BaseModel):
    category: str = Field(description="Checklist item title")
    status: Literal["pass", "warning", "fail"]
    message: str = Field(description="Short reason in Uzbek; for problems include a concrete fix")


class ComplianceResult(BaseModel):
    findings: list[Finding]


def run_check(project) -> "object":
    """Ask Gemini to grade the script against the enabled checklist; store ComplianceCheck."""
    from ..models import ComplianceCheck, ComplianceRule, Project

    rules = list(ComplianceRule.objects.filter(enabled=True))
    script = project.script_json or {}
    narration = "\n".join(s.narration for s in project.scenes.all())
    past = "\n".join(f"- {t}" for t in Project.objects.exclude(pk=project.pk).values_list("topic", flat=True)[:200])
    checklist = "\n".join(f"{i}. {r.title}: {r.instruction}" for i, r in enumerate(rules, start=1))
    prompt = (
        "Review this YouTube explainer script against the checklist. For EACH checklist item return one finding "
        "with status pass/warning/fail and a short Uzbek explanation (with a concrete fix when not pass).\n\n"
        f"CHECKLIST:\n{checklist}\n\nMY PREVIOUS VIDEOS:\n{past or '- none'}\n\n"
        f"TITLE: {project.title or script.get('title', project.topic)}\n"
        f"DESCRIPTION: {project.description or script.get('description', '')}\n\nNARRATION:\n{narration[:30000]}"
    )
    result = gemini_client.generate_json(prompt, ComplianceResult, temperature=0.1)
    findings = [f.model_dump() for f in result.findings]
    status = worst_status(f["status"] for f in findings)
    check, _ = ComplianceCheck.objects.update_or_create(project=project, defaults={"status": status, "findings": findings})
    return check
