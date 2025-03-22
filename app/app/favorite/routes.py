from flask import Blueprint
from flask_login import current_user, login_required

from app import db
from app.favorite.utils import is_api_favorite, is_local_favorite
from app.models import ApiFavorite, LocalFavorite

favorite = Blueprint("favorite", __name__)


# TODO: make the client redirect to login page when it tries to add favorites without being logged in https://htmx.org/headers/hx-redirect/
@favorite.route("/api/favorite/api/<int:favorite_id>/toggle", methods=["POST"])
@login_required
def toggle_user_api_favorite(favorite_id: int):
    # Trova il preferito per l'utente corrente
    favorite = is_api_favorite(favorite_id, current_user)

    if not favorite:
        # Se il preferito non esiste, aggiungi il nuovo preferito
        new_favorite = ApiFavorite(id=favorite_id, user=current_user)
        db.session.add(new_favorite)
        db.session.commit()
        return {"message": "Favorite added"}

    # Se il preferito esiste, rimuovilo
    obj = (
        db.session.query(ApiFavorite)
        .filter_by(id=favorite_id, user_id=current_user.id)
        .first()
    )
    db.session.delete(obj)
    db.session.commit()
    return {"message": "Favorite removed"}


@favorite.route("/api/favorite/local/<uuid:favorite_id>/toggle", methods=["POST"])
@login_required
def toggle_user_local_favorite(favorite_id):
    # Trova il preferito per l'utente corrente
    favorite = is_local_favorite(favorite_id, current_user)

    if not favorite:
        # Se il preferito non esiste, aggiungi il nuovo preferito
        new_favorite = LocalFavorite(id=favorite_id, user=current_user)
        db.session.add(new_favorite)
        db.session.commit()
        return {"message": "Favorite added"}

    # Se il preferito esiste, rimuovilo
    obj = (
        db.session.query(LocalFavorite())
        .filter_by(id=favorite_id, user_id=current_user.id)
        .first()
    )
    db.session.delete(obj)
    db.session.commit()
    return {"message": "Favorite removed"}
