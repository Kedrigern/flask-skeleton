import pytest
from my_web.app import create_app
from my_web.extensions import db
from my_web.db.fixtures import initial_library_data


class AuthActions:
    def __init__(self, client):
        self._client = client

    def register(self, name, email, password):
        return self._client.post(
            "/auth/register",
            data={
                "name": name,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=True,
        )

    def login(self, email, password):
        return self._client.post(
            "/auth/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self._client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        initial_library_data(app)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
