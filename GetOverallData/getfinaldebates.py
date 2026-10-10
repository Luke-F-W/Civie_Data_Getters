"""Parse debate XML records into a cleaner final JSON structure.

This script reads the raw debate metadata collected by getdebates.py, downloads each
XML record, extracts the debate text and speaker metadata, and writes the enriched
results to debatesfinal.json.
"""

from lxml import etree
import os
import re
import unicodedata
import json 
import requests
import time


file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
debatesfile = os.path.join(filepathabove, "Database", "json-all", "debates.json")
outputfile = os.path.join(filepathabove, "Database", "json-all", "debatesfinal.json")

def getpeople(xml_content):
    # Extract person metadata from debate XML for later matching to speeches.
    ns = {"akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD13"}
    tree = etree.fromstring(xml_content)
    people = {}

    for person in tree.findall(".//akn:TLCPerson", ns):
        name = person.get("showAs")
        normalisedname = person.get("eId").lower()
        membercode = person.get("href").split("/")[-1]
        imageurl = "https://data.oireachtas.ie/ie/oireachtas/member/" + membercode + "/image/large"

        people[normalisedname] = {
            "name": name,
            "normalisedname": normalisedname,
            "membercode": membercode,
            "imageURL": imageurl
        }

    return people

def normalisename(name):
    # Remove accents and non-letter characters so speaker names can be matched consistently.
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()

ns = {"akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD13"}

#fixes xml
def getcleantext(speechstuff):
    # Gather plain text from all paragraph tags inside a speech block.
    paragraphs = []
    for p in speechstuff.findall(".//akn:p", ns):
        text = etree.tostring(p, method="text", encoding="unicode")
        text = text.strip()
        if text:
            paragraphs.append(text)
    return " ".join(paragraphs)

def getfromtext(speechstuff):
    from_tag = speechstuff.find("akn:from", ns)
    if from_tag is not None:
        return etree.tostring(from_tag, method="text", encoding="unicode").strip()
    return ""

def parsedebatexml(xmlstuff, people):
    tree = etree.fromstring(xmlstuff)

    # get debate title from preface
    title_block = tree.find(".//akn:block[@name='committee_en']", ns)
    if title_block is None:
        title_block = tree.find(".//akn:block[@name='proponent_en']", ns)
    title = etree.tostring(title_block, method="text", encoding="unicode").strip() if title_block is not None else ""

    sections = []

    for debatesection in tree.findall(".//akn:debateSection", ns):
        # Extract section heading and the speeches contained within it.
        heading = debatesection.find("akn:heading", ns)
        section_title = etree.tostring(heading, method="text", encoding="unicode").strip() if heading is not None else ""

        speeches = []
        for speech in debatesection.findall("akn:speech", ns):
            by = speech.get("by", "")
            speech_text = getcleantext(speech)

            if not speech_text:
                continue

            name = None
            membercode = None
            imageurl = None
            if by and by != "#":
                normalised = normalisename(by.replace("#", ""))
                if normalised in people:
                    person = people[normalised]
                    name = person["name"]
                    membercode = person["membercode"]
                    imageurl = person["imageURL"]

            if name is None:
                from_text = getfromtext(speech)
                if from_text:
                    name = from_text

            speeches.append({
                "name": name,
                "membercode": membercode,
                "imageurl": imageurl,
                "speechtext": speech_text
            })

        if speeches:
            sections.append({
                "title": section_title,
                "speeches": speeches
            })

    return {
        "title": title,
        "sections": sections
    }

print("loading debates...")
with open(debatesfile, "r", encoding="utf-8") as f:
    debates = json.load(f)
print(f"loaded {len(debates)} debates")

# Process each debate record and add parsed XML content.
results = []
for i, obj in enumerate(debates):
    xml_entry = obj["debateRecord"]["formats"].get("xml")
    if not xml_entry:
        results.append(obj)
        continue

    url = xml_entry["uri"]
    print("test")

    try:
        r = requests.get(url, timeout=10)
        people = getpeople(r.content)
        debatestuff = parsedebatexml(r.content, people)
        obj["debatestuff"] = debatestuff
        print("one down gng")
    except Exception as e:
        #print statements move fast, many dashes below to see if an error quickly passes me
        print("Ruh Roh")

    results.append(obj)
    time.sleep(0.2)

print("saving...")
with open(outputfile, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent = 2)

print("done")
