from services.fallback_provider import FallbackProvider
from services.openai_provider import OpenAIProvider


def build_system_prompt(personality=""):
    prompt = (
        "Answer clearly and concisely. Use plain text and short sentences. "
        "If you use markdown, keep it simple: short headings, bullet lists, and bold."
    )
    personality = (personality or "").strip()
    if personality:
        prompt += (
            "\n\nAdopt this personality and stay in character while remaining "
            f"clear and helpful:\n{personality}"
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

    return OpenAIProvider(api_key, model=model, base_url=base_url, system_prompt=system_prompt)
