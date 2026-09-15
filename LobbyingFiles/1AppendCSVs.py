import pandas as pd
import os

file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)

maincsv = os.path.join(filepathabove, "maincsv.csv")
csvs = os.path.join(filepathabove, "csvlist")

x = 1

while x < 34:
    csvfile = os.path.join(csvs, str(x) + ".csv")
    csvv = pd.read_csv(csvfile)

    # Check column D (index 3) for missing values
    if csvv.shape[1] <= 3 or csvv.iloc[:, 3].isna().any():
        print(f"ERROR: {x}.csv has missing Date Published values")

    csvv.to_csv(maincsv, mode="a", header=False, index=False)

    print(str(x) + " has been added <-o->")
    x += 1
