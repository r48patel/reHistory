#!/usr/bin/env python3.7
from flask import Flask, render_template, request, redirect, url_for
from reHistory import get_comments, get_comments_praw
from forms import SearchForm
import os
SECRET_KEY = os.urandom(32)


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == 'POST':
        return redirect((url_for('user_comments', user=form.user.data)))
    return render_template("welcome.html", title="reHistory", form=form)
#     form = SearchForm()
#     if request.method == 'POST' and form.validate_on_submit():
#         return redirect((url_for('search_results', query=form.search.data)))  # or what you want
#     return render_template('search.html', form=form)


@app.route("/<user>")
def user_comments(user):
    # data = get_comments_praw(user)
    data = get_comments(user)
    return render_template("index.html", title="{}'s Reddit Comments".format(user), user=user, info=data)


@app.context_processor
def utility_functions():
    def print_in_console(message):
        print("LOG: " + str(message))

    return dict(console_log=print_in_console)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(debug=True)
