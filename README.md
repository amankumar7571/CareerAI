# CareerAI

CareerAI is an AI-powered career guidance web app that turns a resume into actionable next steps. Users upload a PDF or DOCX resume, the backend extracts skills with NLP, predicts the best-fit career roles with a trained machine learning model, and generates a personalized learning roadmap with recommended courses.

## Core Workflow

1. Upload a resume from the dashboard.
2. Extract recognizable skills using Gemini, spaCy, or keyword fallback logic.
3. Predict the strongest-fit career roles across six modeled paths.
4. Generate a roadmap that highlights missing skills and suggested learning resources.

## Architecture Snapshot

| Layer | Technology | Role |
| --- | --- | --- |
| Frontend | React 19, Vite 5, Tailwind CSS v4, shadcn/ui, React Router v7 | Landing page, auth flow, dashboard UI |
| Backend | FastAPI, SQLAlchemy 2.0, Uvicorn | REST API, auth, upload handling, roadmap generation |
| AI and NLP | Google Gemini 1.5 Flash, spaCy | Context-aware skill extraction and role enrichment |
| ML | scikit-learn | Career-role prediction from extracted skills |
| Data | SQLite (dev), PostgreSQL (prod), local uploads or S3 | Persistence for users, resumes, predictions, and files |

## Key Features

- JWT-based registration and login
- Resume upload with PDF and DOCX text extraction
- Skill extraction with a three-layer fallback pipeline
- Top career-role prediction from a trained ML model
- Personalized roadmap generation with missing-skill analysis
- Profile updates for CGPA, interests, and supporting context

## What The App Models

- 6 career roles: Software Engineer, Data Scientist, Frontend Developer, Backend Developer, Machine Learning Engineer, and DevOps Engineer
- 57 recognizable skills in the NLP layer
- 3 skill extraction paths: Gemini, spaCy PhraseMatcher, and keyword fallback

## Run Locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8000
```

Backend API: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend app: `http://localhost:5173`

## Project Structure

```text
career_guidance_system/
|-- backend/
|   |-- main.py
|   |-- auth.py
|   |-- user_profile.py
|   |-- resume.py
|   |-- prediction.py
|   |-- roadmap.py
|   |-- nlp_service.py
|   |-- models.py
|   |-- database.py
|   |-- ml_pipeline/
|   `-- requirements.txt
|-- frontend/
|   |-- index.html
|   |-- package.json
|   `-- src/
|       |-- App.jsx
|       |-- main.jsx
|       |-- pages/
|       `-- components/
`-- render.yaml
```

## API Flow

- `POST /api/auth/register` creates a new user with a hashed password.
- `POST /api/auth/login` returns a JWT bearer token.
- `GET /api/auth/me` returns the authenticated user profile.
- `POST /api/resume/upload` stores the resume, extracts text, and returns detected skills.
- `POST /api/prediction/predict` predicts the top role matches from extracted skills.
- `POST /api/roadmap/generate` builds the learning roadmap for a selected role.

## Deployment Notes

- `frontend/` can be deployed to Vercel.
- `backend/` can be deployed to Render.
- Use PostgreSQL in production instead of SQLite.
- Set `STORAGE_BACKEND=s3` with S3-compatible credentials for durable production uploads.
- Example environment files live in `backend/.env.example` and `frontend/.env.example`.
