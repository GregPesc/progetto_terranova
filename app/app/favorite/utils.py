from app import db
from app.models import ApiFavorite, LocalFavorite


def is_api_favorite(drink_id: ApiFavorite, current_user):
    return (
        db.session.execute(
            db.select(ApiFavorite).filter(
                ApiFavorite.id == drink_id, ApiFavorite.user_id == current_user.id
            )
        ).scalar_one_or_none()
        is not None
    )


def is_local_favorite(drink_id: LocalFavorite, current_user):
    return (
        db.session.execute(
            db.select(LocalFavorite).filter(
                LocalFavorite.id == drink_id,
                LocalFavorite.user_id == current_user.id,
            )
        ).scalar_one_or_none()
        is not None
    )
