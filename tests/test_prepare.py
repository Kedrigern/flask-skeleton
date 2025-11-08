from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from my_web.app import create_app
from my_web.config import Settings, settings
from my_web.models import db


def test_config():
    assert isinstance(settings, Settings)


def test_db():
    assert isinstance(db, SQLAlchemy)


def test_app():
    app = create_app()
    assert isinstance(app, Flask)
