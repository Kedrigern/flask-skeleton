from my_web.schemas.base import ORMModel


class AuthorSchema(ORMModel):
    id: int
    name: str
