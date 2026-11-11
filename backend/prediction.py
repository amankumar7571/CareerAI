from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import numpy as np
import pickle
import os

import models
from database import get_db
from auth import get_current_user

router = APIRouter()

# Global variables for the ML artifacts
model = None
feature_names = None
label_encoder = None

# Core skills per role (mirrors generate_data.py) — used for independent match scoring
SKILLS_MAP = {
    "Software Engineer": ["Java", "C++", "Python", "Problem Solving", "Data Structures", "Algorithms", "Git", "SQL"],
    "Data Scientist": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Tableau", "Statistics"],
    "Frontend Developer": ["JavaScript", "HTML", "CSS", "React", "Vue", "TypeScript", "TailwindCSS"],
    "Backend Developer": ["Python", "Java", "Node.js", "Express", "Django", "SQL", "PostgreSQL", "REST API", "Docker"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "AWS", "SQL"],
    "DevOps Engineer": ["Linux", "Bash", "Docker", "Kubernetes", "AWS", "Azure", "Git", "CI/CD"],
    "Data Analyst": ["Python", "SQL", "Pandas", "Tableau", "Excel", "Statistics", "NumPy"],
}


def _compute_skill_match(role: str, user_skills: list[str]) -> float:
    """Return a 0-100 match score: what % of the role's core skills the user has."""
    core_skills = SKILLS_MAP.get(role)
    if not core_skills:
        return 0.0
    lower_user = [s.lower() for s in user_skills]
    matched = sum(1 for s in core_skills if s.lower() in lower_user)
    return round(matched / len(core_skills) * 100, 1)


def _build_display_match_scores(top_roles, user_skills: list[str]):
    """Build display scores using independent skill-overlap percentages (0-100 each)."""
    if not top_roles:
        return []

    display_scores = []
    for role, prob in top_roles:
        score = _compute_skill_match(role, user_skills)
        if score == 0 and prob > 0:
            score = 0.1  # tiny floor so the bar isn't empty
        display_scores.append((role, prob, min(score, 100.0)))

    return display_scores


def load_artifacts():
    global model, feature_names, label_encoder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "career_model.pkl")
    features_path = os.path.join(base_dir, "career_model_features.pkl")
    encoder_path = os.path.join(base_dir, "career_roles_encoder.pkl")

    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    if os.path.exists(features_path):
        with open(features_path, "rb") as f:
            feature_names = pickle.load(f)
    if os.path.exists(encoder_path):
        with open(encoder_path, "rb") as f:
            label_encoder = pickle.load(f)

# Initialize on startup
load_artifacts()

@router.post("/predict")
def predict_career(
    skills: List[str] = Body(..., description="List of skill strings"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not model or not feature_names or not label_encoder:
        raise HTTPException(status_code=500, detail="Model artifacts not loaded on the server.")

    # Construct an input DataFrame mapping 1 or 0 for the user's available skills
    input_vector = {}

    # Inject CGPA. Default 7.0 if not set.
    input_vector["CGPA"] = current_user.cgpa if current_user.cgpa else 7.0
    input_vector["Project_Count"] = 2

    lower_skills = [s.lower() for s in skills]
    for feat in feature_names:
        if feat in ["CGPA", "Project_Count"]:
            continue
        # One-hot skills vector (case-insensitive)
        input_vector[feat] = 1 if feat.lower() in lower_skills else 0

    df_input = pd.DataFrame([input_vector], columns=feature_names)

    # Predict probabilities
    probabilities = model.predict_proba(df_input)[0]

    # Match probabilities to classes
    classes = label_encoder.classes_
    role_probs = [(classes[i], float(prob)) for i, prob in enumerate(probabilities)]

    # Sort descending
    role_probs = sorted(role_probs, key=lambda x: x[1], reverse=True)

    # Save the top prediction to DB
    top_role, top_score = role_probs[0]

    prediction_record = models.Prediction(
        user_id=current_user.user_id,
        predicted_role=top_role,
        confidence_score=top_score
    )
    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)
    
    # Take the top N (up to 3) roles for UI recommendations.
    top_3_roles = role_probs[:3]
    display_top_3_roles = _build_display_match_scores(top_3_roles, skills)
    role_names_only = [r for r, _, _ in display_top_3_roles]
    
    enriched_results = []
    
    # NOTE: this system states no salary or job-growth figures. The paper
    # (ICCISS 2027, Sec. VIII) treats that as a requirement, not a
    # limitation: the system has no sourced data for any such figure, and
    # a recommender that fabricates labour-market statistics causes harm
    # in proportion to how much it is trusted. Hardcoded USD ranges that
    # used to live here were removed for that reason (see MODEL_CARD.md).
    
    import google.generativeai as genai
    import json
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            genai_model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert AI Career Counselor.
            The user has these skills: {', '.join(skills)}.
            Our base ML model identified these top career matches: {', '.join(role_names_only)}.
            
            For EACH of these {len(role_names_only)} roles, provide a
            2-sentence personalized description of why this role fits
            their specific skills. Do NOT include any salary range, job
            growth or demand figure: this system states no labour-market
            statistics it cannot source.
            
            Respond with ONLY a valid JSON format EXACTLY matching this schema:
            {{
                "careers": [
                    {{
                        "role": "Role Name",
                        "description": "Personalized description...",
                    }}
                ]
            }}
            Do not include markdown borders or any other text.
            """
            
            response = genai_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            
            # Map generative data back to probability scores
            data = json.loads(response.text)
            generative_careers = data.get("careers", [])
            
            for base_role, raw_prob, display_score in display_top_3_roles:
                # Find matching generated data
                gen_data = next((c for c in generative_careers if c.get("role") == base_role), None)
                if gen_data:
                    enriched_results.append({
                        "role": base_role,
                        "confidence_score": raw_prob,
                        "display_match_score": display_score,
                        "description": gen_data.get("description", f"A great match based on your skills in {', '.join(skills[:3])}."),
                    })
                else:
                    enriched_results.append({
                        "role": base_role,
                        "confidence_score": raw_prob,
                        "display_match_score": display_score,
                        "description": f"Based on your extracted skills, our AI has determined this is a strong career path for your profile.",
                    })
        except Exception as e:
            print(f"Gemini API Career Enrichment failed: {e}. Falling back to default descriptions.")
            # Fallback inner loop on exception
            for base_role, raw_prob, display_score in display_top_3_roles:
                enriched_results.append({
                    "role": base_role,
                    "confidence_score": raw_prob,
                    "display_match_score": display_score,
                    "description": f"Based on your extracted skills, our AI has determined this is a strong career path for your profile.",
                })
    else:
        # Fallback if no API key
        for base_role, raw_prob, display_score in display_top_3_roles:
            enriched_results.append({
                "role": base_role,
                "confidence_score": raw_prob,
                "display_match_score": display_score,
                "description": f"Based on your extracted skills, our AI has determined this is a strong career path for your profile.",
            })

    return {
        "prediction_id": prediction_record.prediction_id,
        "top_prediction": top_role,
        "confidence_score": top_score,
        "enriched_roles": enriched_results,
        "all_probabilities": [{"role": r, "probability": p} for r, p in role_probs]
    }
