"""
Video Renderer Module
=====================
Combines background video + audio + ASS subtitles into a final 1080x1920 MP4.
Uses FFmpeg internally. Handles Windows path escaping for subtitle filter.
"""

from __future__ import annotations
import asyncio
import json
import re
import sys
from pathlib import Path


class VideoRenderer:
    def __init__(self, config):
        self._w = config.get("video", "width", default=1080)
        self._h = config.get("video", "height", default=1920)
        self._fps = config.get("video", "fps", default=30)
        self._crf = config.get("video", "crf", default=23)
        self._preset = config.get("video", "preset", default="fast")

    async def render(
        self,
        bg_video: str,
        audio: str,
        subtitles: str,
        output: str,
    ) -> str:
        duration = await _get_audio_duration(audio)
        cmd = self._build_cmd(bg_video, audio, subtitles, output, duration)
        await _run_ffmpeg(cmd)
        return output

    # ── Command Builder ───────────────────────────────────────────────────

    def _build_cmd(
        self,
        bg: str,
        audio: str,
        subs: str,
        out: str,
        duration: float,
    ) -> list[str]:
        subs_filter = _escape_ass_path(subs)
        vf = (
            f"scale={self._w}:{self._h}:force_original_aspect_ratio=increase,"
            f"crop={self._w}:{self._h},"
            f"setsar=1,"
            f"fps={self._fps},"
            f"ass={subs_filter}"
        )

        return [
            "ffmpeg", "-y",
            "-stream_loop", "-1",   # loop background video if shorter than audio
            "-i", bg,               # input 0: background video
            "-i", audio,            # input 1: mixed audio
            "-t", f"{duration:.3f}",
            "-vf", vf,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", self._preset,
            "-crf", str(self._crf),
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            out,
        ]


# ── Path escaping for FFmpeg ASS filter ───────────────────────────────────

def _escape_ass_path(path: str) -> str:
    """
    FFmpeg's 'ass=' filter uses its own escaping rules.
    On Windows: backslashes → forward slashes, colon after drive letter → \\:
    Wrap in single quotes.
    """
    p = path.replace("\\", "/")
    if sys.platform == "win32":
        # "C:/..." → "C\\:/..."
        p = re.sub(r"^([A-Za-z]):/", r"\1\\:/", p)
    return f"'{p}'"


# ── Shared helpers ────────────────────────────────────────────────────────

async def _get_audio_duration(path: str) -> float:
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


async def _run_ffmpeg(cmd: list[str]):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        decoded = stderr.decode(errors="replace")
        # Show only the last 2000 chars to avoid overwhelming error messages
        raise RuntimeError(
            f"FFmpeg Render-Fehler (exit {proc.returncode}):\n"
            f"{'...' if len(decoded) > 2000 else ''}"
            f"{decoded[-2000:]}"
        )
