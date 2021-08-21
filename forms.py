from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests

# def validate_user(form, user):


class SearchForm(FlaskForm):
    user = StringField('user',  validators=[DataRequired(), Length(min=4)], render_kw={"placeholder": "Enter reddit username to search comment history"})
    submit = SubmitField('Enter reddit username to search comment history')