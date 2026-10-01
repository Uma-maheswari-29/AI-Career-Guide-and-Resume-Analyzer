from flask import Blueprint, redirect, render_template, request, session, url_for

from services.interview_service import build_report, evaluate_answer, generate_questions

interview_bp = Blueprint("interview", __name__, url_prefix="/interview")


@interview_bp.route("/", methods=["GET"])
def interview_form():
    return render_template("interview.html", questions=[], current_question=None, current_index=0, total=0, report=None)


@interview_bp.route("/generate", methods=["POST"])
def generate():
    company = request.form.get("company", "")
    role = request.form.get("role", "Python Developer")
    job_description = request.form.get("job_description", "")
    difficulty = request.form.get("difficulty", "Intermediate")
    question_count = request.form.get("question_count", "5")
    resume_text = request.form.get("resume_text", "")
    skill_gaps = request.form.getlist("skill_gaps") or ["REST API", "Flask", "Docker"]

    questions = generate_questions(
        company=company,
        role=role,
        job_description=job_description,
        resume_text=resume_text,
        skill_gaps=skill_gaps,
        question_count=question_count,
    )

    session["company"] = company
    session["role"] = role
    session["interview_questions"] = questions
    session["current_index"] = 0
    session["history"] = []
    session["question_count"] = len(questions)

    current_question = questions[0] if questions else None
    return render_template(
        "interview.html",
        company=company,
        role=role,
        questions=questions,
        current_question=current_question,
        current_index=0,
        total=len(questions),
        report=None,
    )


@interview_bp.route("/submit", methods=["POST"])
def submit_answer():
    questions = session.get("interview_questions", [])
    if not questions:
        return redirect(url_for("interview.interview_form"))

    current_index = int(session.get("current_index", 0))
    answer = request.form.get("answer", "")
    question = questions[current_index]
    review = evaluate_answer(answer, question)

    history = session.get("history", [])
    history.append({"question": question["question"], "answer": answer, "review": review})
    session["history"] = history

    next_index = current_index + 1
    if next_index >= len(questions):
        report = build_report(session.get("company", "Unknown Company"), session.get("role", "Python Developer"), history)
        session["report"] = report
        return render_template("interview.html", company=session.get("company", ""), role=session.get("role", "Python Developer"), questions=questions, report=report, history=history, current_question=None, current_index=next_index, total=len(questions))

    session["current_index"] = next_index
    next_question = questions[next_index]
    return render_template(
        "interview.html",
        company=session.get("company", ""),
        role=session.get("role", "Python Developer"),
        questions=questions,
        current_question=next_question,
        current_index=next_index,
        total=len(questions),
        review=review,
        history=history,
        report=None,
    )
