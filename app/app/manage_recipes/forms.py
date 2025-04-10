from flask_wtf import FlaskForm
from wtforms import (
    FieldList,
    FileField,
    Form,
    FormField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired, Length


class IngredientForm(Form):
    ingredient = SelectField("Ingrediente")
    quantity = StringField("Quantità")


class RecipeForm(FlaskForm):
    name = StringField("Nome", validators=[InputRequired()])
    category = SelectField("Categoria", validators=[InputRequired()])
    alcoholic_type = SelectField("Alcolico", validators=[InputRequired()])
    instructions = StringField("Istruzioni")
    thumbnail = FileField("Immagine")
    ingredients = FieldList(FormField(IngredientForm), min_entries=1)
    submit = SubmitField("Aggiungi")


class IngredientCreationForm(FlaskForm):
    name = StringField(
        "Nome Ingrediente", validators=[InputRequired(), Length(min=2, max=100)]
    )
    submit = SubmitField("Aggiungi Ingrediente")
