"""
This code gets and saves all bills from the API,
The amount of bill records the api holds is 5961, so
we go through 100 at a time until skip >= 5961, after that
all records are saved and prepared for the API,
The code shown is reused for the other sections of data,
excluding lobbying. This script was only used once, and was
no longer needed as records are now appended to the JSON made here
by appenders
"""
import requests
import json
import os
import time

#get the path to save to
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
out = os.path.join(filepathabove, "Database", "json-all", "bills.json")
data = []
skip = 0

#goes through all records on the API
while skip < 5961:
    url = "https://api.oireachtas.ie/v1/legislation?bill_status=&bill_source=Government,Private%20Member&skip=" + str(skip) + "&limit=100&lang=en"
    
    response = requests.get(url)
    response = response.json()["results"]
    data += response
    #skip by 100 as i get 100 results each time
    skip += 100
    print("got 100 records, we are now at:" + str(skip))
    time.sleep(0.3)
        
with open(out, "w", encoding="utf-8") as d:
    json.dump(data, d, indent=2, ensure_ascii=False)

print("bills is done <-o->")
