"""
Voice Generator Module
======================
Pluggable architecture — add new providers by subclassing VoiceProvider.

Supported providers:
  - elevenlabs  (high quality, requires API key)
  - gtts        (free, uses Google TTS, no API key needed)
  - mock        (silent audio for testing, no dependencies)
"""

from __future__ import annotations
import asyncio
from typing import Optional, List, Dict
from abc import ABC, abstractmethod


# ── Abstract Base ──────────────────────────────────────────────────────────

class VoiceProvider(ABC):
    @abstractmethod
    async def generate(self, text: str, output_path: str, voice_id: Optional[str] = None) -> str:
        ...

    @abstractmethod
    def get_available_voices(self) -> List[Dict]:
        ...


# ── ElevenLabs ─────────────────────────────────────────────────────────────

class ElevenLabsProvider(VoiceProvider):
    _BASE = "https://api.elevenlabs.io/v1"

    # Predefined multilingual voices (work well with German)
    _VOICES = [
        {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam (Männlich, tief)",    "provider": "elevenlabs"},
        {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella (Weiblich, sanft)",  "provider": "elevenlabs"},
        {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (Weiblich, klar)",  "provider": "elevenlabs"},
        {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi (Männlich, jung)",    "provider": "elevenlabs"},
        {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli (Weiblich, freundlich)", "provider": "elevenlabs"},
        {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh (Männlich, energisch)", "provider": "elevenlabs"},
    ]

    def __init__(self, config):
        self._api_key = config.elevenlabs_api_key
        self._stability = config.get("voice", "stability", default=0.5)
        self._similarity = config.get("voice", "similarity_boost", default=0.75)
        self._model = config.get("voice", "model_id", default="eleven_multilingual_v2")
        self._default_voice = config.get("voice", "default_voice_id", default="pNInz6obpgDQGcFmaJgB")

    async def generate(self, text: str, output_path: str, voice_id: Optional[str] = None) -> str:
        import aiohttp
        import aiofiles

        vid = voice_id or self._default_voice
        url = f"{self._BASE}/text-to-speech/{vid}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self._api_key,
        }
        payload = {
            "text": text,
            "model_id": self._model,
            "voice_settings": {
                "stability": self._stability,
                "similarity_boost": self._similarity,
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(
                        f"ElevenLabs Fehler {resp.status}: {body[:400]}"
                    )
                content = await resp.read()

        import aiofiles
        async with aiofiles.open(output_path, "wb") as f:
            await f.write(content)
        return output_path

    def get_available_voices(self) -> List[Dict]:
        return self._VOICES


# ── Google TTS (free fallback) ─────────────────────────────────────────────

class GTTSProvider(VoiceProvider):
    _VOICES = [
        {"id": "gtts_de", "name": "Google TTS Deutsch (kostenlos)", "provider": "gtts"},
    ]

    def __init__(self, config):
        self._lang = config.get("voice", "language", default="de")

    async def generate(self, text: str, output_path: str, voice_id: Optional[str] = None) -> str:
        try:
            from gtts import gTTS
        except ImportError:
            raise RuntimeError(
                "gtts ist nicht installiert. Führe aus: pip install gtts"
            )
        # gTTS is synchronous — run in executor to not block event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._sync_generate, text, output_path)
        return output_path

    def _sync_generate(self, text: str, output_path: str):
        from gtts import gTTS
        tts = gTTS(text=text, lang=self._lang, slow=False)
        tts.save(output_path)

    def get_available_voices(self) -> List[Dict]:
        return self._VOICES


# ── Mock (silent, for CI / no-key testing) ────────────────────────────────

class MockVoiceProvider(VoiceProvider):
    """Generates a short silent MP3 — useful for testing the pipeline without API keys."""

    _VOICES = [{"id": "mock", "name": "Mock (stille Testdatei)", "provider": "mock"}]

    def __init__(self, config):
        self._duration = 15  # seconds of silence

    async def generate(self, text: str, output_path: str, voice_id: Optional[str] = None) -> str:
        # Generate silence via FFmpeg
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono",
            "-t", str(self._duration),
            "-c:a", "libmp3lame",
            output_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        return output_path

    def get_available_voices(self) -> List[Dict]:
        return self._VOICES


# ── Factory ────────────────────────────────────────────────────────────────

_PROVIDERS: dict[str, type[VoiceProvider]] = {
    "elevenlabs": ElevenLabsProvider,
    "gtts": GTTSProvider,
    "mock": MockVoiceProvider,
}


class VoiceGenerator:
    def __init__(self, config):
        self.config = config
        provider_name = config.voice_provider
        cls = _PROVIDERS.get(provider_name)
        if cls is None:
            raise ValueError(
                f"Unbekannter Voice-Provider: '{provider_name}'. "
                f"Erlaubt: {', '.join(_PROVIDERS)}"
            )
        self._provider: VoiceProvider = cls(config)

    async def generate(self, text: str, output_path: str, voice_id: Optional[str] = None) -> str:
        return await self._provider.generate(text, output_path, voice_id)

    def get_available_voices(self) -> List[Dict]:
        voices = []
        for cls in _PROVIDERS.values():
            try:
                voices.extend(cls(self.config).get_available_voices())
            except Exception:
                pass
        return voices
