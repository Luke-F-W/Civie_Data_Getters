"""
This takes members.json and turns each object in the json to a record in the
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
membersfile = os.path.join(filepathabove, "Database", "json-all", "members.json")
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#clears table to add brand new data :D
cur.execute("DELETE FROM Members")
conn.commit()

#opens members.json
with open(membersfile, "r", encoding="utf-8") as f:
    data = json.load(f)

members = data["results"] if isinstance(data, dict) and "results" in data else data

#getting variables for querying
for b in members:
    print("[SQL STATEMENT INSERTED]")

    member = b["member"]
    fullname = member["fullName"]
    fname = member["firstName"]
    lname = member["lastName"]
    image = member["image"]
    membercode = member["memberCode"]

    #add data to SQLite database
    cur.execute("""
        INSERT OR REPLACE INTO Members (
        FullName, FirstName, LastName,
        Image, MemberCode, JSON
        )
        VALUES (?,?,?,?,?,?)
    """, (
        fullname,
        fname,
        lname,
        image,
        membercode,
        json.dumps(b),
    ))

conn.commit()
conn.close()

print("done")