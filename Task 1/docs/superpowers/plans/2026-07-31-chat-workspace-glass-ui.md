# Chat Workspace Glass UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the chat workspace a dark, glassy, motion-rich UI (animated bubbles, bouncing typing dots, hover/press feedback, smooth theme transitions, scroll-to-bottom button) using pure CSS + vanilla JS.

**Architecture:** All chat-page styling goes in a new `static/css/chat-glass.css`, loaded only on the chat page via a `{% block styles %}` hook added to `base.html`. `chat.js` gains typing-dot markup and scroll-to-bottom logic. No backend changes, no new dependencies.

**Tech Stack:** Plain CSS3 (animations, `backdrop-filter`, `color-mix`, `:has()`), vanilla JS, Flask/Jinja templates, pytest.

**Environment notes:**
- Work from `C:\My Stuff\Python Projects\Task 1`.
- NOT a git repo → skip all commit steps.
- Python not on PATH. Use `& "$env:LOCALAPPDATA\Python\bin\python.exe"`.
- Dev server at http://127.0.0.1:5000 (Flask debug auto-reloads; verify via `Invoke-WebRequest`).
- Test login: `tester@example.com` / `password123`.

---

### Task 1: Create `static/css/chat-glass.css`

**Files:**
- Create: `static/css/chat-glass.css`

- [ ] **Step 1: Read the current stylesheet**

Read `static/css/style.css` fully so the new file's overrides are understood in context (base rules for `.bubble`, `.chat-form`, `.chip`, `.history-panel`, the full-screen `body:has(.chat-layout)` layout, and the `--accent` / `--bg` / `--text` variables).

- [ ] **Step 2: Create the glass stylesheet**

Create `static/css/chat-glass.css` with this EXACT content:

```css
/* Chat workspace glass UI — loaded ONLY on the chat page */

/* Always-dark glass workspace */
body:has(.chat-layout) {
    background: linear-gradient(160deg, #0b1220 0%, #111a2e 100%);
}

body:has(.chat-layout) .history-panel,
body:has(.chat-layout) .chat-panel {
    background: linear-gradient(165deg, rgba(30, 41, 59, 0.65), rgba(15, 23, 42, 0.55));
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
    position: relative;
}

body:has(.chat-layout) .chat-thread {
    background: rgba(15, 23, 42, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.06);
}

/* Bubbles */
body:has(.chat-layout) .bubble.user {
    background: linear-gradient(135deg, var(--accent), #1e3a8a);
    box-shadow: 0 4px 18px color-mix(in srgb, var(--accent) 40%, transparent);
    color: #ffffff;
}

body:has(.chat-layout) .bubble.bot {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #e2e8f0;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
}

body:has(.chat-layout) .bubble.typing {
    font-style: normal;
    opacity: 1;
}

/* Bubble entrance animation */
@keyframes glass-in {
    0% { opacity: 0; transform: translateY(14px) scale(0.97); filter: blur(4px); }
    100% { opacity: 1; transform: none; filter: blur(0); }
}

body:has(.chat-layout) .bubble {
    animation: glass-in 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* Typing dots */
.typing-dots {
    display: inline-flex;
    gap: 5px;
    padding: 4px 0;
}

.typing-dots i {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent);
    animation: dot-pulse 1.4s ease-in-out infinite;
}

.typing-dots i:nth-child(2) { animation-delay: 0.2s; }
.typing-dots i:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-pulse {
    0%, 60%, 100% { opacity: 0.35; transform: translateY(0); }
    30% { opacity: 1; transform: translateY(-5px); }
}

/* Input + send button */
body:has(.chat-layout) .chat-form input {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #e2e8f0;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

body:has(.chat-layout) .chat-form input::placeholder {
    color: rgba(226, 232, 240, 0.5);
}

body:has(.chat-layout) .chat-form input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 30%, transparent);
}

body:has(.chat-layout) .chat-form .btn.primary {
    transition: box-shadow 0.2s ease, transform 0.1s ease;
}

body:has(.chat-layout) .chat-form .btn.primary:hover {
    box-shadow:
        0 0 0 3px color-mix(in srgb, var(--accent) 35%, transparent),
        0 4px 16px color-mix(in srgb, var(--accent) 45%, transparent);
}

body:has(.chat-layout) .chat-form .btn.primary:active {
    transform: scale(0.96);
}

/* Sidebar hover feedback */
body:has(.chat-layout) .history-panel li {
    border-radius: 8px;
    padding: 0.4rem 0.55rem;
    transition: background-color 0.18s ease;
}

body:has(.chat-layout) .history-panel li:hover {
    background-color: rgba(255, 255, 255, 0.07);
}

body:has(.chat-layout) .chip {
    transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

body:has(.chat-layout) .chip:hover {
    box-shadow: 0 0 12px color-mix(in srgb, var(--accent) 35%, transparent);
}

body:has(.chat-layout) .history-panel select,
body:has(.chat-layout) .history-panel .toggle-row {
    transition: background-color 0.2s ease;
}

body:has(.chat-layout) .history-panel select:hover,
body:has(.chat-layout) .history-panel .toggle-row:hover {
    background-color: rgba(255, 255, 255, 0.06);
}

/* Smooth theme transitions */
body:has(.chat-layout),
body:has(.chat-layout) .topbar,
body:has(.chat-layout) .history-panel,
body:has(.chat-layout) .chat-panel {
    transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease;
}

/* Scroll-to-bottom button */
.scroll-bottom {
    position: absolute;
    bottom: 5.5rem;
    right: 1.25rem;
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 50%;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #e2e8f0;
    font-size: 1.1rem;
    line-height: 1;
    cursor: pointer;
    display: grid;
    place-items: center;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    opacity: 0;
    transform: translateY(8px);
    pointer-events: none;
    transition: opacity 0.25s ease, transform 0.25s ease, background-color 0.2s ease;
    z-index: 5;
}

.scroll-bottom.visible {
    opacity: 1;
    transform: none;
    pointer-events: auto;
}

.scroll-bottom:hover {
    background: rgba(30, 41, 59, 0.95);
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    body:has(.chat-layout) .bubble,
    .typing-dots i,
    body:has(.chat-layout) .chat-form .btn.primary {
        animation: none;
    }

    .scroll-bottom {
        transition: none;
    }
}
```

