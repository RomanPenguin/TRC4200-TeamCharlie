# app.py

import requests, json
from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
import csv
from todo import todos
import urllib
import os
from datetime import datetime

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

    # use search term entered and call api
    search_term = request.form.get("search")

    # using API calls to get data
    # raw_data = requests.get(
    #     "https://api.data.gov.sg/v1/transport/carpark-availability?date_time=2020-03-15T10%3A10%3A10")
    # parking_data = raw_data.json()
    # if not len(search_term):
    #     return render_template("todo.html", todos=[])
    #
    # res_todos = []
    #
    # # generate a list of carparks based on search term
    # for parking_lot in parking_data["items"][0]["carpark_data"]:
    #     if search_term in parking_lot["carpark_number"]:
    #         res_todos.append(parking_lot)

    with open('carpark.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        res_todos=[]


        amendedsearch = "lot_available_"+search_term
        # match the search term to the csv columns
        # for row in csv_reader:
        #     res = dict(filter(lambda item: search_term in item[0], row.items()))
        #     print(str(res))
        #     break
        # for key in res:
        #     parking_lot = {}
        #
        #     parking_lot["carpark_number"]=key
        #     print(parking_lot["carpark_number"])
        #     parking_lot["lots_available"]=res[key]
        #     print(parking_lot["lots_available"])
        #     res_todos.append(parking_lot)

        # search using csv file
        cp = []
        all_carpark = []
        with open('carpark.csv') as csvfile:
            rows = csv.reader(csvfile)
            res = list(zip(*rows))
        r = len(res)
        for i in range((r - 2) - 1):
            i = i + 2
            if i % 2 == 0:
                cpnum = res[i][0][14:]
                lots = res[i + 1][2]
                avail = res[i][1:]
                time = res[1][1:]
                cp = [cpnum, lots, avail, time]
                all_carpark.append(cp)
        for carpark in all_carpark:
            if carpark[0]==search_term:
                res_todos.append(carpark)
                print(carpark)

    return render_template("todo.html", todos=res_todos)


@app.route("/chart", methods=["GET"])
def chartpage():

    # show chart based on the user's button click
    lot_number = request.args.get('my_var', None)
    parking_available = []
    numbers_list = []
    #parse csv
    cp = []
    all_carpark = []
    with open('carpark.csv') as csvfile:
        rows = csv.reader(csvfile)
        res = list(zip(*rows))
    r = len(res)
    for i in range((r - 2) - 1):
        i = i + 2
        if i % 2 == 0:
            cpnum = res[i][0][14:]
            lots = res[i + 1][2]
            avail = (res[i][1:])
            time = res[1][1:]
            cp = [cpnum, lots, avail, time]
            all_carpark.append(cp)

    # parse data to display on chart
    for carpark in all_carpark:
        if carpark[0] == lot_number:
            for available in carpark[2]:
                parking_available.append(int(available))

            numbers_list = list(range(0, len(carpark[2])))
            numbers_list.reverse()

            #time conversion
            time_list = datetime.strptime('19/04/2021 10:59', '%d/%m/%Y %H:%M')
            print(time_list.strftime("%H%M %d/%m/%Y"))
            print(len(parking_available))
            print(len(numbers_list))
            break
    print(parking_available)

    return render_template("chart.html", parking_data=parking_available, numbers_list=numbers_list, lot_number = lot_number)


@app.route("/map")
def mappage():
    return render_template("map.html")


@app.route("/map_search", methods=["POST"])
def search_place():
    # load API key
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'apikey.txt'), "r") as f:
        api_key = f.readline()
        f.close

    # get search term entered
    search_term = request.form.get("search_input")
    # convert to url format
    search_term = urllib.parse.quote(search_term)

    place = []

    # call API & get data
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    raw_data = requests.get(url + "input=" + search_term + "&inputtype=textquery" + "&fields=formatted_address,name,geometry" + "&key=" + api_key)
    # get first candidate
    if raw_data.json().get("candidates"):
        place = raw_data.json()["candidates"][0]

    return render_template("place.html", place=place)
