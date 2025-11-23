import json
from my_web.db.models import Book


def test_book_index_redirects(fast_client):
    response = fast_client.get("/book/")
    assert response.status_code == 302
    assert "/book/list" in response.location


def test_book_list_render(fast_client):
    response = fast_client.get("/book/list")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "Books" in data
    assert "1984" in data


def test_book_detail_success(fast_client, seeded_data):
    _, books, _ = seeded_data
    book_obj = next(b for b in books if b.title == "1984")

    response = fast_client.get(f"/book/{book_obj.id}")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "1984" in data
    assert "George Orwell" in data


def test_book_detail_404(fast_client):
    response = fast_client.get("/book/999999")
    assert response.status_code == 404
    data = response.get_data(as_text=True)
    assert "Page Not Found" in data


def test_api_list_basic(client):
    response = client.get("/api/v1/book/list")
    assert response.status_code == 200
    data = response.get_json()

    assert "data" in data
    assert "last_page" in data
    assert len(data["data"]) == 7


def test_api_list_pagination(client):
    response = client.get("/api/v1/book/list?page=1&size=2")
    data = response.get_json()

    assert len(data["data"]) == 2
    assert data["last_page"] >= 4  # 7 book / 2 = 4 pages


def test_api_list_filter_title(client):
    filter_data = json.dumps([{"field": "title", "value": "Hobbit"}])

    response = client.get(f"/api/v1/book/list?filter={filter_data}")
    data = response.get_json()

    assert len(data["data"]) == 1
    assert data["data"][0]["title"] == "The Hobbit"


def test_api_list_filter_isbn(client):
    filter_data = json.dumps([{"field": "isbn", "value": "978-0-04-823139-0"}])

    response = client.get(f"/api/v1/book/list?filter={filter_data}")
    data = response.get_json()

    assert len(data["data"]) == 1
    assert data["data"][0]["title"] == "The Silmarillion"


def test_api_list_sorting(client):
    sort_data = json.dumps([{"field": "title", "dir": "desc"}])

    response = client.get(f"/api/v1/book/list?sort={sort_data}")
    data = response.get_json()

    first_book = data["data"][0]
    last_book = data["data"][-1]

    assert first_book["title"].startswith("The Witcher")
    assert last_book["title"] == "1984"


def test_api_detail_success(client):
    book = Book.query.filter_by(title="Good Omens").first()
    response = client.get(f"/api/v1/book/{book.id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Good Omens"
    assert data["isbn"] == "978-0-575-07919-3"


def test_api_detail_404(client):
    response = client.get("/api/v1/book/999999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not found"


def test_api_list_filter_author(client):
    filter_data = json.dumps([{"field": "authors", "value": "Tolkien"}])

    response = client.get(f"/api/v1/book/list?filter={filter_data}")
    data = response.get_json()

    assert len(data["data"]) == 3
    titles = {b["title"] for b in data["data"]}
    assert "The Hobbit" in titles


def test_api_list_sort_author(client):
    sort_data = json.dumps([{"field": "authors", "dir": "asc"}])

    response = client.get(f"/api/v1/book/list?sort={sort_data}")
    data = response.get_json()

    books = data["data"]

    idx_orwell = next(i for i, b in enumerate(books) if b["title"] == "1984")
    idx_tolkien = next(i for i, b in enumerate(books) if b["title"] == "The Hobbit")

    # Orwell (G) < Tolkien (J)
    assert idx_orwell < idx_tolkien


def test_api_list_sort_author_desc(client):
    sort_data = json.dumps([{"field": "authors", "dir": "desc"}])

    response = client.get(f"/api/v1/book/list?sort={sort_data}")
    data = response.get_json()

    first_book = data["data"][0]

    assert "Neil Gaiman" in [a["name"] for a in first_book["authors"]]


def test_api_create_update_lifecycle(client, auth):
    """Lifecycle test: Create, Update, Add author"""

    auth.register("Editor", "editor@example.com", "password")
    auth.login("editor@example.com", "password")

    # 2. Create Book
    resp = client.post("/api/v1/book/", json={"title": "Clean Code", "isbn": "999-888"})
    assert resp.status_code == 201
    book_data = resp.get_json()
    book_id = book_data["id"]
    assert book_data["authors"] == []

    # 3. Update Book
    resp = client.patch(f"/api/v1/book/{book_id}", json={"title": "Clean Coder"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Clean Coder"

    # 4. Add Author (George Orwell has ID 1 from fixtures)
    resp = client.put(f"/api/v1/book/{book_id}/authors/1")
    assert resp.status_code == 200

    # 5. Verify Author Added
    resp = client.get(f"/api/v1/book/{book_id}")
    data = resp.get_json()
    assert len(data["authors"]) == 1
    assert data["authors"][0]["name"] == "George Orwell"

    # 6. Remove Author
    resp = client.delete(f"/api/v1/book/{book_id}/authors/1")
    assert resp.status_code == 200

    # 7. Verify Empty Again
    resp = client.get(f"/api/v1/book/{book_id}")
    assert len(resp.get_json()["authors"]) == 0


def test_api_create_validation_error(client, auth):
    auth.register("Editor", "editor@example.com", "password")
    auth.login("editor@example.com", "password")

    # Title missing
    resp = client.post("/api/v1/book/", json={"isbn": "123"})
    assert resp.status_code == 400
    assert "title" in str(resp.get_json())


def test_api_add_author_not_found(client, auth):
    auth.register("Editor", "editor@example.com", "password")
    auth.login("editor@example.com", "password")

    # Non-existent book
    resp = client.put("/api/v1/book/99999/authors/1")
    assert resp.status_code == 404
