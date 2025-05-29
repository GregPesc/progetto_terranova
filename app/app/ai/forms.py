from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length


class CocktailInventionForm(FlaskForm):
    ingredients = StringField(
        "Ingredienti Preferiti",
        validators=[InputRequired(), Length(min=2, max=500)],
        render_kw={
            "placeholder": "Inserisci i tuoi ingredienti preferiti separati da virgole (es. vodka, lime, menta, zucchero di canna)"
        },
    )
    description = TextAreaField(
        "Descrizione del Cocktail Desiderato",
        validators=[InputRequired(), Length(min=10, max=1000)],
        render_kw={
            "placeholder": "Descrivi che tipo di cocktail vorresti (es. Un cocktail fresco e fruttato perfetto per l'estate, con un tocco di acidità)"
        },
    )
    submit = SubmitField("Inventa il mio Cocktail")
