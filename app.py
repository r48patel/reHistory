#!/usr/bin/env python3.7
from flask import Flask, render_template, redirect, url_for, flash
from reHistory import get_comments
from forms import SearchForm
import os
from flask_wtf import CSRFProtect


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['WTF_CSRF_ENABLED'] = False
csrf = CSRFProtect(app)


@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    is_validated = form.validate_on_submit()
    # print(f"is_validated: {is_validated}. user: {form.user.data}")
    # print(form.errors)
    if not is_validated:
        for error in form.errors:
            flash(f'Error: {form.errors[error][0]}', 'error')
        return render_template("welcome.html", title="reHistory", form=form)
    return redirect((url_for('user_comments', user=form.user.data)))


@app.route("/user/<user>")
def user_comments(user):
    data = get_comments(user)
    return render_template("index.html", title="{}'s Reddit Comments".format(user), user=user, info=data)


@app.context_processor
def utility_functions():
    def print_in_console(message):
        print("LOG: " + str(message))

    return dict(console_log=print_in_console)


if __name__ == '__main__':
    app.run(debug=True)
