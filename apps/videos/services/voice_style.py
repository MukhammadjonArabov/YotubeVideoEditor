"""How a scene should *sound*: the director's emotion / intensity / pace -> delivery settings
for the voice provider. One table, so the mood map is easy to tune by ear.

Edge TTS can only change rate, pitch and volume (Microsoft doesn't allow its speaking styles through
edge-tts), so emotions are expressed as small, natural shifts: tense and scary lines slow down and drop
a little, excited and funny lines speed up and lift, sad and awe lines slow down and soften. Gemini TTS
gets the emotion as words in its prompt. Kept deliberately gentle: big jumps sound robotic.
"""
from __future__ import annotations

from dataclasses import dataclass

# emotion -> (rate %, pitch Hz, volume %) at intensity 2; intensity 1 = half, 3 = 1.5x
EMOTIONS: dict[str, tuple[float, float, float]] = {
    "neutral": (0, 0, 0),
    "curious": (2, 2, 0),
    "excited": (8, 4, 4),
    "happy": (5, 3, 2),
    "funny": (6, 3, 2),
    "scared": (-4, -1, -4),
    "tense": (-5, -2, -2),
    "sad": (-9, -3, -6),
    "awe": (-6, 1, -3),
    "whisper": (-10, -2, -14),
    "serious": (-4, -3, 0),
}
INTENSITY = {1: 0.5, 2: 1.0, 3: 1.5}
PACE = {"slow": -7, "normal": 0, "fast": 7}
LIMITS = {"rate": (-25, 25), "pitch": (-8, 8), "volume": (-25, 10)}
GEMINI_WORDS = {
    "neutral": "calm, warm", "curious": "curious, intrigued", "excited": "excited, energetic", "happy": "cheerful",
    "funny": "playful, amused", "scared": "uneasy, hushed", "tense": "tense, suspenseful", "sad": "gentle, sad",
    "awe": "amazed, in awe", "whisper": "soft, almost whispering", "serious": "serious, measured",
}


# ElevenLabs v3 audio tags: emotion -> (tag at intensity 1-2, tag at intensity 3). Empty = no tag (plain narration).
ELEVEN_TAGS: dict[str, tuple[str, str]] = {
    "neutral": ("", ""),
    "curious": ("[curious]", "[curious][intrigued]"),
    "excited": ("[excited]", "[excited][thrilled]"),
    "happy": ("[happy]", "[happy][delighted]"),
    "funny": ("[playful]", "[playful][amused]"),
    "scared": ("[nervous]", "[fearful][whispers]"),
    "tense": ("[tense]", "[tense][hushed]"),
    "sad": ("[sad]", "[sad][sorrowful]"),
    "awe": ("[in awe]", "[in awe][amazed]"),
    "whisper": ("[whispers]", "[whispers]"),
    "serious": ("[serious]", "[serious][grave]"),
}
ELEVEN_PACE = {"slow": "[slowly]", "fast": "[quickly]"}


@dataclass(frozen=True)
class VoiceStyle:
    emotion: str = "neutral"
    intensity: int = 2
    pace: str = "normal"

    @classmethod
    def for_scene(cls, scene) -> "VoiceStyle":
        return cls(getattr(scene, "emotion", "neutral") or "neutral", int(getattr(scene, "intensity", 2) or 2),
                   getattr(scene, "pace", "normal") or "normal")

    def offsets(self, base_rate: float = 0.0) -> tuple[int, int, int]:
        """(rate %, pitch Hz, volume %) after intensity, pace and limits."""
        r, p, v = EMOTIONS.get(self.emotion, EMOTIONS["neutral"])
        k = INTENSITY.get(self.intensity, 1.0)
        rate = base_rate + r * k + PACE.get(self.pace, 0)
        clamp = lambda x, lim: int(round(min(max(x, lim[0]), lim[1])))  # noqa: E731
        return clamp(rate, LIMITS["rate"]), clamp(p * k, LIMITS["pitch"]), clamp(v * k, LIMITS["volume"])

    def edge_params(self, base_rate: str = "+0%") -> dict[str, str]:
        try:
            base = float(str(base_rate).strip().rstrip("%") or 0)
        except ValueError:
            base = 0.0
        rate, pitch, volume = self.offsets(base)
        return {"rate": f"{rate:+d}%", "pitch": f"{pitch:+d}Hz", "volume": f"{volume:+d}%"}

    def gemini_words(self) -> str:
        words = GEMINI_WORDS.get(self.emotion, GEMINI_WORDS["neutral"])
        pace = {"slow": ", unhurried", "fast": ", brisk"}.get(self.pace, "")
        return words + pace

    def eleven_tags(self) -> str:
        """Audio tags put in front of the line for ElevenLabs v3 (intensity 3 = a stronger pair of tags)."""
        low, high = ELEVEN_TAGS.get(self.emotion, ELEVEN_TAGS["neutral"])
        return (high if self.intensity >= 3 else low) + ELEVEN_PACE.get(self.pace, "")

    def signature(self) -> str:
        return f"{self.emotion}:{self.intensity}:{self.pace}"