- [ ] **Step 3: Verify the file is served**

Fetch `http://127.0.0.1:5000/static/css/chat-glass.css` with `Invoke-WebRequest -UseBasicParsing`.
Expected: HTTP 200 (Flask serves static files from `static/` even if not yet linked in a template). If 404, confirm the file path/name.

---

### Task 2: Load the CSS on the chat page + scroll button + test

**Files:**
- Modify: `templates/base.html:9` — add a `{% block styles %}` hook in `<head>`
- Modify: `templates/chat.html` — add the styles block and the scroll-to-bottom button
- Modify: `tests/test_preferences.py` — add a page-render test

- [ ] **Step 1: Write the failing test**

Append to `tests/test_preferences.py`:

```python
def test_chat_page_loads_glass_ui_assets(auth_client):
    response = auth_client.get("/chat")

    assert response.status_code == 200
    assert b"css/chat-glass.css" in response.data
    assert b'id="scroll-bottom"' in response.data
```

- [ ] **Step 2: Run it to verify it fails**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py::test_chat_page_loads_glass_ui_assets -v`
Expected: FAIL (the chat page does not yet link `chat-glass.css` nor contain the button).

- [ ] **Step 3: Add the styles block to base.html**

In `templates/base.html`, the `<head>` currently ends:

```html
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
```

Change it to:

```html
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block styles %}{% endblock %}
</head>
```

(Other pages get an empty block — their output is unchanged.)

- [ ] **Step 4: Update chat.html**

In `templates/chat.html`, immediately after `{% extends 'base.html' %}` and `{% block title %}Chat Workspace{% endblock %}` (before `{% block content %}`), add:

```html
{% block styles %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/chat-glass.css') }}">
{% endblock %}
```

Then in the chat panel, after the thread div (currently `<div id="chat-thread" class="chat-thread"></div>`) and before the form, add the scroll-to-bottom button:

```html
        <div id="chat-thread" class="chat-thread"></div>
        <button type="button" id="scroll-bottom" class="scroll-bottom" aria-label="Scroll to bottom">&#8595;</button>
        <form id="chat-form" class="chat-form">
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest tests/test_preferences.py::test_chat_page_loads_glass_ui_assets -v`
Expected: PASS.

- [ ] **Step 6: Run the full Python suite**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest -q`
Expected: 18 passed (was 17; +1 new).

---

### Task 3: Typing dots + scroll-to-bottom logic in chat.js

**Files:**
- Modify: `static/js/chat.js`

- [ ] **Step 1: Read chat.js**

Read `static/js/chat.js` fully (145 lines). Note: `appendBubble` at lines 8-18, the typing bubble creation at lines 57-60, `loadHistory()` at line 145.

- [ ] **Step 2: Add the scroll button reference**

After the element declarations at the top (line 6, `const darkModeToggle = ...`), add:

```javascript
const scrollButton = document.getElementById("scroll-bottom");
```

- [ ] **Step 3: Add `updateScrollButton` and call it from `appendBubble`**

After the `appendBubble` function (line 18), add:

```javascript
function updateScrollButton() {
  const distanceFromBottom =
    thread.scrollHeight - thread.scrollTop - thread.clientHeight;
  scrollButton?.classList.toggle("visible", distanceFromBottom > 120);
}
```

Inside `appendBubble`, after the existing `thread.scrollTop = thread.scrollHeight;` line, add:

```javascript
  updateScrollButton();
```

- [ ] **Step 4: Replace the typing indicator text with dots**

Replace the current typing bubble block:

```javascript
  const typing = document.createElement("div");
  typing.className = "bubble bot typing";
  typing.textContent = "Thinking...";
  thread.appendChild(typing);
```

with:

```javascript
  const typing = document.createElement("div");
  typing.className = "bubble bot typing";
  typing.innerHTML = '<span class="typing-dots"><i></i><i></i><i></i></span>';
  thread.appendChild(typing);
```

(The markup is static and contains no user input, so `innerHTML` is safe here.)

- [ ] **Step 5: Add the scroll listeners at the end of the file**

At the end of `chat.js` (after the existing `loadHistory();` line), add:

```javascript
thread?.addEventListener("scroll", updateScrollButton, { passive: true });
scrollButton?.addEventListener("click", () => {
  thread.scrollTo({ top: thread.scrollHeight, behavior: "smooth" });
});
```

- [ ] **Step 6: Syntax-check the JS**

Run: `node --check static/js/chat.js`
Expected: no output, exit code 0 (valid syntax).

---

### Task 4: End-to-end verification

- [ ] **Step 1: Run both test suites**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest -q`
Expected: 18 passed.

Run: `node --test tests/formatter.test.js`
Expected: 11 passed.

- [ ] **Step 2: Verify assets serve**

Fetch with `Invoke-WebRequest -UseBasicParsing`:
- `http://127.0.0.1:5000/static/css/chat-glass.css` → 200
- `http://127.0.0.1:5000/static/js/chat.js` → 200 (content contains `typing-dots` and `scroll-bottom`)

- [ ] **Step 3: Verify the authenticated chat page references everything**

With a `WebRequestSession`, POST `/login` (`email=tester@example.com`, `password=password123`), then GET `/chat`. Confirm HTTP 200 and that the HTML contains `css/chat-glass.css` and `id="scroll-bottom"`.

- [ ] **Step 4: Manual browser checks**

In a browser at http://127.0.0.1:5000, log in and open `/chat`:
1. Send a message: the user bubble animates in (blur-fade), bouncing typing dots appear, the bot reply animates in. No "Thinking..." text.
2. Scroll the thread up: the scroll-to-bottom button fades in; clicking it glides back to the bottom and hides it.
3. Hover the send button (glow), the input (focus ring), history items, and chips (hover highlight).
4. Switch themes / light-dark: colors cross-fade smoothly (~0.25s).
5. Narrow below 900px: the workspace still works (full-screen layout rules apply).
6. DevTools → rendering → "emulate prefers-reduced-motion": animations are disabled.
7. Home / login / signup pages are visually unchanged.

---

## Self-Review Summary

- **Spec coverage:** visual design (Task 1), bubble animation (Task 1), typing dots (Task 1 + Task 3), send/input feedback (Task 1), sidebar hover (Task 1), theme transitions (Task 1), scroll-to-bottom (Task 1 + Task 2 + Task 3), reduced motion (Task 1), scoped loading (Task 2), tests (Task 2 + Task 4). All spec requirements mapped.
- **No placeholders:** full CSS/HTML/JS/test content provided verbatim in every step.
- **Type consistency:** element IDs (`scroll-bottom`, `chat-thread`), classes (`typing-dots`, `scroll-bottom.visible`, `bubble typing`), and the `updateScrollButton` name match across Tasks 1-3.
