import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_skills(skills):
    return {skill.strip().lower() for skill in skills if isinstance(skill, str) and skill.strip()}


def skill_group(role_skills, user_skills):
    existing = []
    partial = []
    missing = []
    normalized_user = normalize_skills(user_skills)
    normalized_role = [skill.strip() for skill in role_skills]

    for skill in normalized_role:
        skill_lower = skill.lower()
        if any(user_skill in skill_lower for user_skill in normalized_user):
            existing.append(skill)
        elif any(skill_lower in user_skill for user_skill in normalized_user):
            existing.append(skill)
        elif any(part in skill_lower for part in ["api", "docker", "aws", "git", "flask", "sql", "python", "testing"]):
            partial.append(skill)
        else:
            missing.append(skill)

    for skill in normalized_role:
        skill_lower = skill.lower()
        if skill_lower in normalized_user:
            continue
        if any(skill_lower in user_skill for user_skill in normalized_user):
            if skill not in existing:
                existing.append(skill)
            continue
        if any(user_skill in skill_lower for user_skill in normalized_user):
            if skill not in existing:
                existing.append(skill)
            continue
        if skill in partial:
            continue
        if skill not in missing:
            missing.append(skill)

    # improve classification by checking user skill fragments
    partial_candidates = []
    for skill in normalized_role:
        if skill in existing or skill in missing:
            continue
        partial_candidates.append(skill)
    partial = partial_candidates[: min(3, len(partial_candidates))]
    missing = [s for s in normalized_role if s not in existing and s not in partial]

    return {
        "existing": existing,
        "partially_known": partial,
        "missing": missing,
        "high_priority": missing[:4],
    }


def build_roadmap(role, available_time, experience_level, missing_skills):
    weekly_focus = missing_skills[:5] if missing_skills else ["Python fundamentals"]
    time_map = {
        "1 hour/day": "light plan with daily revision and fundamentals",
        "2 hours/day": "balanced plan with coding practice and one mini project",
        "3 hours/day": "intensive plan with practical tasks, projects, and practice",
    }
    base = time_map.get(available_time, "balanced plan with coding practice")
    roadmap = []
    for day in range(1, 31):
        topic = weekly_focus[(day - 1) % len(weekly_focus)]
        objective = f"Study {topic} and apply it to a small practical task"
        practice_hours = 1 if available_time == "1 hour/day" else 2 if available_time == "2 hours/day" else 2
        roadmap.append({
            "day": day,
            "topic": topic,
            "objective": objective,
            "practice_time": f"{practice_hours} hrs",
            "time_note": base,
            "experience_level": experience_level,
        })
    return roadmap


def prepare_resources(role, topics):
    resource_data = load_json("resources.json")
    role_resources = resource_data.get(role, {})
    result = []
    for topic in topics:
        resources = role_resources.get(topic, [])
        if not resources:
            resources = [{
                "name": f"{topic} learning guide",
                "url": "https://www.w3schools.com/",
                "description": "A reliable beginner-friendly reference"
            }]
        result.append({"topic": topic, "resources": resources})
    return result


def generate_career_analysis(data):
    role = data.get("target_role", "Python Developer")
    current_skills = data.get("current_skills", "")
    available_time = data.get("available_time", "2 hours/day")
    experience_level = data.get("experience_level", "Fresher")
    user_skill_list = [skill.strip() for skill in current_skills.split(",") if skill.strip()]

    role_data = load_json("careers.json")
    role_details = role_data.get(role, {
        "skills": ["Python", "SQL", "REST API", "Docker", "Git"],
        "certifications": ["Python development", "Cloud fundamentals"],
        "summary": "General role guidance"
    })

    gap = skill_group(role_details.get("skills", []), user_skill_list)
    roadmap = build_roadmap(role, available_time, experience_level, gap["missing"])
    resources = prepare_resources(role, gap["missing"][:5] or role_details.get("skills", [])[:5])

    return {
        "role": role,
        "current_skills": user_skill_list,
        "available_time": available_time,
        "experience_level": experience_level,
        "gap": gap,
        "roadmap": roadmap,
        "resources": resources,
        "certifications": role_details.get("certifications", ["Python development", "Database technologies"]),
        "summary": role_details.get("summary", "This role requires problem-solving, coding discipline, and practical project work."),
    }
