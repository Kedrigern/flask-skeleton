from flask import Blueprint, render_template, redirect, url_for, request
from my_web.services.book import book_service

book_bp = Blueprint("book", __name__, url_prefix="/book")
book_api_bp = Blueprint("api_book", __name__, url_prefix="/api/v1/book")


@book_bp.route("/")
def index():
    return redirect(url_for("book.list"))


@book_bp.route("/<int:id>")
def detail(id: int):
    book = book_service.get(id)
    if not book:
        return render_template("errors/404.html"), 404
    return render_template("book/book.html", book=book)


@book_bp.route("/list")
def list():
    books = book_service.get_all()
    return render_template("book/books.html", books=books)


@book_api_bp.route("/list")
def api_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("size", 10, type=int)
    sort_param = request.args.get("sort")
    filter_param = request.args.get("filter")

    return book_service.get_books(
        page=page, per_page=per_page, sort_param=sort_param, filter_param=filter_param
    )


@book_api_bp.route("/<int:id>")
def api_detail(id: int):
    book = book_service.get(id)
    if not book:
        return {"error": "Not found"}, 404
    return book.as_dict()
