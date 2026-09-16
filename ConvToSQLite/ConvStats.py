"""
This takes stats.json and turns each object in the json to a record in the
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
statsfile = os.path.join(filepathabove, "Database", "json-all", "stats.json")
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#clears table to add brand new data :D
cur.execute("DELETE FROM Stats")
conn.commit()

#opens stats.json
with open(statsfile, "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data["results"] if isinstance(data, dict) and "results" in data else data

#getting variables for querying
for membercode, b in questions.items():
    print("[SQL STATEMENT INSERTED]")

    #add data to SQLite database
    cur.execute("""
        INSERT OR REPLACE INTO Stats (
        MemberCode, JSON
        )
        VALUES (?,?)
    """, (
        membercode,
        json.dumps(b),
    ))

conn.commit()
conn.close()

print("done")