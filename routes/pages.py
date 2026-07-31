from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import UserPreference

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def home():
    return render_template("index.html")


@pages_bp.get("/chat")
@login_required
def chat():
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    theme_name = pref.theme_name if pref else "ocean"
    dark_mode = pref.dark_mode if pref else False
    personality = (pref.personality if pref else "") or ""
    return render_template(
        "chat.html",
        theme_name=theme_name,
        dark_mode=dark_mode,
        personality=personality,
    )
