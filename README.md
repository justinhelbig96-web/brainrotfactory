# 🎬 Brainrot Video Factory

Erstelle automatisch virale TikTok Brainrot Videos (1080x1920, MP4) mit KI-Story, KI-Stimme und animierten Untertiteln — auf Knopfdruck, komplett lokal auf deinem PC.

---

## Features

- **KI-Story** (OpenAI GPT-4o-mini oder Claude) auf Deutsch, Brainrot-Stil mit Hook, Spannung, Cliffhanger
- **KI-Stimme** (ElevenLabs multilingual) oder kostenlose Google TTS
- **Automatische Untertitel** (ASS-Format, TikTok-Stil) synchron zur Stimme
- **Hintergrundvideo** automatisch aus deinem `/assets/backgrounds` Ordner gewählt
- **Hintergrundmusik** optional (aus `/assets/music`)
- **FFmpeg Rendering** → fertiges 1080x1920 MP4
- **Mehrere Kategorien**: Horror, Mystery, Lustig, Verrückt, Reddit, Minecraft, GTA Stories
- **3 Videolängen**: 30s, 60s, 90s
- **3 Untertitel-Stile**: TikTok, Fire, Minimal
- **Job-Queue** mit Echtzeit-Fortschrittsanzeige
- **TikTok Upload** als vorbereitetes Platzhalter-Modul (Version 2)

---

## Voraussetzungen

### 1. Python 3.10+
Download: https://www.python.org/downloads/

### 2. Node.js 18+ (LTS)
Download: https://nodejs.org/

### 3. FFmpeg
Download: https://www.gyan.dev/ffmpeg/builds/
→ `ffmpeg-release-essentials.zip` herunterladen, entpacken
→ Pfad zu `bin/` (z.B. `C:\ffmpeg\bin`) zu den Windows PATH-Umgebungsvariablen hinzufügen
→ Test: `ffmpeg -version` in der Eingabeaufforderung

### 4. API Keys
- **OpenAI**: https://platform.openai.com/api-keys
- **ElevenLabs**: https://elevenlabs.io (Settings → API Key)

---

## Installation & Start

### Option A: Automatisch (empfohlen)
```
start.bat   ← Doppelklick
```
Startet Backend + Frontend automatisch in zwei Fenstern und öffnet den Browser.

### Option B: Manuell

**Terminal 1 — Backend:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Dann: http://localhost:3000 im Browser öffnen

---

## Konfiguration

### 1. API Keys einrichten
```bash
copy .env.example .env
```
Dann `.env` öffnen und deine API Keys eintragen:
```env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
```

### 2. Hintergrundvideos hinzufügen
Lege eigene MP4-Clips in `assets/backgrounds/`:
```
assets/
  backgrounds/
    minecraft_parkour.mp4
    subway_surfers.mp4
    gta_gameplay.mp4
```
Optional: Unterordner für Kategorien:
```
assets/backgrounds/minecraft/
assets/backgrounds/gta/
```

### 3. Hintergrundmusik (optional)
Lege MP3-Dateien in `assets/music/`. Empfehlung: Royalty-free Lofi von https://pixabay.com/music/

### 4. Einstellungen anpassen
Öffne `config.json` für folgende Optionen:

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `story.provider` | `openai` | `openai` oder `claude` |
| `story.model` | `gpt-4o-mini` | OpenAI-Modell |
| `voice.provider` | `elevenlabs` | `elevenlabs` oder `gtts` |
| `video.fps` | `30` | Frames per second |
| `video.crf` | `23` | Qualität (18=hoch, 28=niedrig) |
| `audio.music_volume` | `0.15` | Musik-Lautstärke (0.0–1.0) |
| `subtitles.words_per_line` | `4` | Wörter pro Untertitel-Zeile |

---

## Kostenloser Modus (ohne API Keys)

Wechsle die Provider in `config.json`:
```json
{
  "story": { "provider": "mock" },
  "voice": { "provider": "gtts" }
}
```
- `mock`: Generiert eine Beispiel-Story (kein API Key benötigt)
- `gtts`: Google Text-to-Speech (kostenlos, etwas schlechtere Qualität)

---

## Projektstruktur

