# app.py

import requests, json
from flask import Flask, render_template, request
from flask_assets import Bundle, Environment

from todo import todos
app = Flask(__name__)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")
js = Bundle("src/*.js", output="dist/main.js") # new

assets.register("css", css)
assets.register("js", js) # new
css.build()
js.build() # new


@app.route("/")
def homepage():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/search", methods=["POST"])
def search_todo():
    search_term = requests.get("https://api.data.gov.sg/v1/transport/carpark-availability?date_time=2020-01-15T10%3A10%3A10")
    parking_data = search_term.json()
    if not len(search_term):
        return render_template("todo.html", todos=[])

    res_todos = []
    for todo in todos:
        if search_term in todo["carpark_number"]:
            res_todos.append(todo)

    return render_template("todo.html", todos=res_todos)