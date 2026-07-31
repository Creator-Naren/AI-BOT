import pytest


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


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post(
        "/signup",
        data={
            "username": "demo",
            "email": "demo@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )
    client.post(
        "/login",
        data={"email": "demo@example.com", "password": "password123"},
        follow_redirects=True,
    )
    return client