```
Brainrot/
├── backend/                    # Python FastAPI Backend
│   ├── main.py                 # API Server & Job-Verarbeitung
│   ├── config.py               # Konfiguration
│   ├── requirements.txt
│   └── modules/
│       ├── story_generator.py  # OpenAI/Claude Story-KI
│       ├── voice_generator.py  # ElevenLabs/gTTS Stimme
│       ├── subtitle_generator.py # ASS-Untertitel
│       ├── background_selector.py # Video-Auswahl
│       ├── audio_mixer.py      # FFmpeg Audio-Mix
│       ├── video_renderer.py   # FFmpeg Video-Render
│       ├── export_manager.py   # Output-Verwaltung
│       └── tiktok_uploader.py  # Platzhalter (Version 2)
│
├── frontend/                   # Next.js Frontend
│   └── src/
│       ├── app/page.tsx        # Hauptseite
│       ├── components/
│       │   ├── VideoCreator.tsx # Formular
│       │   └── JobQueue.tsx    # Job-Übersicht
│       └── lib/
│           ├── api.ts          # API-Client
│           └── types.ts        # TypeScript-Typen
│
├── assets/
│   ├── backgrounds/            # ← Eigene Hintergrundvideos hier ablegen
│   ├── music/                  # ← Hintergrundmusik hier ablegen
│   └── sfx/                    # ← Soundeffekte hier ablegen
│
├── output/                     # Fertige Videos
├── config.json                 # Haupt-Konfiguration
├── .env                        # API Keys (lokal, nicht im Git)
├── .env.example                # Vorlage
└── start.bat                   # Windows Start-Skript
```

---

## Video-Pipeline

```
Eingabe
  │
  ▼
[1] Story-KI (OpenAI/Claude)
      → Deutsche Brainrot-Story mit Hook + Cliffhanger
  │
  ▼
[2] Stimmen-KI (ElevenLabs)
      → MP3 Sprachausgabe
  │
  ▼
[3] Untertitel-Generator
      → ASS-Datei mit TikTok-Styling
  │
  ▼
[4] Hintergrundvideo-Auswahl
      → Zufälliger Clip aus /assets/backgrounds
  │
  ▼
[5] Audio-Mixer (FFmpeg)
      → Stimme + optionale Musik gemischt
  │
  ▼
[6] Video-Renderer (FFmpeg)
      → 1080x1920 MP4 mit Untertiteln
  │
  ▼
[7] Export
      → /output/brainrot_DATUM_IDEE.mp4
```

---

## Kosten-Übersicht

| Service | Kosten | Hinweis |
|---|---|---|
| OpenAI GPT-4o-mini | ~0,01€/Video | günstigstes Modell |
| ElevenLabs | ~0,02€/Video | 10.000 Zeichen kostenlos/Monat |
| gTTS | kostenlos | Qualität geringer |
| FFmpeg | kostenlos | Open Source |

---

## Troubleshooting

**"FFmpeg nicht gefunden"**  
→ FFmpeg installieren und bin/-Ordner zum Windows PATH hinzufügen → Neustart des Terminals

**"Keine Hintergrundvideos gefunden"**  
→ MP4-Dateien in `assets/backgrounds/` legen

**"ElevenLabs Fehler 401"**  
→ `ELEVENLABS_API_KEY` in `.env` prüfen

**"OpenAI Fehler 429"**  
→ Rate Limit erreicht, kurz warten oder auf `gpt-3.5-turbo` wechseln

**Backend startet nicht**  
→ Python-Version prüfen: `python --version` (mind. 3.10)  
→ Pakete neu installieren: `pip install -r backend/requirements.txt`

---

## Version 2 (geplant)

- [ ] TikTok Auto-Upload
- [ ] Batch-Verarbeitung (mehrere Videos gleichzeitig)
- [ ] Whisper für präzise Untertitel-Synchronisation
- [ ] SFX automatisch an Spannungsmomenten
- [ ] Video-Vorschau im Browser
- [ ] Scheduling / Auto-Post

---

## Lizenz

Nur für privaten, persönlichen Gebrauch.  
Stelle sicher, dass alle verwendeten Hintergrundvideos und Musikdateien lizenzfrei oder selbst erstellt sind.
