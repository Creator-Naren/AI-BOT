# AI Chatbot Personality & Response Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make bot replies clear and readable (plain-text prompt + client-side markdown formatting) and let each user set a persisted personality that shapes the bot's tone.

**Architecture:** Add a `personality` column to the existing `UserPreference` model. Compose a system prompt from a clarity instruction plus the user's personality, pass it through the existing provider abstraction, and save/load personality via a JSON endpoint. Render bot replies with a small dependency-free `formatMarkdown()` in the browser.

**Tech Stack:** Python 3, Flask, Flask-Login, Flask-SQLAlchemy, SQLite, pytest, HTML/CSS/JS, Node built-in test runner (`node --test`)

**Note:** This project is NOT a git repository. Skip all "Commit" steps (or run `git init` in `Task 1` first if you want version control).

---

## File Structure and Responsibilities

- Modify: `models.py` — add `personality` column to `UserPreference`
- Create: `scripts/migrate_personality.py` — one-time ALTER TABLE for the existing SQLite DB
- Modify: `tests/conftest.py` — clear AI keys in test app so tests stay hermetic
- Modify: `services/ai_provider.py` — add `build_system_prompt()`, pass it through `build_provider()`
- Modify: `services/openai_provider.py` — accept `system_prompt`
- Modify: `services/openrouter_provider.py` — accept `system_prompt`
- Create: `tests/test_ai_provider.py` — unit tests for prompt builder and provider
- Modify: `routes/api.py` — pass preferences to `build_provider`, add personality endpoint
- Modify: `tests/test_preferences.py` — personality endpoint tests
- Modify: `tests/test_chat_api.py` — chat-with-personality test
- Modify: `routes/pages.py` — pass saved personality to the chat template
- Create: `static/js/formatter.js` — dependency-free `formatMarkdown()`
- Create: `tests/formatter.test.js` — Node tests for the formatter
- Modify: `static/js/chat.js` — personality UI wiring + bubble rendering
- Modify: `templates/chat.html` — Bot Personality sidebar section
- Modify: `static/css/style.css` — styles for personality section + formatted bubbles

Python commands in this plan use the full interpreter path because `python` is not on PATH:
`& "$env:LOCALAPPDATA\Python\bin\python.exe"`

---

### Task 1: Add `personality` column and migrate the existing DB

**Files:**
- Modify: `models.py:47-51`
- Create: `scripts/migrate_personality.py`
- Test: `tests/test_preferences.py` (unchanged — column is covered in later tasks)

- [ ] **Step 1: Add the column to the model**

In `models.py`, change the `UserPreference` class to:

```python
class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    theme_name = db.Column(db.String(30), default="ocean")
    personality = db.Column(db.Text, default="", nullable=False)
```

- [ ] **Step 2: Create the migration script**

Create `scripts/migrate_personality.py`:

```python
import sqlite3
from pathlib import Path

db_path = Path("instance/chatbot.db")
if not db_path.exists():
    print("No database found at instance/chatbot.db; nothing to migrate.")
    raise SystemExit(0)

conn = sqlite3.connect(db_path)
columns = [row[1] for row in conn.execute("PRAGMA table_info(user_preference)")]
if "personality" not in columns:
    conn.execute("ALTER TABLE user_preference ADD COLUMN personality TEXT DEFAULT ''")
    conn.commit()
    print("Migrated: added personality column to user_preference")
else:
    print("Column already present; nothing to do")
conn.close()
```

- [ ] **Step 3: Run the migration**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" scripts/migrate_personality.py`
Expected: `Migrated: added personality column to user_preference` (or `Column already present` on re-run).

- [ ] **Step 4: Verify the model imports and column exists**

Run:
```
& "$env:LOCALAPPDATA\Python\bin\python.exe" -c "from models import UserPreference; import inspect; print([c.name for c in UserPreference.__table__.columns])"
```
Expected: `['id', 'user_id', 'dark_mode', 'theme_name', 'personality']`

