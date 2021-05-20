import sqlite3
import time
import requests
import arrow
import json
from datetime import datetime


def AddToTable(datestamp,total_lots,lots_available,carpark_num,conn,c):
    c.execute("INSERT INTO cars VALUES(?,?,?,?)",(datestamp,total_lots,lots_available,carpark_num))
    conn.commit()


def live_populate(conn,c):
    # This function will generate a url, call the api, and parse the json to put new data into the data base
    url,date_requested = generate_timestring(conn,c)
    now = arrow.now('Singapore').shift(hours=-1).format("YYYY-MM-DD HH:mm")  # get singapore time less 1 hour
    fmt = '%Y-%m-%d %H:%M'
    d = datetime.strptime(now, fmt) - datetime.strptime(date_requested, fmt)  # compare current time to time that we want to request
    if d.days>1:  # if data is over a day old, request every minute
        #print("catchup mode")
        catchup = 0
    else: # if data is less than a day old, request every hour
        #print("relaxed mode")
        catchup = 1

    r = requests.get(url) # request data from api
    if r.ok == True:  # check api call worked
        packages_json = r.json()  # Read api into json
        time_last_called = time.time() # update the time that json is called (global)
        if len(r.text)> 100: # if the data is actually in the string (sometimes returns empty string)
            # loop to add data into table
            for carpark in packages_json['items'][0]['carpark_data']:
                total = carpark['carpark_info'][0]['total_lots']
                avail = carpark['carpark_info'][0]['lots_available']
                datestamp = date_requested
                carparknum = carpark['carpark_number']
                # add to table entry by entry
                AddToTable(datestamp, total, avail, carparknum, conn, c)
            time.sleep(60+3540*catchup)  # wait for 1 min or 1 hr
            print("{} done".format(date_requested))

        else:
            print ("{} has failed".format(date_requested))


def generate_timestring(conn, c):
    # makes time string for the hour after the latest entry
    c.execute("SELECT MAX(datestamp) FROM cars")  # get most recent date from database
    latest =c.fetchall()
    ymdhms = arrow.get(latest[0][0]).shift(hours = 1)  # add 1 hr
    h = ymdhms.format("HH")
    m = ymdhms.format("mm")
    s = ymdhms.format("ss")
    ymd = ymdhms.format("YYYY-MM-DD")
    ymdhm = ymdhms.format("YYYY-MM-DD HH:mm")

    # convert date time to api string format
    timestring = "https://api.data.gov.sg/v1/transport/carpark-availability?date_time="+ymd+"T"+h+ "%3A"+ m+ "%3A"+ s+ "%2B08%3A00"
    return timestring, ymdhm


def Main():
    #open database and cursor

    conn = sqlite3.connect("Data.db")
    c = conn.cursor()
    while 1:  #maybe change to be able to stop populating??
        live_populate(conn, c)
    c.close()


if __name__ == '__main__':
    Main()