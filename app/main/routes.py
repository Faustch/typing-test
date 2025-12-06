from flask import render_template, redirect, url_for, session, request,jsonify
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from datetime import datetime, UTC
from bson.objectid import ObjectId


from . import main_bp
from ..extensions import mongo

#FORMS
class TestConfigForm(FlaskForm):
    mode = SelectField(
        "Mode",
        choices = [("time", "Time (seconds)"), ("words", "Words")],
        default="time"
    )
    duration = SelectField(
        "Duration (for time mode)",
        choices=[("15", "15s"), ("30", "30s"), ("60", "60s")],
        default="30",
    )
    word_count = SelectField(
        "Word count (for words mode)",
        choices = [("25", "25 words"), ("50","50 words"), ("100", "100 words")],
        default="50"
    )
    submit = SubmitField("Save config")


#ROUTES
@main_bp.route("/")
def index():
    return render_template("main/index.html")

@main_bp.route("/test/config", methods=["GET", "POST"])
def test_config():
    form = TestConfigForm()

    if request.method=="GET":
        cfg = session.get("test_config", {})
        if "mode" in cfg:
            form.mode.data = cfg["mode"]
        if "duration" in cfg:
            form.duration.data = str(cfg["duration"])
        if "word_count" in cfg:
            form.word_count.data = str(cfg["word_count"])

    if form.validate_on_submit():
        session["test_config"] = {
            "mode":form.mode.data,
            "duration": int(form.duration.data),
            "word_count": int(form.word_count.data)
        }
        return redirect(url_for("main.test"))
    return render_template("main/test_config.html", form=form)

@main_bp.route("/test")
def test():
    cfg = session.get(
        "test_config",
        {"mode": "time", "duration": 30, "word_count": 50}
    )

    #change later on idk what to though
    prompt_text = (
        "The quick brown fox jumps over the lazy dog. "
        "Practice typing this sentence as accurately and quickly as you can."
    )
    return render_template("main/test.html", config=cfg, prompt_text=prompt_text)

@main_bp.route("/test/complete", methods=["POST"])
def test_complete():
    data = request.get_json(silent=True) or {}

    mode = data.get("mode")
    duration = data.get("duration")
    word_count = data.get("word_count")
    wpm = data.get("wpm")
    accuracy = data.get("accuracy")
    errors = data.get("errors")
    backspaces = data.get("backspaces")
    raw_chars = data.get("raw_chars")
    correct_chars= data.get("correct_chars")

    saved = False
    if current_user.is_authenticated:
        doc = {
            "user_id": ObjectId(current_user.id),
            "timestamp":datetime.now(UTC),
            "mode":mode,
            "duration": duration,
            "word_count":word_count,
            "wpm":wpm,
            "accuracy":accuracy,
            "errors":errors,
            "backspaces": backspaces,
            "raw_chars": raw_chars,
            "correct_chars": correct_chars
        }
        mongo.db.tests.insert_one(doc)
        saved = True
    return jsonify({"status":"ok", "saved":saved})

@main_bp.route("/history")
@login_required
def history():
    cursor = mongo.db.tests.find({"user_id": ObjectId(current_user.id)}).sort(
        "timestamp",-1
    )
    tests = list(cursor)
    return render_template("main/history.html", tests=tests)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    cursor = mongo.db.tests.find({"user_id": ObjectId(current_user.id)})
    tests = list(cursor)
    if not tests: 
        stats = {
            "count": 0,
            "avg_wpm": None,
            "best_spm": None,
            "avg_accuracy": None
        }
    else:
        count = len(tests)
        total_wpm = sum(t.get("wpm", 0) or 0 for t in tests)
        best_wpm = max(t.get("wpm", 0) or 0 for t in tests)
        total_acc = sum(t.get("accuracy", 0) or 0 for t in tests)
        stats = {
            "count": count,
            "avg_wpm": total_wpm/count,
            "best_wpm": best_wpm,
            "avg_accuracy": total_acc/ count
        }

    return render_template("main/dashboard.html", stats=stats)