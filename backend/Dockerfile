# CareerAI backend — FastAPI + SQLAlchemy + scikit-learn
# Build from the repo root:  docker build -t careerai-backend ./backend
# Or with Compose (recommended):  docker compose up --build
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# psycopg[binary] needs no build tools, but pdfplumber/pdfminer and
# cryptography wheels are prebuilt for cp312; keep the image slim by
# installing only curl (healthcheck) at the OS level.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Optional: spaCy's small English model improves skill extraction.
# The app falls back to a blank pipeline if it is missing, so a failed
# download must not break the build.
RUN python -m spacy download en_core_web_sm || true

COPY . .

# Train the 6-role demo model at BUILD time (same step render.yaml runs).
# The container then starts instantly and needs no training data at runtime.
# Requires backend/data/synthetic_career_data.csv (copied with the context).
RUN python ml_pipeline/train_model.py

# Writable runtime dirs (SQLite file + resume uploads live here).
RUN mkdir -p uploads && chmod 777 uploads

# Run as a non-root user; the SQLite DB file is created on first start.
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Render / Compose pass PORT; default to 8000 for `docker run` without it.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
