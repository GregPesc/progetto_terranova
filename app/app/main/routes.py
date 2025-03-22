from flask import Blueprint, current_app, render_template, send_from_directory
from flask_login import current_user, login_required

from app.favorite.utils import is_api_favorite, is_local_favorite
from app.models import ApiDrink, UserDrink

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html", title="Applicazione")


@main.route("/catalogo")
def catalogo():
    drinks: list[ApiDrink] = ApiDrink.query.all()

    favorites = {}

    # If user is authenticated, check which drinks are favorites
    if current_user.is_authenticated:
        for drink in drinks:
            favorites[drink.id] = is_api_favorite(drink.id, current_user)

    return render_template(
        "catalogo.html", title="Catalogo", drinks=drinks, favorites=favorites
    )


@main.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@main.route("/mybar")
@login_required
def mybar():
    drinks: list[UserDrink] = UserDrink.query.all()

    favorites = {}

    # If user is authenticated, check which drinks are favorites
    if current_user.is_authenticated:
        for drink in drinks:
            favorites[drink.id] = is_local_favorite(drink.id, current_user)

    return render_template(
        "mybar.html", title="Catalogo", drinks=drinks, favorites=favorites
    )
