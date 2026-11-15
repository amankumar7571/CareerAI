# CareerAI 🚀

**CareerAI** is an intelligent career transition platform that transforms resumes into actionable learning roadmaps. By combining NLP-driven skill extraction with machine learning career matching, it helps users identify their strongest career paths and bridges the gap between their current skills and their next professional goal.

[![Technical Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20ML-blue)](https://github.com/amankumar7571/CareerAI)

## 🌟 Key Features

- **Intelligent Extraction**: PDF/DOCX resume parsing using a three-layer fallback (Gemini 1.5 Flash -> spaCy -> Keyword Matching).
- **Predictive Guidance**: Trained scikit-learn models to predict best-fit roles across 6 major tech paths.
- **Dynamic Roadmaps**: Personalized learning plans generated via AI, identifying missing skills and recommending specific learning resources.
- **Modern Stack**: Built with React 19 (Frontend) and FastAPI (Backend) for high-performance, real-time interactions.

## 🛠 Architecture

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite 5, Tailwind CSS v4, shadcn/ui, Lucid Icons |
| **Backend** | FastAPI, SQLAlchemy 2.0, Uvicorn |
| **AI/NLP** | Google Gemini 1.5 Flash, spaCy (en_core_web_sm) |
| **Machine Learning** | scikit-learn (Random Forest classification) |
| **Persistence** | SQLite (Development), PostgreSQL (Production) |

## 📄 Research Model (ICCISS 2027)

The system evaluated in our paper uses a **43-category TF-IDF + Platt-calibrated
linear SVM** on the ResumeAtlas corpus (13,389 documents → 11,507 deduplicated,
leakage-controlled split): **82.58% top-1 / 94.18% top-3 accuracy** in a 29.45 MB
artifact on two CPU cores. See [MODEL_CARD.md](MODEL_CARD.md) for metrics,
limitations and reproduction steps.

The pipeline code lives in `backend/ml_pipeline/resume_text_classifier.py`
(train with `python ml_pipeline/train_resume_classifier.py --data data/resumes.csv`).
The running demo in this repo uses a separate 6-role tabular model trained on
synthetic data (`backend/ml_pipeline/train_model.py`) — the two systems are
documented separately so the numbers are never mixed up.

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v18+)
- **Python** (v3.10+)
- **Gemini API Key** (Get it from [Google AI Studio](https://aistudio.google.com/))

### Fast Launch (Windows)

Simply run the launcher at the root:
```powershell
./start.ps1
# OR
./start.bat
```

### Run with Docker (recommended for a clean setup)

All free, no accounts needed — Docker Engine + Docker Compose only.

```bash
docker compose up --build
# Backend:  http://localhost:8000 (API docs at /docs)
# Frontend: http://localhost:3000
```

What Compose runs:
- `backend` — FastAPI on :8000 (see `backend/Dockerfile`; the 6-role demo
  model is trained at image-build time, so the container starts instantly).
- `frontend` — the Vite build served by nginx on :3000 (see
  `frontend/Dockerfile` + `frontend/nginx.conf`; SPA fallback included so
  /login, /register and /dashboard resolve client-side).

Data lives in named volumes (`careerai-data`, `careerai-uploads`) and
persists across restarts; `docker compose down -v` wipes it. The JWT secret
in Compose is a dev-only placeholder — never use it in production.

To point the frontend at a deployed backend, rebuild it with a different
build arg (the API URL is baked into the static bundle at build time):

```bash
docker compose build --build-arg VITE_API_BASE_URL=https://<your-backend>/ frontend
```

Individual images (from the repo root):

```bash
docker build -t careerai-backend ./backend
docker build -t careerai-frontend --build-arg VITE_API_BASE_URL=http://localhost:8000 ./frontend
```

### Manual Setup

#### 1. Backend
```bash
cd backend
python -m venv venv
# Activate: .\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
# Copy .env.example to .env and add your GEMINI_API_KEY
python -m uvicorn main:app --reload --reload-exclude uploads --port 8000
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔒 Security & Environment

CareerAI uses `.env` files for configuration. Ensure you never commit your `.env` file containing your `GEMINI_API_KEY` or `JWT_SECRET_KEY`.
See `backend/.env.example` and `frontend/.env.example` for the required structure.

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | No | `sqlite:///./career_db.sqlite` | Free default. Render free disk is ephemeral — data resets on redeploy. No managed/paid database is used. |
| `JWT_SECRET_KEY` | **Yes, in production** | `change-me-in-production-career-guidance` (dev only) | Must be a long random secret on any deployment. Render generates one via `render.yaml` (`generateValue: true`). |
| `JWT_ALGORITHM` | No | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` (7 days) | |
| `CORS_ALLOW_ORIGINS` | No | `http://localhost:5173,http://127.0.0.1:5173` | Set to the deployed frontend origin in production (comma-separated). |
| `GEMINI_API_KEY` | No | — | Optional. Unset = skill extraction falls back to local spaCy / keyword matching. |
| `STORAGE_BACKEND` | No | `local` | Keep `local`. S3 is not enabled — no cloud storage is used. |
| `UPLOAD_DIR` | No | `./uploads` | Local resume uploads. |

### Auth (JWT) — how it works

Login/signup is real, not a demo stub: passwords are bcrypt-hashed in
SQLite, and every feature endpoint requires a valid JWT.

| Endpoint | Auth | What it does |
|---|---|---|
| `POST /api/auth/register` | No | `{name, email, password}` → 201 with the new user (no password returned). Duplicate email → 400. |
| `POST /api/auth/login` | No | OAuth2 form (`username`=email, `password`) → `{access_token, token_type: "bearer"}`. Wrong credentials → 401. |
| `GET /api/auth/me` | Yes | Returns the current user from the token. No/invalid token → 401. |
| `PUT /api/profile/update`, `POST /api/resume/upload`, `POST /api/prediction/predict`, `POST /api/roadmap/generate` | Yes | All require `Authorization: Bearer <token>`. Without one they return 401. |

The frontend stores the token in `localStorage` after login
(`frontend/src/pages/Login.jsx`) and attaches
`Authorization: Bearer <token>` on every Dashboard request
(`frontend/src/pages/Dashboard.jsx`).

### Deploying (free tier only)

- **Backend → Render free web service:** connect the repo and deploy the
  `render.yaml` Blueprint. It sets `plan: free`, trains the demo model at
  build time, and generates a `JWT_SECRET_KEY` automatically. Then update
  `CORS_ALLOW_ORIGINS` to the frontend URL.
- **Frontend → Netlify free static site:** build with
  `VITE_API_BASE_URL=https://<your-render-backend-url>` and deploy the
  `dist/` folder (or connect the repo and let Netlify run `npm run build`).

## 🧪 Running Tests

Backend tests use pytest + FastAPI TestClient. No Gemini key or network is needed — skill extraction falls back to local keyword matching in tests.

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests -v
```

What is covered:
- Resume parsing pipeline (PDF and DOCX text extraction)
- `POST /api/resume/upload` — success, invalid-file rejection, and auth (401 without a token)
- Prediction helpers (skill-match scoring)
- `POST /api/prediction/predict` — clean 500 when model artifacts are missing (regenerate them with `python ml_pipeline/train_model.py`)
- Auth flow (`tests/test_auth.py`, real JWT — no dependency overrides): register 201, duplicate email 400, login returns a bearer token, wrong password / unknown email 401, `GET /api/auth/me` 200 with a token and 401 without one or with a bad one

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

---
© 2026 CareerAI - Intelligent Career Planning
