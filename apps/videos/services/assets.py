"""Parallel asset production: scene images and voice-overs are made at the same time.

Image requests (IMAGE_CONCURRENCY) and voice requests (TTS_CONCURRENCY) run in two thread
pools; both are network-bound, so a 60-scene video no longer waits for 120 requests in a row.
Worker threads never touch the database - they return bytes / temp files and this thread
saves them (SQLite stays happy, and the ORM is only used from one thread).
"""
from __future__ import annotations

import logging
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from django.conf import settings

from .voice_style import VoiceStyle

logger = logging.getLogger(__name__)


@dataclass
class AssetReport:
    images_done: int = 0
    images_failed: int = 0
    images_flagged: int = 0  # saved, but the vision check says the hero still looks different
    images_skipped: int = 0  # not tried because the image quota ran out
    image_quota_hit: bool = False
    voice_failed: list = field(default_factory=list)  # [(scene, TTSError)]


def produce(image_scenes, voice_scenes, image_provider, tts_provider, progress=lambda msg: None,
            salt_fn=None, qa: bool = True) -> AssetReport:
    """Draw `image_scenes` and voice `voice_scenes` concurrently; save results as they arrive."""
    from ..models import Scene
    from . import images, voice
    from .image_providers import ImageProviderError
    from .tts import TTSError

    rep = AssetReport()
    stop = threading.Event()  # set when the image quota is over: queued image jobs are skipped
    image_errors: dict[int, str] = {}
    n_img, n_voice = len(image_scenes), len(voice_scenes)
    done = {"img": 0, "voice": 0}

    def report() -> None:
        parts = []
        if n_img:
            parts.append(f"rasm {done['img']}/{n_img}")
        if n_voice:
            parts.append(f"ovoz {done['voice']}/{n_voice}")
        if image_provider is not None:
            from .image_providers import spent

            cost, _n = spent(image_provider)
            if cost:
                parts.append(f"rasmlarga sarflandi ${cost:.3f}")
        progress("Tayyorlanmoqda (parallel): " + " · ".join(parts))

    def draw(job):
        if stop.is_set():
            return None
        try:
            return images.draw_image(job, image_provider, qa)
        except ImageProviderError as exc:
            if "limit" in str(exc).lower():
                stop.set()  # right here, so the next queued job in this pool is skipped, not sent
            raise

    with tempfile.TemporaryDirectory() as tmp, \
            ThreadPoolExecutor(max_workers=max(1, settings.IMAGE_CONCURRENCY)) as ipool, \
            ThreadPoolExecutor(max_workers=max(1, settings.TTS_CONCURRENCY)) as vpool:
        futures = {}
        for s in voice_scenes:
            futures[vpool.submit(voice.synthesize, s.order, s.narration, tts_provider, Path(tmp),
                                 VoiceStyle.for_scene(s))] = ("voice", s)
        for s in image_scenes:
            job = images.ImageJob(s, image_provider, salt_fn() if salt_fn else 0)
            futures[ipool.submit(draw, job)] = ("img", s)
        report()
        try:
            for fut in as_completed(futures):
                kind, scene = futures[fut]
                done[kind] += 1
                if kind == "voice":
                    try:
                        voice.save_scene_audio(scene, fut.result())
                    except TTSError as exc:
                        rep.voice_failed.append((scene, exc))
                else:
                    try:
                        result = fut.result()
                    except ImageProviderError as exc:
                        rep.images_failed += 1
                        image_errors[scene.pk] = str(exc)
                        logger.warning("Image failed for scene %s: %s", scene.pk, exc)
                        if "limit" in str(exc).lower():
                            rep.image_quota_hit = True
                            stop.set()  # daily quota is over - no point hammering the API
                    else:
                        if result is None:
                            rep.images_skipped += 1
                        else:
                            png, note = result
                            images.save_scene_image(scene, png, note, getattr(image_provider, "name", ""))
                            rep.images_done += 1
                            rep.images_flagged += bool(note)
                report()
        except BaseException:
            stop.set()
            for f in futures:
                f.cancel()
            raise
    # A voice-over saved after a failed image must not hide that image's error from the user.
    for pk, msg in image_errors.items():
        Scene.objects.filter(pk=pk).update(status=Scene.Status.FAILED, error_message=msg)
    return rep
