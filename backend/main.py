import sys
import asyncio
import uuid
import shutil
from pathlib import Path
from typing import Optional

# Windows: use ProactorEventLoop for subprocess support
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import Config
from modules.story_generator import StoryGenerator
from modules.voice_generator import VoiceGenerator
from modules.subtitle_generator import SubtitleGenerator
from modules.background_selector import BackgroundSelector
from modules.audio_mixer import AudioMixer
from modules.video_renderer import VideoRenderer
from modules.export_manager import ExportManager

# ── App setup ──────────────────────────────────────────────────────────────

app = FastAPI(title="Brainrot Video Factory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()

# Serve finished videos
app.mount(
    "/output",
    StaticFiles(directory=str(config.output_dir), html=False),
    name="output",
)

# In-memory job store (sufficient for local single-user tool)
jobs: dict[str, dict] = {}


# ── Schemas ────────────────────────────────────────────────────────────────

class VideoRequest(BaseModel):
    idea: str
    duration: int = 60          # 30 | 60 | 90
    category: str = "Mystery"
    voice_id: Optional[str] = None
    subtitle_style: str = "tiktok"
    include_music: bool = True
    include_sfx: bool = False


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ffmpeg": _check_ffmpeg(),
        "backgrounds": len(BackgroundSelector(config).list_backgrounds()),
    }


@app.get("/config")
async def get_config():
    return config.get_public_config()


@app.get("/voices")
async def get_voices():
    vg = VoiceGenerator(config)
    return vg.get_available_voices()


@app.get("/backgrounds")
async def get_backgrounds():
    bs = BackgroundSelector(config)
    return bs.list_backgrounds()


@app.post("/generate")
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    if not request.idea.strip():
        raise HTTPException(status_code=400, detail="Idee darf nicht leer sein.")
    if request.duration not in (30, 60, 90):
        raise HTTPException(status_code=400, detail="Dauer muss 30, 60 oder 90 sein.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "step": "Wird vorbereitet...",
        "output_file": None,
        "error": None,
        "idea": request.idea,
        "category": request.category,
        "duration": request.duration,
    }
    background_tasks.add_task(_process_video, job_id, request)
    return {"job_id": job_id}


@app.get("/job/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job nicht gefunden.")
    return jobs[job_id]


@app.get("/jobs")
async def list_jobs():
    return sorted(jobs.values(), key=lambda j: j["job_id"], reverse=True)


@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job nicht gefunden.")
    job = jobs.pop(job_id)
    # Optionally delete the output file
    if job.get("output_file"):
        file_path = config.output_dir / job["output_file"]
        if file_path.exists():
            file_path.unlink()
    return {"deleted": job_id}


# ── Background processing ──────────────────────────────────────────────────

def _update(job_id: str, status: str, progress: int, step: str):
    if job_id in jobs:
        jobs[job_id].update({"status": status, "progress": progress, "step": step})


async def _process_video(job_id: str, req: VideoRequest):
    temp_dir = config.output_dir / f"temp_{job_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1 — Generate Story
        _update(job_id, "processing", 5, "Story wird generiert...")
        story_gen = StoryGenerator(config)
        story = await story_gen.generate(req.idea, req.duration, req.category)

        # 2 — Generate Voice
        _update(job_id, "processing", 20, "Stimme wird synthetisiert...")
        voice_gen = VoiceGenerator(config)
        voice_path = str(temp_dir / "voice.mp3")
        await voice_gen.generate(story["text"], voice_path, req.voice_id)

        # 3 — Generate Subtitles
        _update(job_id, "processing", 38, "Untertitel werden berechnet...")
        sub_gen = SubtitleGenerator(config)
        subtitle_path = str(temp_dir / "subtitles.ass")
        await sub_gen.generate(story["sentences"], voice_path, subtitle_path, req.subtitle_style)

        # 4 — Select Background
        _update(job_id, "processing", 48, "Hintergrundvideo wird ausgewählt...")
        bg_selector = BackgroundSelector(config)
        bg_path = str(bg_selector.select_random(req.category))

        # 5 — Mix Audio
        _update(job_id, "processing", 58, "Audio wird gemischt...")
        audio_mixer = AudioMixer(config)
        mixed_audio = str(temp_dir / "mixed.aac")
        await audio_mixer.mix(
            voice_path=voice_path,
            output_path=mixed_audio,
            include_music=req.include_music,
            include_sfx=req.include_sfx,
        )

        # 6 — Render Video
        _update(job_id, "processing", 72, "Video wird gerendert (FFmpeg)...")
        renderer = VideoRenderer(config)
        raw_output = str(temp_dir / "rendered.mp4")
        await renderer.render(
            bg_video=bg_path,
            audio=mixed_audio,
            subtitles=subtitle_path,
            output=raw_output,
        )

        # 7 — Export / Move to /output
        _update(job_id, "processing", 94, "Export wird finalisiert...")
        export_mgr = ExportManager(config)
        final_path = await export_mgr.finalize(raw_output, req.idea)

        # Cleanup temp folder
        shutil.rmtree(str(temp_dir), ignore_errors=True)

        jobs[job_id].update({
            "status": "done",
            "progress": 100,
            "step": "Fertig!",
            "output_file": Path(final_path).name,
        })

    except Exception as exc:
        shutil.rmtree(str(temp_dir), ignore_errors=True)
        jobs[job_id].update({
            "status": "error",
            "progress": 0,
            "step": "Fehler aufgetreten",
            "error": str(exc),
        })


# ── Helpers ────────────────────────────────────────────────────────────────

def _check_ffmpeg() -> bool:
    import subprocess
    try:
        r = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
