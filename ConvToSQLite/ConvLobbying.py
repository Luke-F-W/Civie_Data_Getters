"""
This takes lobbying.json and turns each object in the json to a record in the
SQLite database. The SQLite database has many fields for just general data on
the record, like membercodes, tallies, dates etc... just to query by, then the last
section is JSON of the object which will be returned to the end client via my
super cool API
"""

import json, sqlite3, os

#path
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
lobbyingfile = os.path.join(filepathabove, "Database", "json-all", "lobbying.json")
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#clears table to add brand new data :D
cur.execute("DELETE FROM Lobbying")
conn.commit()

#opens lobby.json
with open(lobbyingfile, "r", encoding="utf-8") as f:
    data = json.load(f)

lobbying = data["results"] if isinstance(data, dict) and "results" in data else data

#changes membercodes to names
def codestonames(codes):
    names = []
    for code in codes.split("|"):
        name = code.split(".")[0]
        name = name.replace("-", " ")
        names.append(name)
    return " | ".join(names)

#the lobbying data has weird date formats, to make compatible with other types of data, i change
def fixdate(date):
    if not date:
        return None
    date = date.split(" ")[0]
    d = date.split("/")[0]
    m = date.split("/")[1]
    y = date.split("/")[2]
    return y + "-" + m + "-" + d

#getting variables for querying
for b in lobbying:
    print("[SQL STATEMENT INSERTED]")
    id = b["Id"]
    lobbyistname = b["Lobbyist Name"]
    lobbyistcode = b["LobbyistCode"]
    contextdate = fixdate(b["Date Published"])
    relevantmatter = b["Relevant Matter"]
    details = b["Specific Details"]
    lobbied = b["DPOs Lobbied"]
    subjectmatter = b["Subject Matter"]
    intendedresults = b["Intended Results"]
    lobbyingactivities = b["Lobbying Activities"]
    mainlobbyist = b["Person primarily responsible for lobbying on this activity"]
    membercodes = b["MemberCodes"]
    namesofmembers = codestonames(membercodes) if membercodes else ""

    #add data to SQLite database
    cur.execute("""
        INSERT OR REPLACE INTO Lobbying (
        ID, LobbyistName, LobbyistCode, contextDate, RelevantMatter, Details,
        Lobbied, SubjectMatter, IntendedResults,
        LobbyingActivities, MainLobbyist, Membercodes, NamesOfMembers, JSON
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        id,
        lobbyistname,
        lobbyistcode,
        contextdate,
        relevantmatter,
        details,
        lobbied,
        subjectmatter,
        intendedresults,
        lobbyingactivities,
        mainlobbyist,
        membercodes,
        namesofmembers,
        json.dumps(b)
    ))

conn.commit()
conn.close()

print("done")