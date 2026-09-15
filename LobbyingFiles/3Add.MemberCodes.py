"""This script normalises names (To find minor mismatches
in names, e.g. Susan Keat and susan keat both become
susankeat). After this member codes are mapped to the
normalised names and added to records, This is required
as the API uses membercodes to identify politicians
actions, and the lobbyingCSV doesnt have membercodes
prior to this
"""
import pandas as pd
import unicodedata
import re
import os
import json

#normalises names (i reuse this function in the stats section)
def normalisename(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()

file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
maincsv = os.path.join(filepathabove, "maincsv.csv")  #csv that i add membercodes to
membersfile = os.path.join(filepathabove, "Database", "json-all", "members.json")  #json file with member records

csvv = pd.read_csv(maincsv, header=None)

with open(membersfile, 'r', encoding='utf-8') as f:
    members = json.load(f)

codemap = {}

#normalise name from membercode and add to codemap
for entry in members:
    membercode = entry.get("member", {}).get("memberCode")
    if not membercode:
        continue

    namepiece = membercode.split('.')[0]
    namepiece = normalisename(namepiece)
    codemap[namepiece] = membercode

#normalise cell names, matches them then returns them
def matchmembertocodes(cell):
    names = []
    #Malcolm Noonan|Councillor|Kilkenny County Council::Matt Doran|Councillor|Kilkenny County Council is a example of what a cell looks like
    if not pd.isna(cell):
        for name in cell.split("::"):
            toappend = name.split('|')[0]
            names.append(toappend)

    normallist = []
    for n in names:
        n = normalisename(n)
        normallist.append(n)

    match = []
    for n in normallist:
        if n in codemap:
            n = codemap[n]
            match.append(n)

    return "|".join(match)

#19 and 8 are columns in the CSV
csvv[19] = csvv[8].apply(matchmembertocodes)

csvv.to_csv(maincsv, index=False, header=None)
print("finished <-o->")