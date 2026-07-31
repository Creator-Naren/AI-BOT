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


def test_build_system_prompt_none_and_whitespace():
    for personality in (None, "   "):
        prompt = build_system_prompt(personality)
        assert "Answer clearly and concisely" in prompt
        assert "Adopt this personality" not in prompt


def test_build_provider_returns_fallback_without_api_key():
    from services.fallback_provider import FallbackProvider

    provider = build_provider({"OPENAI_API_KEY": None})
    assert isinstance(provider, FallbackProvider)


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
