import json
import os
import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_text_from_file(file_storage):
    if file_storage is None:
        raise ValueError("No file provided")

    filename = file_storage.filename.lower()
    text = ""

    if filename.endswith(".pdf"):
        reader = PdfReader(file_storage)
        pages = reader.pages
        for page in pages:
            text += page.extract_text() or " "
    elif filename.endswith(".docx"):
        doc = Document(file_storage)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type")

    return text or ""


def normalize_tokens(text):
    return re.findall(r"[A-Za-z][A-Za-z+/#.-]*", text.lower())


def match_skills(resume_text, role_skills):
    tokens = set(normalize_tokens(resume_text))
    matched = []
    missing = []
    for skill in role_skills:
        skill_lower = skill.lower()
        if skill_lower in resume_text.lower():
            matched.append(skill)
        elif any(word in tokens for word in skill_lower.split()[:2]):
            matched.append(skill)
        else:
            missing.append(skill)
    return matched, missing


def calculate_ats(resume_text, role, role_skills):
    matched, missing = match_skills(resume_text, role_skills)
    keyword_match = max(50, min(98, 65 + (len(matched) * 8) - (len(missing) * 5)))
    skills_match = max(55, min(97, 70 + (len(matched) * 7) - (len(missing) * 6)))
    structure = 78 if "experience" in resume_text.lower() or "education" in resume_text.lower() else 65
    experience_relevance = 72 if "experience" in resume_text.lower() else 60
    project_relevance = 80 if "project" in resume_text.lower() or "portfolio" in resume_text.lower() else 70
    education = 92 if "bachelor" in resume_text.lower() or "degree" in resume_text.lower() or "education" in resume_text.lower() else 80

    return {
        "overall": round((keyword_match + skills_match + structure + experience_relevance + project_relevance + education) / 6),
        "keyword_match": min(100, keyword_match),
        "skills_match": min(100, skills_match),
        "resume_structure": structure,
        "experience_relevance": experience_relevance,
        "project_relevance": project_relevance,
        "education": education,
        "matched_skills": matched,
        "missing_skills": missing[:5],
    }


def build_resume_report(role, resume_text):
    role_data = load_json("careers.json")
    role_details = role_data.get(role, {"skills": ["Python", "SQL", "Flask", "Docker", "REST API"], "certifications": ["Python development", "Database technologies"]})
    role_skills = role_details.get("skills", [])
    matched_skills, missing_skills = match_skills(resume_text, role_skills)
    ats = calculate_ats(resume_text, role, role_skills)

    strengths = []
    if "python" in resume_text.lower():
        strengths.append("Clear Python-related experience")
    if "project" in resume_text.lower() or "portfolio" in resume_text.lower():
        strengths.append("Relevant project work is mentioned")
    if "education" in resume_text.lower() or "degree" in resume_text.lower():
        strengths.append("Education information is included")
    if not strengths:
        strengths = ["Resume includes enough text to perform a basic ATS review"]

    improvements = []
    if missing_skills:
        improvements.append(f"Add role-specific keywords like {', '.join(missing_skills[:3])}")
    if "project" not in resume_text.lower():
        improvements.append("Include a project section with technologies and measurable impact")
    if "skills" not in resume_text.lower():
        improvements.append("Add a dedicated skills section that matches the target role")
    if not improvements:
        improvements = ["Keep the resume concise and emphasize measurable outcomes"]

    certifications = role_details.get("certifications", ["Python development", "Database technologies"])

    return {
        "role": role,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "certification_areas": certifications,
        "ats": ats,
        "strengths": strengths,
        "improvements": improvements,
        "resume_summary": {
            "length_chars": len(resume_text),
            "preview": resume_text[:300].replace("\n", " ")
        },
    }


def analyze_resume(role, file_storage):
    text = extract_text_from_file(file_storage)
    return build_resume_report(role, text)
