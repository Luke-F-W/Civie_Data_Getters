"""
This code gets and saves all debates from the API,
The amount of debate records the api holds is 10000, so
we go through 100 at a time until skip == 10000, after that
all records are successfully saved and prepared for the API,
The code shown is reused for the other 3 sections of data,
excluding lobbying. This script was only used once, and was
no longer needed as records are now appended to the JSON made here
by appenders
"""

import requests
import time
import json
import os

#get the path to save to
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
out = os.path.join(filepathabove, "Database", "json-all", "debates.json")

data = []
skip = 0

#goes through all records on the API
while skip < 10000:
    url = "https://api.oireachtas.ie/v1/debates?skip=" + str(skip) + "&limit=100"
    
    response = requests.get(url)
    response = response.json()["results"]
    data += response
    #skip by 100 as i get 100 results each time
    skip += 100
    print("got 100 records, we are now at:" + str(skip))
    time.sleep(0.3)

        
with open(out, "w", encoding="utf-8") as d:
    json.dump(data, d, indent=2, ensure_ascii=False)
       
print("debates is done <-o->")