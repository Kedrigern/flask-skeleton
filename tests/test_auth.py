from my_web.db.models import User


def logout(client):
    return client.get("/auth/logout", follow_redirects=True)


def test_register_success(auth):
    response = auth.register("Test", "abcd@example.com", "password")
    data = response.get_data(as_text=True)
    assert "User profile" in data
    user = User.query.filter_by(email="abcd@example.com").first()
    assert user is not None


def test_register_duplicate_email(auth):
    auth.register("Test", "test@example.com", "password")
    response = auth.register("Test2", "test@example.com", "password2")
    data = response.get_data(as_text=True)
    assert "Email already registered" in data


def test_login_success(auth):
    response = auth.login("test@example.com", "password")
    data = response.get_data(as_text=True)
    assert "User profile" in data


def test_login_invalid(auth):
    response = auth.login("test@example.com", "wrongpass")
    data = response.get_data(as_text=True)
    assert "Invalid email or password" in data


def test_logout(auth):
    auth.register("Test", "test@example.com", "password")
    auth.login("test@example.com", "password")
    response = auth.logout()
    data = response.get_data(as_text=True)
    assert "Login" in data


def test_profile_requires_login(client):
    response = client.get("/user/profile", follow_redirects=True)
    data = response.get_data(as_text=True)
    assert "Login" in data


def test_profile_shows_user_data(auth, client):
    auth.register("Test", "test@example.com", "password")
    auth.login("test@example.com", "password")
    response = client.get("/user/profile")
    data = response.get_data(as_text=True)
    assert "Test" in data
    assert "test@example.com" in data
    assert "user" in data
