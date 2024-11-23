import requests


def search_by_name(name: str) -> str:
    """Search cocktail by name."""
    return requests.get(
        f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
    ).json()


def full_cocktail_by_id(id: str | int) -> str:
    """Lookup full cocktail details by id."""
    return requests.get(
        f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={id}"
    ).json()


if __name__ == "__main__":
    print(search_by_name("margarita"))
    print(full_cocktail_by_id("11007"))
