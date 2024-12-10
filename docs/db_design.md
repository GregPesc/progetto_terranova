[2021 TCDB dump](https://github.com/lauriharpf/thecocktaildb-downloader)

**Esempio drink da API**

```
{
    "idDrink": "11007",
    "strDrink": "Margarita",
    "strDrinkAlternate": null,
    "strTags": "IBA,ContemporaryClassic",
    "strVideo": null,
    "strCategory": "Ordinary Drink",
    "strIBA": "Contemporary Classics",
    "strAlcoholic": "Alcoholic",
    "strGlass": "Cocktail glass",
    "strInstructions": "Rub the rim of the glass with the lime slice to make the salt stick to it. Take care to moisten only the outer rim and sprinkle the salt on it. The salt should present to the lips of the imbiber and never mix into the cocktail. Shake the other ingredients with ice, then carefully pour into the glass.",
    "strInstructionsES": "Frota el borde del vaso con la rodaja de lima para que la sal se adhiera a él. Procure humedecer sólo el borde exterior y espolvorear la sal sobre él. La sal debe presentarse en los labios del imbibidor y nunca mezclarse en el cóctel. Agite los demás ingredientes con hielo y viértalos con cuidado en el vaso.",
    "strInstructionsDE": "Reiben Sie den Rand des Glases mit der Limettenscheibe, damit das Salz daran haftet. Achten Sie darauf, dass nur der äußere Rand angefeuchtet wird und streuen Sie das Salz darauf. Das Salz sollte sich auf den Lippen des Genießers befinden und niemals in den Cocktail einmischen. Die anderen Zutaten mit Eis schütteln und vorsichtig in das Glas geben.",
    "strInstructionsFR": "Frotter le bord du verre avec la tranche de citron vert pour faire adhérer le sel. Veillez à n'humidifier que le bord extérieur et à y saupoudrer le sel. Le sel doit se présenter aux lèvres du buveur et ne jamais se mélanger au cocktail. Secouez les autres ingrédients avec de la glace, puis versez-les délicatement dans le verre.",
    "strInstructionsIT": "Strofina il bordo del bicchiere con la fetta di lime per far aderire il sale.\r\nAvere cura di inumidire solo il bordo esterno e cospargere di sale.\r\nIl sale dovrebbe presentarsi alle labbra del bevitore e non mescolarsi mai al cocktail.\r\nShakerare gli altri ingredienti con ghiaccio, quindi versarli delicatamente nel bicchiere.",
    "strInstructionsZH-HANS": null,
    "strInstructionsZH-HANT": null,
    "strDrinkThumb": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg",
    "strIngredient1": "Tequila",
    "strIngredient2": "Triple sec",
    "strIngredient3": "Lime juice",
    "strIngredient4": "Salt",
    "strIngredient5": null,
    "strIngredient6": null,
    "strIngredient7": null,
    "strIngredient8": null,
    "strIngredient9": null,
    "strIngredient10": null,
    "strIngredient11": null,
    "strIngredient12": null,
    "strIngredient13": null,
    "strIngredient14": null,
    "strIngredient15": null,
    "strMeasure1": "1 1/2 oz ",
    "strMeasure2": "1/2 oz ",
    "strMeasure3": "1 oz ",
    "strMeasure4": null,
    "strMeasure5": null,
    "strMeasure6": null,
    "strMeasure7": null,
    "strMeasure8": null,
    "strMeasure9": null,
    "strMeasure10": null,
    "strMeasure11": null,
    "strMeasure12": null,
    "strMeasure13": null,
    "strMeasure14": null,
    "strMeasure15": null,
    "strImageSource": "https://commons.wikimedia.org/wiki/File:Klassiche_Margarita.jpg",
    "strImageAttribution": "Cocktailmarler",
    "strCreativeCommonsConfirmed": "Yes",
    "dateModified": "2015-08-18 14:42:59"
}
```



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
