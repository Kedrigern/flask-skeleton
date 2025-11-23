from pydantic import BaseModel, Field
from my_web.schemas.base import ORMModel


class AuthorSchema(ORMModel):
    id: int
    name: str


class AuthorCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)