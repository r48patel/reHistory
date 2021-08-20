#!/usr/bin/env python3.7
from flask import Flask, render_template
from reHistory import user_comments

app = Flask(__name__)
test_data = {
    'formula1': ['test1', 'test2'],
    'formula2': ['test1', 'test2'],
    'formula3': ['test1', 'test2']
}


# @app.route("/")
@app.route("/<user>")
def hello_world(user):
    data = user_comments(user)
    return render_template("index.html", user=user, info=data)


@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(console_log=print_in_console)


if __name__ == '__main__':
    app.run(debug=True)