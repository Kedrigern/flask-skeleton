from my_web.db.models import Author, Book, User, Role
from my_web.extensions import db, bcrypt
from my_web.schemas.user import UserCreateSchema
from my_web.schemas.book import BookCreateSchema
from my_web.schemas.author import AuthorCreateSchema

RAW_AUTHORS = [
    {"name": "George Orwell"},
    {"name": "J.R.R. Tolkien"},
    {"name": "Andrzej Sapkowski"},
    {"name": "Terry Pratchett"},
    {"name": "Neil Gaiman"},
]

RAW_BOOKS = [
    {"data": {"title": "1984", "isbn": "9780452284234"}, "authors": ["George Orwell"]},
    {
        "data": {"title": "The Hobbit", "isbn": "9780547928227"},
        "authors": ["J.R.R. Tolkien"],
    },
    {
        "data": {"title": "The Lord of the Rings", "isbn": None},
        "authors": ["J.R.R. Tolkien"],
    },
    {
        "data": {"title": "The Silmarillion", "isbn": "978-0-04-823139-0"},
        "authors": ["J.R.R. Tolkien"],
    },
    {
        "data": {"title": "The Witcher: The Last Wish", "isbn": "978-0-575-08244-1"},
        "authors": ["Andrzej Sapkowski"],
    },
    {
        "data": {"title": "Good Omens", "isbn": "978-0-575-07919-3"},
        "authors": ["Terry Pratchett", "Neil Gaiman"],
    },
    {
        "data": {"title": "American Gods", "isbn": "978-0-06-257223-3"},
        "authors": ["Neil Gaiman"],
    },
]

RAW_USERS = [
    {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "password",
        "role": Role.ADMIN,
    },
    {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password",
        "role": Role.USER,
    },
]


def get_initial_data() -> tuple[list[Author], list[Book], list[User]]:
    """
    Returns clean data (model instances) without DB session binding.
    Data is validated via Pydantic schemas.
    Used for testing mocks.
    """
    authors_orm = []
    for author_data in RAW_AUTHORS:
        schema = AuthorCreateSchema(**author_data)
        authors_orm.append(Author(**schema.model_dump()))

    # Map for quick author lookup by name
    auth_map = {a.name: a for a in authors_orm}

    books_orm = []

    for entry in RAW_BOOKS:
        book_schema = BookCreateSchema(**entry["data"])

        # Convert validated schema to ORM object
        book_instance = Book(**book_schema.model_dump())

        # 3. Manually handle relationships (Many-to-Many)
        # Since BookCreateSchema doesn't handle relationship logic, we do it here
        for author_name in entry["authors"]:
            if author_name in auth_map:
                book_instance.authors.append(auth_map[author_name])
            else:
                raise ValueError(
                    f"Author '{author_name}' not found in author definitions."
                )

        books_orm.append(book_instance)

    users_orm = []
    for user_data in RAW_USERS:
        schema = UserCreateSchema(**user_data)

        # Prepare ORM data (hash password)
        data = schema.model_dump()
        plain_password = data.pop("password")
        hashed_pw = bcrypt.generate_password_hash(plain_password).decode("utf-8")

        # Create User instance
        user_instance = User(hashed_password=hashed_pw, **data)
        users_orm.append(user_instance)

    return authors_orm, books_orm, users_orm


def initial_library_data(app) -> None:
    """
    Seed initial authors and books into the real DB.
    Idempotent: existing authors/books are reused to prevent duplicates.
    """
    authors_to_create, books_to_create, users_to_create = get_initial_data()

    with app.app_context():
        for user_orm in users_to_create:
            existing_user = User.query.filter_by(email=user_orm.email).first()
            if not existing_user:
                db.session.add(user_orm)

        persisted_authors = {}

        # Persist authors
        for author in authors_to_create:
            existing = Author.query.filter_by(name=author.name).first()
            if existing:
                persisted_authors[author.name] = existing
            else:
                # Add new instance to the session
                db.session.add(author)
                persisted_authors[author.name] = author

        db.session.commit()

        # Persist books
        for book_orm in books_to_create:
            existing_book = Book.query.filter_by(title=book_orm.title).first()

            if not existing_book:
                # Remap authors to those present in the current DB session
                # because `book_orm.authors` contains "offline" instances from get_initial_data
                real_authors = [persisted_authors[a.name] for a in book_orm.authors]

                # Clear "offline" authors and attach "online" (session-bound) authors
                book_orm.authors = []
                for ra in real_authors:
                    book_orm.authors.append(ra)

                db.session.add(book_orm)
            else:
                # If book exists, ensure all authors are associated
                target_author_names = [a.name for a in book_orm.authors]
                real_authors = [persisted_authors[name] for name in target_author_names]

                for ra in real_authors:
                    if ra not in existing_book.authors:
                        existing_book.authors.append(ra)

        db.session.commit()
