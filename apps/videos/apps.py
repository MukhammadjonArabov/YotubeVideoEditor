from django.apps import AppConfig
from django.db.models.signals import post_migrate


class VideosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.videos"
    verbose_name = "AutoExplainer videos"

    def ready(self) -> None:
        from .signals import ensure_policy_schedule

        post_migrate.connect(ensure_policy_schedule, sender=self)
