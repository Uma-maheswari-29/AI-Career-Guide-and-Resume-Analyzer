import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_questions(company, role, job_description="", resume_text="", skill_gaps=None, question_count=5):
    interview_topics = load_json("interview_topics.json")
    skill_gaps = skill_gaps or []
    questions = []
    role_data = load_json("careers.json")
    role_skills = role_data.get(role, {}).get("skills", ["Python", "SQL", "REST API", "Flask"])

    base_questions = [
        {"category": "Technical", "difficulty": "Intermediate", "question": f"Explain the key differences between common Python data structures you would use in a {role} role."},
        {"category": "Project", "difficulty": "Intermediate", "question": "Describe a project you built and explain the architecture, trade-offs, and challenges you solved."},
        {"category": "Resume-Based", "difficulty": "Intermediate", "question": f"You have highlighted {role_skills[0] if role_skills else role} in your resume. How have you used it in your work or projects?"},
        {"category": "HR", "difficulty": "Easy", "question": "Tell me about yourself and why you are interested in this opportunity."},
        {"category": "Behavioral", "difficulty": "Intermediate", "question": "Describe a challenge you faced in a project and how you handled it."},
    ]

    for item in base_questions:
        questions.append({"id": len(questions) + 1, **item})

    if skill_gaps:
        for skill in skill_gaps[:2]:
            questions.append({
                "id": len(questions) + 1,
                "category": "Role-Specific",
                "difficulty": "Intermediate",
                "question": f"How would you improve your understanding of {skill} in a real-world {role} project?"
            })

    while len(questions) < max(1, int(question_count)):
        questions.append({
            "id": len(questions) + 1,
            "category": "Technical",
            "difficulty": "Intermediate",
            "question": f"Discuss the main technical considerations when designing a scalable application for a {role} project at {company}."
        })

    return questions[: max(1, int(question_count))]


def evaluate_answer(answer, question):
    answer_text = (answer or "").lower()
    score = 72
    correctness = 80
    relevance = 85
    completeness = 75
    clarity = 78

    if len(answer_text.split()) > 40:
        completeness += 10
    if any(word in answer_text for word in ["because", "example", "therefore", "first", "then", "also"]):
        clarity += 8
    if any(word in answer_text for word in ["api", "database", "project", "architecture", "testing", "debugging", "performance"]):
        correctness += 8
    if any(word in answer_text for word in ["i", "used", "implemented", "learned", "applied"]):
        relevance += 6

    score = max(55, min(98, round((correctness + relevance + completeness + clarity) / 4)))

    strengths = []
    if "project" in answer_text or "used" in answer_text:
        strengths.append("Relevant practical examples were included")
    if "because" in answer_text or "therefore" in answer_text:
        strengths.append("The explanation included reasoning and structure")
    if not strengths:
        strengths = ["The answer is clear and attempt-focused"]

    improvements = []
    if "api" not in answer_text and "database" not in answer_text:
        improvements.append("Add a concrete technical example")
    if len(answer_text.split()) < 30:
        improvements.append("Expand the answer with more detail and a practical example")
    if not improvements:
        improvements = ["Consider adding a brief real-world example to strengthen the answer"]

    return {
        "score": score,
        "correctness": min(100, correctness),
        "relevance": min(100, relevance),
        "completeness": min(100, completeness),
        "clarity": min(100, clarity),
        "strengths": strengths,
        "improvements": improvements,
    }


def build_report(company, role, all_answers):
    scores = [entry["score"] for entry in all_answers if isinstance(entry, dict) and "score" in entry]
    average_score = round(sum(scores) / len(scores)) if scores else 0
    strong_topics = ["Python", "Project explanation", "Communication"]
    weak_topics = ["REST APIs", "Flask", "Behavioral questions"]
    return {
        "company": company,
        "role": role,
        "questions": len(all_answers),
        "completed": len(all_answers),
        "average_score": average_score,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "recommended_preparation": [
            "Review REST APIs and HTTP fundamentals",
            "Practice Flask and project-based scenarios",
            "Work on behavioral question storytelling",
            "Complete another mock interview to track progress"
        ],
    }
