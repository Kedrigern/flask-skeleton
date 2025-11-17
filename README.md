# Flask skeleton 

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/built%20with-uv-blueviolet)](https://astral.sh/blog/uv)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)

[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white)](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white)

Example of basic Flask application with

- proper directory structure 
- managed by [uv](https://astral.sh/blog/uv)
- unit tests with [pytest](https://docs.pytest.org/)
- DB through [SQLAlchemy](https://www.sqlalchemy.org/)
- Authentication with [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- Alembic (db migration) with [Flask-Migrate](https://flask-migrate.readthed

## Basic usage

### Prequisites

```
cp .env.example .env    # copy example env file, change values
uv run db-upgrade       # create database tables
uv run pytest           # run tests
```

### Running the app

```
uv run web              # run the web server
```

### Debugging with shell

```
uv run shell            # run a python shell with app context
```
