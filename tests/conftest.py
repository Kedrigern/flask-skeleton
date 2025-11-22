import pytest
from unittest.mock import MagicMock, patch
from my_web.app import create_app
from my_web.extensions import db
from my_web.db.models import Author, Book
from my_web.db.fixtures import initial_library_data, get_initial_data


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


class MockSession:
    def __init__(self, initial_authors=None, initial_books=None):
        self.store = {
            Author: {a.id: a for a in
                     initial_authors} if initial_authors else {},
            Book: {b.id: b for b in initial_books} if initial_books else {},
        }
        self.new_id_counters = {
            Author: len(initial_authors) + 1 if initial_authors else 1,
            Book: len(initial_books) + 1 if initial_books else 1,
        }

    def get(self, model, id):
        return self.store.get(model, {}).get(id)

    def add(self, instance):
        model = type(instance)
        if model not in self.store:
            self.store[model] = {}
            self.new_id_counters[model] = 1

        if getattr(instance, 'id', None) is None:
            instance.id = self.new_id_counters[model]
            self.new_id_counters[model] += 1

        self.store[model][instance.id] = instance

    def delete(self, instance):
        model = type(instance)
        if model in self.store and instance.id in self.store[model]:
            del self.store[model][instance.id]

    def commit(self):
        pass

    def flush(self):
        pass

    def rollback(self):
        pass

    def execute(self, statement):
        mock_result = MagicMock()
        target_model = None

        if hasattr(statement, "column_descriptions"):
            for desc in statement.column_descriptions:
                model_cls = desc.get("type")
                if model_cls in self.store:
                    target_model = model_cls
                    break

        if target_model:
            items = list(self.store[target_model].values())

            mock_scalars = MagicMock()
            mock_scalars.all.return_value = items
            mock_scalars.first.return_value = items[0] if items else None

            mock_result.scalars.return_value = mock_scalars
        else:
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars

        return mock_result

    def remove(self):
        pass


@pytest.fixture
def seeded_data():
    authors, books = get_initial_data()

    for i, author in enumerate(authors, start=1):
        author.id = i

    for i, book in enumerate(books, start=1):
        book.id = i

    return authors, books

@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }

    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()
        initial_library_data(app)
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

@pytest.fixture
def fast_app(seeded_data):
    """
    App without DB, using MockSession filled with fixture data.
    """
    authors, books = seeded_data
    mock_session = MockSession(initial_authors=authors, initial_books=books)

    test_config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Will be ignored
    }

    with patch("my_web.extensions.db.session", mock_session):
        app = create_app(test_config=test_config)
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def fast_client(fast_app):
    return fast_app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
