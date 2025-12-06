from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from . import auth_bp
from ..models import User 
from ..extensions import mongo, oauth
from bson.objectid import ObjectId

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email_or_username = StringField("Email or Username", validators = [DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Log In")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing = mongo.db.users.find_one(
            {
                "$or": [
                    {"username": form.username.data},
                    {"email":form.email.data}
                ]
            }
        )
        if existing:
            flash("Username or email already in use.", "danger")
            return render_template("auth/register.html", form = form)
        
        password_hash = generate_password_hash(form.password.data)
        user = User.create(
            username=form.username.data,
            email = form.email.data,
            password_hash=password_hash,
        )
        login_user(user)
        flash("Registration successful. Logged in!", "success")
        return redirect(url_for("main.index"))
    
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email_or_username.data
        doc = mongo.db.users.find_one(
            {"$or": [{"username":identifier}, {"email":identifier}]}
        )
        if not doc or not check_password_hash(doc.get("password_hash", ""), form.password.data):
            flash("Invalid credentials.", "danger")
            return render_template("auth/login.html", form=form)
        
        user = User.from_doc(doc)
        login_user(user, remember=form.remember_me.data)
        flash("Logged in successfully.", "success")
        next_page = request.args.get("next") or url_for("main.index")
        return redirect(next_page)
    
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

@auth_bp.route("/login/google")
def google_login():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()

    resp = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo")
    profile=resp.json()

    google_id = profile.get("sub")
    email = profile.get("email")
    name = profile.get("name") or email.split("@")[0]

    if not email:
        flash("Google login failed: no email returned.", "danger")
        return redirect(url_for("auth.login"))
    
    doc = mongo.db.users.find_one(
        {"oauth_provider": "google", "oauth_id": google_id}
    )

    if not doc:
        doc = mongo.db.users.find_one({"email": email})
        if doc:
            mongo.db.users.update_one(
                {"_id": doc["_id"]},
                {"$set": {"oauth_provider": "google", "oauth_id": google_id}},
            )
        else:
            result = mongo.db.users.insert_one(
                {
                    "username": email.split("@")[0],
                    "email": email,
                    "display_name":name,
                    "oauth_provider":"google",
                    "oauth_id":google_id,
                }
            )
            doc = mongo.db.users.find_one({"_id":result.inserted_id})
    
    user = User.from_doc(doc)
    login_user(user)
    flash("Logged in with Google.", "success")
    next_page = request.args.get("next") or url_for("main.index")
    return redirect(next_page)


