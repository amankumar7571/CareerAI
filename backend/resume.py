from pathlib import Path

import pdfplumber
import docx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import models
from config import get_settings
from database import get_db
from auth import get_current_user
from nlp_service import extract_skills_from_text
from storage import cleanup_local_temp, persist_upload, prepare_upload

router = APIRouter()

settings = get_settings()
UPLOAD_DIR = settings.upload_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    safe_name = Path(file.filename).name if file.filename else ""
    if not safe_name.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed.")

    prepared_upload = prepare_upload(file, current_user.user_id)

    extracted_text = ""
    try:
        if safe_name.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(str(prepared_upload.temp_path))
        elif safe_name.lower().endswith(".docx"):
            extracted_text = extract_text_from_docx(str(prepared_upload.temp_path))
    except Exception as e:
        cleanup_local_temp(prepared_upload)
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

    stored_file_path = persist_upload(prepared_upload)

    new_resume = models.Resume(
        user_id=current_user.user_id,
        file_path=stored_file_path,
        parsed_text=extracted_text
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    # Run NLP skills extraction
    extracted_skills = extract_skills_from_text(extracted_text)
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "resume_id": new_resume.resume_id,
        "extracted_skills": extracted_skills,
        "parsed_text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
    }
