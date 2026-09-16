"""
This takes bills.json and turns each object in the json to a record in the
SQLite database. The SQLite database has many fields for just general data on
the record, like membercodes, tallies, dates etc... just to query by, then the last
section is JSON of the object which will be returned to the end client via my
super cool API
"""
import json, sqlite3, os
from bs4 import BeautifulSoup

#paths
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
billsfile = os.path.join(filepathabove, "Database", "json-all", "bills.json")
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#clears table to add brand new data :D
cur.execute("DELETE FROM Legislation")
conn.commit()


#changes membercodes to names
def codestonames(codes):
    names = []
    for code in codes.split("|"):
        name = code.split(".")[0]
        name = name.replace("-", " ")
        names.append(name)
    return " | ".join(names)

#open bills.json
with open(billsfile, "r", encoding="utf-8") as f:
    data = json.load(f)

bills = data["results"] if isinstance(data, dict) and "results" in data else data

def clean(x):
    return BeautifulSoup(x, "html.parser").get_text() if x else None

#getting variables for querying
for b in bills:
    print("[SQL STATEMENT INSERTED]")
    bill = b["bill"]
    bill_no = bill["billNo"] #bill number
    longTitleEn = bill["longTitleEn"] #long title en
    shortTitleEn = bill["shortTitleEn"] #short title en
    longTitleGa = bill["longTitleGa"] #long title ga
    shortTitleGa = bill["shortTitleGa"] #short title ga

    #json has HTML in these, must be cleaned
    longTitleEn = clean(longTitleEn)
    longTitleGa = clean(longTitleGa)
    shortTitleEn = clean(shortTitleEn)
    shortTitleGa = clean(shortTitleGa)
    status = bill["status"]
    context_date = b["contextDate"]
    source = bill["source"]
    billType = bill["billType"]
    billYear = bill["billYear"]

    #membercodes, which are annoying
    sponsors = bill.get("sponsors", [])
    membercodes_list = []
    for s in sponsors:
        uri = (
            s.get("sponsor", {})
            .get("by", {})
            .get("uri")
        )
        if uri:
            membercode = uri.split("/")[-1]
            membercodes_list.append(membercode)
    membercodes = "|".join(membercodes_list)

    namesofmembers = codestonames(membercodes) if membercodes else ""

    #insert cool data into cool SQLite table
    cur.execute("""
        INSERT OR REPLACE INTO Legislation (
            BillNo, BillType, BillYear,
            LongTitleEn, LongTitleGa,
            ShortTitleEn, ShortTitleGa,
            Source, Status,
            contextDate, Membercodes, NamesOfMembers, JSON
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        bill_no,
        billType,
        billYear,

        longTitleEn,
        longTitleGa,
        shortTitleEn,
        shortTitleGa,

        source,
        status,
        context_date,

        membercodes,
        namesofmembers,
        json.dumps(b)
    ))

conn.commit()
conn.close()

print("done")
