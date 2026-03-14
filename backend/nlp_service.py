import os
import json
from typing import List
import google.generativeai as genai

# Try loading spacy; fallback gracefully so the server doesn't crash on import.
try:
    import spacy
    from spacy.matcher import PhraseMatcher
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        _nlp = spacy.blank("en")
    _SPACY_AVAILABLE = True
except ImportError:
    _nlp = None
    _SPACY_AVAILABLE = False

# Full list of skills recognizable by the system
MASTER_SKILLS: List[str] = [
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "React",
    "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "AWS", "Azure",
    "GCP", "Docker", "Kubernetes", "Machine Learning", "Deep Learning",
    "Data Science", "Artificial Intelligence", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "Git",
    "Agile", "Scrum", "Jira", "Linux", "Bash", "REST API", "GraphQL",
    "HTML", "CSS", "TailwindCSS", "Sass", "Redux", "Data Structures",
    "Algorithms", "Problem Solving", "Tableau", "Power BI", "Excel",
    "Statistics", "CI/CD",
]

# Build a lowercase → original-casing lookup once
_SKILL_LOOKUP = {s.lower(): s for s in MASTER_SKILLS}

def _simple_keyword_extract(text: str) -> List[str]:
    """
    Fast fallback: split text on word boundaries and look up known skills.
    Works even when spaCy is not installed.
    """
    text_lower = text.lower()
    found = set()
    for skill_lower, skill_orig in _SKILL_LOOKUP.items():
        if skill_lower in text_lower:
            found.add(skill_orig)
    return list(found)

def _spacy_keyword_extract(text: str) -> List[str]:
    """Uses spaCy PhraseMatcher when available; falls back to simple keyword search."""
    if not _SPACY_AVAILABLE or _nlp is None:
        return _simple_keyword_extract(text)
    try:
        matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
        patterns = [_nlp.make_doc(skill.lower()) for skill in MASTER_SKILLS]
        matcher.add("SKILLS", patterns)
        doc = _nlp(text.lower())
        matches = matcher(doc)
        found = set()
        for _, start, end in matches:
            span_text = doc[start:end].text.lower()
            original = _SKILL_LOOKUP.get(span_text)
            if original:
                found.add(original)
        return list(found)
    except Exception:
        return _simple_keyword_extract(text)

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from resume text.
    1st Priority: Use Gemini API for intelligent, context-aware extraction.
    2nd Priority: Fall back to spaCy or keyword exact match.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Falling back to keyword skill extraction.")
        return _spacy_keyword_extract(text)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an expert technical recruiter analyzing a resume. 
        Read the following resume text and deeply analyze it to extract all technical skills, programming languages, 
        tools, platforms, frameworks, soft skills, and domain knowledge present.
        
        Resume text:
        {text[:8000]} # Limit to 8k chars
        
        Respond with ONLY a valid JSON format matching this schema exactly:
        {{
            "extracted_skills": ["Skill 1", "Skill 2"]
        }}
        Do not include markdown borders or any other text.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        data = json.loads(response.text)
        skills = data.get("extracted_skills", [])
        
        # Merge with traditional keyword extraction to ensure nothing obvious was missed
        keyword_skills = _spacy_keyword_extract(text)
        merged = list(set(skills + keyword_skills))
        
        # Standardize capitalization where possible against MASTER_SKILLS
        final_list = []
        for s in merged:
            matched_master = _SKILL_LOOKUP.get(s.lower())
            final_list.append(matched_master if matched_master else s)
            
        return list(set(final_list))
        
    except Exception as e:
        print(f"Gemini API skill extraction failed: {e}. Falling back to keyword extraction.")
        return _spacy_keyword_extract(text)
