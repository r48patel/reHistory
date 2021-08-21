from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, ValidationError
from datetime import datetime
import requests


class SearchForm(FlaskForm):
    user = StringField('user',
                       validators=[Length(min=1, message="Enter valid username")],
                       render_kw={"placeholder": "Enter reddit username to search comment history",
                                  "novalidate": "novalidate"})
    submit = SubmitField('Enter reddit username to search comment history')

    def validate_user(self, user):
        r = requests.get(f"https://www.reddit.com/user/{user.data}.json",
                         headers={'User-agent': f"reHistory:v0.0 (by /u/r48patel at {datetime.now()})"})
        data = r.json()
        # print(f'user: {user.data}, r: {r}({r.url}), data: {data}')
        if r.status_code != requests.codes.okay:
            raise ValidationError("Enter valid username")

        if 'error' in data.keys():
            raise ValidationError("Enter valid username")