- [ ] **Step 5: Run the full test suite to confirm nothing broke**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest -q`
Expected: all existing tests PASS.

---

### Task 2: Keep tests hermetic (no real API calls)

Now that `Task 1/.env` contains a real API key, the test app would make live network calls. Clear the AI keys in the test fixture.

**Files:**
- Modify: `tests/conftest.py:4-14`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_preferences.py`:

```python
def test_test_app_has_no_ai_key(app):
    assert app.config.get("OPENAI_API_KEY") is None
    assert app.config.get("AI_BASE_URL") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py::test_test_app_has_no_ai_key -v`
Expected: FAIL — `app.config["OPENAI_API_KEY"]` is the real key from `.env`.

- [ ] **Step 3: Update the fixture**

In `tests/conftest.py`, change the `app` fixture to:

```python
@pytest.fixture
def app():
    from app import create_app
    from extensions import db

    app = create_app(testing=True)
    app.config["OPENAI_API_KEY"] = None
    app.config["AI_BASE_URL"] = None
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py::test_test_app_has_no_ai_key -v`
Expected: PASS.

- [ ] **Step 5: Run the full suite**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest -q`
Expected: all PASS (including `test_chat_api.py` using the fallback provider).

---

### Task 3: System prompt builder + provider support

**Files:**
- Modify: `services/ai_provider.py`
- Modify: `services/openai_provider.py`
- Modify: `services/openrouter_provider.py`
- Create: `tests/test_ai_provider.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ai_provider.py`:

```python
from services.ai_provider import build_provider, build_system_prompt
from services.openai_provider import OpenAIProvider


def test_build_system_prompt_default():
    prompt = build_system_prompt("")
    assert "Answer clearly and concisely" in prompt
    assert "Adopt this personality" not in prompt


def test_build_system_prompt_with_personality():
    prompt = build_system_prompt("You are a sarcastic pirate.")
    assert "Answer clearly and concisely" in prompt
    assert "Adopt this personality" in prompt
    assert "You are a sarcastic pirate." in prompt


def test_build_provider_default_system_prompt():
    provider = build_provider(
        {"OPENAI_API_KEY": "sk-test", "AI_BASE_URL": "https://example.com", "AI_MODEL": "model-x"}
    )
    assert isinstance(provider, OpenAIProvider)
    assert provider.system_prompt == build_system_prompt("")


def test_build_provider_includes_personality():
    class Pref:
        personality = "Warm and encouraging."
        ai_model = None

    provider = build_provider(
        {"OPENAI_API_KEY": "sk-test", "AI_MODEL": "model-x"},
        user_preferences=Pref(),
    )
    assert "Warm and encouraging." in provider.system_prompt


def test_generate_reply_sends_system_prompt():
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["messages"] = kwargs["messages"]

            class ChoiceMessage:
                content = "ok"

            class Choice:
                message = ChoiceMessage()

            class Response:
                choices = [Choice()]

            return Response()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    provider = OpenAIProvider("sk-test", model="m", base_url="https://example.com", system_prompt="Be terse.")
    provider.client = FakeClient()
    reply = provider.generate_reply("hi")

    assert reply == "ok"
    assert captured["messages"][0] == {"role": "system", "content": "Be terse."}
    assert captured["messages"][1] == {"role": "user", "content": "hi"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_ai_provider.py -v`
Expected: FAIL — `build_system_prompt` not defined.

- [ ] **Step 3: Implement `build_system_prompt` and `build_provider`**

In `services/ai_provider.py`, replace the whole file with:

```python
from services.fallback_provider import FallbackProvider
from services.openai_provider import OpenAIProvider


def build_system_prompt(personality=""):
    prompt = (
        "Answer clearly and concisely. Use plain text and short sentences. "
        "If you use markdown, keep it simple: short headings, bullet lists, and bold."
    )
    if personality.strip():
        prompt += (
            "\n\nAdopt this personality and stay in character while remaining "
            f"clear and helpful:\n{personality.strip()}"
        )
    return prompt


def build_provider(config, user_preferences=None):
    api_key = config.get("OPENAI_API_KEY")
    if not api_key:
        return FallbackProvider()

    base_url = config.get("AI_BASE_URL")
    model = config.get("AI_MODEL")
    if not model:
        model = "openai/gpt-4o-mini" if base_url else "gpt-4o-mini"

    personality = ""
    if user_preferences:
        personality = getattr(user_preferences, "personality", "") or ""
    system_prompt = build_system_prompt(personality)

    if user_preferences and getattr(user_preferences, "ai_model", None):
        model = user_preferences.ai_model

    return OpenAIProvider(api_key, model=model, base_url=base_url, system_prompt=system_prompt)
```

- [ ] **Step 4: Implement `system_prompt` in the OpenAI provider**

In `services/openai_provider.py`, replace the whole file with:

```python
from openai import OpenAI


class OpenAIProvider:
    def __init__(self, api_key, model="gpt-4o-mini", base_url=None, system_prompt="You are a helpful AI assistant."):
        self.model = model
        self.system_prompt = system_prompt
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)

    def generate_reply(self, message):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.5,
        )
        return (response.choices[0].message.content or "").strip()
