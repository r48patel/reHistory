#!/usr/bin/env python3.7
from flask import Flask, render_template
from reHistory import get_comments, get_comments_praw

app = Flask(__name__)


# @app.route("/")
@app.route("/<user>")
def user_comments(user):
    # data = get_comments_praw(user)
    data = get_comments(user)
    return render_template("index.html", user=user, info=data)


@app.context_processor
def utility_functions():
    def print_in_console(message):
        print("LOG: " + str(message))

    return dict(console_log=print_in_console)


if __name__ == '__main__':
    app.run(debug=True)
