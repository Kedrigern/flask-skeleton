from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import redirect, url_for, request, flash
from flask_login import login_user, logout_user

from my_web.db.models import User, db
from my_web.app import bcrypt

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html", user=current_user)


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.hashed_password, password):
            login_user(user)
            return redirect(url_for("user.profile"))
        flash("Invalid email or password.")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("auth.register"))
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, email=email, hashed_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("user.profile"))
    return render_template("auth/register.html")
