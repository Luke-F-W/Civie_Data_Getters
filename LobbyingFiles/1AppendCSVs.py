"""
This script adds all the CSVs together into 1 mainCSV
"""

import pandas as pd
import os

file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)

maincsv = os.path.join(filepathabove, "maincsv.csv")
csvs = os.path.join(filepathabove, "csvlist")

header = pd.read_csv(maincsv, nrows=0).columns

for x in range(1, 33):
    csvv = pd.read_csv(os.path.join(csvs, str(x) + ".csv"), dtype=str, keep_default_na=False)
    csvv = csvv.reindex(columns=header, fill_value="")
    csvv.to_csv(maincsv, mode="a", header=False, index=False)
    print(str(x) + " has been added <-o->")
