from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from flask_login import UserMixin

from my_web.extensions import db


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


class User(db.Model, UserMixin):
    """
    Application user model.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.USER, nullable=False)


def prepare_db() -> None:
    db.create_all()
