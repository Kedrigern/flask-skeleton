from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from my_web.db.models import Role
from my_web.schemas.base import ORMModel


class UserSchema(ORMModel):
    id: int
    name: str
    email: str
    role: Role

    created_at: datetime
    updated_at: datetime


class UserCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Role = Role.USER
