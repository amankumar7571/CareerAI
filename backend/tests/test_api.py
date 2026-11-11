"""Tests for the CareerAI backend: resume parsing, upload, and prediction.

Covers the two things the resume claims about this project:
  * "Wrote pytest unit tests for FastAPI endpoints and the parsing pipeline"
  * PDF/DOCX resume parsing with skill extraction

Run from backend/:  python -m pytest tests -v
No Gemini key or network needed; skill extraction uses the local fallback.
"""
import io
from pathlib import Path

import docx
import pytest

import models
from conftest import TEST_ENGINE, TestingSessionLocal
from prediction import (
    _build_display_match_scores,
    _compute_skill_match,
    load_artifacts,
)
from resume import extract_text_from_docx, extract_text_from_pdf

import prediction as prediction_module


def _make_docx_bytes(lines):
    """Build a small .docx in memory with the given text lines."""
    doc = docx.Document()
    for line in lines:
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


def _make_minimal_pdf_bytes(text: str) -> bytes:
    """Build a minimal one-page PDF containing `text` (valid xref table)."""
    esc = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({esc}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return bytes(out)


# ---------------------------------------------------------------------------
# App health
# ---------------------------------------------------------------------------


def test_root_returns_welcome(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to CareerAI API"}


# ---------------------------------------------------------------------------
# Parsing pipeline (pure functions, no auth / DB needed)
# ---------------------------------------------------------------------------


def test_extract_text_from_docx(tmp_path):
    path = tmp_path / "sample.docx"
    path.write_bytes(
        _make_docx_bytes(["Aman Kumar", "Python SQL React FastAPI", "Machine Learning"])
    )
    text = extract_text_from_docx(str(path))
    assert "Aman Kumar" in text
    assert "Python" in text


def test_extract_text_from_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    path.write_bytes(_make_minimal_pdf_bytes("Python SQL Machine Learning"))
    text = extract_text_from_pdf(str(path))
    assert "Python" in text
    assert "SQL" in text


# ---------------------------------------------------------------------------
# Resume upload endpoint
# ---------------------------------------------------------------------------


def test_upload_rejects_non_resume_file(client):
    resp = client.post(
        "/api/resume/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
    assert "Only PDF or DOCX" in resp.json()["detail"]


def test_upload_docx_succeeds_and_extracts_skills(client):
    docx_bytes = _make_docx_bytes(
        ["Aman Kumar", "Python SQL React FastAPI", "Machine Learning"]
    )
    resp = client.post(
        "/api/resume/upload",
        files={
            "file": (
                "resume.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["message"] == "Resume uploaded and parsed successfully"
    assert body["resume_id"]
    assert "Aman Kumar" in body["parsed_text_preview"]
    # Keyword fallback (no Gemini key in tests) must still find the skills.
    assert "Python" in body["extracted_skills"]
    assert "SQL" in body["extracted_skills"]

    # The resume row really landed in the database.
    with TestingSessionLocal() as db:
        row = db.query(models.Resume).filter(
            models.Resume.resume_id == body["resume_id"]
        ).first()
    assert row is not None
    assert "Aman Kumar" in row.parsed_text


def test_upload_pdf_succeeds(client):
    pdf_bytes = _make_minimal_pdf_bytes("Python SQL Machine Learning")
    resp = client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert resp.status_code == 200, resp.text
    assert "Python" in resp.json()["parsed_text_preview"]


def test_upload_without_token_is_rejected(bare_client):
    resp = bare_client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Prediction helpers (pure functions)
# ---------------------------------------------------------------------------


def test_skill_match_full_and_partial():
    all_sde = [
        "Java", "C++", "Python", "Problem Solving",
        "Data Structures", "Algorithms", "Git", "SQL",
    ]
    assert _compute_skill_match("Software Engineer", all_sde) == 100.0
    assert _compute_skill_match("Software Engineer", ["Python"]) == 12.5
    assert _compute_skill_match("Unknown Role", all_sde) == 0.0


def test_display_match_scores_empty_and_floor():
    assert _build_display_match_scores([], ["Python"]) == []
    # 2 of 7 Data Analyst core skills -> 28.6
    scored = _build_display_match_scores([("Data Analyst", 0.9)], ["Python", "SQL"])
    assert scored[0][0] == "Data Analyst"
    assert scored[0][2] == pytest.approx(28.6)
    # Zero overlap but non-zero model probability gets the 0.1 display floor.
    scored = _build_display_match_scores([("DevOps Engineer", 0.5)], ["Cooking"])
    assert scored[0][2] == 0.1


# ---------------------------------------------------------------------------
# Prediction endpoint: model artifacts are gitignored and regenerated with
# ml_pipeline/train_model.py, so a fresh clone must fail cleanly (500),
# not crash. If artifacts ARE present, a real prediction must work.
# ---------------------------------------------------------------------------


def test_predict_endpoint(client):
    load_artifacts()
    has_model = (
        prediction_module.model is not None
        and prediction_module.feature_names is not None
        and prediction_module.label_encoder is not None
    )
    resp = client.post("/api/prediction/predict", json=["Python", "SQL", "React"])
    if not has_model:
        assert resp.status_code == 500
        assert "Model artifacts not loaded" in resp.json()["detail"]
    else:
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["top_prediction"]
        assert 0.0 <= body["confidence_score"] <= 1.0
        assert len(body["enriched_roles"]) >= 1
