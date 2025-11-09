import pytest
from my_web.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = False  # For testing
    with app.test_client() as client:
        yield client


def test_home_renders_template(client):
    response = client.get("/")
    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<html" in data
    assert "Hello world" in data
    assert "My web" in data


def test_home_about_renders_template(client):
    response = client.get("/about")
    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Repository" in data


def test_404_error_renders_template(client):
    response = client.get("/nonexistent")
    data = response.get_data(as_text=True)
    assert response.status_code == 404
    assert "404 - Page Not Found" in data
    assert "The page you are looking for does not exist." in data


def test_500_error_renders_template(client, monkeypatch):
    # Simulate a view raising an exception
    from flask import Blueprint
    bp = Blueprint("fail", __name__)

    @bp.route("/fail")
    def fail():
        raise Exception("Test exception")

    client.application.register_blueprint(bp)
    response = client.get("/fail")
    data = response.get_data(as_text=True)
    assert response.status_code == 500
    assert "500 - Internal Server Error" in data
    assert "Something went wrong on our end." in data
