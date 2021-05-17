import csv
from datetime import datetime


def parseCSV(lot_number):
    cp = []
    parking_available = []
    numbers_list = []
    all_carpark = []
    time_list=datetime.strptime('19/04/2021 10:59', '%d/%m/%Y %H:%M')
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

            # time conversion
            time_list = datetime.strptime('19/04/2021 10:59', '%d/%m/%Y %H:%M')
            print(time_list.strftime("%H%M %d/%m/%Y"))
            break
    print(parking_available)

    return parking_available, numbers_list, time_list