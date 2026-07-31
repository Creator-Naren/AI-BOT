def test_theme_preference_can_be_saved(auth_client):
    response = auth_client.post(
        "/api/preferences/theme",
        json={"theme": "midnight", "dark_mode": True},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["theme"] == "midnight"
    assert payload["dark_mode"] is True


def test_test_app_has_no_ai_key(app):
    assert app.config.get("OPENAI_API_KEY") is None
    assert app.config.get("AI_BASE_URL") is None


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


def test_personality_ignores_non_string_input(auth_client):
    response = auth_client.post("/api/preferences/personality", json={"personality": 123})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["personality"] == ""


def test_chat_page_renders_saved_personality(auth_client):
    auth_client.post("/api/preferences/personality", json={"personality": "Warm mentor"})
    response = auth_client.get("/chat")

    assert response.status_code == 200
    assert b"Warm mentor" in response.data


def test_chat_page_loads_glass_ui_assets(auth_client):
    response = auth_client.get("/chat")

    assert response.status_code == 200
    assert b"css/chat-glass.css" in response.data
    assert b'id="scroll-bottom"' in response.data
    assert b'class="scroll-bottom"' in response.data
