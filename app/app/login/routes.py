import flask_bcrypt
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user

from app import db
from app.login.forms import LoginForm, RegisterForm
from app.models import User

login = Blueprint("login", __name__)


@login.route("/login", methods=["GET", "POST"])
def login_route():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            user = db.session.execute(
                db.select(User).filter_by(email=form.email.data.lower())
            ).scalar_one_or_none()

            if user and flask_bcrypt.check_password_hash(
                user.password, form.password.data
            ):
                login_user(user, remember=form.remember.data)
                return redirect(url_for("main.home"))

        flash("Credenziali invalide.", category="danger")

    return render_template("login.html", title="Login", form=form)


@login.route("/register", methods=["GET", "POST"])
def register_route():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()

    if request.method == "POST" and form.validate_on_submit():
        processed_pw = flask_bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )

        new_user = User(email=form.email.data.lower(), password=processed_pw)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("User registered.")
        return redirect(url_for("main.home"))

    return render_template("register.html", title="Register", form=form)
