from flask import Blueprint, render_template

from app.models import ApiDrink

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html", title="Applicazione")


@main.route("/catalogo")
def catalogo():
    # get all the drinks from the database
    drinks = ApiDrink.query.all()
    return render_template("catalogo.html", title="Catalogo", drinks=drinks)
