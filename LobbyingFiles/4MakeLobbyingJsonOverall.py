"""
This script turns the CSV into a large flat JSON 
file.
"""
import pandas as pd
import os 

file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
maincsv = os.path.join(filepathabove, "maincsv.csv") #csv to make json from
save = os.path.join(filepathabove, "Database", "json-all", "lobbying.json") #save to here

csvv = pd.read_csv(maincsv, sep=',')

#make json & save
csvv.to_json(
    save,
    orient="records",
    indent=2,
    force_ascii=False
)
print("csv has been changed to json!! <-o->")
