def test_login_success(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"user": "admin1", "pass": "Password@123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin1"
    assert data["user"]["role"] == "institution_admin"
    assert data["user"]["institution_id"] == "INS-001"


def test_login_invalid_password(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"user": "admin1", "pass": "WrongPassword"},
    )
    assert res.status_code == 401
    assert "Incorrect" in res.json()["detail"]


def test_login_nonexistent_user(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"user": "nonexistent_user", "pass": "Password@123"},
    )
    assert res.status_code == 401


def test_get_current_user_profile(client, token_admin_ins1):
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
    assert res.json()["username"] == "admin1"


def test_logout_clears_cookie(client, token_admin_ins1):
    res = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
