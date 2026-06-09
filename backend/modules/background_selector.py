"""
Background Selector Module
===========================
Randomly selects a video from /assets/backgrounds.
Supports category subfolders (e.g. backgrounds/minecraft/).
"""

from __future__ import annotations
import random
from pathlib import Path
from typing import Optional, List

_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

# Map category names to subfolder names
_CATEGORY_MAP: dict[str, list[str]] = {
    "Minecraft Stories": ["minecraft"],
    "GTA Stories":       ["gta"],
    "Horror":            ["horror"],
    "Mystery":           ["mystery"],
    "Lustig":            ["lustig", "funny"],
    "Verrückt":          ["verruckt", "crazy"],
    "Reddit Stories":    ["reddit"],
}


class BackgroundSelector:
    def __init__(self, config):
        self._dir = config.backgrounds_dir

    def select_random(self, category: Optional[str] = None) -> Path:
        videos = self._find_videos(category)
        if not videos:
            raise FileNotFoundError(
                f"Keine Hintergrundvideos in '{self._dir}' gefunden.\n"
                "Lege eigene MP4-Clips (z.B. Minecraft Parkour, Subway Surfers) in diesen Ordner."
            )
        return random.choice(videos)

    def list_backgrounds(self) -> List[dict]:
        result = []
        for ext in _VIDEO_EXTS:
            for p in self._dir.glob(f"**/*{ext}"):
                try:
                    rel = p.relative_to(self._dir)
                    result.append({
                        "name": p.name,
                        "path": str(rel).replace("\\", "/"),
                        "size_mb": round(p.stat().st_size / (1024 * 1024), 1),
                    })
                except ValueError:
                    pass
        return sorted(result, key=lambda x: x["name"])

    # ── Private ───────────────────────────────────────────────────────────

    def _find_videos(self, category: Optional[str]) -> List[Path]:
        if not self._dir.exists():
            self._dir.mkdir(parents=True, exist_ok=True)
            return []

        videos: List[Path] = []

        # 1. Try category-specific subfolder
        if category and category in _CATEGORY_MAP:
            for folder_name in _CATEGORY_MAP[category]:
                sub = self._dir / folder_name
                if sub.is_dir():
                    for ext in _VIDEO_EXTS:
                        videos.extend(sub.glob(f"*{ext}"))

        # 2. Fallback: all videos in the backgrounds dir (recursive)
        if not videos:
            for ext in _VIDEO_EXTS:
                videos.extend(self._dir.glob(f"**/*{ext}"))

        return videos
