from flask import Blueprint
from flask_login import current_user

from app import db
from app.models import Favorite

favorite = Blueprint("favorite", __name__)


# Route per ottenere tutti i preferiti per un utente
@favorite.route("/api/favorite", methods=["GET"])
def get_user_favorites():
    if not current_user.is_authenticated:
        return {"error": "User not authenticated"}, 401

    # Filtra i preferiti per l'utente corrente
    favorites = (
        db.session.execute(
            db.select(Favorite)
            .filter(Favorite.user_id == current_user.id)
            .order_by(Favorite.drink_id)
        )
        .scalars()
        .all()
    )

    return {
        "favorites": [
            {"id": favorite.id, "name": favorite.name, "thumbnail": favorite.thumbnail}
            for favorite in favorites
        ]
    }


# Route per eliminare un preferito
@favorite.route("/api/favorite/<int:favorite_id>", methods=["DELETE"])
def delete_user_favorite(favorite_id):
    if not current_user.is_authenticated:
        return {"error": "User not authenticated"}, 401

    # Trova il preferito per l'utente corrente
    favorite = db.session.execute(
        db.select(Favorite).filter(
            Favorite.id == favorite_id, Favorite.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if favorite is None:
        return {"error": "Favorite not found"}, 404

    db.session.delete(favorite)
    db.session.commit()

    return {"message": "Favorite deleted"}


# Route per aggiungere un preferito
@favorite.route("/api/favorite/<int:favorite_id>", methods=["POST"])
def add_user_favorite(favorite_id):
    if not current_user.is_authenticated:
        return {"error": "User not authenticated"}, 401

    # Trova il preferito per l'utente corrente
    favorite = db.session.execute(
        db.select(Favorite).filter(
            Favorite.id == favorite_id, Favorite.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if favorite is None:
        return {"error": "Favorite not found"}, 404

    # Aggiungi il preferito all'utente
    current_user.favorites.append(favorite)
    db.session.commit()

    return {"message": "Favorite added"}
