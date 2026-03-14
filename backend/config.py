import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    def __init__(self) -> None:
        raw_database_url = os.getenv("DATABASE_URL", "sqlite:///./career_db.sqlite")
        self.database_url = _normalize_database_url(raw_database_url)
        self.jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY",
            "change-me-in-production-career-guidance",
        )
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7))
        )
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        raw_origins = os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        self.cors_allow_origins = ["*"] if raw_origins.strip() == "*" else _split_csv(raw_origins)

        self.storage_backend = os.getenv("STORAGE_BACKEND", "local").strip().lower()
        upload_dir = os.getenv("UPLOAD_DIR")
        self.upload_dir = Path(upload_dir) if upload_dir else BASE_DIR / "uploads"
        self.s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        self.s3_region = os.getenv("S3_REGION")
        self.s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")
        self.s3_access_key_id = os.getenv("S3_ACCESS_KEY_ID")
        self.s3_secret_access_key = os.getenv("S3_SECRET_ACCESS_KEY")
        self.s3_key_prefix = os.getenv("S3_KEY_PREFIX", "resumes").strip("/")

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def uses_s3_storage(self) -> bool:
        return self.storage_backend == "s3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
