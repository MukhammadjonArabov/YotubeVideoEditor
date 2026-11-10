"""Data model for AutoExplainer. See README / prompt section 4."""
from __future__ import annotations

from pathlib import PurePosixPath

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------- upload paths
# FileField names are stored with "/" by Django on every OS; the storage backend
# converts them to native paths, so PurePosixPath is correct here.

def _project_dir(project_id: int | None) -> PurePosixPath:
    return PurePosixPath("projects") / f"p{project_id or 'new'}"


def scene_image_path(instance: "Scene", filename: str) -> str:
    return str(_project_dir(instance.project_id) / "images" / f"scene_{instance.order:03d}.png")


def scene_video_path(instance: "Scene", filename: str) -> str:
    ext = PurePosixPath(filename).suffix or ".mp4"
    return str(_project_dir(instance.project_id) / "video" / f"scene_{instance.order:03d}{ext}")


def scene_audio_path(instance: "Scene", filename: str) -> str:
    ext = PurePosixPath(filename).suffix or ".mp3"
    return str(_project_dir(instance.project_id) / "audio" / f"scene_{instance.order:03d}{ext}")


def scene_clip_path(instance: "Scene", filename: str) -> str:
    return str(_project_dir(instance.project_id) / "clips" / f"scene_{instance.order:03d}.mp4")


def project_video_path(instance: "Project", filename: str) -> str:
    return str(_project_dir(instance.pk) / "final" / PurePosixPath(filename).name)


def thumbnail_path(instance: "ThumbnailOption", filename: str) -> str:
    return str(_project_dir(instance.project_id) / "thumbnails" / PurePosixPath(filename).name)


# ---------------------------------------------------------------- niche
class Niche(models.Model):
    """The content direction every video, suggestion and style follows. For now there is one."""

    name = models.CharField("Nomi", max_length=120)
    name_en = models.CharField("Inglizcha nomi", max_length=120, blank=True)
    description = models.TextField("Tavsif", blank=True)
    audience = models.TextField("Tomoshabin", blank=True)
    tone = models.TextField("Ohang va uslub", blank=True)
    title_formula = models.TextField("Sarlavha formulasi", blank=True)
    content_pillars = models.TextField("Asosiy mavzu yo'nalishlari (har qatorda bittadan)", blank=True)
    avoid_topics = models.TextField("Qochiladigan mavzular (har qatorda bittadan)", blank=True)
    originality_rules = models.TextField("O'ziga xoslik qoidalari", blank=True)
    style_guide = models.TextField("Rasm uslubi", blank=True)
    character_description = models.TextField("Asosiy personaj tavsifi", blank=True)
    character_reference = models.ImageField(
        "Personaj namunasi (rasm)", upload_to="niche/", blank=True,
        help_text="Asosiy qahramonning bitta aniq rasmi: har bir sahna shunga solishtiriladi",
    )
    default_minutes = models.FloatField("Standart davomiylik (daqiqa)", default=9)
    default_seconds_per_image = models.PositiveIntegerField("Standart: har rasm necha soniya", default=8)
    default_mood = models.CharField("Standart musiqa kayfiyati", max_length=40, default="mysterious")
    slug = models.SlugField("Havola nomi", max_length=60, blank=True, default="")
    emoji = models.CharField("Belgi", max_length=8, default="🎬")
    language = models.CharField("Video tili (en, uz)", max_length=8, default="en")
    tts_voice = models.CharField("Ovoz (Edge TTS nomi, bo'sh = umumiy)", max_length=80, blank=True)
    words_per_minute = models.PositiveIntegerField("Nutq tezligi (so'z/daqiqa)", default=150)
    realistic = models.BooleanField("Fotorealistik rasmlar (qahramonsiz)", default=False)
    kind = models.CharField("Turi", max_length=8, default="video", choices=[("video", "Tushuntirish videolari"), ("music", "Musiqa videolari")])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_active", "name"]

    def __str__(self) -> str:
        return self.name

    @classmethod
    def active(cls) -> "Niche | None":
        return cls.objects.filter(is_active=True).first()

    def lines(self, field: str) -> list[str]:
        return [x.strip(" -•\t") for x in (getattr(self, field) or "").splitlines() if x.strip(" -•\t")]

    def prompt_brief(self) -> str:
        """Compact English brief injected into every Gemini prompt."""
        parts = [
            f"Niche: {self.name_en or self.name}",
            f"Audience: {self.audience}" if self.audience else "",
            f"Tone: {self.tone}" if self.tone else "",
            f"Title formula: {self.title_formula}" if self.title_formula else "",
            "Content pillars: " + "; ".join(self.lines("content_pillars")) if self.content_pillars else "",
            "Avoid: " + "; ".join(self.lines("avoid_topics")) if self.avoid_topics else "",
            f"Originality rules: {self.originality_rules}" if self.originality_rules else "",
        ]
        return "\n".join(p for p in parts if p)


