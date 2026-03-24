
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from config import get_settings
from database import engine
import auth
import user_profile
import resume
import prediction
import roadmap

settings = get_settings()

# Create all tables in sqlite directly for local testing without migrations (for now).
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CareerAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user_profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["roadmap"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CareerAI API"}
