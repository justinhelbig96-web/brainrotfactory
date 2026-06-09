"""
Export Manager Module
=====================
Moves the rendered video to the final output directory
with a clean, readable filename.
"""

from __future__ import annotations
import re
import shutil
from datetime import datetime
from pathlib import Path


class ExportManager:
    def __init__(self, config):
        self._output_dir = config.output_dir
        self._prefix = config.get("output", "filename_prefix", default="brainrot")

    async def finalize(self, rendered_path: str, idea: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _slugify(idea, max_len=30)
        filename = f"{self._prefix}_{timestamp}_{slug}.mp4"
        dest = self._output_dir / filename
        shutil.move(rendered_path, str(dest))
        return str(dest)


def _slugify(text: str, max_len: int = 30) -> str:
    # Remove characters that are problematic in filenames
    clean = re.sub(r"[^\w\s\-]", "", text, flags=re.UNICODE)
    clean = re.sub(r"\s+", "_", clean.strip())
    return clean[:max_len] if clean else "video"