# ---------------------------------------------------------------- research
class ChannelSource(models.Model):
    class State(models.TextChoices):
        NEW = "new", "Yangi"
        WORKING = "working", "Tahlil qilinmoqda"
        READY = "ready", "Tayyor"
        FAILED = "failed", "Xato"

    niche = models.ForeignKey(Niche, null=True, blank=True, on_delete=models.SET_NULL, related_name="channels")
    name = models.CharField(max_length=200)
    youtube_channel_id = models.CharField(max_length=64, blank=True)
    handle_or_url = models.CharField(max_length=300)
    handle = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    subscriber_count = models.BigIntegerField(null=True, blank=True)
    view_count = models.BigIntegerField(null=True, blank=True)
    video_count = models.IntegerField(null=True, blank=True)
    uploads_playlist_id = models.CharField(max_length=64, blank=True)
    last_analyzed_at = models.DateTimeField(null=True, blank=True)
    style_notes = models.TextField(blank=True)
    state = models.CharField(max_length=16, choices=State.choices, default=State.NEW)
    progress_message = models.CharField(max_length=300, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ChannelVideo(models.Model):
    """A public video of a reference channel (for watching, stats and dedup)."""

    channel = models.ForeignKey(ChannelSource, on_delete=models.CASCADE, related_name="videos")
    youtube_id = models.CharField(max_length=20)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    duration_sec = models.PositiveIntegerField(default=0)
    view_count = models.BigIntegerField(default=0)
    like_count = models.BigIntegerField(default=0)
    comment_count = models.BigIntegerField(default=0)
    thumbnail_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ["-published_at"]
        unique_together = [("channel", "youtube_id")]

    def __str__(self) -> str:
        return self.title

    @property
    def duration_label(self) -> str:
        m, s = divmod(self.duration_sec, 60)
        return f"{m}:{s:02d}"


class SuggestedTopic(models.Model):
    class Status(models.TextChoices):
        SUGGESTED = "suggested", "Taklif"
        USED = "used", "Ishlatilgan"
        DISMISSED = "dismissed", "Rad etilgan"

    # Empty for topics you add by hand on the "Yangi video" page.
    channel = models.ForeignKey(ChannelSource, null=True, blank=True, on_delete=models.CASCADE, related_name="suggestions")
    topic_text = models.CharField(max_length=300)
    rationale = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUGGESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.topic_text

    @property
    def is_manual(self) -> bool:
        return self.channel_id is None


# ---------------------------------------------------------------- media library
class MusicTrack(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="library/music/")
    duration = models.FloatField(default=0)
    mood_tags = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=100, default="youtube_audio_library", blank=True)
    license_note = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class SoundEffect(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="library/sfx/")
    tags = models.JSONField(default=list, blank=True)
    duration = models.FloatField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------- projects
