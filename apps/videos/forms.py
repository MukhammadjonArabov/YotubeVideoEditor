"""Forms for AutoExplainer (labels in Uzbek)."""
from __future__ import annotations

from django import forms
from django.conf import settings

from .models import Project, Scene


class NewProjectForm(forms.Form):
    topic = forms.CharField(
        label="Mavzu (ingliz tilida)",
        max_length=300,
        widget=forms.TextInput(attrs={"placeholder": "Masalan: What Did Ancient Humans Eat for Breakfast?"}),
    )
    target_minutes = forms.FloatField(min_value=0.5, max_value=60, initial=8, label="Davomiyligi (daqiqa)")
    seconds_per_image = forms.IntegerField(
        min_value=3, max_value=30, initial=settings.DEFAULT_SECONDS_PER_IMAGE, label="Har rasm necha soniya"
    )
    tts_provider = forms.ChoiceField(choices=Project.TTS_CHOICES, label="Ovoz")
    auto_approve = forms.BooleanField(
        required=False,
        label="Ssenariyni avtomatik tasdiqlash (tekshiruvdan o'tmasa baribir to'xtaydi)",
    )
    source_suggestion = forms.IntegerField(required=False, widget=forms.HiddenInput)
    confirm_duplicate = forms.BooleanField(
        required=False, label="O'xshash video borligini bilaman — baribir yaratilsin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tts_provider"].initial = settings.TTS_PROVIDER


class ProjectMetaForm(forms.ModelForm):
    """Title / description / tags shown on the studio page."""

    tags_text = forms.CharField(
        label="Teglar (vergul bilan)", required=False,
        widget=forms.TextInput(attrs={"placeholder": "ancient humans, history, human behavior"}),
    )

    class Meta:
        model = Project
        fields = ["title", "description"]
        labels = {"title": "Sarlavha", "description": "Tavsif"}
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags_text"].initial = ", ".join(self.instance.tags or [])

    def save(self, commit: bool = True) -> Project:
        obj = super().save(commit=False)
        obj.tags = [t.strip() for t in self.cleaned_data["tags_text"].split(",") if t.strip()]
        if commit:
            obj.save()
        return obj


