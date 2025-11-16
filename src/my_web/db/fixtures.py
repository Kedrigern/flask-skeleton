from my_web.db.models import Author, Book
from my_web.extensions import db


def initial_library_data(app):
    """Seed initial authors and books with proper many-to-many relationships.

    Idempotent: existing authors/books are reused; missing relationships added.
    """
    authors = [
        Author(name="George Orwell"),
        Author(name="J.R.R. Tolkien"),
        Author(name="Andrzej Sapkowski"),
        Author(name="Terry Pratchett"),
        Author(name="Neil Gaiman"),
    ]

    books_data = [
        {"title": "1984", "authors": [authors[0]]},
        {"title": "The Hobbit", "authors": [authors[1]]},
        {"title": "The Lord of the Rings", "authors": [authors[1]]},
        {"title": "The Silmarillion", "isbn": "978-0-04-823139-0", "authors": [authors[1]]},
        {"title": "The Witcher: The Last Wish", "isbn": "978-0-575-08244-1", "authors": [authors[2]]},
        {"title": "Good Omens", "isbn": "978-0-575-07919-3", "authors": [authors[3], authors[4]]},  # co-authored
        {"title": "American Gods", "isbn": "978-0-06-257223-3", "authors": [authors[4]]},
    ]

    with app.app_context():
        persisted_authors = {}
        for author in authors:
            existing_author = Author.query.filter_by(name=author.name).first()
            if existing_author:
                persisted_authors[author.name] = existing_author
            else:
                db.session.add(author)
                persisted_authors[author.name] = author
        db.session.commit()

        for data in books_data:
            title = data["title"]
            isbn = data.get("isbn")
            authors_list = [persisted_authors[a.name] for a in data["authors"]]

            book = Book.query.filter_by(title=title).first()
            if not book:
                book = Book(title=title, isbn=isbn)
                for a in authors_list:
                    book.authors.append(a)
                db.session.add(book)
            else:
                # Add missing authors to existing book
                for a in authors_list:
                    if a not in book.authors:
                        book.authors.append(a)
        db.session.commit()
