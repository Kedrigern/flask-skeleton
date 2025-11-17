from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from my_web.db.models import User, db
from my_web.forms.auth import LoginForm, RegisterForm
from my_web.app import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
            user.hashed_password, form.password.data
        ):
            login_user(user)
            flash("Login succesful.", "success")  # Přidána kategorie zprávy
            return redirect(url_for("user.profile"))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered..", "warning")
            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            name=form.name.data, email=form.email.data, hashed_password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Register sucesful.", "success")
        return redirect(url_for("user.profile"))

    return render_template("auth/register.html", form=form)
