"""
Subtitle Generator Module
=========================
Generates ASS (Advanced SubStation Alpha) subtitle files.
Timing is calculated proportionally from audio duration.

Styles available: tiktok | minimal | fire
"""

from __future__ import annotations
import asyncio
import json
import subprocess
from typing import List, Dict

# ── Styles ─────────────────────────────────────────────────────────────────
#  ASS colour format: &HAABBGGRR

STYLES: dict[str, dict] = {
    "tiktok": {
        "font":          "Arial Black",
        "size":          72,
        "primary":       "&H00FFFFFF",   # white text
        "outline_color": "&H00000000",   # black outline
        "back_color":    "&H00000000",
        "bold":          1,
        "outline":       3,
        "shadow":        0,
        "margin_v":      130,
        "alignment":     2,              # bottom-centre
    },
    "minimal": {
        "font":          "Arial",
        "size":          58,
        "primary":       "&H00FFFFFF",
        "outline_color": "&H00000000",
        "back_color":    "&H80000000",   # semi-transparent box
        "bold":          0,
        "outline":       2,
        "shadow":        0,
        "margin_v":      100,
        "alignment":     2,
    },
    "fire": {
        "font":          "Impact",
        "size":          80,
        "primary":       "&H0000FFFF",   # yellow
        "outline_color": "&H000000FF",   # red outline
        "back_color":    "&H00000000",
        "bold":          1,
        "outline":       4,
        "shadow":        0,
        "margin_v":      130,
        "alignment":     2,
    },
}


class SubtitleGenerator:
    def __init__(self, config):
        self._words_per_line = config.get("subtitles", "words_per_line", default=4)
        self._min_time = config.get("subtitles", "min_display_time", default=0.5)

    async def generate(
        self,
        sentences: List[str],
        audio_path: str,
        output_path: str,
        style: str = "tiktok",
    ) -> str:
        duration = await _get_audio_duration(audio_path)
        chunks = self._sentences_to_timed_chunks(sentences, duration)
        style_cfg = STYLES.get(style, STYLES["tiktok"])
        _write_ass(chunks, output_path, style_cfg)
        return output_path

    # ── Timing ────────────────────────────────────────────────────────────

    def _sentences_to_timed_chunks(
        self, sentences: List[str], total_duration: float
    ) -> List[Dict]:
        """
        Split sentences into word chunks and assign proportional timing
        based on character count relative to total text length.
        """
        full_text = " ".join(sentences)
        total_chars = max(len(full_text), 1)
        chunks: List[Dict] = []
        current = 0.0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Duration for this sentence proportional to its length
            sentence_duration = (len(sentence) / total_chars) * total_duration

            words = sentence.split()
            word_groups: List[str] = []
            for i in range(0, len(words), self._words_per_line):
                group = " ".join(words[i : i + self._words_per_line])
                if group.strip():
                    word_groups.append(group.strip())

            if not word_groups:
                continue

            chunk_dur = sentence_duration / len(word_groups)

            for group in word_groups:
                dur = max(chunk_dur, self._min_time)
                chunks.append({
                    "start": current,
                    "end": current + dur,
                    "text": group,
                })
                current += dur

        return chunks


# ── ASS Writer ─────────────────────────────────────────────────────────────

def _write_ass(subtitles: List[Dict], output_path: str, style: dict):
    s = style
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{s['font']},{s['size']},"
        f"{s['primary']},&H000000FF,"
        f"{s['outline_color']},{s['back_color']},"
        f"{s['bold']},0,0,0,100,100,0,0,1,"
        f"{s['outline']},{s['shadow']},{s['alignment']},"
        f"80,80,{s['margin_v']},1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    lines = [header]
    for sub in subtitles:
        start = _fmt_time(sub["start"])
        end = _fmt_time(sub["end"])
        text = sub["text"].replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _fmt_time(seconds: float) -> str:
    """Format float seconds → ASS time string H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


# ── FFprobe helper ─────────────────────────────────────────────────────────

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
