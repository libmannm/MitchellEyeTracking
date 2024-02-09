import pandas as pd
import numpy as np
import os

def filter(fName):
    df = pd.read_csv(fName, skiprows = 30, usecols=["Timestamp","ET_PupilLeft","ET_PupilRight"])
    data = df.to_numpy()
    data2 = []
    for row in data:
        if row[1]*0 == 0:
            row2 = row
            for i,val in enumerate(row):
                if val == -1:
                    row2[i] = np.nan
            data2.append(row2)
    expName = fName[:-4] + "filtered.csv"

    data2 = np.array(data2)
    df2 = pd.DataFrame(data2, columns = ["Timestamp","ET_PupilLeft","ET_PupilRight"])
    df2.to_csv(expName,index=False)
    
path = "M:\\Research\\Kaiyo\\Variants\\Variant Raw Sensor Data\\2-8Update\\"    
csvList = os.listdir(path)
for word in csvList:
    if ".csv" in word:
        filter(path+word)