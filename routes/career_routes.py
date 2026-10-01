from flask import Blueprint, render_template, request

from services.career_service import generate_career_analysis

career_bp = Blueprint("career", __name__, url_prefix="/career")


@career_bp.route("/", methods=["GET", "POST"])
def career():
    analysis = None
    form = {
        "name": "",
        "target_role": "Python Developer",
        "current_skills": "Python, SQL, HTML, CSS",
        "available_time": "2 hours/day",
        "experience_level": "Fresher",
        "education": "",
        "projects": "",
        "preferred_learning_mode": "Self-paced",
    }

    if request.method == "POST":
        form = {
            "name": request.form.get("name", ""),
            "target_role": request.form.get("target_role", "Python Developer"),
            "current_skills": request.form.get("current_skills", ""),
            "available_time": request.form.get("available_time", "2 hours/day"),
            "experience_level": request.form.get("experience_level", "Fresher"),
            "education": request.form.get("education", ""),
            "projects": request.form.get("projects", ""),
            "preferred_learning_mode": request.form.get("preferred_learning_mode", "Self-paced"),
        }
        analysis = generate_career_analysis(form)

    return render_template("career.html", analysis=analysis, form=form)
