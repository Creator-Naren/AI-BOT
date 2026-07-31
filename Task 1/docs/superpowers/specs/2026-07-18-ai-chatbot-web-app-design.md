# AI Chatbot Web Application — Design Spec

Date: 2026-07-18  
Approach: Flask monolith (server-rendered UI + JS-enhanced chat)

## 1) Objective

Build a clean, responsive AI chatbot web app where authenticated users can chat with a bot, view history, and personalize UI with dark mode and themes.

## 2) Scope

### Required
- Attractive homepage/UI
- Chat interface
- User message + bot response loop
- Responsive design
- Python backend integration
- Loading/typing animation

### Included optional features (requested)
- Chat history section
- Login/signup system
- Dark mode
- Database integration
- AI response improvement via OpenAI
- Multiple chat themes

### Excluded from v1
- Voice chatbot

## 3) Architecture

Single Flask application with clear module boundaries:

- **Presentation layer**: Jinja templates + static CSS/JS
- **Application layer**: Flask routes and API endpoints
- **Domain/service layer**: Chatbot service abstraction
  - OpenAI provider when API key is configured
  - Local fallback provider when API key is missing or provider fails
- **Persistence layer**: SQLAlchemy models on SQLite (default dev DB)
- **Auth/session**: Flask-Login + password hashing

This keeps deployment and grading simple while supporting requested functionality.

## 4) Components

1. **Auth module**
   - Signup, login, logout
   - Password hashing and session management

2. **Chat module**
   - `/api/chat` endpoint for message exchange
   - Typing/loading experience in frontend

3. **History module**
   - Persist user and assistant messages
   - Sidebar/history retrieval endpoints

4. **Theme module**
   - Dark/light mode
   - Multiple theme presets (stored per user)

5. **UI module**
   - Homepage, auth pages, chat page
   - Responsive layout and polished components

6. **AI provider module**
   - OpenAI adapter
   - Fallback bot adapter

## 5) Data Model

Core entities:

- **User**
  - id, username, email, password_hash, created_at

- **Conversation**
  - id, user_id, title, created_at, updated_at

- **Message**
  - id, conversation_id, role (`user`/`assistant`), content, created_at

- **UserPreference**
  - id, user_id, dark_mode (bool), theme_name

## 6) Request/Data Flow

1. User authenticates and opens chat UI.
2. Frontend sends user message to `/api/chat`.
3. Backend validates auth and input.
4. User message is saved to DB.
5. Chat service resolves provider:
   - OpenAI provider if configured and healthy
   - Otherwise fallback provider
6. Assistant message is saved.
7. JSON response returns to frontend.
8. Frontend animates typing and renders response.
9. History and preferences are loaded/persisted through dedicated endpoints.

## 7) Error Handling

Use structured error categories:
- `validation_error`
- `auth_error`
- `provider_error`
- `persistence_error`
- `unexpected_error`

API error payload format:

```json
{
  "success": false,
  "code": "provider_timeout",
  "message": "The AI service timed out. Please try again.",
  "details": {}
}
```

Rules:
- Always return explicit, actionable user-facing messages.
- Log technical context server-side (without leaking secrets).
- On provider failure, activate fallback bot and return a traceable code (`fallback_activated`).
- Frontend uses centralized error handling to clear loading state and support retry.

## 8) UX/Frontend Behavior

- Responsive layout for mobile/tablet/desktop
- Smooth send/receive interactions
- Typing/loading indicator before bot response
- History sidebar for conversation recall
- Dark mode toggle + theme selector
- Clear feedback banners/toasts for failures and fallbacks

## 9) Testing and Verification

Automated:
- Auth flow tests (signup/login/logout)
- Protected route/API tests
- Chat API success path
- OpenAI-missing/failure fallback path
- History persistence tests
- Theme preference persistence tests

Manual:
- Responsive behavior across breakpoints
- Typing/loading animation
- History interactions
- Dark mode and theme switching
- Fallback messaging visibility

## 10) Non-Functional Requirements

- Clean folder structure and naming
- Readable, maintainable code and separation of concerns
- No hardcoded secrets in source
- Environment-driven configuration for API keys

## 11) Delivery Artifacts

- Source code/project folder
- Screenshots
- GitHub repository link
- Live hosted link
- Short project description

## 12) Implementation Notes

- Start with Flask monolith for speed and clarity.
- Keep provider interface abstract so OpenAI and fallback remain swappable.
- Ensure app works even without OpenAI key.
