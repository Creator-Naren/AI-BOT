def test_signup_login_logout_flow(client):
    signup = client.post(
        "/signup",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "strongpass123",
        },
        follow_redirects=True,
    )
    assert signup.status_code == 200
    assert b"Account created" in signup.data

    login = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "strongpass123"},
        follow_redirects=True,
    )
    assert login.status_code == 200
    assert b"Chat Workspace" in login.data

    logout = client.get("/logout", follow_redirects=True)
    assert logout.status_code == 200
    assert b"Logged out" in logout.data
