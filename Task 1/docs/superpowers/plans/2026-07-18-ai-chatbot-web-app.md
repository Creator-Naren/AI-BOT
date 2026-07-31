# AI Chatbot Web Application Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-style Flask chatbot app with authentication, OpenAI + fallback responses, persistent chat history, dark mode, and multi-theme support.

**Architecture:** Implement a Flask monolith with server-rendered pages and JSON chat APIs. Use SQLAlchemy for persistence and Flask-Login for auth/session controls. Route responses through a provider abstraction that chooses OpenAI when configured and a local fallback provider when unavailable or failing.

**Tech Stack:** Python 3, Flask, Flask-Login, Flask-SQLAlchemy, Werkzeug security helpers, HTML/CSS/JavaScript, SQLite, pytest

---

## File Structure and Responsibilities

- Create: `requirements.txt` — runtime and test dependencies
- Create: `.env.example` — environment variable template
- Create: `app.py` — Flask app factory, extension initialization, blueprint registration
- Create: `config.py` — configuration classes and env parsing
- Create: `models.py` — SQLAlchemy models for users, conversations, messages, preferences
- Create: `services/ai_provider.py` — provider interface + selector
- Create: `services/openai_provider.py` — OpenAI adapter
- Create: `services/fallback_provider.py` — local fallback response engine
- Create: `routes/auth.py` — signup/login/logout routes
- Create: `routes/pages.py` — homepage/dashboard/chat page routes
- Create: `routes/api.py` — chat/history/preferences JSON endpoints
- Create: `templates/base.html` — shared shell and theme wiring
- Create: `templates/index.html` — attractive landing page
- Create: `templates/login.html` — login page
- Create: `templates/signup.html` — signup page
- Create: `templates/chat.html` — chat workspace with history sidebar
- Create: `static/css/style.css` — responsive styling + dark mode + themes
- Create: `static/js/chat.js` — chat UI logic, loading/typing animation, history and themes
- Create: `tests/conftest.py` — test app/db fixtures
- Create: `tests/test_auth.py` — auth flow tests
- Create: `tests/test_chat_api.py` — chat API + fallback behavior tests
- Create: `tests/test_history_and_preferences.py` — persistence and theme tests
- Create: `README.md` — setup, run, test, submission notes

### Task 1: Bootstrap project and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `config.py`
- Test: `python -m pip install -r requirements.txt`

- [ ] **Step 1: Write the failing environment load test**

```python
# tests/test_config_smoke.py
from config import Config

def test_config_has_required_flags():
    assert hasattr(Config, "SECRET_KEY")
    assert hasattr(Config, "SQLALCHEMY_DATABASE_URI")
    assert hasattr(Config, "OPENAI_API_KEY")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config_smoke.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Write minimal implementation**

```python
# config.py
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///chatbot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

```txt
# requirements.txt
Flask==3.0.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.1
openai==1.40.0
pytest==8.3.2
```

```env
# .env.example
SECRET_KEY=replace-with-secure-secret
DATABASE_URL=sqlite:///chatbot.db
OPENAI_API_KEY=
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config_smoke.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .env.example config.py tests/test_config_smoke.py
git commit -m "chore: bootstrap config and dependencies"
```

### Task 2: Implement app factory, models, and database wiring

**Files:**
- Create: `app.py`
- Create: `models.py`
- Create: `tests/conftest.py`
- Test: `tests/test_models_smoke.py`

- [ ] **Step 1: Write the failing model creation test**

```python
# tests/test_models_smoke.py
from app import create_app, db
from models import User

def test_user_model_can_be_created():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        user = User(username="alice", email="alice@example.com")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()
        assert User.query.count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models_smoke.py -v`  
Expected: FAIL because `app.py`/`models.py` not implemented

- [ ] **Step 3: Write minimal implementation**

```python
# app.py
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    if testing:
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    db.init_app(app)
    login_manager.init_app(app)
    from routes.auth import auth_bp
    from routes.pages import pages_bp
    from routes.api import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
```

```python
# models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), default="New Chat")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    theme_name = db.Column(db.String(30), default="ocean")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models_smoke.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app.py models.py tests/test_models_smoke.py
git commit -m "feat: add flask app factory and core models"
```

### Task 3: Build authentication flow (signup/login/logout)

**Files:**
- Create: `routes/auth.py`
- Create: `templates/login.html`
- Create: `templates/signup.html`
- Create: `tests/test_auth.py`
- Modify: `templates/base.html`

- [ ] **Step 1: Write the failing auth test**

```python
# tests/test_auth.py
def test_signup_login_logout_flow(client):
    resp = client.post("/signup", data={
        "username": "bob",
        "email": "bob@example.com",
        "password": "supersecret"
    }, follow_redirects=True)
    assert b"Account created" in resp.data

    resp = client.post("/login", data={
        "email": "bob@example.com",
        "password": "supersecret"
    }, follow_redirects=True)
    assert b"Chat" in resp.data

    resp = client.get("/logout", follow_redirects=True)
    assert b"Logged out" in resp.data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_auth.py::test_signup_login_logout_flow -v`  
