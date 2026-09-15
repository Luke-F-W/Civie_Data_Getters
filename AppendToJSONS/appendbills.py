"""
This gets new bill records and adds them to the pre-existing bills.json file.
I will add these files to my SQLite Database.
"""

import requests
import json
import os
import time

#filepaths
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
billsfile = os.path.join(filepathabove, "Database", "json-all", "bills.json")
skip = 0

#open billsfile
with open(billsfile, "r", encoding="utf-8") as d:
    jsonloaded = json.load(d)

#looks for records not in the json already
while skip < 10000:
    url = "https://api.oireachtas.ie/v1/legislation?bill_status=&skip=" + str(skip) + "&limit=1000&lang=en"
    response = requests.get(url)
    response = response.json()["results"]

    for record in response:
        showas = record.get("bill", {}).get("uri")
        if not any(item.get("bill", {}).get("uri") == showas for item in jsonloaded):
            jsonloaded.append(record)
            print(record)
        else:
            pass   
            print("skipped")
    
    skip += 1000
    time.sleep(0.1)

#put new records into json
with open(billsfile, "w", encoding="utf-8") as d:
    json.dump(jsonloaded, d, ensure_ascii=False, indent=2)

print("bills is done <-o->")
