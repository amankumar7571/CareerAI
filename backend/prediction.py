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


def _build_display_match_scores(top_roles):
    if not top_roles:
        return []

    adjusted_probs = [prob + 0.01 for _, prob in top_roles]
    total = sum(adjusted_probs)
    display_scores = []
    allocated = 0

    for index, ((role, prob), adjusted_prob) in enumerate(zip(top_roles, adjusted_probs)):
        if index == len(top_roles) - 1:
            score = max(1, 100 - allocated)
        else:
            score = max(1, round((adjusted_prob / total) * 100))
            allocated += score
        display_scores.append((role, prob, min(score, 99 if len(top_roles) > 1 else 100)))

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
    display_top_3_roles = _build_display_match_scores(top_3_roles)
    role_names_only = [r for r, _, _ in display_top_3_roles]
    
    enriched_results = []
    
    ROLE_STATS = {
        "Software Engineer": {"salary": "$110k - $160k", "growth": "+22% (2025)"},
        "Data Scientist": {"salary": "$125k - $175k", "growth": "+36% (2025)"},
        "Frontend Developer": {"salary": "$90k - $140k", "growth": "+15% (2025)"},
        "Backend Developer": {"salary": "$100k - $150k", "growth": "+18% (2025)"},
        "Machine Learning Engineer": {"salary": "$135k - $185k", "growth": "+40% (2025)"},
        "DevOps Engineer": {"salary": "$115k - $165k", "growth": "+21% (2025)"},
        "Data Analyst": {"salary": "$75k - $110k", "growth": "+20% (2025)"}
    }
    
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
            
            For EACH of these {len(role_names_only)} roles, provide:
            1. A 2-sentence personalized description of why this role fits their specific skills.
            2. An estimated average Salary Range in USD (e.g., "$110k - $150k").
            3. A projected 2025 Job Growth percentage (e.g., "+15% (2025)").
            
            Respond with ONLY a valid JSON format EXACTLY matching this schema:
            {{
                "careers": [
                    {{
                        "role": "Role Name",
                        "description": "Personalized description...",
                        "salary_range": "$100k - $140k",
                        "growth": "+12% (2025)"
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
                        "salaryRange": gen_data.get("salary_range", ROLE_STATS.get(base_role, {}).get("salary", "$100k - $150k")),
                        "growth": gen_data.get("growth", ROLE_STATS.get(base_role, {}).get("growth", "+15% (2025)"))
                    })
                else:
                    enriched_results.append({
                        "role": base_role,
                        "confidence_score": raw_prob,
                        "display_match_score": display_score,
                        "description": f"Based on your extracted skills, our AI has determined this is a strong career path for your profile.",
                        "salaryRange": ROLE_STATS.get(base_role, {}).get("salary", "$120k - $160k"),
                        "growth": ROLE_STATS.get(base_role, {}).get("growth", "+18% (2025)")
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
                    "salaryRange": ROLE_STATS.get(base_role, {}).get("salary", "$120k - $160k"),
                    "growth": ROLE_STATS.get(base_role, {}).get("growth", "+18% (2025)")
                })
    else:
        # Fallback if no API key
        for base_role, raw_prob, display_score in display_top_3_roles:
            enriched_results.append({
                "role": base_role,
                "confidence_score": raw_prob,
                "display_match_score": display_score,
                "description": f"Based on your extracted skills, our AI has determined this is a strong career path for your profile.",
                "salaryRange": ROLE_STATS.get(base_role, {}).get("salary", "$120k - $160k"),
                "growth": ROLE_STATS.get(base_role, {}).get("growth", "+18% (2025)")
            })

    return {
        "prediction_id": prediction_record.prediction_id,
        "top_prediction": top_role,
        "confidence_score": top_score,
        "enriched_roles": enriched_results,
        "all_probabilities": [{"role": r, "probability": p} for r, p in role_probs]
    }
