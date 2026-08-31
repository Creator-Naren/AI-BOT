def test_chat_api_returns_response_and_persists_history(auth_client):
    response = auth_client.post("/api/chat", json={"message": "Hello bot"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert isinstance(payload["assistant_message"], str)
    assert len(payload["assistant_message"]) > 0

    history = auth_client.get("/api/history")
    history_payload = history.get_json()
    assert history.status_code == 200
    assert history_payload["success"] is True
    assert len(history_payload["conversations"]) >= 1


def test_chat_api_passes_personality_to_provider(auth_client, monkeypatch):
    auth_client.post("/api/preferences/personality", json={"personality": "Be funny"})

    captured = {}

    class FakeProvider:
        def generate_reply(self, message):
            return "echo"

    def fake_build(config, user_preferences=None):
        captured["personality"] = getattr(user_preferences, "personality", None)
        return FakeProvider()

    import routes.api

    monkeypatch.setattr(routes.api, "build_provider", fake_build)

    response = auth_client.post("/api/chat", json={"message": "Hello bot"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["assistant_message"] == "echo"
    assert captured["personality"] == "Be funny"


def test_get_conversation_messages_and_new_conversation(auth_client):
    new_resp = auth_client.post("/api/conversations/new")
    new_data = new_resp.get_json()
    assert new_resp.status_code == 200
    assert new_data["success"] is True
    conv_id = new_data["conversation_id"]

    chat_resp = auth_client.post(
        "/api/chat", json={"message": "Hello new chat", "conversation_id": conv_id}
    )
    assert chat_resp.status_code == 200

    msg_resp = auth_client.get(f"/api/conversations/{conv_id}/messages")
    msg_data = msg_resp.get_json()
    assert msg_resp.status_code == 200
    assert msg_data["success"] is True
    assert len(msg_data["messages"]) == 2
    assert msg_data["messages"][0]["role"] == "user"
    assert msg_data["messages"][0]["content"] == "Hello new chat"
    assert msg_data["messages"][1]["role"] == "assistant"
