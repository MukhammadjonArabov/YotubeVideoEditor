"""Background jobs of the music section (django-q): make takes of the track, render the long video."""
from __future__ import annotations

import logging

from django_q.tasks import async_task

from .models import MusicVideo

logger = logging.getLogger(__name__)


def enqueue(func_name: str, mv: MusicVideo, *args) -> str:
    MusicVideo.objects.filter(pk=mv.pk).update(is_working=True, error_message="")
    return async_task(f"apps.videos.music_tasks.{func_name}", mv.pk, *args, task_name=f"{func_name}-m{mv.pk}")


def _progress(mv_id: int):
    return lambda msg: MusicVideo.objects.filter(pk=mv_id).update(progress_message=msg[:300])


def generate_takes(mv_id: int, count: int = 1) -> None:
    """ElevenLabs makes `count` takes (each a 1-5 minute track that is looped later, so only these cost credits).
    Every take is checked automatically; the first one is selected."""
    from .services import music_video as mvs

    progress = _progress(mv_id)
    made = 0
    try:
        for i in range(1, max(1, min(4, int(count))) + 1):
            mv = MusicVideo.objects.get(pk=mv_id)
            progress(f"Musiqa yaratilmoqda: {i}/{count}-variant ({mv.music_seconds} soniya, 1-3 daqiqa kuting)...")
            data = mvs.compose_music(mv.music_prompt, mv.music_seconds, mv.vocals)
            take = mvs.add_take(mv, data, source="elevenlabs", prompt=mvs.build_prompt(mv.music_prompt, mv.vocals), name=f"take_{i}.mp3")
            made += 1
            progress(f"{i}/{count}-variant tayyor (sifat bahosi {take.score}/100).")
        progress(f"{made} ta variant tayyor. Tinglab, eng yaxshisini tanlang.")
    except mvs.MusicError as exc:
        MusicVideo.objects.filter(pk=mv_id).update(error_message=str(exc), progress_message=f"{made} ta variant yaratildi, keyingisi xato.")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Music generation failed for %s", mv_id)
        MusicVideo.objects.filter(pk=mv_id).update(error_message=str(exc)[:400], progress_message="Musiqa yaratilmadi.")
    finally:
        MusicVideo.objects.filter(pk=mv_id).update(is_working=False)


def render_video(mv_id: int) -> None:
    from django.core.files import File

    from .services import media_library, music_video as mvs

    mv = MusicVideo.objects.get(pk=mv_id)
    progress = _progress(mv_id)
    try:
        MusicVideo.objects.filter(pk=mv_id).update(status=MusicVideo.Status.RENDERING)
        out, total = mvs.render_music_video(mv, progress)
        mv.refresh_from_db()
        if mv.final_video:
            mv.final_video.delete(save=False)
        with open(out, "rb") as fh:
            mv.final_video.save(f"musiqa_{mv.pk}.mp4", File(fh), save=False)
        mv.actual_duration_sec = round(media_library.audio_duration(out) or total, 1)
        mv.status = MusicVideo.Status.DONE
        mv.progress_message = f"Tayyor: {mv.actual_duration_sec / 60:.1f} daqiqa."
        mv.save(update_fields=["final_video", "actual_duration_sec", "status", "progress_message", "updated_at"])
        out.unlink(missing_ok=True)  # the copy under media/ is the deliverable
        try:
            from .services import monetization
            monetization.check_music(mv)
        except Exception:  # noqa: BLE001  the check must never fail a finished render
            logger.exception("Monetization check failed for music %s", mv_id)
    except mvs.MusicError as exc:
        MusicVideo.objects.filter(pk=mv_id).update(status=MusicVideo.Status.FAILED, error_message=str(exc), progress_message="Montaj bo'lmadi.")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Music render failed for %s", mv_id)
        MusicVideo.objects.filter(pk=mv_id).update(status=MusicVideo.Status.FAILED, error_message=str(exc)[:400], progress_message="Montaj bo'lmadi.")
    finally:
        MusicVideo.objects.filter(pk=mv_id).update(is_working=False)
