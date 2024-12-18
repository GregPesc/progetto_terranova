from flask import Blueprint, request

from app import db
from app.models import Category

search = Blueprint("search", __name__)


@search.route("/api/catalog-search")
def catalog_search(): ...


def bar_search(): ...
