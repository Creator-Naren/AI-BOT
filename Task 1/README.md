# AI Chatbot Web Application

Flask-based chatbot application with:
- Responsive homepage and chat UI
- User authentication (signup/login/logout)
- OpenAI integration with fallback chatbot mode
- Chat history persistence
- Dark mode and multiple themes

## Setup

1. Create virtual environment
   - `python -m venv .venv`
2. Activate virtual environment (Windows)
   - `.venv\\Scripts\\activate`
3. Install dependencies
   - `pip install -r requirements.txt`
4. Configure environment
   - Copy `.env.example` to `.env`
5. Run app
   - `python app.py`

## Tests

Run:

`python -m pytest -q`
