from pydantic import BaseModel, Field, EmailStr
from my_web.schemas.base import ORMModel
from my_web.db.models import Role


class UserSchema(ORMModel):
    id: int
    name: str
    email: str
    role: Role


class UserCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Role = Role.USER
