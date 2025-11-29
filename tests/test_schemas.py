from datetime import datetime

import pydantic
import pytest

from my_web.schemas.book import BookSchema


def test_book_schema_validation():
    now = datetime.now()
    raw_data = {
        "id": 1,
        "title": "Test Book",
        "authors": [{"id": 2, "name": "Author", "created_at": now, "updated_at": now}],
        "created_at": now,
        "updated_at": now,
    }

    book = BookSchema(**raw_data)
    assert book.id == 1
    assert book.title == "Test Book"


def test_book_schema_invalid():
    with pytest.raises(pydantic.ValidationError):
        BookSchema(id=1, isbn="123")
