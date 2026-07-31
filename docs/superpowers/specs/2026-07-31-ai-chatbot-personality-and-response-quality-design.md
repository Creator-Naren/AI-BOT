# Design: AI Chatbot Personality & Response Quality

**Date:** 2026-07-31
**Status:** Approved

## Problem

Two issues reported by the user:

1. **Messy responses.** The AI returns markdown-formatted replies (headings, bold, lists), but the chat UI renders them as raw text via `textContent`. Users see walls of `#`, `**`, `-`, and `1.` symbols with no paragraph structure.
2. **No personality control.** Users cannot influence the bot's tone or character.

## Goal

- Make bot responses clear and readable: prompt the model for plain, well-structured text and render any markdown it still produces.
- Let each user set a personality for the bot that is persisted and applied to every reply.

## Approach

DB-backed personality + prompt engineering + a small built-in markdown formatter. No new dependencies.

## Backend

### Data model

Add a `personality` column to the existing `UserPreference` model:

```python
personality = db.Column(db.Text, default="", nullable=False)
```

- Fresh databases get the column automatically via `db.create_all()`.
- The existing `chatbot.db` needs a one-time migration:

```sql
ALTER TABLE user_preference ADD COLUMN personality TEXT DEFAULT '';
```

- Tests use in-memory databases, so `create_all()` is sufficient there.

### System prompt

New function in `services/ai_provider.py`:

```python
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
```

- Empty personality → the default clarity prompt only.

### Providers

- `services/openai_provider.py` and `services/openrouter_provider.py` accept a `system_prompt` parameter (default `"You are a helpful AI assistant."`).
- `generate_reply` uses it as the system message.
- `build_provider(config, user_preferences=None)` builds the system prompt from `user_preferences.personality` and passes it to the provider.

### Chat route

- `routes/api.py` `chat()` loads the current user's `UserPreference` and passes it to `build_provider(current_app.config, user_preferences)`.

### Preferences endpoint

New endpoint:

```
POST /api/preferences/personality
Body: { "personality": "..." }
```

- Saves the personality to the user's `UserPreference` (creates the row if missing).
- Truncates input to 500 characters.
- Returns the saved value.

## Frontend

### Chat page

- `routes/pages.py` `chat()` passes `personality=pref.personality` (default `""`) to the template.
- `chat.html` sets `window.initialPersonality = "{{ personality }}"`.
- New "Bot Personality" section in the sidebar (above Theme):
  - Preset chips: **None**, **Friendly**, **Professional**, **Humorous**.
  - Free-text box (`textarea`) for custom personality.
  - **Save** button with a transient "Saved" status.
  - Clicking a preset chip fills the text box with a preset description.

Preset descriptions:

| Preset | Value |
| --- | --- |
| None | *(empty)* |
| Friendly | "You are warm, encouraging, and approachable." |
| Professional | "You are professional, precise, and to the point." |
| Humorous | "You are witty and playful, using light humor where appropriate." |

### chat.js

- On load, populate the text box from `window.initialPersonality`.
- Preset chips set the text box value.
- Save button POSTs `{ personality }` to `/api/preferences/personality` and shows a short "Saved" message.
- `appendBubble("bot", text)` renders via the new formatter; user bubbles keep `textContent`.

### Markdown formatter

New file `static/js/formatter.js` exporting `formatMarkdown(text)`:

- Escape all HTML entities first (XSS-safe).
- Format, in order:
  - Code spans: `` `code` `` → `<code>code</code>`.
  - Bold: `**text**` → `<strong>text</strong>`.
  - Italic: `*text*` → `<em>text</em>`.
  - Headings: lines starting with `### ` → `<h4>`, `## ` → `<h3>`, `# ` → `<h2>`.
  - Bullet lists: consecutive lines starting with `- ` → `<ul><li>`.
  - Numbered lists: consecutive lines starting with `1. `/`2. `/... → `<ol><li>`.
  - Paragraphs/line breaks: single `\n` → `<br>`, blank line separates paragraphs.
- The formatter is pure (no DOM/state) and dependency-free.

### CSS

- `.bubble.bot` inner elements: headings, `ul`/`ol`, `li`, `code`, and paragraph spacing.

## Error handling

- Personality text is capped at 500 chars on save.
- The AI call already falls back to `FallbackProvider` on API errors; unchanged.
- Formatter is safe because all input is HTML-escaped before any tags are applied.

## Testing

- New unit tests:
  - `build_system_prompt("")` returns the clarity prompt without a personality line.
  - `build_system_prompt("sarcastic")` includes the personality text.
  - `POST /api/preferences/personality` saves and returns the value; empty input clears it.
  - `chat()` continues to return success (uses `FallbackProvider` in tests since no API key is configured in the test app).
- Existing tests (`test_auth.py`, `test_chat_api.py`, `test_preferences.py`) keep passing.

## Out of scope

- Full markdown support (tables, images, fenced code blocks with syntax highlighting).
- Per-conversation personalities.
- Temperature/creativity controls.
