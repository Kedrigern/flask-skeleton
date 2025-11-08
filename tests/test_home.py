import pytest
from my_web.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_renders_template(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data
    assert b"Hello world" in response.data
    assert b"My Web App" in response.data
