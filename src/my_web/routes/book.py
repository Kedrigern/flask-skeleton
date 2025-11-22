from http import HTTPStatus
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from pydantic import ValidationError
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
    try:
        payload = request.get_json()
        schema = BookCreateSchema(**payload)
        book = book_service.create(schema.model_dump())
        return BookSchema.model_validate(book).model_dump(), HTTPStatus.CREATED
    except ValidationError as e:
        return {
            "error": "Validation error",
            "details": e.errors(),
        }, HTTPStatus.BAD_REQUEST
    except ValueError as e:
        return {"error": str(e)}, HTTPStatus.CONFLICT


@book_api_bp.route("/<int:id>", methods=["PUT", "PATCH"])
@login_required
def api_update(id: int):
    try:
        payload = request.get_json()
        schema = BookUpdateSchema(**payload)
        data = schema.model_dump(exclude_unset=True)

        updated_book = book_service.update(id, data)
        if not updated_book:
            return {"error": "Not found"}, HTTPStatus.NOT_FOUND

        return BookSchema.model_validate(updated_book).model_dump(), HTTPStatus.OK
    except ValidationError as e:
        return {
            "error": "Validation error",
            "details": e.errors(),
        }, HTTPStatus.BAD_REQUEST
    except ValueError as e:
        return {"error": str(e)}, HTTPStatus.CONFLICT


@book_api_bp.route("/<int:book_id>/authors/<int:author_id>", methods=["PUT"])
@login_required
def api_add_author(book_id: int, author_id: int):
    success = book_service.add_author(book_id, author_id)
    if not success:
        return {"error": "Book or Author not found"}, HTTPStatus.NOT_FOUND
    return {}, HTTPStatus.NO_CONTENT


@book_api_bp.route("/<int:book_id>/authors/<int:author_id>", methods=["DELETE"])
@login_required
def api_remove_author(book_id: int, author_id: int):
    success = book_service.remove_author(book_id, author_id)
    if not success:
        return {"error": "Book or Author not found"}, HTTPStatus.NOT_FOUND
    return {}, HTTPStatus.NO_CONTENT
