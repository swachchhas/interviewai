# app/blueprints/main/routes.py
from flask import Blueprint, render_template, request, session, flash, jsonify, redirect
from app.ai_client import generate_questions_with_model
from app.config import Config

users_db = {}
main_bp = Blueprint("main", __name__)

MAX_RESUME_LENGTH = 1500  # same as frontend truncation

# Homepage
@main_bp.route("/", methods=["GET"])
def index():
    user_logged_in = 'user' in session
    user_name = session.get('user', '')
    return render_template("index.html", user_logged_in=user_logged_in, user_name=user_name)

# Upload resume
@main_bp.route("/upload", methods=["POST"])
def upload():
    if "resume_file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    file = request.files["resume_file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    try:
        resume_text = file.read().decode("utf-8", errors="ignore")
        if len(resume_text) > MAX_RESUME_LENGTH:
            resume_text = resume_text[:MAX_RESUME_LENGTH] + "\n\n[Truncated resume]"
        return jsonify({"resume_text": resume_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Generate AI questions with multi-model fallback
@main_bp.route("/generate_questions", methods=["POST"])
def generate_questions_route():
    try:
        data = request.get_json()
        resume = data.get("resume", "")
        role = data.get("role", "")
        skills = data.get("skills", "")
        years = data.get("years", "")

        if not resume:
            return jsonify({"error": "No resume text provided."}), 400

        questions = []
        fallback_messages = []

        # Try all models in order
        for model_name in Config.MODELS:
            try:
                questions = generate_questions_with_model(
                    resume, role, skills, years, model_name=model_name
                )
                fallback_messages.append(f"Used model: {model_name}")
                if questions and not questions[0].startswith("Error"):
                    break
            except Exception as e:
                fallback_messages.append(f"Model {model_name} failed: {str(e)}")
                continue

        if not questions:
            questions = ["No questions generated. Please try again."]

        return jsonify({
            "questions": questions,
            "fallback_messages": fallback_messages
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Sign Up
@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Username and password are required!", "error")
            return redirect('/signup')
        if username in users_db:
            flash("Username already exists!", "error")
            return redirect('/signup')
        users_db[username] = password
        flash(f"Account created for {username}!", "success")
        return redirect('/signin')
    return render_template('signup.html')

# Sign In
@main_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Username and password are required!", "error")
            return redirect('/signin')
        if users_db.get(username) == password:
            session['user'] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect("/")
        else:
            flash("Invalid username or password!", "error")
            return redirect('/signin')
    return render_template('signin.html')

# Logout
@main_bp.route('/logout')
def logout():
    user = session.pop('user', None)
    if user:
        flash(f"Goodbye, {user}!", "success")
    return redirect("/")
