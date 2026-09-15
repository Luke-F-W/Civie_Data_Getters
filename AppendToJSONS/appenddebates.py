"""
This gets new debate records and adds them to the pre-existing debates.json file.
I still must add more data to my json before, this just adds to debates.json, but
appendtofinaldebates.py will add in the extra data and debatesfinal.json will be what
is added to the SQLite database.
"""

import requests
import json
import os
import time

#filepaths
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
debatesfile = os.path.join(filepathabove, "Database", "json-all", "debates.json")
skip = 0

#open debatesfile
with open(debatesfile, "r", encoding="utf-8") as d:
    jsonloaded = json.load(d)

#looks for records not in the json already
while skip < 10000:
    url = "https://api.oireachtas.ie/v1/debates?skip=" + str(skip) + "&limit=1000"
    response = requests.get(url)
    response = response.json()["results"]

    for record in response:
        showas = record.get("debateRecord", {}).get("uri")
        if not any(item.get("debateRecord", {}).get("uri") == showas for item in jsonloaded):
            jsonloaded.append(record)
            print(record)
        else:
            pass   
            print("skipped")
    
    skip += 1000
    time.sleep(0.1)

#put new records into json
with open(debatesfile, "w", encoding="utf-8") as d:
    json.dump(jsonloaded, d, ensure_ascii=False, indent=2)

print("debates is done <-o->")