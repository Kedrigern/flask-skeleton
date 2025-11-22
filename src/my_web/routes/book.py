from http import HTTPStatus
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from my_web.services.book import book_service
from my_web.schemas.pagination import PaginatedResponse
from my_web.schemas.book import BookSchema, BookCreateSchema, BookUpdateSchema

book_bp = Blueprint("book", __name__, url_prefix="/book")
book_api_bp = Blueprint("api_book", __name__, url_prefix="/api/v1/book")


@book_bp.route("/")
def index():
    return redirect(url_for("book.list"))


@book_bp.route("/<int:id>")
def detail(id: int):
    book = book_service.get(id)
    if not book:
        return render_template("errors/404.html"), HTTPStatus.NOT_FOUND
    return render_template("book/book.html", book=book)


@book_bp.route("/list")
def list():
    books = book_service.get_all()
    return render_template("book/books.html", books=books)


@book_api_bp.route("/list")
def api_list() -> dict:
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("size", 10, type=int)
    sort_param = request.args.get("sort")
    filter_param = request.args.get("filter")

    result = book_service.get_books(
        page=page, per_page=per_page, sort_param=sort_param, filter_param=filter_param
    )
    response_schema = PaginatedResponse[BookSchema](
        last_page=result["last_page"],
        data=[BookSchema.model_validate(b) for b in result["data"]],
    )

    return response_schema.model_dump()


@book_api_bp.route("/<int:id>")
def api_detail(id: int) -> dict:
    book = book_service.get(id)
    if not book:
        return {"error": "Not found"}, HTTPStatus.NOT_FOUND
    return BookSchema.model_validate(book).model_dump()


@book_api_bp.route("/", methods=["POST"])
@login_required
def api_create():
    """
    Creates a new book.

    Note: Exceptions are handled by global error handlers in `my_web.errors`.
    - ValidationError -> 400 Bad Request
    - ValueError -> 409 Conflict
    """
    payload = request.get_json()
    schema = BookCreateSchema(**payload)
    book = book_service.create(schema.model_dump())
    return BookSchema.model_validate(book).model_dump(), HTTPStatus.CREATED


@book_api_bp.route("/<int:id>", methods=["PUT", "PATCH"])
@login_required
def api_update(id: int):
    """
    Updates an existing book.
    Note: Exceptions are handled by global error handlers.
    """
    payload = request.get_json()
    schema = BookUpdateSchema(**payload)
    data = schema.model_dump(exclude_unset=True)

    updated_book = book_service.update(id, data)
    if not updated_book:
        return {"error": "Not found"}, HTTPStatus.NOT_FOUND

    return BookSchema.model_validate(updated_book).model_dump(), HTTPStatus.OK


@book_api_bp.route("/<int:book_id>/authors/<int:author_id>", methods=["PUT"])
@login_required
def api_add_author(book_id: int, author_id: int):
    """
    Adds an author to a book.
    Note: Raises ResourceNotFound if entities do not exist -> 404 Not Found.
    """
    book_service.add_author(book_id, author_id)
    book_service.add_author(book_id, author_id)
    return {"status": "success", "message": "Author added"}, HTTPStatus.OK


@book_api_bp.route("/<int:book_id>/authors/<int:author_id>", methods=["DELETE"])
@login_required
def api_remove_author(book_id: int, author_id: int):
    """
    Removes an author from a book.
    Note: Raises ResourceNotFound if entities do not exist -> 404 Not Found.
    """
    book_service.remove_author(book_id, author_id)
    return {"status": "success", "message": "Author removed"}, HTTPStatus.OK
