"""
TikTok Uploader — Platzhalter-Modul (Version 2)
================================================

Dieses Modul ist als Scaffold für den späteren TikTok Auto-Upload vorbereitet.
In Version 1 ist es NICHT aktiv — der Fokus liegt auf der lokalen MP4-Erzeugung.

Geplante Features (Version 2):
  - TikTok OAuth 2.0 Login-Flow
  - Video-Upload via TikTok Content Posting API v2
  - Automatische Caption- und Hashtag-Generierung
  - Upload-Scheduling / Queue
  - Upload-Status Tracking

Voraussetzungen für Version 2:
  1. TikTok Developer Account: https://developers.tiktok.com
  2. App registrieren → Client Key & Client Secret
  3. TIKTOK_CLIENT_KEY und TIKTOK_CLIENT_SECRET in .env setzen
  4. Redirect URI konfigurieren

Doku: https://developers.tiktok.com/doc/content-posting-api-get-started
"""

from __future__ import annotations
from typing import Optional, Dict, Any


class TikTokUploader:
    """Scaffold for TikTok auto-upload — NOT implemented in v1."""

    VERSION = "placeholder-v1"
    ENABLED = False

    def __init__(self, config):
        self._config = config
        # Future: self._client_key = os.getenv("TIKTOK_CLIENT_KEY")
        # Future: self._client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

    def is_configured(self) -> bool:
        """Returns True once API keys are set and the module is implemented."""
        return False

    async def upload(
        self,
        video_path: str,
        caption: str,
        hashtags: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError(
            "TikTok-Upload ist in Version 1 noch nicht implementiert.\n"
            "Füge TIKTOK_CLIENT_KEY und TIKTOK_CLIENT_SECRET zur .env hinzu "
            "und implementiere dieses Modul in Version 2."
        )

    async def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        raise NotImplementedError("Noch nicht implementiert (Version 2).")

    async def get_auth_url(self) -> str:
        raise NotImplementedError("Noch nicht implementiert (Version 2).")

    def get_setup_guide(self) -> str:
        return __doc__
