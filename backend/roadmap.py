import os
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
import models
from auth import get_current_user

# Load env variables (for GEMINI_API_KEY)
load_dotenv()

router = APIRouter()

# Static Fallbacks in case API fails or key is missing
SKILLS_MAP = {
    "Software Engineer": ["Java", "C++", "Python", "Problem Solving", "Data Structures", "Algorithms", "Git", "SQL"],
    "Data Scientist": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Tableau", "Statistics"],
    "Frontend Developer": ["JavaScript", "HTML", "CSS", "React", "Vue", "TypeScript", "TailwindCSS"],
    "Backend Developer": ["Python", "Java", "Node.js", "Express", "Django", "SQL", "PostgreSQL", "REST API", "Docker"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "AWS", "SQL"],
    "DevOps Engineer": ["Linux", "Bash", "Docker", "Kubernetes", "AWS", "Azure", "Git", "CI/CD"],
    "Data Analyst": ["SQL", "Excel", "Tableau", "Power BI", "Python", "Statistics", "Data Cleaning"]
}

COURSE_RECOMMENDATIONS = {
    "Java": {"course": "Java Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=Java+full+course+playlist"},
    "Python": {"course": "Python Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=Python+full+course+playlist"},
    "React": {"course": "React Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=React+full+course+playlist"},
    "Machine Learning": {"course": "Machine Learning Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=Machine+Learning+full+course+playlist"},
    "Docker": {"course": "Docker Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=Docker+full+course+playlist"},
    "AWS": {"course": "AWS Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=AWS+full+course+playlist"},
    "SQL": {"course": "SQL Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=SQL+full+course+playlist"},
    "JavaScript": {"course": "JavaScript Full Course Playlist", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=JavaScript+full+course+playlist"},
}

def get_static_roadmap(predicted_role: str, user_skills: List[str]):
    required_skills = set(SKILLS_MAP.get(predicted_role, ["Python", "SQL", "Git", "Communication"]))
    current_skills = set(user_skills)
    
    required_lower = {s.lower(): s for s in required_skills}
    current_lower = {s.lower() for s in current_skills}

    missing_keys = set(required_lower.keys()) - current_lower
    missing_skills = [required_lower[k] for k in missing_keys]

    courses = []
    for skill in missing_skills:
        fallback = {"course": f"{skill} Full Course Playlist", "platform": "YouTube", "url": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+full+course+playlist"}
        courses.append({
            "skill": skill,
            **COURSE_RECOMMENDATIONS.get(skill, fallback)
        })

    match_pct = round((len(required_skills) - len(missing_skills)) / len(required_skills) * 100, 1) if required_skills else 0

    return {
        "role": predicted_role,
        "required_skills": sorted(list(required_skills)),
        "existing_skills": sorted(list(current_skills)),
        "missing_skills": sorted(missing_skills),
        "recommended_courses": courses,
        "match_percentage": match_pct
    }


@router.post("/generate")
def generate_roadmap(
    predicted_role: str = Query(..., description="The predicted career role"),
    user_skills: List[str] = Body(..., description="List of the user's current skills"),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a personalized learning roadmap based on the predicted career role
    and the user's current skill set. Tries to use Gemini API for dynamic generation,
    and falls back to static mappings if it fails.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Using static roadmap fallback.")
        return get_static_roadmap(predicted_role, user_skills)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Act as an expert AI Career Coach. The user is aspiring to become a '{predicted_role}'.
        Their current skillset is: {', '.join(user_skills) if user_skills else 'None'}.
        
        Analyze what core skills are required for a '{predicted_role}', identify which ones the user is missing, and recommend the best specific online courses for them to bridge this gap.
        
        You MUST respond with a valid JSON format EXACTLY matching this schema:
        {{
            "required_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5", "Skill 6", "Skill 7", "Skill 8"],
            "missing_skills_analysis": [
                {{
                    "skill": "Missing Skill 1",
                    "course": "Name of highly-rated YouTube full course playlist",
                    "platform": "YouTube",
                    "url": "A YouTube search URL exactly like this: https://www.youtube.com/results?search_query=Skill+Name+full+course+playlist",
                    "duration": "Estimated time to complete"
                }}
            ]
        }}
        Do not include markdown blocks or any other text, just the raw JSON.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        data = json.loads(response.text)
        
        required_skills = set(data.get("required_skills", []))
        current_skills = set(user_skills)
        
        # Determine exact missing skills based on Gemini's required skills
        required_lower = {s.lower(): s for s in required_skills}
        current_lower = {s.lower() for s in current_skills}
        missing_keys = set(required_lower.keys()) - current_lower
        exact_missing_skills = [required_lower[k] for k in missing_keys]
        
        # Calculate match percentage
        match_pct = round((len(required_skills) - len(exact_missing_skills)) / len(required_skills) * 100, 1) if required_skills else 0
        
        return {
            "role": predicted_role,
            "required_skills": sorted(list(required_skills)),
            "existing_skills": sorted(list(current_skills)),
            "missing_skills": sorted(exact_missing_skills),
            "recommended_courses": data.get("missing_skills_analysis", []),
            "match_percentage": match_pct
        }
        
    except Exception as e:
        print(f"Gemini API roadmap generation failed: {e}. Falling back to static.")
        return get_static_roadmap(predicted_role, user_skills)
