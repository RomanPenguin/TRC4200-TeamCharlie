import os.path
# For serialization:
import pickle
import sqlite3

import pmdarima.arima as pm
from pathlib import Path

## https://alkaline-ml.com/pmdarima/serialization.html ##
def create_table():
    conn = sqlite3.connect("Data.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS model_coefficients (carpark_number TEXT, coefficients TEXT)')
    c.close()

def AddToTable(carpark_number,coefficients,conn,c):
    c.execute("INSERT INTO model_coefficients VALUES(?,?)",(carpark_number,coefficients))
    conn.commit()


def predict(cp, h, conn, c):
    y = car_search(cp,conn,c)
    #yp=[float(j) for j in y]#convert list elements from string to number
    fit = pm.auto_arima(y,seasonal=True,m=24,stepwise=True)
    pdq = fit.order
    s_pdq = fit.seasonal_order
    coefs = [pdq, s_pdq]
    AddToTable(cp, str(coefs), conn, c)
    #raw = fit.predict(n_periods = int(h))
    #predict = [round(j) for j in raw]
    #return(predict,len(y),fit)
    return fit


def get_coef(cpnum):
    root = Path(".")
    my_path = root/"models"/cpnum
    with open(my_path, 'rb') as pkl:
        loaded = pickle.load(pkl)
        pdq = loaded.order
        s_pdq = loaded.seasonal_order
        coefs = [pdq, s_pdq]
    return str(coefs)

def store_model(model,name):
    # Serialize with Pickle
    root = Path(".")
    my_path = root/"models"/name
    with open(my_path, 'wb') as pkl:
        pickle.dump(model, pkl)

def coef_exists(cpnum,conn,c):
    c.execute("SELECT 1 FROM model_coefficients WHERE carpark_number = (?)", (cpnum,))
    b=c.fetchall()
    return b


def read_model(model_name,h):
    # Now read it back and make a prediction
    root = Path(".")
    my_path = root/"models"/model_name
    with open(my_path, 'rb') as pkl:
        loaded = pickle.load(pkl)
        pred = loaded.predict(n_periods=int(h))
        nobs = loaded.nobs_
    return pred, nobs


def car_search(name, conn, c):
    # returns list of available car parks for a given car park number
    c.execute("SELECT lots_available FROM cars WHERE carpark_number = (?) ORDER BY datetime(datestamp) DESC ",(name,))
    g=c.fetchall()
    a=str(g[1][0])
    if a=='NA':
        print("Carpark data is corrupted")
        return(False)
    else:
        return g



def Main():
    create_table()
    conn = sqlite3.connect("Data.db")
    c = conn.cursor()
    conn.commit()
    c.execute("SELECT DISTINCT carpark_number FROM cars")
    unique_names = c.fetchall()
    name_len = len(unique_names)
    for i in range(name_len):
        name = unique_names[i][0]
        h=6
        g= car_search(name, conn, c)
        if (g != False):
            # if stored, read, else create model
            check=coef_exists(name,conn, c)
            if len(check) >0:
                print("model {} made already... coefs are saved".format(name))
                #coefs = get_coef(name)
                #AddToTable(name,coefs,conn,c)
            else:
                print("fitting model: {}.".format(name))
                print("model {} out of {}".format(i,name_len))
                #forecast, l, fit = predict(name, h, conn, c)
                fit = predict(name, h, conn, c)
                #store_model(fit, name)
                print("completed {}.".format(name))
    exec(open("./jsontodatabase.py").read())


if __name__ == '__main__':
    Main()