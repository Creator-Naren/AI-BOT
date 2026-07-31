from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, RateLimitError

from extensions import db
from models import Conversation, Message, UserPreference
from services.ai_provider import build_provider
from services.fallback_provider import FallbackProvider

api_bp = Blueprint("api", __name__)


def _ensure_conversation():
    conversation = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .first()
    )
    if conversation:
        return conversation
    conversation = Conversation(user_id=current_user.id, title="General Chat")
    db.session.add(conversation)
    db.session.commit()
    return conversation


@api_bp.post("/chat")
@login_required
def chat():
    payload = request.get_json(silent=True) or {}
    message_text = (payload.get("message") or "").strip()
    if not message_text:
        return (
            jsonify(
                {
                    "success": False,
                    "code": "validation_error",
                    "message": "Message cannot be empty.",
                }
            ),
            400,
        )

    conversation = _ensure_conversation()
    db.session.add(
        Message(conversation_id=conversation.id, role="user", content=message_text)
    )

    preference = UserPreference.query.filter_by(user_id=current_user.id).first()
    provider = build_provider(current_app.config, user_preferences=preference)
    fallback_code = None

    try:
        assistant_reply = provider.generate_reply(message_text)
    except (APITimeoutError, APIConnectionError, RateLimitError, AuthenticationError, APIError):
        assistant_reply = FallbackProvider().generate_reply(message_text)
        fallback_code = "fallback_activated"

    db.session.add(
        Message(conversation_id=conversation.id, role="assistant", content=assistant_reply)
    )
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "assistant_message": assistant_reply,
            "code": fallback_code,
        }
    )


@api_bp.get("/history")
@login_required
def history():
    conversations = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return jsonify(
        {
            "success": True,
            "conversations": [
                {
                    "id": item.id,
                    "title": item.title,
                    "updated_at": item.updated_at.isoformat(),
                }
                for item in conversations
            ],
        }
    )


@api_bp.post("/preferences/theme")
@login_required
def set_theme():
    payload = request.get_json(silent=True) or {}
    theme_name = (payload.get("theme") or "ocean").strip() or "ocean"
    dark_mode = bool(payload.get("dark_mode", False))

    preference = UserPreference.query.filter_by(user_id=current_user.id).first()
    if preference is None:
        preference = UserPreference(user_id=current_user.id)
        db.session.add(preference)

    preference.theme_name = theme_name
    preference.dark_mode = dark_mode
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "theme": preference.theme_name,
            "dark_mode": preference.dark_mode,
        }
    )


@api_bp.post("/preferences/personality")
@login_required
def set_personality():
    payload = request.get_json(silent=True) or {}
    personality = payload.get("personality")
    personality = personality if isinstance(personality, str) else ""
    personality = personality.strip()[:500]

    preference = UserPreference.query.filter_by(user_id=current_user.id).first()
    if preference is None:
        preference = UserPreference(user_id=current_user.id)
        db.session.add(preference)

    preference.personality = personality
    db.session.commit()

    return jsonify({"success": True, "personality": preference.personality})
