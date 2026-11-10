"""Keep the recurring policy-watch job registered after every migrate."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def ensure_policy_schedule(sender, **kwargs) -> None:
    try:
        from .services.policy_watch import ensure_schedule

        ensure_schedule()
    except Exception as exc:  # noqa: BLE001 - never break migrate because of this
        logger.warning("Could not register policy-watch schedule: %s", exc)
