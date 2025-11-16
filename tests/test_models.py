from my_web.db.models import Author, Book, BookAuthorAssociation, db


def test_seed_authors_present(app):
    assert Author.query.count() >= 5
    names = {a.name for a in Author.query.all()}
    for expected in ["George Orwell", "J.R.R. Tolkien", "Neil Gaiman"]:
        assert expected in names


def test_seed_books_present(app):
    titles = {b.title for b in Book.query.all()}
    for expected in ["1984", "The Hobbit", "The Lord of the Rings", "Good Omens"]:
        assert expected in titles


def test_many_to_many_associations(app):
    tolkien = Author.query.filter_by(name="J.R.R. Tolkien").first()
    assert tolkien is not None
    # Tolkien should have multiple books
    assert len(tolkien.books) >= 3

    good_omens = Book.query.filter_by(title="Good Omens").first()
    assert good_omens is not None
    author_names = {a.name for a in good_omens.authors}
    assert {"Terry Pratchett", "Neil Gaiman"}.issubset(author_names)


def test_book_as_dict_includes_authors(app):
    book = Book.query.filter_by(title="1984").first()
    data = book.as_dict()
    assert "authors" in data
    assert isinstance(data["authors"], list)
    assert any(a["name"] == "George Orwell" for a in data["authors"])


def test_cascade_delete_book_associations(app):
    # Count associations before
    before = BookAuthorAssociation.query.count()
    book = Book.query.filter_by(title="1984").first()
    assert book is not None
    db.session.delete(book)
    db.session.commit()
    after = BookAuthorAssociation.query.count()
    # At least one association removed
    assert after < before
    # Author remains
    orwell = Author.query.filter_by(name="George Orwell").first()
    assert orwell is not None


