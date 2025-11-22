from my_web.schemas.base import ORMModel
from my_web.schemas.author import AuthorSchema


class BookSchema(ORMModel):
    id: int
    title: str
    isbn: str | None = None
    authors: list[AuthorSchema] = []