Expected: FAIL because auth routes/templates missing

- [ ] **Step 3: Write minimal implementation**

```python
# routes/auth.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import db
from models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("pages.chat"))
    if request.method == "POST":
        user = User(username=request.form["username"], email=request.form["email"])
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        flash("Account created", "success")
        return redirect(url_for("auth.login"))
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("pages.chat"))
        flash("Invalid credentials", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for("auth.login"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_auth.py::test_signup_login_logout_flow -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add routes/auth.py templates/login.html templates/signup.html templates/base.html tests/test_auth.py
git commit -m "feat: implement auth flow"
```

### Task 4: Implement AI providers (OpenAI + fallback)

**Files:**
- Create: `services/ai_provider.py`
- Create: `services/openai_provider.py`
- Create: `services/fallback_provider.py`
- Create: `tests/test_ai_provider.py`

- [ ] **Step 1: Write the failing provider-selection test**

```python
# tests/test_ai_provider.py
from services.ai_provider import build_provider

def test_fallback_provider_when_key_missing():
    provider = build_provider(openai_api_key=None)
    reply = provider.generate_reply("Hello")
    assert isinstance(reply, str)
    assert len(reply) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ai_provider.py::test_fallback_provider_when_key_missing -v`  
Expected: FAIL because provider modules missing

- [ ] **Step 3: Write minimal implementation**

```python
# services/ai_provider.py
from services.fallback_provider import FallbackProvider
from services.openai_provider import OpenAIProvider

def build_provider(openai_api_key):
    if openai_api_key:
        return OpenAIProvider(openai_api_key)
    return FallbackProvider()
```

```python
# services/fallback_provider.py
class FallbackProvider:
    def generate_reply(self, message):
        lowered = message.lower()
        if "hello" in lowered:
            return "Hi! How can I help you today?"
        if "help" in lowered:
            return "I can help summarize ideas, answer questions, and draft plans."
        return "I could not reach AI services, but I am still here to help. Please try rephrasing."
```

```python
# services/openai_provider.py
from openai import OpenAI

class OpenAIProvider:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_reply(self, message):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ai_provider.py::test_fallback_provider_when_key_missing -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/ai_provider.py services/openai_provider.py services/fallback_provider.py tests/test_ai_provider.py
git commit -m "feat: add ai provider abstraction with fallback"
```

### Task 5: Build chat APIs and persistence (message flow + history)

**Files:**
- Create: `routes/api.py`
- Create: `tests/test_chat_api.py`
- Create: `tests/test_history_and_preferences.py`
- Modify: `models.py`

- [ ] **Step 1: Write the failing chat API test**

```python
# tests/test_chat_api.py
def test_chat_api_stores_user_and_bot_messages(auth_client):
    resp = auth_client.post("/api/chat", json={"message": "Hello"})
    payload = resp.get_json()
    assert resp.status_code == 200
    assert payload["success"] is True
    assert payload["assistant_message"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chat_api.py::test_chat_api_stores_user_and_bot_messages -v`  
Expected: FAIL because `/api/chat` missing

- [ ] **Step 3: Write minimal implementation**

```python
# routes/api.py
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from app import db
from models import Conversation, Message, UserPreference
from services.ai_provider import build_provider

api_bp = Blueprint("api", __name__)

def _ensure_conversation(user_id):
    convo = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).first()
    if convo:
        return convo
    convo = Conversation(user_id=user_id, title="General Chat")
    db.session.add(convo)
    db.session.commit()
    return convo

@api_bp.post("/chat")
@login_required
def chat():
    body = request.get_json(silent=True) or {}
    text = (body.get("message") or "").strip()
    if not text:
        return jsonify({"success": False, "code": "validation_error", "message": "Message cannot be empty."}), 400

    convo = _ensure_conversation(current_user.id)
    db.session.add(Message(conversation_id=convo.id, role="user", content=text))

    provider = build_provider(current_app.config.get("OPENAI_API_KEY"))
    try:
        reply = provider.generate_reply(text)
        code = None
    except Exception:
        from services.fallback_provider import FallbackProvider
        reply = FallbackProvider().generate_reply(text)
        code = "fallback_activated"

    db.session.add(Message(conversation_id=convo.id, role="assistant", content=reply))
    db.session.commit()
    return jsonify({"success": True, "assistant_message": reply, "code": code})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_chat_api.py::test_chat_api_stores_user_and_bot_messages -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add routes/api.py tests/test_chat_api.py tests/test_history_and_preferences.py
git commit -m "feat: add chat api with persistence and fallback handling"
```

### Task 6: Create homepage/chat UI with responsive layout and typing animation

