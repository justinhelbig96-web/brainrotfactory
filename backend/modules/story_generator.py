"""
Story Generator Module
======================
Supports: OpenAI (default) | Claude
Provider is set in config.json → story.provider or via STORY_PROVIDER env var.
"""

import re
from typing import Dict, Any, List

# ── Prompts ────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Du bist ein Elite-Brainrot-Story-Schreiber für TikTok. \
Deine Stories sind auf Deutsch, explosiv, absurd, und extrem fesselnd. \
Keine Erklärungen, keine Metakommentare — nur die Story direkt."""

_CATEGORY_CONTEXT: dict[str, str] = {
    "Horror":         "Horrorstory: gruselig, unerklärlich, bedrohlich, psychologisch.",
    "Mystery":        "Mystery-Story: rätselhaft, spannend, mit unbekannten Elementen.",
    "Lustig":         "Komische Story: absurder Humor, unerwartete Wendungen, maximal witzig.",
    "Verrückt":       "Surreale Story: komplett verrückt, unmöglich, aber irgendwie fesselnd.",
    "Reddit Stories": "Reddit-Stil (Ich-Perspektive): realistisch, kontrovers, unglaublich aber wahr.",
    "Minecraft Stories": "Minecraft-Story: ingame Mysterien, seltsame NPCs, Seed-Horrormomente.",
    "GTA Stories":    "GTA-Story: Straßenleben, Chaos, verrückte Zufallsereignisse.",
}

_DURATION_SETTINGS: dict[int, dict] = {
    30: {"max_tokens": 220, "sentences_hint": 7},
    60: {"max_tokens": 420, "sentences_hint": 14},
    90: {"max_tokens": 620, "sentences_hint": 21},
}


def _build_prompt(idea: str, duration: int, category: str) -> str:
    cfg = _DURATION_SETTINGS.get(duration, _DURATION_SETTINGS[60])
    ctx = _CATEGORY_CONTEXT.get(category, _CATEGORY_CONTEXT["Mystery"])
    return f"""{ctx}

IDEE: {idea}

REGELN (unbedingt einhalten):
- Sprache: Deutsch
- Erster Satz = sofortiger Hook (Schock, Frage oder Aussage die neugierig macht)
- Maximal 10 Wörter pro Satz
- Spannung alle 3-4 Sätze steigern
- Kein Begrüßungstext, direkt in die Handlung
- Ende: Cliffhanger ODER "Teil 2?" ODER offene Frage
- Optimiert für genau {duration} Sekunden Sprechzeit
- Ziel: ca. {cfg['sentences_hint']} Sätze

Schreibe jetzt die Story (nur Text, kein Titel, kein Kommentar):"""


# ── Generator ─────────────────────────────────────────────────────────────

class StoryGenerator:
    def __init__(self, config):
        self.config = config
        self.provider = config.story_provider

    async def generate(self, idea: str, duration: int = 60, category: str = "Mystery") -> Dict[str, Any]:
        cfg = _DURATION_SETTINGS.get(duration, _DURATION_SETTINGS[60])
        prompt = _build_prompt(idea, duration, category)

        if self.provider == "openai":
            text = await self._openai(prompt, cfg["max_tokens"])
        elif self.provider == "claude":
            text = await self._claude(prompt, cfg["max_tokens"])
        elif self.provider == "mock":
            text = _mock_story(idea)
        else:
            raise ValueError(
                f"Unbekannter Story-Provider: '{self.provider}'. "
                "Erlaubt: openai, claude, mock"
            )

        text = text.strip()
        sentences = _split_sentences(text)

        return {
            "text": text,
            "sentences": sentences,
            "idea": idea,
            "category": category,
            "duration": duration,
        }

    async def _openai(self, prompt: str, max_tokens: int) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.config.openai_api_key)
        model = self.config.get("story", "model", default="gpt-4o-mini")
        temp = self.config.get("story", "temperature", default=0.9)

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temp,
        )
        return response.choices[0].message.content

    async def _claude(self, prompt: str, max_tokens: int) -> str:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.config.claude_api_key)
        model = self.config.get("story", "model", default="claude-3-haiku-20240307")

        message = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


# ── Helpers ────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _mock_story(idea: str) -> str:
    """Offline fallback for testing without API keys."""
    return (
        f"Stell dir vor: {idea}. "
        "Es beginnt ganz harmlos. "
        "Doch dann passiert es. "
        "Das Unvorstellbare. "
        "Niemand hätte das kommen sehen. "
        "Überall Zeichen — doch alle ignorieren sie. "
        "Nur er nicht. "
        "Er weiß die Wahrheit. "
        "Und die Wahrheit ist schlimmer als alles. "
        "Was würdest du tun? "
        "Teil 2?"
    )
