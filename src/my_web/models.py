from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


db = SQLAlchemy()


class User(db.Model):
    """
    Application user model.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.USER, nullable=False)
