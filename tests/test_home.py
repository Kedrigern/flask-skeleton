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
    assert response.status_code == 200
    assert b"<html" in response.data
    assert b"Hello world" in response.data
    assert b"My Web App" in response.data


def test_404_error_renders_template(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data
    assert b"The page you are looking for does not exist." in response.data


def test_500_error_renders_template(client, monkeypatch):
    # Simulate a view raising an exception
    from flask import Blueprint
    bp = Blueprint("fail", __name__)

    @bp.route("/fail")
    def fail():
        raise Exception("Test exception")

    client.application.register_blueprint(bp)
    response = client.get("/fail")
    assert response.status_code == 500
    assert b"500 - Internal Server Error" in response.data
    assert b"Something went wrong on our end." in response.data
