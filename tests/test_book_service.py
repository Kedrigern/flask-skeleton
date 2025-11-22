import pytest
from my_web.db.models import Book
from my_web.services.book import book_service


@pytest.mark.usefixtures("app")
class TestBookService:
    def test_01_create_book_success(self):
        """Tests creating a new book using a dictionary (DTO)."""
        data = {"title": "New Simple Book", "isbn": "123-456-789"}

        book = book_service.create(data)

        assert book.id is not None
        assert book.title == "New Simple Book"
        assert book.isbn == "123-456-789"

        # Verify persistence
        retrieved_book = Book.query.filter_by(title="New Simple Book").first()
        assert retrieved_book is not None

    def test_02_get_book_success(self):
        """Tests retrieving a book by ID."""
        # '1984' exists from fixtures
        book_in_db = Book.query.filter_by(title="1984").first()

        book = book_service.get(book_in_db.id)

        assert book is not None
        assert book.title == "1984"

    def test_03_update_book_success(self):
        """Tests updating a book's attributes."""
        book = book_service.create({"title": "Old Title"})
        new_title = "Updated Title"

        updated_book = book_service.update(book.id, {"title": new_title})

        assert updated_book is not None
        assert updated_book.title == new_title

        # Verify persistence
        db_book = book_service.get(book.id)
        assert db_book.title == new_title

    def test_04_delete_book_success(self):
        """Tests deleting an existing book."""
        book = book_service.create({"title": "To Be Deleted"})
        book_id = book.id

        result = book_service.delete(book_id)

        assert result is True
        assert book_service.get(book_id) is None

    def test_05_upsert_create_new(self):
        """Tests creating a new book via upsert (ID=None)."""
        data = {"title": "Upserted New Book"}

        book, is_new = book_service.upsert(None, data)

        assert is_new is True
        assert book.title == "Upserted New Book"
        assert book.id is not None

    def test_06_upsert_update_existing(self):
        """Tests updating an existing book via upsert."""
        book = book_service.create({"title": "Original Upsert"})

        updated_book, is_new = book_service.upsert(
            book.id, {"title": "Updated via Upsert"}
        )

        assert is_new is False
        assert updated_book.id == book.id
        assert updated_book.title == "Updated via Upsert"

    def test_07_get_paginated_basic(self):
        """Tests basic pagination."""
        # Fixtures contain 7 books
        result = book_service.get_paginated(page=1, per_page=3)

        assert len(result["data"]) == 3
        assert result["last_page"] >= 3

    def test_08_get_paginated_filter_success(self):
        """Tests filtering by FILTER_FIELD ('title')."""
        result = book_service.get_paginated(filter_value="Hobbit")

        assert len(result["data"]) == 1
        assert result["data"][0].title == "The Hobbit"

    def test_09_get_paginated_sort(self):
        """Tests sorting by title."""
        # Sorting DESC: 'The Witcher...' should be near top, '1984' near bottom
        result = book_service.get_paginated(
            page=1, per_page=10, sort_field="title", sort_dir="desc"
        )

        titles = [b.title for b in result["data"]]
        # Just check that the first item is alphabetically "larger" than the last
        assert titles[0] > titles[-1]
