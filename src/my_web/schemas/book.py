from pydantic import BaseModel, Field
from my_web.schemas.base import ORMModel
from my_web.schemas.author import AuthorSchema


class BookSchema(ORMModel):
    id: int
    title: str
    isbn: str | None = None
    authors: list[AuthorSchema] = []


class BookCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    isbn: str | None = Field(None, max_length=20)


class BookUpdateSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    isbn: str | None = Field(None, max_length=20)
