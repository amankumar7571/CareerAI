import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from config import get_settings

try:
    import boto3
except ImportError:
    boto3 = None


settings = get_settings()
TEMP_UPLOAD_DIR = settings.upload_dir / "_tmp"


@dataclass
class PreparedUpload:
    safe_name: str
    storage_name: str
    temp_path: Path
    content_type: str | None


def _build_storage_name(user_id: int, safe_name: str) -> str:
    return f"{user_id}_{uuid4().hex}_{safe_name}"


def prepare_upload(file: UploadFile, user_id: int) -> PreparedUpload:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    safe_name = Path(file.filename).name
    storage_name = _build_storage_name(user_id, safe_name)

    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = TEMP_UPLOAD_DIR / storage_name

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return PreparedUpload(
        safe_name=safe_name,
        storage_name=storage_name,
        temp_path=temp_path,
        content_type=file.content_type,
    )


def _build_s3_client():
    if boto3 is None:
        raise HTTPException(status_code=500, detail="S3 storage requires boto3 to be installed.")

    client_kwargs = {}
    if settings.s3_region:
        client_kwargs["region_name"] = settings.s3_region
    if settings.s3_endpoint_url:
        client_kwargs["endpoint_url"] = settings.s3_endpoint_url
    if settings.s3_access_key_id:
        client_kwargs["aws_access_key_id"] = settings.s3_access_key_id
    if settings.s3_secret_access_key:
        client_kwargs["aws_secret_access_key"] = settings.s3_secret_access_key
    return boto3.client("s3", **client_kwargs)


def _persist_to_s3(upload: PreparedUpload) -> str:
    if not settings.s3_bucket_name:
        raise HTTPException(status_code=500, detail="S3 storage is enabled but S3_BUCKET_NAME is missing.")

    key = "/".join(part for part in [settings.s3_key_prefix, upload.storage_name] if part)
    extra_args = {"ContentType": upload.content_type} if upload.content_type else None

    client = _build_s3_client()
    upload_kwargs = {"Filename": str(upload.temp_path), "Bucket": settings.s3_bucket_name, "Key": key}
    if extra_args:
        upload_kwargs["ExtraArgs"] = extra_args
    client.upload_file(**upload_kwargs)
    cleanup_local_temp(upload)

    return f"s3://{settings.s3_bucket_name}/{key}"


def _persist_locally(upload: PreparedUpload) -> str:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    final_path = settings.upload_dir / upload.storage_name
    upload.temp_path.replace(final_path)
    return str(final_path)


def persist_upload(upload: PreparedUpload) -> str:
    try:
        if settings.uses_s3_storage:
            return _persist_to_s3(upload)
        return _persist_locally(upload)
    except HTTPException:
        cleanup_local_temp(upload)
        raise
    except Exception as exc:
        cleanup_local_temp(upload)
        raise HTTPException(status_code=500, detail=f"Failed to store uploaded resume: {exc}") from exc


def cleanup_local_temp(upload: PreparedUpload) -> None:
    if upload.temp_path.exists():
        upload.temp_path.unlink()
