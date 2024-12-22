[2021 TCDB dump](https://github.com/lauriharpf/thecocktaildb-downloader)

# Tabelle DB

**NON AGGIORNATO. VEDERE `models.py` DIRETTAMENTE**

## ApiDrink
> Id, nome e immagine dei drink dell'API.  
Chiamate API solo quando informazioni complete sono richieste (es: pagina cocktail specifico).



## UserDrink
> Drink creati dell'utente.  
(Sottoinsieme dei campi dei drink dall'API).



## Favorite
> Drink contrassegnati preferiti dall'utente.

> NOTA: se `islocal` è `0` allora `drink_id` si riferisce all'`id` dell'API, se è `1` si riferisce all'`id` della tabella `UserDrink`.
