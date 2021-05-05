import csv
cp = []
all=[]
with open('carpark.csv') as csvfile:
    rows = csv.reader(csvfile)
    res = list(zip(*rows))
r = len(res)
for i in range((r-2)-1):
    i = i + 2
    if (i % 2==0):
        cpnum= res[i][0][14:]
        lots= res[i+1][2]
        avail = res[i][1:]
        time = res[1][1:]
        cp=[cpnum, lots, avail,time]
        all.append(cp)

#print(res[3][0:5])
print(all[7][0])