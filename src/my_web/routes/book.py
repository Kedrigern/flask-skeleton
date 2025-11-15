from flask import Blueprint, render_template, redirect, url_for, jsonify

book_bp = Blueprint("book", __name__, url_prefix="/book")
book_api_bp = Blueprint("api_book", __name__, url_prefix="/api/v1/book")


@book_bp.route("/")
def index():
    return redirect(url_for("book.list"))


@book_bp.route("/<int:id>")
def detail(id: int):
    return render_template("book/book.html", id=id)


@book_bp.route("/list")
def list():
    return render_template("book/books.html")


@book_api_bp.route("/list")
def api_list():
    return []


@book_api_bp.route("/<int:id>")
def api_detail(id: int):
    return jsonify({"id": id})
