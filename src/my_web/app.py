import code
import os
import sys
from flask import Flask, render_template
from flask_migrate import upgrade, init, history, current, migrate as migrate_command
from my_web.config import settings
from my_web.extensions import db, bcrypt, login_manager, migrate, csrf
from my_web.db.fixtures import initial_library_data
from my_web.routes.home import home_bp
from my_web.routes.auth import auth_bp
from my_web.routes.user import user_bp
from my_web.routes.book import book_bp, book_api_bp

HELP = """Usage:

uv run web              # Run the Flask web server
uv run shell            # Run a shell in the app context
uv run db-init          # Initialize the database (create migration repository and initial migration)
uv run db-migrate       # Create a new database migration from code changes
uv run db-upgrade       # Apply database migrations to DB
uv run db-fixtures      # Load initial data fixtures into the database
uv run db-history       # Show the database migration history
uv run db-current       # Show the current database revision
uv run help             # Show this help message

Do not forget to set environment variables in a .env file.
"""


@login_manager.user_loader
def load_user(user_id):
    from my_web.db.models import User

    return User.query.get(int(user_id))


def create_app() -> Flask:
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    app = Flask(settings.name, template_folder=template_dir)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.sqlalchemy_database_uri
    app.config["SECRET_KEY"] = settings.secret_key
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(book_api_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    return app


def db_init() -> None:
    app = create_app()
    with app.app_context():
        init()


def db_migrate() -> None:
    app = create_app()
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    with app.app_context():
        migrate_command(message=msg)


def db_upgrade() -> None:
    app = create_app()
    with app.app_context():
        upgrade()


def db_fixtures() -> None:
    app = create_app()
    with app.app_context():
        initial_library_data(app)


def db_history() -> None:
    app = create_app()
    with app.app_context():
        history()


def db_current() -> None:
    app = create_app()
    with app.app_context():
        current()


def run() -> None:
    """Run the Flask app."""
    app = create_app()
    app.run(debug=settings.debug, host=settings.host, port=settings.port)


def app_help() -> None:
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


login_manager.login_view = "auth.login"
