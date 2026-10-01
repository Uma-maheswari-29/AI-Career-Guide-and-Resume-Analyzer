from flask import Blueprint, render_template, request

from services.resume_service import analyze_resume

resume_bp = Blueprint("resume", __name__, url_prefix="/resume")


@resume_bp.route("/", methods=["GET", "POST"])
def resume():
    result = None
    form = {"target_role": "Python Developer"}

    if request.method == "POST":
        form = {"target_role": request.form.get("target_role", "Python Developer")}
        file = request.files.get("resume")
        if not file or file.filename == "":
            result = {"error": "Please provide the required information."}
            return render_template("resume.html", result=result, form=form)

        try:
            result = analyze_resume(form["target_role"], file)
            result["status"] = "success"
        except ValueError:
            result = {"error": "We could not read this resume. Please upload a valid PDF or DOCX file."}
        except Exception as exc:  # pragma: no cover
            result = {"error": "We could not read this resume. Please upload a valid PDF or DOCX file."}
            print(f"Resume processing error: {exc}")

    return render_template("resume.html", result=result, form=form)
