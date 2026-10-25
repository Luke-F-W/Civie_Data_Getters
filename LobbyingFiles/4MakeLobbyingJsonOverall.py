"""
This script turns the CSV into a large flat JSON 
file.
"""
import pandas as pd
import os
import re
import unicodedata

file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
maincsv = os.path.join(filepathabove, "maincsv.csv") #csv to make json from
save = os.path.join(filepathabove, "Database", "json-all", "lobbying.json") #save to here

#turns a name into a code
def normalisename(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()

csvv = pd.read_csv(maincsv, sep=',')
csvv = csvv.loc[:, :"MemberCodes"]

#add lobbyistcode
csvv["LobbyistCode"] = csvv["Lobbyist Name"].fillna("").apply(normalisename)

#make json & save
csvv.to_json(
    save,
    orient="records",
    indent=2,
    force_ascii=False
)
print("csv has been changed to json!! <-o->")