import os

class Config:
    """
    Basic configuration for Flask app.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        ''
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
