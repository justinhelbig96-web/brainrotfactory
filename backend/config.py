import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_root = Path(__file__).parent.parent
load_dotenv(_root / ".env")


class Config:
    def __init__(self):
        config_path = _root / "config.json"
        with open(config_path, encoding="utf-8") as f:
            self._cfg = json.load(f)

        # Allow env overrides for providers
        env_story = os.getenv("STORY_PROVIDER")
        if env_story:
            self._cfg.setdefault("story", {})["provider"] = env_story

        env_voice = os.getenv("VOICE_PROVIDER")
        if env_voice:
            self._cfg.setdefault("voice", {})["provider"] = env_voice

    # ── Helpers ──────────────────────────────────────────────

    def get(self, *keys, default=None):
        val = self._cfg
        for key in keys:
            if isinstance(val, dict):
                val = val.get(key, default)
            else:
                return default
        return val

    # ── API Keys ─────────────────────────────────────────────

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def claude_api_key(self) -> str:
        return os.getenv("CLAUDE_API_KEY", "")

    @property
    def elevenlabs_api_key(self) -> str:
        return os.getenv("ELEVENLABS_API_KEY", "")

    # ── Providers ────────────────────────────────────────────

    @property
    def story_provider(self) -> str:
        return self.get("story", "provider", default="openai")

    @property
    def voice_provider(self) -> str:
        return self.get("voice", "provider", default="elevenlabs")

    # ── Paths ────────────────────────────────────────────────

    @property
    def base_dir(self) -> Path:
        return _root

    @property
    def assets_dir(self) -> Path:
        return _root / "assets"

    @property
    def output_dir(self) -> Path:
        p = _root / self.get("output", "directory", default="output")
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def backgrounds_dir(self) -> Path:
        return self.assets_dir / "backgrounds"

    @property
    def music_dir(self) -> Path:
        return self.assets_dir / "music"

    @property
    def sfx_dir(self) -> Path:
        return self.assets_dir / "sfx"

    # ── Public API ───────────────────────────────────────────

    def get_public_config(self) -> dict:
        """Return non-sensitive config for the frontend."""
        return {
            "story": {k: v for k, v in self._cfg.get("story", {}).items() if k != "provider"},
            "voice": {k: v for k, v in self._cfg.get("voice", {}).items() if "key" not in k},
            "video": self._cfg.get("video", {}),
            "subtitles": self._cfg.get("subtitles", {}),
            "audio": self._cfg.get("audio", {}),
            "providers": {
                "story": self.story_provider,
                "voice": self.voice_provider,
            },
        }
