import code

# from dotenv import load_dotenv
from flask import Flask

from my_web.config import settings
from my_web.models import User, db

HELP = """Usage:

uv run web      # Run the Flask web server
uv run shell    # Run a shell in the app context
uv run help     # Show this help message

Don not forget to set environment variables in a .env file.
"""


def create_app() -> Flask:
    app = Flask(settings.name)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.db_uri
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


def run() -> None:
    """Run the Flask app."""
    app = create_app()
    app.run(debug=settings.debug, host=settings.host, port=settings.port)


def help() -> None:
    """Print help message."""
    print(HELP)


def shell() -> None:
    """Run a shell in the app context."""
    app = create_app()
    with app.app_context():
        try:
            from IPython import embed

            embed(header="", user_ns=dict(globals(), **locals()))
        except ImportError:
            code.interact(local=dict(globals(), **locals()))
