import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import mongo, login_manager, oauth
from .auth.routes import auth_bp
from .main.routes import main_bp
from .models import load_user

def create_app():
    load_dotenv

    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["MONGO_URI"] = os.getenv(
        "MONGO_URI", "mongodb://localhost:27017/finalCMSC388J"
    )

    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")

    mongo.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app