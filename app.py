# app.py

import requests, json
from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
import csv
from todo import todos

app = Flask(__name__)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")
js = Bundle("src/*.js", output="dist/main.js")  # new

assets.register("css", css)
assets.register("js", js)  # new
css.build()
js.build()  # new


@app.route("/")
def homepage():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)


@app.route("/search", methods=["POST"])
def search_todo():
    search_term = request.form.get("search")
    raw_data = requests.get(
        "https://api.data.gov.sg/v1/transport/carpark-availability?date_time=2020-01-15T10%3A10%3A10")
    parking_data = raw_data.json()
    if not len(search_term):
        return render_template("todo.html", todos=[])

    res_todos = []
    for parking_lot in parking_data["items"][0]["carpark_data"]:
        if search_term in parking_lot["carpark_number"]:
            res_todos.append(parking_lot)

    return render_template("todo.html", todos=res_todos)


@app.route("/chart")
def chartpage():
    with open('carpark.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        parking_data_dict = {}
        parking_available = []
        numbers_list = []
        i = 0

        for row in csv_reader:
            parking_data_dict[i]={}
            parking_data_dict[i]["available"] = row["lot_available_HE12"]
            parking_available.append(int(parking_data_dict[i]["available"]))
            parking_data_dict[i]["timestamp"] = row["timestamp"]
            numbers_list.append(int(i))
            i = i+1

    return render_template("chart.html",parking_data = parking_available, numbers_list = numbers_list)
