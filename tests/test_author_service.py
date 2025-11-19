import pytest
from my_web.db.models import Author
from my_web.extensions import db
from my_web.services.base import CRUDService
from my_web.services.author import AuthorService


@pytest.mark.usefixtures("app")
class TestAuthorService:

    def test_01_create_author_success(self):
        data = {"name": "Test Author A"}

        author = AuthorService.create(data)

        assert author.id is not None
        assert author.name == "Test Author A"

        retrieved_author = Author.query.filter_by(name="Test Author A").first()
        assert retrieved_author.id == author.id

    def test_02_get_author_success(self):
        """Tests retrieving an author by ID."""
        new_author = AuthorService.create({"name": "Test Author B"})

        author = AuthorService.get(new_author.id)

        assert author is not None
        assert author.name == "Test Author B"

    def test_03_get_author_not_found(self):
        """Tests that None is returned for a non-existent ID."""
        author = AuthorService.get(999999)
        assert author is None

    def test_04_update_author_success(self):
        """Tests updating the author's name."""
        author = AuthorService.create({"name": "Test Author C"})
        new_name = "Updated Author C"

        updated_author = AuthorService.update(author.id, {"name": new_name})

        assert updated_author is not None
        assert updated_author.name == new_name

        # Verify in the database that the change was committed
        db_author = AuthorService.get(author.id)
        assert db_author.name == new_name

    def test_05_update_author_ignores_pk(self):
        """Tests that the method ignores attempts to overwrite the PK (id)."""
        author = AuthorService.create({"name": "Test Author D"})

        # Attempt to overwrite ID and Name
        updated_author = AuthorService.update(author.id, {"id": 999, "name": "Name Change"})

        assert updated_author is not None
        assert updated_author.id == author.id  # ID REMAINS ORIGINAL
        assert updated_author.name == "Name Change"

    def test_06_delete_author_success(self):
        """Tests deleting an existing author."""
        author = AuthorService.create({"name": "Test Author E"})
        author_id = author.id

        result = AuthorService.delete(author_id)

        assert result is True
        assert AuthorService.get(author_id) is None  # Verify deletion

    def test_07_delete_author_not_found(self):
        """Tests deleting a non-existent author."""
        result = AuthorService.delete(999999)
        assert result is False

    def test_08_create_integrity_error(self):
        """Tests that create raises an error on integrity violation (UniqueConstraint)."""
        AuthorService.create({"name": "Unique Name"})

        with pytest.raises(ValueError):
            AuthorService.create({"name": "Unique Name"})

    def test_09_upsert_create_new(self):
        """Tests creating a new author using upsert."""
        new_name = "New Upsert Author"
        data = {"name": new_name}

        author, is_new = AuthorService.upsert(None, data)

        assert is_new is True
        assert author.name == new_name
        assert AuthorService.get(author.id) is not None

    def test_10_upsert_update_existing(self):
        """Tests updating an existing author using upsert."""
        author = AuthorService.create({"name": "Initial Name"})
        new_name = "Updated Upsert Name"

        updated_author, is_new = AuthorService.upsert(author.id, {"name": new_name})

        assert is_new is False
        assert updated_author.name == new_name
        assert updated_author.id == author.id

    def test_11_upsert_ignores_pk_in_data(self):
        """Tests that upsert ignores overwriting ID in update data."""
        author = AuthorService.create({"name": "PK Check"})

        updated_author, is_new = AuthorService.upsert(author.id, {"id": 9999, "name": "PK Ignored"})

        assert is_new is False
        assert updated_author.id == author.id
        assert updated_author.name == "PK Ignored"

    def test_12_get_paginated_basic(self):
        """Tests basic pagination."""
        # Fixtures should have at least 5 authors

        result = AuthorService.get_paginated(page=1, per_page=2)

        assert len(result["data"]) == 2
        assert result["last_page"] >= 3

    def test_13_get_paginated_sort_desc(self):
        """Tests sorting by name in descending order."""
        result = AuthorService.get_paginated(page=1, per_page=10, sort_field="name", sort_dir="desc")

        # 'Tolkien' (J) should be before 'Orwell' (G)
        first_author_name = result["data"][0]["name"]

        # Assume 'Terry Pratchett' or 'J.R.R. Tolkien' is at the end of the alphabet
        assert first_author_name.startswith("Terry") or first_author_name.startswith("J.R.R.")

    def test_14_get_paginated_filter_success(self):
        """Tests filtering by FILTER_FIELD ('name')."""
        result = AuthorService.get_paginated(filter_value="Tolkien")

        assert len(result["data"]) == 1  # Should find 'J.R.R. Tolkien'
        assert result["data"][0]["name"] == "J.R.R. Tolkien"

    def test_15_get_paginated_no_filter_field(self):
        """Tests that the method ignores filter if FILTER_FIELD is not set."""

        # Create a temporary service class without FILTER_FIELD
        class NoFilterService(CRUDService[Author]):
            MODEL = Author

        result = NoFilterService.get_paginated(filter_value="Tolkien")

        # Should return all authors (no filter), i.e. more than 1
        assert len(result["data"]) > 1
