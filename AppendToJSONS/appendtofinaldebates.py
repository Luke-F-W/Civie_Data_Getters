from lxml import etree
import os, re, unicodedata, json, requests, time

#paths
filepathabove = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
debatesfile = os.path.join(filepathabove, "Database", "json-all", "debates.json")
outputfile = os.path.join(filepathabove, "Database", "json-all", "debatesfinal.json")

# the xml files use this "namespace" prefix
ns = {"akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD13"}


#either get normal text from xml, or just "" if nothing is there
def get_text(element):
    if element is None:
        return ""
    return etree.tostring(element, method="text", encoding="unicode").strip()


#normalises names, this function is used everywhere atp, makes Jamie O'Donoghue turn into jamieodonoghue
def normalisename(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()


#read all the people listed in the xml and store their info in a dict
def getpeople(xml_content):
    tree = etree.fromstring(xml_content)
    people = {}
    for person in tree.findall(".//akn:TLCPerson", ns):
        code = person.get("href").split("/")[-1]
        people[person.get("eId").lower()] = {
            "name": person.get("showAs"),
            "membercode": code,
            "imageURL": "https://data.oireachtas.ie/ie/oireachtas/member/" + code + "/image/large"
        }
    return people


#turn one <speech> tag into a dict with name + text, or "" if empty :D
def parse_speech(speech, people):
    #grab every paragraph's text and join it into one block of text
    paragraphs = []
    for p in speech.findall(".//akn:p", ns):
        p_text = get_text(p)
        if p_text:
            paragraphs.append(p_text)
    text = " ".join(paragraphs)

    if not text:
        return None

    #figure out who said it, using the people dict if we can
    by = normalisename(speech.get("by", ""))
    by = by.replace("#", "")
    person = people.get(by)

    if person:
        name = person["name"]
    else:
        from_tag = speech.find("akn:from", ns)
        name = get_text(from_tag) if from_tag is not None else None

    return {
        "name": name,
        "membercode": person["membercode"] if person else None,
        "imageurl": person["imageURL"] if person else None,
        "speechtext": text
    }


#turn a whole debate xml file into a dict with a title + list of sections
def parse_debate_xml(xml_content, people):
    tree = etree.fromstring(xml_content)

    #title is in one of either block
    title_block = tree.find(".//akn:block[@name='committee_en']", ns) or tree.find(".//akn:block[@name='proponent_en']", ns)
    title = get_text(title_block)

    #go through every section and collect its speeches
    sections = []
    for sec in tree.findall(".//akn:debateSection", ns):
        heading = sec.find("akn:heading", ns)

        speeches = []
        for speech in sec.findall("akn:speech", ns):
            parsed = parse_speech(speech, people)
            if parsed is not None:
                speeches.append(parsed)

        #only keep sections that actually have speeches in them
        if speeches:
            sections.append({
                "title": get_text(heading),
                "speeches": speeches
            })

    return {"title": title, "sections": sections}


#gets debates.json
with open(debatesfile, "r", encoding="utf-8") as f:
    raw = json.load(f)

#load the debates we've already finished
with open(outputfile, "r", encoding="utf-8") as f:
    final = json.load(f)

#make a quick-lookup set of debates already done
existing = {d.get("debateRecord", {}).get("uri") for d in final}

#go through every debate and process the ones we haven't done yet
for obj in raw:
    uri = obj.get("debateRecord", {}).get("uri")
    if uri in existing:
        continue

    #if this debate has an xml version available, download and parse it
    xml_entry = obj.get("debateRecord", {}).get("formats", {}).get("xml")
    if xml_entry:
        try:
            r = requests.get(xml_entry["uri"], timeout=10)
            people = getpeople(r.content)
            obj["debatestuff"] = parse_debate_xml(r.content, people)
        except Exception as e:
            print(f"failed {xml_entry['uri']}: {e}")
        time.sleep(0.1)

    final.append(obj)
    print(f"added {uri}")

#save everything to debatesfinal.json
with open(outputfile, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print("done")
