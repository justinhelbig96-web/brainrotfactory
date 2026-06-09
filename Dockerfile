# ── Build stage ───────────────────────────────────────────────────────────
FROM python:3.11-slim

# Install FFmpeg + system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Working dir = project root (so config.json is at /app/config.json
# and backend/ is at /app/backend/, matching local path expectations)
WORKDIR /app

# Install Python deps first (layer cache)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy project files (excluding frontend, assets etc. via .dockerignore)
COPY backend/ ./backend/
COPY config.json ./config.json

# Create required asset + output dirs
RUN mkdir -p assets/backgrounds assets/music assets/sfx output

# Expose port
EXPOSE 8000

# Start uvicorn from the backend directory
WORKDIR /app/backend
# PORT is injected by Railway at runtime; fallback to 8000 for local Docker
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
