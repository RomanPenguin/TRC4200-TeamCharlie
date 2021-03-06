# app.py

import requests, json
from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
import csv
from todo import todos
import urllib
import os
from datetime import datetime
import pandas as pd
import numpy as np
import SVY21 as SV
from parseCSV import parseCSV
from arima import arima, car_search_his


app = Flask(__name__)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")
js = Bundle("src/*.js", output="dist/main.js")  # new

assets.register("css", css)
assets.register("js", js)  # new
css.build()
js.build()  # new

################## maps API set up ##################

# load API key
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'apikey.txt'), "r") as f:
    api_key = f.readline()
    f.close


# read carpark list file
cf = pd.read_csv(os.path.join(__location__, 'hdb-carpark-information.csv'),
                 usecols=['car_park_no', 'address', 'x_coord', 'y_coord'])
# convert x & y coords' columns to float
cf['x_coord'] = cf['x_coord'].astype(float)
cf['y_coord'] = cf['y_coord'].astype(float)

# convert geo coords from SVY21 to latitude longitude
coord_change = SV.SVY21()
lat_lon = [None] * len(cf['x_coord'])
for i, r in cf.iterrows():
    lat_lon[i] = coord_change.computeLatLon(r['y_coord'], r['x_coord'])
# convert to panda dataframe
cps_coords = pd.DataFrame(lat_lon, columns=['y', 'x'])


place_marker = np.empty((1, 2), float)
markers = np.empty((3, 2), float)

#######################################################

@app.route("/")
def homepage():
    return render_template("map.html", api_key=api_key)



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


@app.route("/carparks", methods=["POST", "GET"])
def carpark_search():
    return render_template("carparksearch.html")


@app.route("/chart", methods=["GET"])
def chartpage():

    # show chart based on the user's button click
    lot_number = request.args.get('my_var', None)
    result = list(car_search_his(lot_number,48))
    result[1] = [str(s) + " hrs ago" for s in result[1]]
    print(result)
    prediction = list(arima(lot_number,12))
    prediction[1] = [str(s) + " hrs from now" for s in prediction[1]]

    result[0]= result[0]+prediction[0]
    result[1] = result[1]+prediction[1]
    print(result)


    # find latitude longitude to send to embedded map
    cp_i = cf[cf['car_park_no'] == lot_number].index.values
    lat = cps_coords['y'].values[cp_i]
    lon = cps_coords['x'].values[cp_i]
    map_src = api_key + "&q=" + str(lat)[1:-1] + "," + str(lon)[1:-1]

    # get carpark address
    address = str(cf['address'].values[cp_i])[2:-2]

    return render_template("chart.html", parking_data=result[0], numbers_list=result[1], lot_number=lot_number,
                           map_src=map_src, address=address)


@app.route("/map_search", methods=["POST"])
def search_place():
    # get search term entered
    search_term = request.form.get("search_input") + " singapore"
    # convert to url format
    search_term = urllib.parse.quote(search_term)

    place = []

    # call API & get data
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    raw_data = requests.get(url + "input=" + search_term + "&inputtype=textquery" + "&fields=formatted_address,name,geometry" + "&key=" + api_key)
    # get first candidate
    if raw_data.json().get("candidates"):
        place = raw_data.json()["candidates"][0]

    # convert place x & y coords to array, then to panda dataframe
    place_np = np.full((2158, 2), [place['geometry']['location']['lat'], place['geometry']['location']['lng']],
                       dtype=float)
    place_coords = pd.DataFrame(place_np, columns=['y', 'x'])
    place_coords = place_coords.astype(float)

    # find differences in coords
    diff = cps_coords.sub(place_coords)
    # use differences to find direct distances
    diff = diff.pow(2)
    dists = diff['y'].add(diff['x'])
    dists = dists.pow(0.5)

    # find 3 carparks with shortest distances + their coordinates
    global markers
    shortest = [None] * 3
    chart_data = []
    for idx in range(len(shortest)):
        shortest_i = dists.idxmin()
        shortest[idx] = cf['car_park_no'][shortest_i]
        dists[shortest_i] += 1
        hist_data = list(car_search_his(shortest[idx], 48))
        hist_data[1] = [str(s) + " hrs ago" for s in hist_data[1]]
        chart_data.append(hist_data)

        # get coords for map markers
        lat = cps_coords['y'].values[shortest_i]
        lon = cps_coords['x'].values[shortest_i]
        markers[idx, :] = [lat, lon]

    # get place markers
    global place_marker
    place_marker[0, :] = place_np[0, :]

    return render_template("place.html", place=place, shortest=shortest, chart_data=chart_data, markers=markers,
                           place_marker=place_marker)


@app.route("/contact")
def contact():
    return render_template("contact.html")
