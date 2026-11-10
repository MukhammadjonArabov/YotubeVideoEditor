"""Install a missing pip package into the *running* Python (the venv that runs
`manage.py dev`), so the user does not have to fix ModuleNotFoundError by hand."""
from __future__ import annotations

import importlib
import logging
import subprocess
import sys
import threading

logger = logging.getLogger(__name__)
_lock = threading.Lock()
_tried: set[str] = set()


def ensure_module(module: str, requirement: str) -> bool:
    """Import `module`; if missing, pip-install `requirement` once and retry. Returns True if importable."""
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        pass
    with _lock:
        if requirement not in _tried:
            _tried.add(requirement)
            logger.warning("Module %s missing - installing %s into %s", module, requirement, sys.executable)
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", requirement],
                               check=True, capture_output=True, timeout=600)
            except (subprocess.SubprocessError, OSError) as exc:
                logger.error("Auto-install of %s failed: %s", requirement, exc)
                return False
            importlib.invalidate_caches()
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        return False