class ProjectSettingsForm(forms.ModelForm):
    target_minutes = forms.FloatField(min_value=0.5, max_value=60, label="Davomiyligi (daqiqa)")

    class Meta:
        model = Project
        fields = ["topic", "seconds_per_image", "tts_provider", "auto_approve", "style_guide"]
        labels = {
            "topic": "Mavzu",
            "seconds_per_image": "Har rasm necha soniya",
            "tts_provider": "Ovoz",
            "auto_approve": "Avtomatik tasdiqlash",
            "style_guide": "Rasm uslubi (bo'sh = standart uslub)",
        }
        widgets = {"style_guide": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_minutes"].initial = self.instance.target_minutes
        self.fields["style_guide"].widget.attrs["placeholder"] = settings.DEFAULT_STYLE_GUIDE

    def save(self, commit: bool = True) -> Project:
        obj = super().save(commit=False)
        obj.target_duration_sec = round(self.cleaned_data["target_minutes"] * 60)
        if commit:
            obj.save()
        return obj


def _sfx_choices():
    return [("", "— yo'q —")] + [(t, settings.SFX_LABELS.get(t, t)) for t in settings.SFX_TAGS]


def _transition_choices():
    main = [(t.value, t.label) for t in Scene.Transition]
    extra = [(t, settings.TRANSITION_LABELS.get(t, t)) for t in settings.TRANSITIONS if t not in dict(main)]
    return [("", "Avtomatik"), ("Asosiy", main), ("Qo'shimcha", extra)]


SFX_SLOTS = 3  # SFX rows in the scene editor


class SceneForm(forms.ModelForm):
    transition_in = forms.ChoiceField(label="Kirish o'tishi", required=False, choices=_transition_choices)
    camera_move = forms.ChoiceField(label="Kamera harakati", required=False,
                                    choices=[("", "Avtomatik")] + list(Scene.CameraMove.choices))
    intensity = forms.TypedChoiceField(label="Kuchi", coerce=int, choices=[(1, "1 — yengil"), (2, "2 — o'rta"), (3, "3 — kuchli")])
    new_image = forms.ImageField(label="O'z rasmingiz (ixtiyoriy)", required=False)
    unlock_image = forms.BooleanField(
        label="Qo'lda yuklangan rasmni olib tashlash (AI qayta chizsin)", required=False
    )

    class Meta:
        model = Scene
        fields = ["narration", "image_prompt", "beat_type", "transition_in", "emotion", "intensity", "pace",
                  "pause_after_ms", "camera_move", "music_cue", "on_screen_text", "fact_source"]
        labels = {
            "narration": "Matn (diktor o'qiydi, inglizcha)",
            "image_prompt": "Rasm tavsifi (AI uchun, inglizcha)",
            "beat_type": "Sahna turi",
            "emotion": "His-tuyg'u",
            "pace": "Diktor tezligi",
            "pause_after_ms": "Gapdan keyin pauza (ms)",
            "music_cue": "Musiqa",
            "on_screen_text": "Ekrandagi yozuv (1-4 so'z)",
            "fact_source": "Fakt manbasi (faktli sahna uchun)",
        }
        widgets = {
            "narration": forms.Textarea(attrs={"rows": 3}),
            "image_prompt": forms.Textarea(attrs={"rows": 2}),
            "pause_after_ms": forms.NumberInput(attrs={"min": 0, "max": 3000, "step": 100}),
            "on_screen_text": forms.TextInput(attrs={"placeholder": "30,000 YEARS AGO"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.OPTIONAL_DIRECTION:  # missing in a post -> keep the scene's current value
            self.fields[name].required = False
        items = list(getattr(self.instance, "sfx", None) or [])
        for i in range(SFX_SLOTS):
            item = items[i] if i < len(items) and isinstance(items[i], dict) else {}
            self.fields[f"sfx{i}_tag"] = forms.ChoiceField(label="Effekt", required=False, choices=_sfx_choices,
                                                           initial=item.get("tag", ""))
            self.fields[f"sfx{i}_offset"] = forms.IntegerField(
                label="Boshidan (ms)", required=False, min_value=0, max_value=60_000, initial=item.get("offset_ms", 0),
                widget=forms.NumberInput(attrs={"step": 100}))
            self.fields[f"sfx{i}_gain"] = forms.FloatField(
                label="Balandlik (dB)", required=False, min_value=-40, max_value=6,
                initial=item.get("gain_db", settings.SFX_GAIN_DB), widget=forms.NumberInput(attrs={"step": 1}))

    OPTIONAL_DIRECTION = ("emotion", "intensity", "pace", "pause_after_ms", "music_cue")

    def sfx_rows(self):
        return [(self[f"sfx{i}_tag"], self[f"sfx{i}_offset"], self[f"sfx{i}_gain"]) for i in range(SFX_SLOTS)]

    def clean(self):
        data = super().clean()
        items = []
        for i in range(SFX_SLOTS):
            tag = data.get(f"sfx{i}_tag")
            if tag:
                offset = data.get(f"sfx{i}_offset")
                gain = data.get(f"sfx{i}_gain")
                items.append({"tag": tag, "offset_ms": int(offset or 0),
                              "gain_db": float(settings.SFX_GAIN_DB if gain is None else gain)})
        data["sfx"] = sorted(items, key=lambda x: x["offset_ms"])
        data["on_screen_text"] = " ".join((data.get("on_screen_text") or "").split())
        for name in self.OPTIONAL_DIRECTION:
            if data.get(name) in (None, ""):
                data[name] = getattr(self.instance, name)
        return data

    def save(self, commit: bool = True):
        obj = super().save(commit=False)
        obj.sfx = self.cleaned_data["sfx"]
        obj.on_screen_text = self.cleaned_data["on_screen_text"]
        if commit:
            obj.save()
        return obj


# ------------------------------------------------------------------ niche / channels / library / policy
from .models import ChannelSource, ComplianceRule, Niche, PolicyDocument  # noqa: E402


class NicheForm(forms.ModelForm):
    class Meta:
        model = Niche
        fields = [
            "name", "name_en", "description", "audience", "tone", "title_formula", "content_pillars",
            "avoid_topics", "originality_rules", "style_guide", "character_description", "character_reference",
            "default_minutes", "default_seconds_per_image", "default_mood",
        ]
        widgets = {f: forms.Textarea(attrs={"rows": 3}) for f in [
            "description", "audience", "tone", "title_formula", "originality_rules", "style_guide", "character_description"]}
        widgets.update({"content_pillars": forms.Textarea(attrs={"rows": 6}), "avoid_topics": forms.Textarea(attrs={"rows": 6})})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["default_mood"] = forms.ChoiceField(
            label="Standart musiqa kayfiyati", choices=[(m, m) for m in settings.MUSIC_MOODS])


class ChannelAddForm(forms.Form):
    url = forms.CharField(
        label="Kanal manzili yoki @handle", max_length=300,
        widget=forms.TextInput(attrs={"placeholder": "https://www.youtube.com/@Inkexplainer96"}),
    )

    def clean_url(self):
        from .services.channel_research import YouTubeError, parse_channel_input

        value = self.cleaned_data["url"].strip()
        try:
            parse_channel_input(value)
        except YouTubeError as exc:
            raise forms.ValidationError(str(exc)) from exc
        if ChannelSource.objects.filter(handle_or_url__iexact=value).exists():
            raise forms.ValidationError("Bu kanal allaqachon qo'shilgan.")
        return value


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "audio/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return [single(data, initial)] if data else []


class AudioUploadForm(forms.Form):
    files = MultipleFileField(label="Audio fayllar (bir nechtasini tanlash mumkin)")
    title = forms.CharField(label="Nomi (ixtiyoriy, bitta fayl uchun)", required=False, max_length=200)
    tags = forms.CharField(
        label="Teglar (vergul bilan; bo'sh qoldirsangiz avtomatik tanlanadi)", required=False,
        widget=forms.TextInput(attrs={"placeholder": "masalan: mysterious, calm"}),
    )
    license_note = forms.CharField(
        label="Manba / litsenziya izohi", required=False,
        widget=forms.TextInput(attrs={"placeholder": "YouTube Audio Library, no attribution required"}),
    )

    def clean_files(self):
        files = self.cleaned_data["files"]
        from pathlib import Path

        from .services.media_library import AUDIO_EXTS

        bad = [f.name for f in files if Path(f.name).suffix.lower() not in AUDIO_EXTS]
        if bad:
            raise forms.ValidationError("Audio emas: " + ", ".join(bad))
        if not files:
            raise forms.ValidationError("Kamida bitta fayl tanlang.")
        return files


class PolicyDocumentForm(forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["label", "url"]
        labels = {"label": "Nomi", "url": "Rasmiy sahifa manzili"}


class ComplianceRuleForm(forms.ModelForm):
    class Meta:
        model = ComplianceRule
        fields = ["title", "instruction", "enabled"]
        labels = {"title": "Nomi", "instruction": "Gemini uchun ko'rsatma (inglizcha)", "enabled": "Yoqilgan"}
        widgets = {"instruction": forms.Textarea(attrs={"rows": 3})}


class ManualSuggestionForm(forms.Form):
    """A topic idea you add yourself to the "Mavzu takliflari" list."""

    topic_text = forms.CharField(label="Mavzu (inglizcha)", max_length=300,
                                 widget=forms.TextInput(attrs={"placeholder": "Why did ancient people fear eclipses?"}))
    rationale = forms.CharField(label="Izoh (ixtiyoriy)", max_length=500, required=False,
                                widget=forms.TextInput(attrs={"placeholder": "Nega bu mavzu qiziq?"}))

    def clean_topic_text(self) -> str:
        text = " ".join(self.cleaned_data["topic_text"].split())
        if len(text) < 4:
            raise forms.ValidationError("Mavzu juda qisqa.")
        return text
