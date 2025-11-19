import json
from sqlalchemy import func
from my_web.extensions import db
from my_web.db.models import Book, Author, BookAuthorAssociation
from my_web.services.base import CRUDService


class BookService(CRUDService[Book]):
    MODEL = Book
    PK_NAME = 'id'
    FILTER_FIELD = 'title'

    @staticmethod
    def get_books(page: int, per_page: int, sort_param: str | None = None, filter_param: str | None = None) -> dict:
        """Retrieves a paginated, filtered, and sorted list of books for API."""

        columns_map = {"id": Book.id, "title": Book.title, "isbn": Book.isbn}
        stmt = db.select(Book)

        if filter_param:
            try:
                filters = json.loads(filter_param)
                for f in filters:
                    field = f.get("field")
                    value = f.get("value")

                    if not value:
                        continue

                    if field == "authors":
                        stmt = stmt.join(Book.author_associations).join(BookAuthorAssociation.author)
                        stmt = stmt.where(Author.name.ilike(f"%{value}%"))

                    elif field in columns_map:
                        col = columns_map[field]
                        stmt = stmt.where(col.ilike(f"%{value}%"))
            except (ValueError, TypeError) as e:
                print(f"Filter parsing error: {e}")

        if sort_param:
            try:
                sorters = json.loads(sort_param)
                for s in sorters:
                    field = s.get("field")
                    direction = s.get("dir")

                    if field == "authors":
                        stmt = stmt.outerjoin(Book.author_associations).outerjoin(BookAuthorAssociation.author)
                        stmt = stmt.group_by(Book.id)
                        order_col = func.min(Author.name)

                        if direction == "desc":
                            stmt = stmt.order_by(order_col.desc())
                        else:
                            stmt = stmt.order_by(order_col.asc())

                    elif field in columns_map:
                        col = columns_map[field]
                        if direction == "desc":
                            stmt = stmt.order_by(col.desc())
                        else:
                            stmt = stmt.order_by(col.asc())
            except (ValueError, TypeError) as e:
                print(f"Sort parsing error: {e}")
        else:
            stmt = stmt.order_by(Book.title.asc())

        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

        return {
            "last_page": pagination.pages,
            "data": [book.as_dict() for book in pagination.items],
        }
