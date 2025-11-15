from flask import Blueprint, render_template, redirect, url_for
from my_web.db.models import Book

book_bp = Blueprint("book", __name__, url_prefix="/book")
book_api_bp = Blueprint("api_book", __name__, url_prefix="/api/v1/book")


@book_bp.route("/")
def index():
    return redirect(url_for("book.list"))


@book_bp.route("/<int:id>")
def detail(id: int):
    book = Book.query.get(id)
    return render_template("book/book.html", book=book)


@book_bp.route("/list")
def list():
    books = Book.query.all()
    return render_template("book/books.html", books=books)


@book_api_bp.route("/list")
def api_list():
    return [book.as_dict() for book in Book.query.all()]


@book_api_bp.route("/<int:id>")
def api_detail(id: int):
    book = Book.query.get(id)
    return book.as_dict()
