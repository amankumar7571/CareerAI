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

### Manual Setup

#### 1. Backend
```bash
cd backend
python -m venv venv
# Activate: .\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
# Copy .env.example to .env and add your GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔒 Security & Environment

CareerAI uses `.env` files for configuration. Ensure you never commit your `.env` file containing your `GEMINI_API_KEY`. 
See `backend/.env.example` and `frontend/.env.example` for the required structure.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

---
© 2026 CareerAI - Intelligent Career Planning
