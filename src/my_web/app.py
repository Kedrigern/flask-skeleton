import os
import code
from flask import Flask
from dotenv import load_dotenv
from my_web.models import db

load_dotenv()

def create_app() -> Flask:
    app = Flask(os.getenv("NAME"))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
    db.init_app(app)
    return app

def run() -> None:
    """Run the Flask app."""
    app = create_app()
    app.run(debug=os.getenv("DEBUG"), host=os.getenv("HOST"), port=int(os.getenv("PORT")))

def shell() -> None:
    """Run a shell in the app context."""
    app = create_app()
    with app.app_context():
        try:
            from IPython import embed
            embed(header="", user_ns=dict(globals(), **locals()))
        except ImportError:
            code.interact(local=dict(globals(), **locals()))