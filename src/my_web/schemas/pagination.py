from typing import Generic, TypeVar
from my_web.schemas.base import ORMModel

T = TypeVar("T")


class PaginatedResponse(ORMModel, Generic[T]):
    last_page: int
    data: list[T]
