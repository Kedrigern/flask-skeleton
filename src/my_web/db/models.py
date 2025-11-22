from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.associationproxy import association_proxy

from flask_login import UserMixin

from my_web.extensions import db


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


class User(db.Model, UserMixin):
    """Application user model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.USER, nullable=False)

    def __repr__(self) -> str:  # helpful for debugging
        return f"<User id={self.id} email={self.email} role={self.role.value}>"


class BookAuthorAssociation(db.Model):
    """Association table for many-to-many Book <-> Author.

    Kept as explicit model (instead of raw Table) to allow future extra columns
    like contribution_type, order, etc.
    """

    __tablename__ = "book_author"

    book_id: Mapped[int] = mapped_column(db.ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(
        db.ForeignKey("authors.id"), primary_key=True
    )

    book = relationship("Book", back_populates="author_associations")
    author = relationship("Author", back_populates="book_associations")

    def __repr__(self) -> str:
        return (
            f"<BookAuthorAssociation book_id={self.book_id} author_id={self.author_id}>"
        )


class Author(db.Model):
    """Author model representing a book author."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)

    book_associations = relationship(
        "BookAuthorAssociation", back_populates="author", cascade="all, delete-orphan"
    )
    # Convenient direct access to books
    books = association_proxy(
        "book_associations",
        "book",
        creator=lambda book: BookAuthorAssociation(book=book),
    )

    def __repr__(self) -> str:
        return f"<Author id={self.id} name={self.name}>"


class Book(db.Model):
    """Book model representing a book."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)

    author_associations = relationship(
        "BookAuthorAssociation", back_populates="book", cascade="all, delete-orphan"
    )
    # Convenient direct access to authors
    authors = association_proxy(
        "author_associations",
        "author",
        creator=lambda author: BookAuthorAssociation(author=author),
    )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title}>"
