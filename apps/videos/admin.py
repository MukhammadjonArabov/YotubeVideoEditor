from django.contrib import admin

from . import models


class SceneInline(admin.TabularInline):
    model = models.Scene
    extra = 0
    fields = ("order", "beat_type", "emotion", "narration", "status", "audio_duration", "transition_in")


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "status", "target_duration_sec", "actual_duration_sec", "created_at")
    list_filter = ("status", "tts_provider")
    search_fields = ("topic", "title")
    inlines = [SceneInline]


for m in (
    models.Scene, models.ThumbnailOption, models.ChannelSource, models.SuggestedTopic,
    models.MusicTrack, models.SoundEffect, models.PolicyDocument, models.PolicyChangeNote,
    models.ComplianceCheck,
):
    admin.site.register(m)
