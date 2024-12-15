import contextlib

import flask_bcrypt
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user
from sqlalchemy.exc import NoResultFound

from app import db
from app.login.forms import LoginForm
from app.models import User

login = Blueprint("login", __name__)


@login.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        with contextlib.suppress(NoResultFound):
            user = db.session.execute(
                db.select(User).filter_by(email=form.email.data.lower())
            ).one()

            if flask_bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for("main.home"))

        flash("Credenziali invalide.", category="danger")

    return render_template("login.html", title="Login", form=form)
