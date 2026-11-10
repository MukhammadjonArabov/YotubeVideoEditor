"""File housekeeping helpers."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


def project_media_dir(project_id: int) -> Path:
    return Path(settings.MEDIA_ROOT) / "projects" / f"p{project_id}"


def delete_project_files(project) -> None:
    """Remove the project's media folder (only called when the user deletes a project)."""
    folder = project_media_dir(project.pk)
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)
        logger.info("Deleted media folder %s", folder)
