from flask import Blueprint, render_template
from flask_login import current_user

from app.favorite.utils import is_api_favorite
from app.models import ApiDrink

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
