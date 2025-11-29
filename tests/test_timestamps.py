from time import sleep

import pytest

from my_web.schemas.book import BookCreateSchema
from my_web.services.book import book_service


@pytest.mark.usefixtures("app")
class TestTimestamps:
    def test_created_at_is_set_automatically(self):
        data = BookCreateSchema(title="Time Book").model_dump()
        book = book_service.create(data)

        assert book.created_at is not None
        assert book.updated_at is not None
        assert book.created_at == book.updated_at

    def test_updated_at_changes_on_update(self):
        """Testuje, že updated_at se změní při editaci."""
        book = book_service.create(BookCreateSchema(title="Original").model_dump())
        original_update_time = book.updated_at

        sleep(1.1)  # SQLite is very unprecise

        book_service.update(book.id, {"title": "Updated"})

        from my_web.extensions import db

        db.session.refresh(book)

        assert book.updated_at > original_update_time
        assert book.created_at < book.updated_at