class Project(models.Model):
    """Permanent record of every video made. Never hard-deleted by the pipeline."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        SCRIPT_READY = "script_ready", "Ssenariy tayyor"
        APPROVED = "approved", "Tasdiqlandi"
        GENERATING_ASSETS = "generating_assets", "Rasm va ovoz"
        RENDERING = "rendering", "Montaj"
        DONE = "done", "Tayyor"
        FAILED = "failed", "Xato"

    # Order used for the progress bar.
    PIPELINE_STEPS = [
        Status.DRAFT, Status.SCRIPT_READY, Status.APPROVED,
        Status.GENERATING_ASSETS, Status.RENDERING, Status.DONE,
    ]
    # While in one of these, a background job is (or should be) running.
    BUSY_STATUSES = {Status.APPROVED, Status.GENERATING_ASSETS, Status.RENDERING}

    TTS_CHOICES = [("edge", "Edge TTS (bepul)"), ("gemini", "Gemini TTS"), ("elevenlabs", "ElevenLabs")]

    niche = models.ForeignKey(Niche, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects")
    topic = models.CharField(max_length=300)
    topic_hash = models.CharField(max_length=64, db_index=True, blank=True)
    source_suggestion = models.ForeignKey(
        SuggestedTopic, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects"
    )
    target_duration_sec = models.PositiveIntegerField(default=300)
    seconds_per_image = models.PositiveIntegerField(default=8)
    tts_provider = models.CharField(max_length=20, choices=TTS_CHOICES, default="edge")
    auto_approve = models.BooleanField(default=False)
    style_guide = models.TextField(blank=True, help_text="Image style guide; empty = default from settings")
    # Per-video art style (e.g. an anime video in the stickman niche): empty = the niche's hero.
    character_override = models.TextField(blank=True, help_text="Hero description for this video only")
    character_reference_override = models.ImageField(upload_to="projects/refs/", blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_working = models.BooleanField(default=False, help_text="A background job is running")
    progress_message = models.CharField(max_length=300, blank=True)

    title = models.CharField(max_length=300, blank=True)
    # Claude workflow (CLAUDE.md): your idea in Uzbek -> enriched Uzbek concept -> English script
    idea = models.TextField("G'oya (sizning so'zlaringiz)", blank=True)
    concept = models.TextField("Konsepsiya (o'zbekcha, tasdiqlangan)", blank=True)
    script_author = models.CharField(max_length=20, blank=True, help_text="claude | gemini | upload")
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    script_json = models.JSONField(null=True, blank=True)
    final_video = models.FileField(upload_to=project_video_path, blank=True)
    preview_video = models.FileField(upload_to=project_video_path, blank=True)
    actual_duration_sec = models.FloatField(null=True, blank=True)
    music_track = models.ForeignKey(
        MusicTrack, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    has_unrendered_changes = models.BooleanField(
        default=False, help_text="Edited after the last render; a re-render is needed"
    )
    image_cost = models.FloatField(default=0, help_text="USD spent on this project's pictures (paid providers)")
    image_cost_count = models.PositiveIntegerField(default=0, help_text="Pictures counted in image_cost")
    image_model = models.CharField(
        max_length=120, blank=True, help_text="Runware model id for this project's pictures (empty = .env default)"
    )
    flow_character = models.CharField(
        max_length=60, blank=True, help_text="Name of the hero in Flow's Characters section (e.g. main_hero)"
    )
    flow_auto_render = models.BooleanField(
        default=False, help_text="When the Flow queue is empty, make the video (voice + render) automatically, once"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"#{self.pk} {self.topic}"

    def save(self, *args, **kwargs):
        from .services.topics import topic_hash

        self.topic_hash = topic_hash(self.topic)
        super().save(*args, **kwargs)

    # ---- helpers used by templates
    @property
    def target_minutes(self) -> float:
        return round(self.target_duration_sec / 60, 1)

    @property
    def effective_style_guide(self) -> str:
        if self.style_guide:
            return self.style_guide
        if self.niche and self.niche.style_guide:
            return self.niche.style_guide
        return settings.DEFAULT_STYLE_GUIDE

    @property
    def character_description(self) -> str:
        if self.character_override:
            return self.character_override
        return (self.niche.character_description if self.niche else "") or ""

    @property
    def step_index(self) -> int:
        try:
            return self.PIPELINE_STEPS.index(self.status)
        except ValueError:  # failed
            return -1

    @property
    def is_busy(self) -> bool:
        """True only while a background job really runs (jobs set is_working)."""
        return self.is_working

    @property
    def duration_off_pct(self) -> float | None:
        if not self.actual_duration_sec or not self.target_duration_sec:
            return None
        return round((self.actual_duration_sec - self.target_duration_sec) / self.target_duration_sec * 100, 1)

    def set_status(self, status: str, message: str = "") -> None:
        """Persist a status change without touching other fields (safe from background jobs)."""
        self.status = status
        self.progress_message = message
        fields = ["status", "progress_message", "updated_at"]
        if status == self.Status.DONE:
            self.finished_at = timezone.now()
            fields.append("finished_at")
        self.save(update_fields=fields)


class Scene(models.Model):
    class BeatType(models.TextChoices):
        HOOK = "hook", "Hook (ilgak)"
        BUILD = "build", "Rivojlanish"
        PUNCHLINE = "punchline", "Zarba nuqtasi"
        NORMAL = "normal", "Oddiy"

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        READY = "ready", "Tayyor"
        FAILED = "failed", "Xato"

    # ---- direction (filled by the "Rejissyor" step, editable by hand)
    class Emotion(models.TextChoices):
        NEUTRAL = "neutral", "😐 Neytral"
        CURIOUS = "curious", "🤔 Qiziquvchan"
        EXCITED = "excited", "🤩 Hayajonli"
        HAPPY = "happy", "😊 Quvnoq"
        FUNNY = "funny", "😄 Kulgili"
        SCARED = "scared", "😨 Qo'rqqan"
        TENSE = "tense", "😬 Taranglik"
        SAD = "sad", "😢 G'amgin"
        AWE = "awe", "😮 Hayrat"
        WHISPER = "whisper", "🤫 Pichirlash"
        SERIOUS = "serious", "🧐 Jiddiy"

    class Pace(models.TextChoices):
        SLOW = "slow", "Sekin"
        NORMAL = "normal", "Oddiy"
        FAST = "fast", "Tez"

    class CameraMove(models.TextChoices):
        NONE = "none", "Harakatsiz"
        SLOW_ZOOM_IN = "slow_zoom_in", "Sekin yaqinlashish"
        SLOW_ZOOM_OUT = "slow_zoom_out", "Sekin uzoqlashish"
        PAN_LEFT = "pan_left", "Chapga surilish"
        PAN_RIGHT = "pan_right", "O'ngga surilish"
        PUNCH_ZOOM = "punch_zoom", "Keskin zoom (punch)"
        SHAKE = "shake", "Silkinish"

    class Transition(models.TextChoices):
        CUT = "cut", "Keskin kesish"
        CROSSFADE = "crossfade", "Crossfade"
        WHIP = "whip", "Whip (tez surilish + whoosh)"
        DIP_TO_BLACK = "dip_to_black", "Qora orqali"
        FLASH = "flash", "Oq chaqnash"

    class MusicCue(models.TextChoices):
        CONTINUE = "continue", "Davom etadi"
        DROP_OUT = "drop_out", "Jimlik (musiqa to'xtaydi)"
        SWELL = "swell", "Kuchayish"
        CHANGE_MOOD = "change_mood", "Kayfiyat almashadi"
        STINGER = "stinger", "Stinger (qisqa urg'u)"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="scenes")
    order = models.PositiveIntegerField()
    narration = models.TextField()
    image_prompt = models.TextField(blank=True)
    beat_type = models.CharField(max_length=16, choices=BeatType.choices, default=BeatType.NORMAL)
    image = models.ImageField(upload_to=scene_image_path, blank=True)
    image_locked = models.BooleanField(
        default=False, help_text="Image uploaded by hand - never regenerate it automatically"
    )
    # Optional moving picture (Google Flow / Veo) for a hook scene; replaces the still image in the render.
    video = models.FileField(upload_to=scene_video_path, blank=True)
    audio = models.FileField(upload_to=scene_audio_path, blank=True)
    audio_duration = models.FloatField(null=True, blank=True)
    subtitle_words = models.JSONField(null=True, blank=True)
    clip = models.FileField(upload_to=scene_clip_path, blank=True)
    clip_hash = models.CharField(max_length=64, blank=True)
    # "" = automatic. Besides Transition, older xfade names (circleopen, smoothleft...) still work.
    transition_in = models.CharField(max_length=32, blank=True)
    emotion = models.CharField(max_length=16, choices=Emotion.choices, default=Emotion.NEUTRAL)
    intensity = models.PositiveSmallIntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(3)])
    pace = models.CharField(max_length=8, choices=Pace.choices, default=Pace.NORMAL)
    pause_after_ms = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(3000)])
    camera_move = models.CharField(max_length=16, choices=CameraMove.choices, blank=True,
                                   help_text="Empty = automatic rotation")
    # [{"tag": "whoosh", "offset_ms": 0, "gain_db": -8.0}, ...] - offset from the scene start
    sfx = models.JSONField(default=list, blank=True)
    music_cue = models.CharField(max_length=16, choices=MusicCue.choices, default=MusicCue.CONTINUE)
    on_screen_text = models.CharField(max_length=40, blank=True)
    # Where a fact scene's claim comes from (shown in the studio, used for fact-checking).
    fact_source = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["project", "order"]
        unique_together = [("project", "order")]

    def __str__(self) -> str:
        return f"{self.project_id}:{self.order}"

    @property
    def shows_hero(self) -> bool:
        """Hero scene (the main character is drawn) vs fact scene - read from the image prompt."""
        from .services.images import mentions_main_character

        return mentions_main_character(self.image_prompt)


def flow_result_path(instance: "FlowJob", filename: str) -> str:
    ext = PurePosixPath(filename).suffix or ".bin"
    return str(_project_dir(instance.project_id) / "flow" / f"job_{instance.pk}{ext}")


class FlowJob(models.Model):
    """One prompt for Google Flow, worked off by the Chrome extension (flow_extension/)."""

    class Kind(models.TextChoices):
        IMAGE = "image", "Rasm"
        VIDEO = "video", "Video (hook)"

    class Status(models.TextChoices):
        PENDING = "pending", "Navbatda"
        RUNNING = "running", "Flow'da"
        REVIEW = "review", "Tekshiring"
        DONE = "done", "Tayyor"
        FAILED = "failed", "Xato"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="flow_jobs")
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name="flow_jobs")
    kind = models.CharField(max_length=8, choices=Kind.choices)
    prompt = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    note = models.TextField(blank=True, help_text="Why it was retried / needs a look / failed")
    result = models.FileField(upload_to=flow_result_path, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["project", "kind", "scene__order"]

    def __str__(self) -> str:
        return f"{self.kind} #{self.scene.order} ({self.status})"


def music_audio_path(instance: "MusicVideo", filename: str) -> str:
    ext = PurePosixPath(filename).suffix or ".mp3"
    return f"music/m{instance.pk}/music{ext}"


def music_take_path(instance: "MusicTake", filename: str) -> str:
    import time

    ext = PurePosixPath(filename).suffix or ".mp3"
    return f"music/m{instance.video_id}/takes/take_{int(time.time() * 1000)}{ext}"


def music_clip_path(instance: "MusicClip", filename: str) -> str:
    ext = PurePosixPath(filename).suffix or ".mp4"
    return f"music/m{instance.video_id}/clip_{instance.order:02d}{ext}"


def music_final_path(instance: "MusicVideo", filename: str) -> str:
    return f"music/m{instance.pk}/final/{PurePosixPath(filename).name}"


class MusicVideo(models.Model):
    """A long relaxing-music video: one 3-10 minute track (made once) looped to 20-30 minutes, over 1-4 short
    animated clips (made in Google Flow) that are looped too, with Subscribe / Like animations."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        MUSIC_READY = "music_ready", "Musiqa tayyor"
        RENDERING = "rendering", "Montaj"
        DONE = "done", "Tayyor"
        FAILED = "failed", "Xato"

    title = models.CharField(max_length=200)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    is_working = models.BooleanField(default=False)
    progress_message = models.CharField(max_length=300, blank=True)
    error_message = models.TextField(blank=True)
    niche = models.ForeignKey("Niche", null=True, blank=True, on_delete=models.SET_NULL, related_name="music_videos")
    music_prompt = models.TextField(blank=True)
    music_minutes = models.PositiveSmallIntegerField(default=6, help_text="Length of the track to generate (3-10)")
    music_seconds = models.PositiveSmallIntegerField(default=210, help_text="Length of each generated take in seconds (60-300)")
    vocals = models.BooleanField(default=True, help_text="Wordless female vocals (not instrumental only)")
    flow_prompts = models.JSONField(default=list, blank=True)
    kit = models.JSONField(default=dict, blank=True)
    music_file = models.FileField(upload_to=music_audio_path, blank=True)
    music_duration = models.FloatField(default=0)
    target_minutes = models.PositiveSmallIntegerField(default=30, help_text="Length of the finished video")
    add_subscribe = models.BooleanField(default=True)
    add_like = models.BooleanField(default=True)
    cta_every_min = models.PositiveSmallIntegerField(default=5)
    final_video = models.FileField(upload_to=music_final_path, blank=True)
    actual_duration_sec = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class MusicTake(models.Model):
    """One generated (or uploaded) version of the track; the selected one is used for the video."""

    video = models.ForeignKey(MusicVideo, on_delete=models.CASCADE, related_name="takes")
    file = models.FileField(upload_to=music_take_path)
    duration = models.FloatField(default=0)
    prompt = models.TextField(blank=True)
    source = models.CharField(max_length=12, default="elevenlabs")  # elevenlabs | upload
    qc = models.JSONField(default=dict, blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class MusicClip(models.Model):
    video = models.ForeignKey(MusicVideo, on_delete=models.CASCADE, related_name="clips")
    order = models.PositiveSmallIntegerField(default=1)
    file = models.FileField(upload_to=music_clip_path)
    duration = models.FloatField(default=0)

    class Meta:
        ordering = ["order"]


class ThumbnailOption(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="thumbnails")
    image = models.ImageField(upload_to=thumbnail_path)
    is_selected = models.BooleanField(default=False)


# ---------------------------------------------------------------- policy & compliance
class PolicyDocument(models.Model):
    label = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    enabled = models.BooleanField(default=True)
    last_content_hash = models.CharField(max_length=64, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_changed_at = models.DateTimeField(null=True, blank=True)
    last_check_ok = models.BooleanField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    last_text = models.TextField(blank=True, help_text="Cleaned text from the last successful fetch")

    def __str__(self) -> str:
        return self.label


class ComplianceRule(models.Model):
    """One item of the per-video compliance checklist (editable on the Qoidalar page)."""

    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    instruction = models.TextField(help_text="English instruction sent to Gemini")
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self) -> str:
        return self.title


class PolicyChangeNote(models.Model):
    policy_document = models.ForeignKey(PolicyDocument, on_delete=models.CASCADE, related_name="notes")
    detected_at = models.DateTimeField(auto_now_add=True)
    plain_summary = models.TextField()
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-detected_at"]


class ComplianceCheck(models.Model):
    class Status(models.TextChoices):
        PASS = "pass", "O'tdi"
        WARNING = "warning", "Ogohlantirish"
        FAIL = "fail", "O'tmadi"

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="compliance")
    status = models.CharField(max_length=10, choices=Status.choices)
    findings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