```

- [ ] **Step 5: Implement `system_prompt` in the OpenRouter provider**

In `services/openrouter_provider.py`, replace the whole file with:

```python
from openai import OpenAI


class OpenRouterProvider:
    def __init__(self, api_key, model="openai/gpt-4o-mini", base_url="https://openrouter.ai/api/v1", system_prompt="You are a helpful AI assistant."):
        self.model = model
        self.system_prompt = system_prompt
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_reply(self, message):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.5,
        )
        return (response.choices[0].message.content or "").strip()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_ai_provider.py -v`
Expected: all 5 tests PASS.

---

### Task 4: Personality endpoint + chat route passes preferences

**Files:**
- Modify: `routes/api.py:27-69`
- Test: `tests/test_preferences.py`
- Test: `tests/test_chat_api.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_preferences.py`:

```python
def test_personality_can_be_saved(auth_client):
    response = auth_client.post(
        "/api/preferences/personality", json={"personality": "You are a sarcastic pirate."}
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["personality"] == "You are a sarcastic pirate."


def test_personality_can_be_cleared(auth_client):
    auth_client.post("/api/preferences/personality", json={"personality": "Be funny"})
    response = auth_client.post("/api/preferences/personality", json={"personality": ""})
    payload = response.get_json()

    assert payload["success"] is True
    assert payload["personality"] == ""


def test_personality_is_truncated_to_500_chars(auth_client):
    response = auth_client.post(
        "/api/preferences/personality", json={"personality": "x" * 600}
    )
    payload = response.get_json()

    assert payload["success"] is True
    assert len(payload["personality"]) == 500
```

Append to `tests/test_chat_api.py`:

```python
def test_chat_api_works_with_saved_personality(auth_client):
    auth_client.post("/api/preferences/personality", json={"personality": "Be funny"})
    response = auth_client.post("/api/chat", json={"message": "Hello bot"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert len(payload["assistant_message"]) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py tests/test_chat_api.py -v`
Expected: FAIL — 404 for `/api/preferences/personality`.

- [ ] **Step 3: Implement the endpoint and update the chat route**

In `routes/api.py`:

1. In `chat()`, after the `_ensure_conversation()` call, load the user's preference and pass it to the provider. Change:

```python
    conversation = _ensure_conversation()
    db.session.add(
        Message(conversation_id=conversation.id, role="user", content=message_text)
    )

    provider = build_provider(current_app.config)
    fallback_code = None
```

to:

```python
    conversation = _ensure_conversation()
    db.session.add(
        Message(conversation_id=conversation.id, role="user", content=message_text)
    )

    preference = UserPreference.query.filter_by(user_id=current_user.id).first()
    provider = build_provider(current_app.config, user_preferences=preference)
    fallback_code = None
```

2. Append the new endpoint at the end of the file:

```python
@api_bp.post("/preferences/personality")
@login_required
def set_personality():
    payload = request.get_json(silent=True) or {}
    personality = (payload.get("personality") or "").strip()[:500]

    preference = UserPreference.query.filter_by(user_id=current_user.id).first()
    if preference is None:
        preference = UserPreference(user_id=current_user.id)
        db.session.add(preference)

    preference.personality = personality
    db.session.commit()

    return jsonify({"success": True, "personality": preference.personality})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py tests/test_chat_api.py -v`
Expected: all PASS.

---

### Task 5: Chat page renders saved personality

**Files:**
- Modify: `routes/pages.py:14-20`
- Test: `tests/test_preferences.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_preferences.py`:

```python
def test_chat_page_renders_saved_personality(auth_client):
    auth_client.post("/api/preferences/personality", json={"personality": "Warm mentor"})
    response = auth_client.get("/chat")

    assert response.status_code == 200
    assert b"Warm mentor" in response.data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py::test_chat_page_renders_saved_personality -v`
Expected: FAIL — `Warm mentor` not in the response (template doesn't include it yet).

- [ ] **Step 3: Pass personality from the chat page route**

In `routes/pages.py`, change the `chat()` view to:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py::test_chat_page_renders_saved_personality -v`
Expected: PASS.

---

### Task 6: Markdown formatter (Node-tested)

**Files:**
- Create: `static/js/formatter.js`
- Create: `tests/formatter.test.js`

- [ ] **Step 1: Write the failing tests**

Create `tests/formatter.test.js`:

```javascript
const { test } = require("node:test");
const assert = require("node:assert");
const { formatMarkdown } = require("../static/js/formatter.js");

test("escapes HTML", () => {
  const out = formatMarkdown("<script>alert(1)</script>");
  assert.ok(!out.includes("<script>"));
  assert.ok(out.includes("&lt;script&gt;"));
});

test("formats bold and italic", () => {
  const out = formatMarkdown("Hello **world** and *you*");
  assert.ok(out.includes("<strong>world</strong>"));
  assert.ok(out.includes("<em>you</em>"));
});

test("formats headings", () => {
  const out = formatMarkdown("### Title");
  assert.ok(out.includes("<h4>Title</h4>"));
});

test("formats bullet and numbered lists", () => {
  const out = formatMarkdown("- one\n- two");
  assert.ok(out.includes("<ul>"));
  assert.ok(out.includes("<li>one</li>"));

  const out2 = formatMarkdown("1. first\n2. second");
  assert.ok(out2.includes("<ol>"));
  assert.ok(out2.includes("<li>first</li>"));
});

test("preserves line breaks in paragraphs", () => {
  const out = formatMarkdown("line one\nline two");
  assert.ok(out.includes("line one<br>line two"));
});

test("formats inline code", () => {
  const out = formatMarkdown("run `npm install`");
  assert.ok(out.includes("<code>npm install</code>"));
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tests/formatter.test.js`
Expected: FAIL — `Cannot find module '../static/js/formatter.js'`.

- [ ] **Step 3: Implement the formatter**

Create `static/js/formatter.js`:

```javascript
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatMarkdown(text) {
  const raw = escapeHtml(text).split("\n");
  const blocks = [];
  let para = [];
  let list = null;

  const flushPara = () => {
    if (para.length) {
      blocks.push({ type: "p", content: para.join("<br>") });
      para = [];
    }
  };

  const closeList = () => {
    if (list) {
      blocks.push({ type: list.kind, items: list.items });
      list = null;
    }
  };

  for (const line of raw) {
    const item = line.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
    if (item) {
      flushPara();
      if (!list) {
        list = { kind: /^\s*\d/.test(line) ? "ol" : "ul", items: [] };
      }
      list.items.push(item[1]);
      continue;
    }
    closeList();

    const heading = line.match(/^(#{1,3})\s+(.*)$/);
    if (heading) {
      flushPara();
      blocks.push({ type: "h", level: heading[1].length + 1, content: heading[2] });
      continue;
    }

    if (line.trim() === "") {
      flushPara();
      continue;
    }

    para.push(line);
  }
  flushPara();
  closeList();

  const html = blocks
    .map((block) => {
      if (block.type === "h") return `<h${block.level}>${block.content}</h${block.level}>`;
      if (block.type === "ul") return `<ul>${block.items.map((i) => `<li>${i}</li>`).join("")}</ul>`;
      if (block.type === "ol") return `<ol>${block.items.map((i) => `<li>${i}</li>`).join("")}</ol>`;
      return `<p>${block.content}</p>`;
    })
    .join("\n");

  return html
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { formatMarkdown };
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/formatter.test.js`
Expected: all 6 tests PASS.

---

### Task 7: Chat page personality UI + bubble rendering

**Files:**
- Modify: `templates/chat.html`
- Modify: `static/js/chat.js`
- Modify: `static/css/style.css`

- [ ] **Step 1: Add the personality section and script tag to the template**

In `templates/chat.html`, replace the sidebar `<hr>`/Theme block (lines 8-18) with:

```html
        <hr>
        <div class="personality-section">
            <h3>Bot Personality</h3>
            <div class="preset-chips">
                <button type="button" class="chip" data-preset="">None</button>
                <button type="button" class="chip" data-preset="friendly">Friendly</button>
                <button type="button" class="chip" data-preset="professional">Professional</button>
                <button type="button" class="chip" data-preset="humorous">Humorous</button>
            </div>
            <textarea id="personality-input" rows="3" maxlength="500"
                placeholder="Describe the bot's personality..."></textarea>
            <div class="personality-save-row">
                <button type="button" id="personality-save" class="btn primary small">Save</button>
                <span id="personality-status"></span>
            </div>
        </div>
        <hr>
        <label for="theme-select">Theme</label>
        <select id="theme-select">
            <option value="ocean">Ocean</option>
            <option value="midnight">Midnight</option>
            <option value="sunset">Sunset</option>
        </select>
        <label class="toggle-row">
            <input id="dark-mode-toggle" type="checkbox" {% if dark_mode %}checked{% endif %}>
            Dark mode
        </label>
```

Replace the script block at the bottom with:

```html
<script>
    window.initialTheme = "{{ theme_name }}";
    window.initialPersonality = {{ personality | tojson }};
</script>
<script src="{{ url_for('static', filename='js/formatter.js') }}"></script>
<script src="{{ url_for('static', filename='js/chat.js') }}"></script>
```

`{{ personality | tojson }}` emits a properly escaped JS string literal (handles quotes, backslashes, newlines), so `window.initialPersonality = {{ personality | tojson }};` becomes e.g. `window.initialPersonality = "You are a \"pirate\"";`.

- [ ] **Step 2: Update chat.js**

In `static/js/chat.js`:

1. Replace `appendBubble` with:

```javascript
function appendBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  if (role === "bot") {
    bubble.innerHTML = formatMarkdown(text);
  } else {
    bubble.textContent = text;
  }
  thread.appendChild(bubble);
  thread.scrollTop = thread.scrollHeight;
}
```

2. Add the personality constants and wiring at the end of the file:

```javascript
const PERSONALITY_PRESETS = {
  "": "",
  friendly: "You are warm, encouraging, and approachable.",
  professional: "You are professional, precise, and to the point.",
  humorous: "You are witty and playful, using light humor where appropriate.",
};

const personalityInput = document.getElementById("personality-input");
const personalitySave = document.getElementById("personality-save");
const personalityStatus = document.getElementById("personality-status");

if (personalityInput) {
  personalityInput.value = window.initialPersonality || "";
}

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    personalityInput.value = PERSONALITY_PRESETS[chip.dataset.preset] || "";
    if (personalityStatus) personalityStatus.textContent = "";
  });
});

personalitySave?.addEventListener("click", async () => {
  const personality = (personalityInput?.value || "").trim();
  const response = await fetch("/api/preferences/personality", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ personality }),
  });
  const payload = await response.json();
  if (payload.success && personalityStatus) {
    personalityStatus.textContent = "Saved";
    setTimeout(() => (personalityStatus.textContent = ""), 2000);
  } else if (personalityStatus) {
    personalityStatus.textContent = "Save failed";
  }
});
```

- [ ] **Step 3: Add CSS**

Append to `static/css/style.css`:

```css
.personality-section { display: grid; gap: 0.5rem; margin-top: 0.75rem; }
.preset-chips { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.chip {
    border: 1px solid var(--accent);
    background: transparent;
    color: var(--accent);
    border-radius: 999px;
    padding: 0.25rem 0.65rem;
    cursor: pointer;
    font-size: 0.85rem;
}
.chip:hover { background: var(--accent); color: #fff; }
#personality-input {
    width: 100%;
    border: 1px solid #94a3b8;
    border-radius: 8px;
    padding: 0.5rem;
    resize: vertical;
    font-family: inherit;
}
.personality-save-row { display: flex; align-items: center; gap: 0.5rem; }
.btn.small { padding: 0.35rem 0.7rem; font-size: 0.85rem; }
#personality-status { font-size: 0.85rem; color: #16a34a; min-height: 1rem; }

.bubble.bot p { margin: 0.3rem 0; }
.bubble.bot p:first-child { margin-top: 0; }
.bubble.bot p:last-child { margin-bottom: 0; }
.bubble.bot ul, .bubble.bot ol { margin: 0.3rem 0; padding-left: 1.2rem; }
.bubble.bot h2, .bubble.bot h3, .bubble.bot h4 { margin: 0.4rem 0 0.2rem; }
.bubble.bot code {
    background: rgba(0, 0, 0, 0.08);
    border-radius: 4px;
    padding: 0.1rem 0.3rem;
    font-size: 0.9em;
}
```

- [ ] **Step 4: Run the full Python test suite**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest -q`
Expected: all PASS.

- [ ] **Step 5: Run the Node formatter tests**

Run: `node --test tests/formatter.test.js`
Expected: all 6 PASS.

- [ ] **Step 6: Manual end-to-end verification**

1. Start the server:
   `Start-Process -FilePath "$env:LOCALAPPDATA\Python\bin\python.exe" -ArgumentList "app.py" -WorkingDirectory "C:\My Stuff\Python Projects\Task 1"`
2. Log in at http://127.0.0.1:5000/login (tester@example.com / password123).
3. Send a message like "Explain how to make a simple web app in 3 steps." — verify the reply shows formatted headings, bold, and lists instead of raw `#`, `**`, `-` symbols.
4. In the sidebar, click the **Humorous** chip, then **Save** — verify "Saved" appears.
5. Send a new message — verify the bot's tone shifts accordingly.
6. Reload the page — verify the Humorous personality text is still in the text box (persisted).

---

## Self-Review Checklist

- [ ] Spec coverage: personality column ✓ (Task 1), system prompt + providers ✓ (Task 3), personality endpoint ✓ (Task 4), pages render ✓ (Task 5), formatter ✓ (Task 6), UI wiring ✓ (Task 7), 500-char cap ✓ (Task 4), error handling/fallback unchanged ✓ (existing), tests ✓ (Tasks 2-6).
- [ ] No placeholders: every step has complete code and exact commands.
- [ ] Type consistency: `build_system_prompt(personality="")`, `build_provider(config, user_preferences=None)`, `OpenAIProvider(... system_prompt=...)`, `OpenRouterProvider(... system_prompt=...)`, `set_personality`, `formatMarkdown`, `window.initialPersonality`, `#personality-input`, `#personality-save`, `#personality-status`, `data-preset` keys `""/friendly/professional/humorous` match across tasks.
