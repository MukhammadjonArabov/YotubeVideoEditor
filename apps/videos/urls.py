from django.urls import path

from . import views, views_music

app_name = "videos"

urlpatterns = [
    path("", views.home, name="home"),
    path("yonalish/<slug:slug>/", views.niche_detail, name="niche"),
    path("videolar/", views.home, name="project_list"),
    path("videolar/<int:pk>/", views.video_detail, name="project_detail"),
    # music niche: relaxing long videos from one looped track
    path("musiqa/", views_music.music_list, name="music_list"),
    path("musiqa/yangi/", views_music.music_create, name="music_create"),
    path("musiqa/<int:pk>/", views_music.music_detail, name="music_detail"),
    path("musiqa/<int:pk>/saqlash/", views_music.music_save, name="music_save"),
    path("musiqa/<int:pk>/flow/", views_music.music_flow_save, name="music_flow_save"),
    path("musiqa/<int:pk>/yaratish/", views_music.music_generate, name="music_generate"),
    path("musiqa/<int:pk>/yuklash/", views_music.music_upload_audio, name="music_upload_audio"),
    path("musiqa/<int:pk>/ulanish/", views_music.music_loop_preview, name="music_loop_preview"),
    path("musiqa/<int:pk>/birlashtirish/", views_music.music_combine, name="music_combine"),
    path("musiqa/<int:pk>/klip/", views_music.music_upload_clips, name="music_upload_clips"),
    path("musiqa/<int:pk>/montaj/", views_music.music_render, name="music_render"),
    path("musiqa/<int:pk>/ochirish/", views_music.music_delete, name="music_delete"),
    path("musiqa/variant/<int:pk>/tanlash/", views_music.music_take_select, name="music_take_select"),
    path("musiqa/variant/<int:pk>/ochirish/", views_music.music_take_delete, name="music_take_delete"),
    path("musiqa/klip/<int:pk>/ochirish/", views_music.music_clip_delete, name="music_clip_delete"),
]
