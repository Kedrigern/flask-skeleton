from my_web.db.models import Author, Book
from my_web.extensions import db


def get_initial_data():
    """
    Vrací čistá data (instance modelů) bez vazby na DB session.
    Toto využijeme v testech pro naplnění Mocku.
    """
    authors = [
        Author(name="George Orwell"),
        Author(name="J.R.R. Tolkien"),
        Author(name="Andrzej Sapkowski"),
        Author(name="Terry Pratchett"),
        Author(name="Neil Gaiman"),
    ]

    auth_map = {a.name: a for a in authors}

    books = [
        Book(title="1984", isbn=None, authors=[auth_map["George Orwell"]]),
        Book(title="The Hobbit", isbn=None,
             authors=[auth_map["J.R.R. Tolkien"]]),
        Book(title="The Lord of the Rings", isbn=None,
             authors=[auth_map["J.R.R. Tolkien"]]),
        Book(title="The Silmarillion", isbn="978-0-04-823139-0",
             authors=[auth_map["J.R.R. Tolkien"]]),
        Book(title="The Witcher: The Last Wish", isbn="978-0-575-08244-1",
             authors=[auth_map["Andrzej Sapkowski"]]),
        Book(title="Good Omens", isbn="978-0-575-07919-3",
             authors=[auth_map["Terry Pratchett"], auth_map["Neil Gaiman"]]),
        Book(title="American Gods", isbn="978-0-06-257223-3",
             authors=[auth_map["Neil Gaiman"]]),
    ]

    return authors, books


def initial_library_data(app):
    """
    Seed initial authors and books into real DB.
    Idempotent: existing authors/books are reused.
    """
    authors_to_create, books_to_create = get_initial_data()

    with app.app_context():
        persisted_authors = {}
        for author in authors_to_create:
            existing = Author.query.filter_by(name=author.name).first()
            if existing:
                persisted_authors[author.name] = existing
            else:
                db.session.add(author)
                persisted_authors[author.name] = author
        db.session.commit()

        for book_data in books_to_create:
            existing_book = Book.query.filter_by(title=book_data.title).first()

            if not existing_book:
                real_authors = [persisted_authors[a.name] for a in
                                book_data.authors]

                new_book = Book(title=book_data.title, isbn=book_data.isbn)
                for a in real_authors:
                    new_book.authors.append(a)

                db.session.add(new_book)
            else:
                real_authors = [persisted_authors[a.name] for a in
                                book_data.authors]
                for a in real_authors:
                    if a not in existing_book.authors:
                        existing_book.authors.append(a)

        db.session.commit()