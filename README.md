# AI Career Guidance System

An AI-powered career guidance platform that analyzes your resume, predicts ideal career matches using a trained ML model, and generates a personalized learning roadmap with skill gap analysis.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + Tailwind CSS v4 |
| Backend | FastAPI + SQLAlchemy + SQLite |
| ML | scikit-learn + pandas + spaCy |
| Auth | JWT (python-jose) + bcrypt |

## Features

- 🔐 **Auth** – JWT-based register/login
- 📄 **Resume Upload** – PDF & DOCX parsing with NLP skill extraction
- 🤖 **AI Career Prediction** – ML model predicts best-fit role from skills
- 🗺️ **Learning Roadmap** – Personalized skill-gap analysis with course recommendations
- 👤 **Profile Management** – Update CGPA & interests

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+

---

### Backend Setup

```bash
cd career_guidance_system/backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# (Optional) Download spaCy English model for better NLP
python -m spacy download en_core_web_sm

# Run the API server
uvicorn main:app --reload --port 8000
```

API will be available at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

### Frontend Setup

```bash
cd career_guidance_system/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

App will be available at: **http://localhost:5173**

---

## Deployment

Recommended production setup:

- Deploy `frontend/` to Vercel
- Deploy `backend/` to Render

### Vercel

- Root Directory: `frontend`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variable: `VITE_API_BASE_URL=https://your-backend-service.onrender.com`

### Render

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt && python ml_pipeline/train_model.py`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  - `JWT_SECRET_KEY`
  - `DATABASE_URL`
  - `CORS_ALLOW_ORIGINS=https://your-frontend-domain.vercel.app`
  - `GEMINI_API_KEY` (optional)

Example env files are included in `backend/.env.example` and `frontend/.env.example`.

---

## Project Structure

```
career_guidance_system/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── auth.py              # JWT authentication
│   ├── user_profile.py      # Profile management
│   ├── resume.py            # Resume upload & parsing
│   ├── prediction.py        # ML career prediction
│   ├── roadmap.py           # Skill gap & roadmap engine
│   ├── nlp_service.py       # NLP skill extraction
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # DB config & session
│   ├── schemas.py           # Pydantic schemas
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   └── Dashboard.jsx
    │   ├── App.jsx
    │   └── index.css        # Global + glassmorphism styles
    ├── index.html
    └── package.json
```

## Notes

- The SQLite database file (`career_db.sqlite`) is git-ignored and will be auto-created on first run.
- The pre-trained ML model `.pkl` files are git-ignored (large binaries). Re-train using `backend/ml_pipeline/` scripts if needed.
- User-uploaded resumes in `backend/uploads/` are git-ignored for privacy.
