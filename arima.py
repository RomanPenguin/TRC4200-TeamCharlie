import numpy as np
import sqlite3
import statsmodels.api as sm


def car_search(name,conn,c):
    # returns list of available car parks for a given car park number
    c.execute("SELECT lots_available FROM cars WHERE carpark_number = (?) ORDER BY datetime(datestamp) ASC ",(name,))
    g=c.fetchall()
    return g


def car_search_his(name,past):
    # returns list of available car parks for a given car park number
    conn = sqlite3.connect("Data.db")
    c = conn.cursor()
    c.execute("SELECT lots_available FROM cars WHERE carpark_number = (?) ORDER BY datetime(datestamp) ASC ",(name,))
    g=c.fetchall()
    short = list(g[-past:])
    historic_data = [i[0] for i in short]
    hours_generated = list(range(1, past+1))
    hours_generated.reverse()
    return historic_data, hours_generated


def model_search(name, conn, c):
    # returns coefficients of the Sarima model given a car park name
    c.execute("SELECT coefficients FROM model_coefficients WHERE carpark_number = (?)",(name,))
    g=c.fetchall()
    return g


def coef_exists(cpnum,conn,c):
    # Returns 1 if the model exists in the coefficients database
    c.execute("SELECT 1 FROM model_coefficients WHERE carpark_number = (?)", (cpnum,))
    b=c.fetchall()
    return b


def model_from_coef(cp, h, conn, c):
    # generates forecasts given a car park number, and number of steps ahead

    y = car_search(cp, conn, c)  # get time series of the car park
    coef = model_search(cp, conn, c)  # obtain model coefficients (string)

    # assign coefficients from string
    p, d, q = coef[0][0][2],coef[0][0][5],coef[0][0][8]
    ps, ds, qs = coef[0][0][13],coef[0][0][16],coef[0][0][19]

    # obtain the model
    model = sm.tsa.statespace.SARIMAX(endog= y,order = [int(p),int(d),int(q)],seasonal_order = [int(ps),int(ds),int(qs),24])
    fit = model.fit()
    raw = fit.forecast(steps=h)
    predict = [round(j) for j in raw]  # round up
    return predict


def arima(lot_number, hours_generated):
    # initialise connection to database
    conn = sqlite3.connect("Data.db")
    c = conn.cursor()
    name = lot_number  # this is what the car park number called should be set as
    fc_len = hours_generated  # Amount of hours ahead forecasted
    # check model exists
    check = coef_exists(name, conn, c)  # (returns a weird list tuple format)
    if len(check) >0:
        forecast = model_from_coef(name, fc_len, conn, c)
        print(forecast)
    else:
        forecast = []
        print("model does not yet exist")

    hours_generated = numbers_list = list(range(0, fc_len))
    return forecast, hours_generated