**Files:**
- Create: `routes/pages.py`
- Create: `templates/base.html`
- Create: `templates/index.html`
- Create: `templates/chat.html`
- Create: `static/css/style.css`
- Create: `static/js/chat.js`

- [ ] **Step 1: Write the failing UI route test**

```python
# tests/test_pages.py
def test_homepage_and_chat_routes(client, auth_client):
    home = client.get("/")
    assert home.status_code == 200
    assert b"AI Chatbot" in home.data

    chat = auth_client.get("/chat")
    assert chat.status_code == 200
    assert b"Type your message" in chat.data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pages.py::test_homepage_and_chat_routes -v`  
Expected: FAIL because page routes/templates not implemented

- [ ] **Step 3: Write minimal implementation**

```python
# routes/pages.py
from flask import Blueprint, render_template
from flask_login import login_required

pages_bp = Blueprint("pages", __name__)

@pages_bp.get("/")
def home():
    return render_template("index.html")

@pages_bp.get("/chat")
@login_required
def chat():
    return render_template("chat.html")
```

```javascript
// static/js/chat.js
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const thread = document.getElementById("chat-thread");

function appendBubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  thread.appendChild(div);
  thread.scrollTop = thread.scrollHeight;
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  appendBubble("user", message);
  input.value = "";

  const typing = document.createElement("div");
  typing.className = "bubble bot typing";
  typing.textContent = "Typing...";
  thread.appendChild(typing);

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  const data = await res.json();
  typing.remove();
  appendBubble("bot", data.assistant_message || data.message || "Something went wrong.");
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pages.py::test_homepage_and_chat_routes -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add routes/pages.py templates/base.html templates/index.html templates/chat.html static/css/style.css static/js/chat.js tests/test_pages.py
git commit -m "feat: add responsive pages and chat interaction ui"
```

### Task 7: Add dark mode, multi-theme preferences, and history panel endpoints

**Files:**
- Modify: `routes/api.py`
- Modify: `static/js/chat.js`
- Modify: `static/css/style.css`
- Modify: `templates/chat.html`
- Test: `tests/test_history_and_preferences.py`

- [ ] **Step 1: Write the failing preferences/history test**

```python
# tests/test_history_and_preferences.py
def test_theme_and_history_endpoints(auth_client):
    set_theme = auth_client.post("/api/preferences/theme", json={"theme": "midnight", "dark_mode": True})
    assert set_theme.status_code == 200
    assert set_theme.get_json()["success"] is True

    history = auth_client.get("/api/history")
    assert history.status_code == 200
    assert "conversations" in history.get_json()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_history_and_preferences.py::test_theme_and_history_endpoints -v`  
Expected: FAIL because `/api/preferences/theme` and `/api/history` are missing

- [ ] **Step 3: Write minimal implementation**

```python
# routes/api.py (additions)
@api_bp.get("/history")
@login_required
def history():
    convos = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
    return jsonify({
        "success": True,
        "conversations": [{"id": c.id, "title": c.title, "updated_at": c.updated_at.isoformat()} for c in convos]
    })

@api_bp.post("/preferences/theme")
@login_required
def set_theme():
    body = request.get_json(silent=True) or {}
    theme = body.get("theme", "ocean")
    dark_mode = bool(body.get("dark_mode", False))
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.session.add(pref)
    pref.theme_name = theme
    pref.dark_mode = dark_mode
    db.session.commit()
    return jsonify({"success": True, "theme": theme, "dark_mode": dark_mode})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_history_and_preferences.py::test_theme_and_history_endpoints -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add routes/api.py static/js/chat.js static/css/style.css templates/chat.html tests/test_history_and_preferences.py
git commit -m "feat: add history panel and user theme preferences"
```

### Task 8: Final integration, docs, and submission readiness

**Files:**
- Create: `README.md`
- Modify: `app.py`
- Test: full test suite

- [ ] **Step 1: Write failing smoke run test**

```python
# tests/test_app_smoke.py
from app import create_app

def test_app_boots():
    app = create_app(testing=True)
    assert app.testing is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_app_smoke.py -v`  
Expected: FAIL until final wiring is complete

- [ ] **Step 3: Write minimal implementation**

```python
# app.py (entrypoint)
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

```md
# README.md
## Setup
1. `python -m venv .venv`
2. `.venv\\Scripts\\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and configure values
5. `python app.py`

## Tests
`pytest -v`

## Submission checklist
- Source code/project folder
- Screenshots
- GitHub repo link
- Live hosted link
- Short project description
```

- [ ] **Step 4: Run tests to verify everything passes**

Run: `pytest -v`  
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: complete ai chatbot web app and docs"
```

## Self-Review (Writing-Plans Checklist)

- Spec coverage: All required features and requested optional features (except voice) are mapped to tasks.
- Placeholder scan: No TBD/TODO placeholders remain.
- Type consistency: `build_provider`, `generate_reply`, `/api/chat`, `/api/history`, `/api/preferences/theme` signatures are consistent across tasks.
