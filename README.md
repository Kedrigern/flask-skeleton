# Flask Skeleton

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/built%20with-uv-blueviolet)](https://astral.sh/blog/uv)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=Flask&logoColor=white)](https://flask.palletsprojects.com/)

A production-ready Flask skeleton application designed to demonstrate modern best practices, separation of concerns, and robust tooling.

**Key Features:**

- **Managed by [uv](https://astral.sh/blog/uv)**: Fast Python package manager and resolver.
- **Service Layer Pattern**: Business logic is separated from HTTP routes.
- **Pydantic Validation**: Strict data validation for APIs and internal logic (replacing loose dictionaries).
- **[SQLAlchemy](https://www.sqlalchemy.org/) 2.0+**: Modern ORM usage with type hints.
- **Generic CRUD Service**: Reduce boilerplate for standard database operations.
- **Frontend ready**: Bootstrap 5 with Dark/Light mode and Tabulator integration.
- **Testing**: Pre-configured [pytest](https://docs.pytest.org/) with database fixtures and factory patterns.
- Authentication with [Flask-Login](https://flask-login.readthedocs.io/en/latest/).
- Alembic (db migration) with [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/).

## 📂 Project Structure

The project follows a modular structure to keep code maintainable:

```text
src/my_web/
├── config.py           # Configuration via Pydantic Settings
├── app.py              # Application factory & CLI commands
├── db/
│   ├── models.py       # SQLAlchemy Database Models
│   └── fixtures.py     # Initial data seeding
├── routes/             # HTTP Handlers (Blueprints)
│   ├── auth.py         # Authentication routes
│   └── book.py         # Mixed HTML and JSON API routes
├── schemas/            # Pydantic Schemas (Data Transfer Objects)
├── services/           # Business Logic Layer
│   ├── base.py         # Generic CRUD Service
│   └── book.py         # Book-specific logic
├── templates/          # Jinja2 HTML Templates
└── static/             # CSS/JS assets
```

## 🚀 Quick Start

### Prerequisites

```
cp .env.example .env    # copy example env file, change values
uv run db-upgrade       # create database tables
uv run pytest           # run tests
```

### Databse setup

```
uv run db-upgrade       # Apply migrations
uv run db-fixtures      # Load initial demo data (users, books)
```

### Running the app

```
uv run web              # run the web server
```

## 🛠 Development Workflow

Database Migrations

When you modify models.py, generate a migration:

```
uv run db-migrate "Description of changes"  # Create migration file
uv run db-upgrade                           # Apply to DB
```

Interactive Shell

```
uv run shell
>>> from my_web.services.book import book_service
>>> book_service.get_all()
```