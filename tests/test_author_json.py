import pytest
from my_web.services.author import author_service
from my_web.schemas.author import AuthorCreateSchema
from my_web.extensions import db


@pytest.mark.usefixtures("app")
class TestAuthorJson:
    def test_create_author_with_preferences(self):
        """Tests saving JSON data when creating an author."""
        prefs = {
            "language": "en",
            "genre_focus": ["scifi", "fantasy"],
            "contact": {"twitter": "@handle"},
        }

        payload = {"name": "Json Author", "preferences": prefs}

        # Validate via Pydantic and save
        data = AuthorCreateSchema(**payload).model_dump()
        author = author_service.create(data)

        # Verify correct retrieval
        assert author.preferences == prefs
        assert author.preferences["contact"]["twitter"] == "@handle"

    def test_update_mutable_json(self):
        """
        Critical test: Verifies that SQLAlchemy detects in-place changes within JSON.
        Without MutableDict, this test would fail.
        """
        # 1. Create
        author = author_service.create(
            {
                "name": "Mutable Author",
                "preferences": {"theme": "dark", "notifications": True},
            }
        )

        # 2. Mutate value IN-PLACE
        fetched_author = author_service.get(author.id)
        fetched_author.preferences["theme"] = "light"

        # Commit directly to simulate model usage (Service.update usually replaces dicts)
        db.session.commit()

        # 3. Verify in new transaction
        db.session.expire_all()

        reloaded_author = author_service.get(author.id)
        assert reloaded_author.preferences["theme"] == "light"

    def test_service_update_preferences(self):
        """Tests updating the entire JSON object via Service layer."""
        author = author_service.create({"name": "Service Update Author"})
        assert author.preferences == {}  # Default

        new_prefs = {"newsletter": True}
        updated_author = author_service.update(author.id, {"preferences": new_prefs})

        assert updated_author.preferences == new_prefs