"""
Django settings for the AutoExplainer project (YotubeVideo).

All secrets and machine-specific values come from `.env` (see `.env.example`).
Paths are built with pathlib so the project runs on Windows and Linux.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    TTS_PROVIDER=(str, "edge"),
    EDGE_TTS_VOICE=(str, "en-US-AndrewMultilingualNeural"),
    FFMPEG_PATH=(str, "ffmpeg"),
    POLICY_CHECK_INTERVAL_DAYS=(int, 7),
    MAX_IMAGES_PER_PROJECT=(int, 100),
)
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    # parse_comments=True: allow "KEY=value  # comment" lines in .env
    environ.Env.read_env(str(_env_file), parse_comments=True)
    # ...and drop the spaces that were left before such a comment.
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _key = _line.split("=", 1)[0].strip()
        if "=" in _line and not _key.startswith("#") and _key in os.environ:
            os.environ[_key] = os.environ[_key].strip()

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_q",
    "apps.videos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database: SQLite by default, PostgreSQL (or anything) if DATABASE_URL is set ---
def _use_system_libpq() -> None:
    """Windows: psycopg-binary's bundled DLL can be blocked by Smart App Control ("An Application Control
    policy has blocked this file"). Use psycopg's pure-Python mode with the signed libpq.dll that ships
    with PostgreSQL instead. PG_BIN in .env overrides the auto-detected PostgreSQL bin folder."""
    import glob

    if os.name != "nt" or os.environ.get("PSYCOPG_IMPL"):
        return
    pg_bin = env("PG_BIN", default="")
    if not pg_bin:
        found = sorted(glob.glob(r"C:\Program Files\PostgreSQL\*\bin"),
                       key=lambda p: int(Path(p).parent.name) if Path(p).parent.name.isdigit() else 0)
        pg_bin = found[-1] if found else ""
    if pg_bin and (Path(pg_bin) / "libpq.dll").exists():
        os.environ["PATH"] = pg_bin + os.pathsep + os.environ.get("PATH", "")
        os.environ["PSYCOPG_IMPL"] = "python"


if env("DATABASE_URL", default=""):
    if env("DATABASE_URL").startswith(("postgres", "pgsql")):
        _use_system_libpq()
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            # Longer lock timeout: web server and qcluster share one SQLite file.
            "OPTIONS": {"timeout": 30},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"  # UI language (the videos themselves are narrated in English)
TIME_ZONE = env("TIME_ZONE", default="Asia/Tashkent")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Everything the app writes stays on the project drive (C: is full): temp files of voice-over / render jobs and
# the downloaded speech model (faster-whisper) live inside the project folder.
TEMP_DIR = BASE_DIR / "tmp"
TEMP_DIR.mkdir(exist_ok=True)
tempfile.tempdir = str(TEMP_DIR)
os.environ.setdefault("HF_HOME", str(BASE_DIR / "models" / "huggingface"))


def _flow_token() -> str:
    """Shared secret between the Chrome extension (flow_extension/) and the local API; shown on the Flow page."""
    import secrets

    token = os.environ.get("FLOW_API_TOKEN", "").strip()
    if token:
        return token
    f = TEMP_DIR / "flow_token.txt"
    if not f.exists():
        f.write_text(secrets.token_urlsafe(24), encoding="utf-8")
    return f.read_text(encoding="utf-8").strip()


FLOW_API_TOKEN = _flow_token()
FLOW_MAX_ATTEMPTS = 2  # automatic tries per scene (every try spends Flow credits)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Bulk image upload: a long video has up to MAX_IMAGES_PER_PROJECT pictures in one request.
DATA_UPLOAD_MAX_NUMBER_FILES = 300
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# --- Background jobs: django-q2 with the ORM broker (no Redis/Celery needed) ---
Q_CLUSTER = {
    "name": "autoexplainer",
    "workers": 1,  # low-spec laptop: one worker is enough
    "recycle": 50,
    "timeout": 3600,  # rendering can take a while
    "retry": 3700,  # must be > timeout
    "max_attempts": 1,
    "queue_limit": 10,
    "orm": "default",
    "catch_up": False,
    "poll": 1,
}

# --- External services (read from .env, never logged) ---
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
# The owner stopped using Gemini (2026-10-30): False makes every Gemini step report "not configured",
# so callers skip it (image QA) or Claude does the job by hand (director marks, compliance).
GEMINI_ENABLED = env.bool("GEMINI_ENABLED", default=True)
GEMINI_TEXT_MODEL = env("GEMINI_TEXT_MODEL", default="")
# Tried in order when the main model is overloaded (503) or rate-limited (429).
GEMINI_FALLBACK_MODELS = env("GEMINI_FALLBACK_MODELS", default="gemini-3.5-flash-lite")
GEMINI_IMAGE_MODEL = env("GEMINI_IMAGE_MODEL", default="")
YOUTUBE_API_KEY = env("YOUTUBE_API_KEY", default="")
TTS_PROVIDER = env("TTS_PROVIDER")
EDGE_TTS_VOICE = env("EDGE_TTS_VOICE")
EDGE_TTS_RATE = env("EDGE_TTS_RATE", default="+0%")  # e.g. +5% for a slightly faster narrator
GEMINI_TTS_MODEL = env("GEMINI_TTS_MODEL", default="")
GEMINI_TTS_VOICE = env("GEMINI_TTS_VOICE", default="")
ELEVENLABS_API_KEY = env("ELEVENLABS_API_KEY", default="")
ELEVENLABS_VOICE_ID = env("ELEVENLABS_VOICE_ID", default="nPczCjzI2devNBz1zQrb")  # Brian (premade documentary voice)
# eleven_v3 understands emotion tags ([whispers], [excited]...); eleven_multilingual_v2 is flatter but cheaper to retry.
ELEVENLABS_MODEL = env("ELEVENLABS_MODEL", default="eleven_v3")
FFMPEG_PATH = env("FFMPEG_PATH")

# Image generation: cloudflare (free daily quota) | gemini (paid, phase 5)
IMAGE_PROVIDER = env("IMAGE_PROVIDER", default="cloudflare").strip().lower()
CLOUDFLARE_ACCOUNT_ID = env("CLOUDFLARE_ACCOUNT_ID", default="")
CLOUDFLARE_API_TOKEN = env("CLOUDFLARE_API_TOKEN", default="")
CLOUDFLARE_IMAGE_MODEL = env("CLOUDFLARE_IMAGE_MODEL", default="@cf/black-forest-labs/flux-1-schnell")
CLOUDFLARE_FACT_SIZE = env("CLOUDFLARE_FACT_SIZE", default="")  # e.g. 1024x576: cheaper pictures for scenes without the hero
CLOUDFLARE_FACT_MODEL = env("CLOUDFLARE_FACT_MODEL", default="")  # cheap model for scenes without a hero reference
CLOUDFLARE_IMAGE_STEPS = env.int("CLOUDFLARE_IMAGE_STEPS", default=4)  # 1..8, more = nicer but slower
# Backups used automatically when the main provider's free quota runs out (comma separated).
REPLICATE_API_TOKEN = env("REPLICATE_API_TOKEN", default="")
REPLICATE_MODEL = env("REPLICATE_MODEL", default="black-forest-labs/flux-schnell")
RUNWARE_API_KEY = env("RUNWARE_API_KEY", default="")
RUNWARE_MODEL = env("RUNWARE_MODEL", default="runware:100@1")  # AIR id from the model's Runware page (default: FLUX.1 schnell)
RUNWARE_STEPS = env.int("RUNWARE_STEPS", default=0)  # 0 = the model's own default
RUNWARE_USE_REFERENCES = env.bool("RUNWARE_USE_REFERENCES", default=False)  # send the hero picture (models that accept references)
IMAGE_FALLBACK_PROVIDERS = env("IMAGE_FALLBACK_PROVIDERS", default="")
POLICY_CHECK_INTERVAL_DAYS = env("POLICY_CHECK_INTERVAL_DAYS")

# --- AutoExplainer app settings ---
MAX_IMAGES_PER_PROJECT = env("MAX_IMAGES_PER_PROJECT")
# Speed: how many scenes are worked on at the same time.
IMAGE_CONCURRENCY = env.int("IMAGE_CONCURRENCY", default=3)  # parallel image requests
TTS_CONCURRENCY = env.int("TTS_CONCURRENCY", default=4)  # parallel voice-over requests
RENDER_WORKERS = env.int("RENDER_WORKERS", default=0)  # parallel ffmpeg clips; 0 = half the CPU threads
# "Rejissyor": after the script, Gemini marks emotion / camera / SFX / music for every scene.
DIRECTOR_ENABLED = env.bool("DIRECTOR_ENABLED", default=True)
# Animated "Subscribe" button: once mid-video (first calm scene after N seconds) and once at the end.
SUBSCRIBE_CTA = env.bool("SUBSCRIBE_CTA", default=True)
SUBSCRIBE_CTA_AT_SEC = env.int("SUBSCRIBE_CTA_AT_SEC", default=40)
SUBSCRIBE_CTA_END = env.bool("SUBSCRIBE_CTA_END", default=True)
# Word timings from the audio (faster-whisper) when the voice provider gives none (ElevenLabs v3, Gemini, clones).
ALIGN_MISSING_TIMINGS = env.bool("ALIGN_MISSING_TIMINGS", default=True)
VIGNETTE = env.bool("VIGNETTE", default=True)  # very light darkening of the frame corners
WHISPER_MODEL = env("WHISPER_MODEL", default="base.en")  # tiny.en = faster, small.en = more exact
# Scripts written by Claude in Claude Code (see CLAUDE.md): max share of 5-word phrases shared with an older script.
MAX_SCRIPT_OVERLAP = env.float("MAX_SCRIPT_OVERLAP", default=0.08)
DEFAULT_SECONDS_PER_IMAGE = 8
WORDS_PER_MINUTE = 150

DEFAULT_STYLE_GUIDE = (
    "hand-drawn flat 2D cartoon, simple stick-figure characters with large round white heads, "
    "simple expressive faces, thin black line limbs, clean black outlines, bright flat colors, "
    "natural outdoor or simple indoor backgrounds with soft blue sky, 16:9, no text, no watermark, "
    "consistent character design across all scenes"
)

# Fixed vocabularies (used by script generation, auto-tagging and matching).
SFX_TAGS = ["whoosh", "ding", "riser", "pop", "boing", "swoosh", "impact", "click"]
MUSIC_MOODS = [
    "calm", "mysterious", "playful", "tense", "wholesome", "epic", "sad", "quirky",
]

# Scene transitions. The first five are the main ones (Scene.Transition); the rest are extra xfade
# styles kept for hand-picking. "cut" = no xfade (hard cut).
TRANSITIONS = [
    "cut", "crossfade", "whip", "dip_to_black", "flash",
    "smoothleft", "smoothright", "zoomin", "wipeleft", "wiperight", "slideup", "slidedown", "circleopen", "pixelize",
]
JARRING_TRANSITIONS = ["pixelize"]  # used at most once per video
# SFX level relative to full scale before the final -14 LUFS normalization (voice sits ~6-10 dB above).
SFX_GAIN_DB = env.float("SFX_GAIN_DB", default=-8.0)

# Uzbek display names for the UI
SFX_LABELS = {
    "whoosh": "Vush (tez o'tish)", "ding": "Ding", "riser": "Kuchayib boruvchi", "pop": "Pop",
    "boing": "Boing (kulgili)", "swoosh": "Svush", "impact": "Zarba", "click": "Chiq",
}
TRANSITION_LABELS = {
    "cut": "Keskin kesish", "crossfade": "Crossfade", "whip": "Whip (tez surilish + whoosh)",
    "dip_to_black": "Qora orqali", "flash": "Oq chaqnash", "wipeleft": "Chapga surish",
    "wiperight": "O'ngga surish", "slideup": "Yuqoriga siljish", "slidedown": "Pastga siljish",
    "circleopen": "Doira ochilishi", "pixelize": "Piksellash", "smoothleft": "Silliq chapga",
    "smoothright": "Silliq o'ngga", "zoomin": "Zoom bilan kirish",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "loggers": {
        "apps": {"handlers": ["console"], "level": "INFO"},
    },
}
