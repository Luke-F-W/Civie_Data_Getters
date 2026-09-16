"""
This takes questions.json and turns each object in the json to a record in the
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
questionsfile = os.path.join(filepathabove, "Database", "json-all", "questions.json")
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#clears table to add brand new data :D
cur.execute("DELETE FROM Questions")
conn.commit()

#opens questions.json
with open(questionsfile, "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data["results"] if isinstance(data, dict) and "results" in data else data

#getting variables for querying
for b in questions:
    print("[SQL STATEMENT INSERTED]")

    quest = b["question"]

    questionno = quest["questionNumber"]
    questiontype = quest["questionType"]
    question = quest["showAs"]
    answertext = quest["answerText"]
    contextDate = b["contextDate"]
    questionTo = quest["to"]["showAs"]
    questionBy = quest["by"]["showAs"]
    membercodeBy = quest["by"]["memberCode"]

    #add data to SQLite database
    cur.execute("""
        INSERT OR REPLACE INTO Questions (
        QuestionNumber, QuestionType, Question, answerText, contextDate, QuestionTo,
        QuestionBy, MembercodeBy, JSON
        )
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        questionno,
        questiontype,
        question,
        answertext,
        contextDate,
        questionTo,
        questionBy,
        membercodeBy,
        json.dumps(b),
    ))

conn.commit()
conn.close()

print("done")