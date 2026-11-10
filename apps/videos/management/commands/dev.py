"""`python manage.py dev` - run the web server AND the django-q2 worker in one terminal.

Ctrl+C stops both. Works on Windows and Linux.
"""
from __future__ import annotations

import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from django.core.management.base import BaseCommand

MANAGE_PY = Path(__file__).resolve().parents[4] / "manage.py"


def _pump(proc: subprocess.Popen, prefix: str) -> None:
    """Copy a child's output to our stdout with a [web]/[worker] prefix."""
    assert proc.stdout is not None
    for line in iter(proc.stdout.readline, ""):
        sys.stdout.write(f"{prefix} {line}")
        sys.stdout.flush()


class Command(BaseCommand):
    help = "Run runserver + qcluster together (Ctrl+C stops both)."

    def add_arguments(self, parser):
        parser.add_argument("addrport", nargs="?", default="127.0.0.1:8000")

    def handle(self, *args, **opts):
        py = sys.executable
        # Apply pending migrations first, so new features never crash with "column does not exist".
        self.stdout.write("Ma'lumotlar bazasi yangilanmoqda (migrate)...")
        subprocess.run([py, str(MANAGE_PY), "migrate", "--noinput", "-v", "0"], check=False)
        commands = {
            "[web]   ": [py, "-u", str(MANAGE_PY), "runserver", opts["addrport"]],
            "[worker]": [py, "-u", str(MANAGE_PY), "qcluster"],
        }
        kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT, "text": True, "bufsize": 1}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        procs: list[subprocess.Popen] = []
        for prefix, cmd in commands.items():
            p = subprocess.Popen(cmd, **kwargs)
            threading.Thread(target=_pump, args=(p, prefix), daemon=True).start()
            procs.append(p)

        self.stdout.write(self.style.SUCCESS(
            f"Web: http://{opts['addrport']}/  +  background worker started. Press Ctrl+C to stop both."
        ))
        try:
            while all(p.poll() is None for p in procs):
                time.sleep(0.5)
            self.stderr.write("One of the processes exited - stopping the other.")
        except KeyboardInterrupt:
            self.stdout.write("\nStopping...")
        finally:
            for p in procs:
                if p.poll() is None:
                    if sys.platform == "win32":
                        p.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        p.terminate()
            for p in procs:
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
