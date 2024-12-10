from flask import Blueprint, current_app, render_template

# from app import db
# from app.models import *  # noqa: F403

main = Blueprint("main", __name__)


@main.route("/")
def home():
    # Inserting and querying code example

    # # Creating Ingredients
    # ingredient1 = Ingredient(name="Rum")
    # ingredient2 = Ingredient(name="Mint leaves")
    # ingredient3 = Ingredient(name="Sugar")

    # # Creating a Drink and associating ingredients
    # cocktail1 = UserDrink(
    #     name="Mojito",
    #     alcoholic_type=AlcoholicType.ALCOHOLIC,
    #     ingredients=[ingredient1, ingredient2, ingredient3],
    # )
    # cocktail2 = UserDrink(
    #     name="kkjhsbdfkjahsbd",
    #     alcoholic_type=AlcoholicType.NON_ALCOHOLIC,
    #     ingredients=[ingredient1, ingredient3],
    # )

    # with current_app.app_context():
    #     # Adding to session
    #     db.session.add(cocktail1)
    #     db.session.add(cocktail2)
    #     db.session.commit()

    # drink = UserDrink.query.get(1)

    # for ingredient in drink.ingredients:
    #     current_app.logger.info(ingredient.name)

    return render_template("index.html", title="Applicazione")
