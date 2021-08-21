from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, ValidationError
import requests


class SearchForm(FlaskForm):
    user = StringField('user',
                       validators=[Length(min=1, message="Enter valid username")],
                       render_kw={"placeholder": "Enter reddit username to search comment history",
                                  "novalidate": "novalidate"})
    submit = SubmitField('Enter reddit username to search comment history')

    def validate_user(self, user):
        r = requests.get(f"https://www.reddit.com/user/{user}.json")
        data = r.json()
        if data['error'] == requests.codes.not_found:
            raise ValidationError("Enter valid username")
