"""
This takes debates.json and turns each object in the json to a record in the
SQLite database. The SQLite database has many fields for just general data on
the record, like membercodes, tallies, dates etc... just to query by, then the last
section is JSON of the object which will be returned to the end client via my
super cool API
"""
import json, sqlite3, os

#paths
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
debatesfile = os.path.join(filepathabove, "Database", "json-all", "debatesfinal.json")
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#clears table to add brand new data :D
cur.execute("DELETE FROM debates")
conn.commit()

#changes membercodes to names
def codestonames(codes):
    names = []
    for code in codes.split("|"):
        name = code.split(".")[0]
        name = name.replace("-", " ")
        names.append(name)
    return " | ".join(names)

#gets membercodes from an obj
def getmembercodes(obj):
    codes = []
    seen = set()
    debatestuff = obj.get("debatestuff", {})
    for section in debatestuff.get("sections", []):
        for speech in section.get("speeches", []):
            code = speech.get("membercode")
            if code and code not in seen:
                seen.add(code)
                codes.append(code)
    return "|".join(codes)

#gets titles from json
def getsectiontitles(obj):
    titles = []
    debatestuff = obj.get("debatestuff", {})
    for section in debatestuff.get("sections", []):
        title = section.get("title")
        if title:
            titles.append(title)
    return "|".join(titles)

#open debates.json
with open(debatesfile, "r", encoding="utf-8") as f:
    data = json.load(f)

debates = data["results"] if isinstance(data, dict) and "results" in data else data

#getting variables for querying
for b in debates:
    print("[SQL STATEMENT INSERTED]")
    debate = b["debateRecord"]

    contextdate = b["contextDate"]
    membercodes = getmembercodes(b)
    titles = getsectiontitles(b)
    housecode = debate["house"]["houseCode"]
    debatetype = debate["debateType"]
    jsondump = json.dumps(b, ensure_ascii=False)
    namesofmembers = codestonames(membercodes) if membercodes else ""
    #add data to SQLite database
    cur.execute("""
        INSERT OR REPLACE INTO debates (
        ContextDate, MemberCodes, DebateTitles,
        HouseCode, DebateType, NamesOfMembers, JSON
        )
        VALUES (?,?,?,?,?,?,?)
    """, (
        contextdate,
        membercodes,
        titles,
        housecode,
        debatetype,
        namesofmembers,
        jsondump
    ))

conn.commit()
conn.close()

print("done")