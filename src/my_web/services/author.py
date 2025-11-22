from my_web.db.models import Author
from my_web.services.base import CRUDService


class AuthorService(CRUDService[Author]):
    MODEL = Author
    PK_NAME = "id"
    FILTER_FIELD = "name"


author_service = AuthorService()
