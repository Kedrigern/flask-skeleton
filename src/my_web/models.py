from enum import Enum
from flask_sqlalchemy import SQLAlchemy

class Role(Enum):
    USER = "user"
    ADMIN = "admin"

db = SQLAlchemy()

class User(db.Model):
    """
    Application user model.
    """
    __tablename__ = "users"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(128), nullable=False)
    email: str = db.Column(db.String(128), unique=True, nullable=False)
    hashed_password: str = db.Column(db.String(256), nullable=False)
    role: Role = db.Column(db.Enum(Role), default=Role.USER, nullable=False)

