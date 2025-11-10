import code
import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from my_web.config import settings
from my_web.routes.home import home_bp

HELP = """Usage:

uv run web      # Run the Flask web server
uv run shell    # Run a shell in the app context
uv run help     # Show this help message

Don not forget to set environment variables in a .env file.
"""

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app() -> Flask:
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    app = Flask(settings.name, template_folder=template_dir)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.sqlalchemy_database_uri
    app.config["SECRET_KEY"] = settings.secret_key
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    with app.app_context():
        # is this necessary?
        from my_web.models import prepare_db
        prepare_db()
    app.register_blueprint(home_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    return app


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
