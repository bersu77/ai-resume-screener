import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from resume_parser import allowed_file, extract_text
from screener import screen_resume

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/screen", methods=["POST"])
def screen():
    if "resume" not in request.files:
        flash("No file uploaded.", "error")
        return redirect(url_for("index"))

    file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    if not job_description:
        flash("Please provide a job description.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        flash("Invalid file type. Please upload a PDF, DOCX, or TXT file.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    try:
        resume_text = extract_text(file_path)
        if not resume_text:
            flash("Could not extract text from the resume.", "error")
            return redirect(url_for("index"))

        result = screen_resume(resume_text, job_description)
        return render_template("result.html", result=result, filename=filename)

    except Exception as e:
        flash(f"Error processing resume: {str(e)}", "error")
        return redirect(url_for("index"))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
