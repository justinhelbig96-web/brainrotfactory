"""
Audio Mixer Module
==================
Combines voice audio with optional background music using FFmpeg.
SFX support is prepared as a placeholder for future enhancement.
"""

from __future__ import annotations
import asyncio
import json
import random
from pathlib import Path
from typing import Optional

_AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}


class AudioMixer:
    def __init__(self, config):
        self._music_dir = config.music_dir
        self._sfx_dir = config.sfx_dir
        self._music_vol = config.get("audio", "music_volume", default=0.15)
        self._sfx_vol = config.get("audio", "sfx_volume", default=0.5)
        self._voice_vol = config.get("audio", "voice_volume", default=1.0)
        self._bitrate = config.get("audio", "audio_bitrate", default="192k")

    async def mix(
        self,
        voice_path: str,
        output_path: str,
        include_music: bool = True,
        include_sfx: bool = False,
    ) -> str:
        music_path = self._pick_random(self._music_dir) if include_music else None

        if music_path:
            await self._mix_with_music(voice_path, str(music_path), output_path)
        else:
            # No music — just re-encode voice to AAC
            await self._reencode(voice_path, output_path)

        # SFX injection placeholder (v2 feature)
        # if include_sfx:
        #     sfx_path = self._pick_random(self._sfx_dir)
        #     if sfx_path:
        #         await self._add_sfx(output_path, str(sfx_path))

        return output_path

    # ── FFmpeg operations ─────────────────────────────────────────────────

    async def _mix_with_music(self, voice: str, music: str, out: str):
        duration = await _get_duration(voice)
        cmd = [
            "ffmpeg", "-y",
            "-i", voice,
            "-stream_loop", "-1",
            "-i", music,
            "-filter_complex",
            (
                f"[0:a]volume={self._voice_vol}[v];"
                f"[1:a]volume={self._music_vol},atrim=0:{duration:.3f},asetpts=PTS-STARTPTS[m];"
                "[v][m]amix=inputs=2:duration=first[out]"
            ),
            "-map", "[out]",
            "-c:a", "aac",
            "-b:a", self._bitrate,
            "-t", str(duration),
            out,
        ]
        await _run(cmd)

    async def _reencode(self, voice: str, out: str):
        cmd = [
            "ffmpeg", "-y",
            "-i", voice,
            "-c:a", "aac",
            "-b:a", self._bitrate,
            out,
        ]
        await _run(cmd)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _pick_random(self, directory: Path) -> Optional[Path]:
        if not directory.exists():
            return None
        files = [f for ext in _AUDIO_EXTS for f in directory.glob(f"*{ext}")]
        return random.choice(files) if files else None


# ── Shared FFmpeg helpers ──────────────────────────────────────────────────

async def _run(cmd: list):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg Audio-Fehler:\n{stderr.decode(errors='replace')[-1500:]}")


async def _get_duration(path: str) -> float:
    proc = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    try:
        data = json.loads(stdout)
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                return float(stream.get("duration", 60.0))
    except (json.JSONDecodeError, ValueError):
        pass
    return 60.0
