"""Template context shared by every page."""
from __future__ import annotations

from django.db.utils import OperationalError, ProgrammingError


def policy_banner(request) -> dict:
    """Unreviewed policy change notes show as a banner across the app (prompt 5.9)."""
    from .models import PolicyChangeNote

    try:
        count = PolicyChangeNote.objects.filter(reviewed=False).count()
    except (OperationalError, ProgrammingError):  # before first migrate
        count = 0
    from .models import Niche

    try:
        niche = Niche.active()
    except (OperationalError, ProgrammingError):
        niche = None
    return {"unreviewed_policy_notes": count, "active_niche": niche}
