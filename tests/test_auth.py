from my_web.models import User


def register(client, name, email, password):
    return client.post(
        "/auth/register",
        data={"name": name, "email": email, "password": password},
        follow_redirects=True,
    )


def login(client, email, password):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def logout(client):
    return client.get("/auth/logout", follow_redirects=True)


def test_register_success(client):
    response = register(client, "Test", "test@example.com", "password")
    data = response.get_data(as_text=True)
    assert "Profil uživatele" in data
    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None


def test_register_duplicate_email(client):
    register(client, "Test", "test@example.com", "password")
    response = register(client, "Test2", "test@example.com", "password2")
    data = response.get_data(as_text=True)
    assert "Email already registered" in data


def test_login_success(client):
    register(client, "Test", "test@example.com", "password")
    response = login(client, "test@example.com", "password")
    data = response.get_data(as_text=True)
    assert "Profil uživatele" in data


def test_login_invalid(client):
    register(client, "Test", "test@example.com", "password")
    response = login(client, "test@example.com", "wrongpass")
    data = response.get_data(as_text=True)
    assert "Invalid email or password" in data


def test_logout(client):
    register(client, "Test", "test@example.com", "password")
    login(client, "test@example.com", "password")
    response = logout(client)
    data = response.get_data(as_text=True)
    assert "Přihlásit" in data or "Prihlasit" in data


def test_profile_requires_login(client):
    response = client.get("/user/profile", follow_redirects=True)
    data = response.get_data(as_text=True)
    assert "Přihlášení" in data or "Prihlaseni" in data


def test_profile_shows_user_data(client):
    register(client, "Test", "test@example.com", "password")
    login(client, "test@example.com", "password")
    response = client.get("/user/profile")
    data = response.get_data(as_text=True)
    assert "Test" in data
    assert "test@example.com" in data
    assert "user" in data
