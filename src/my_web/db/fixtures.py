from my_web.db.models import Author, Book
from my_web.extensions import db


def initial_library_data(app):
    """
    Returns initial data for the library database.
    """
    authors = [
        Author(name="George Orwell"),
        Author(name="J.R.R. Tolkien"),
        Author(name="Andrzej Sapkowski"),
    ]

    books = [
        Book(title="1984", author_id=1),
        Book(title="The Hobbit", author_id=2),
        Book(title="The Lord of the Rings", author_id=2),
        Book(title="The Silmarillion", author_id=2, isbn="978-0-04-823139-0"),
        Book(title="The Witcher: The Last Wish", author_id=3, isbn="978-0-575-08244-1"),
    ]

    with app.app_context():
        for author in authors:
            existing_author = Author.query.filter_by(name=author.name).first()
            if not existing_author:
                db.session.add(author)
        db.session.commit()

        for book in books:
            existing_book = Book.query.filter_by(title=book.title).first()
            if not existing_book:
                db.session.add(book)

        db.session.commit()
