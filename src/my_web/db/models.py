from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from flask_login import UserMixin

from my_web.extensions import db


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


class User(db.Model, UserMixin):
    """
    Application user model.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.USER, nullable=False)


class Author(db.Model):
    """
    Author model representing a book author
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)


class Book(db.Model):
    """
    Book model representing a book
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    # And what about co-authors?
    author_id: Mapped[int] = mapped_column(db.ForeignKey("authors.id"), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author_id": self.author_id,
            "isbn": self.isbn,
        }


def prepare_db() -> None:
    db.create_all()
