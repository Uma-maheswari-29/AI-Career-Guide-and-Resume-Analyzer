import os

from flask import Flask, render_template

from routes.career_routes import career_bp
from routes.interview_routes import interview_bp
from routes.resume_routes import resume_bp
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    app.register_blueprint(career_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
