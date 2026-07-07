import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

# 1. Basic setup and parsing
INPUT_FILE = "./Data/Spanish_ALL/data_gnd.xml"
OUTPUT_FILE = "./Data/Spanish_ALL/corpus.jsonl"
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

# 1a. Form/genre labels to exclude when they show up as GND keywords
forms_to_exclude = [
    "Autobiografie", "Bibliografie", "Biografie", "Festschrift", "Schulbuch",
    "Adressbuch", "Anthologie", "Atlas", "Aufgabensammlung", "Aufsatzsammlung",
    "Ausstellungskatalog", "Beispielsammlung", "Bilderbuch", "Brief",
    "Datensammlung", "Diagramm", "Drehbuch", "Einblattdruck", "Einführung",
    "Enzyklopädie", "Fahrplan", "Faksimile", "Fallstudiensammlung",
    "Fiktionale Darstellung", "Film", "Filmografie", "Flugblatt", "Flugschrift",
    "Formelsammlung", "Formularsammlung", "Forschungsbericht", "Forschungsdaten",
    "Fotografie", "Führer", "Fundstellenverzeichnis", "Genealogische Tafel",
    "Gespräch", "Globus", "Grafik", "Graphzine", "Handschrift", "Haushaltsplan",
    "Hochschulschrift", "Hörbuch", "Hörspiel", "Humoristische Darstellung",
    "Inkunabel", "Interview", "Inventar", "Jugendbuch", "Jugendsachbuch",
    "Kalender", "Karikatur", "Karte", "Katalog", "Kinderbuch", "Kindersachbuch",
    "Kochbuch", "Kolumnensammlung", "Kommentar", "Konferenzschrift",
    "Konkordanz", "Künstlerbuch", "Kunstführer", "Laudatio", "Lehrbuch",
    "Lehrerhandbuch", "Lehr- und Lernressource", "Lehrplan", "Lernsoftware",
    "Lesebuch", "Liederbuch", "Literaturbericht", "Loseblattsammlung",
    "Mehrsprachiges Wörterbuch", "Mitgliederverzeichnis", "Modell",
    "Monografische Reihe", "Musikhandschrift", "Nachruf", "Norm",
    "Ortsverzeichnis", "Papyrus", "Patentschrift", "Plakat", "Plan", "Podcast",
    "Postkarte", "Praktikum", "Predigthilfe", "Pressendruck", "Pressestimme",
    "Programmheft", "Puzzle", "Quelle", "Ratgeber", "Rede", "Referateorgan",
    "Regest", "Reisebericht", "Reportagensammlung", "Rezension", "Richtlinie",
    "Röntgenbild", "Rückläufiges Wörterbuch", "Sachbilderbuch", "Satzung",
    "Schematismus", "Schulprogramm", "Software", "Spiel", "Spielfilm",
    "Sprachatlas", "Sprachführer", "Sprachkurs (Lehr- und Lernressource)",
    "Stadtplan", "Statistik", "Tabelle", "Tafel", "Tagebuch",
    "Technische Zeichnung", "Telefonbuch", "Testmaterial", "Theaterstück",
    "Thesaurus", "Übungssammlung", "Umfrage", "Unterrichtseinheit", "Urkunde",
    "Verkaufskatalog", "Verzeichnis", "Vorlesungsverzeichnis", "Weblog",
    "Website", "Weltkarte", "Werkverzeichnis", "Werkzeitschrift", "Wörterbuch",
    "Zeichnung", "Zeitschrift", "Zeittafel", "Zeitung", "Zitatensammlung",
    "Amateurfilm", "Buchobjekt", "Bühnenmanuskript", "Digitale Edition",
    "Dokumentarfilm", "Edeldruck", "Fernsehsendung", "Fotobuch", "Gebetbuch",
    "Gelegenheitsschrift", "Gesangbuch", "Grünbuch", "Konzertzettel",
    "Kritische Ausgabe", "Kurzfilm", "Lehrfilm", "Leichenpredigt", "Missale",
    "Ortsansicht", "Persönliches Fotobuch", "Pop-up-Buch", "Stummfilm",
    "Theaterzettel", "Trailer (Film)", "Vedute", "Vogelschaukarte",
    "Wandkarte", "Werbefilm", "Wochenschau",
]

# 2. Helper functions


def text_of(element):
    return element.text.strip() if element is not None and element.text else None


def map_keywords_to_id(record):
    """
    Extract GND-linked keywords from 044K, 041A and 044L fields, using
    subfield 7 as a strict gatekeeper: a datafield only yields a keyword if
    it carries a non-empty subfield 7 (the GND id) and its subfield A is not
    exactly "ARK". Keyword text comes from subfield a or A (A is fused with
    subfield D, e.g. "Cervantes, Miguel de"), and generic form/genre labels
    (forms_to_exclude) are dropped.
    """
    mapped = []
    for tag in ("044K", "041A", "044L"):
        for datafield in record.findall(f".//ns1:datafield[@tag='{tag}']", ns):
            subfield7 = datafield.find("ns1:subfield[@code='7']", ns)
            id_text = text_of(subfield7) or ""
            ark_subfield = datafield.find("ns1:subfield[@code='A']", ns)
            ark_text = text_of(ark_subfield) or ""

            # Only proceed if subfield 7 is present and non-empty and
            # subfield A is not exactly "ARK"
            if not id_text or ark_text.upper() == "ARK":
                continue

            for subfield in datafield.findall("ns1:subfield", ns):
                code = subfield.attrib.get("code")
                if code not in ("a", "A"):
                    continue

                keyword_text = text_of(subfield) or ""
                if not keyword_text:
                    continue

                # omit any keyword forms that are in the exclusion list
                if keyword_text in forms_to_exclude:
                    continue

                # If subfield is A, check for subfield D and fuse them as "A, D"
                if code == "A":
                    subfield_d = datafield.find("ns1:subfield[@code='D']", ns)
                    d_text = text_of(subfield_d)
                    if d_text:
                        keyword_text = f"{keyword_text}, {d_text}"

                mapped.append({"id": id_text, "keyword": keyword_text})
                break

    return mapped


def extract_gnd_keywords(record):
    """
    Extract GND ids from 044K/041A/044L using the map_keywords_to_id
    gatekeeper logic (subfield 7 required, ARK subfield A excluded, form
    labels filtered out). Returns just the ids, since that's what the rest
    of the pipeline turns into URIs.
    """
    return [item["id"] for item in map_keywords_to_id(record)]



def change_ids_to_uris(keywords_set):
    uris = set()
    for keyword in keywords_set:
        if keyword.startswith("gnd"):
            gnd_id = keyword[3:]
            uris.add(f"https://d-nb.info/gnd{gnd_id}")
        else:
            uris.add(keyword)
    return uris


def remove_records(records, parent):
    """Remove a list of records from the specified parent element."""
    for record in records:
        try:
            parent.remove(record)
        except ValueError:
            pass


def write_record_to_file(record):
    """Write a single record as a JSON line to the output file if not already present."""
    title = record.get("text")
    if title is None:
        return
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as out:
            for line in out:
                try:
                    existing = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # if an existing record has the same title, do not add
                if existing.get("text") == title:
                    return
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        out.write(json.dumps(record, ensure_ascii=False) + "\n")




# 4. Extract data needed to identify duplicates

records_by_author_title = defaultdict(list)

for record in root:
    title = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
    subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
    author_first_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='D']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='D']", ns))
    author_last_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='A']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='A']", ns))
    isbn = text_of(record.find(".//ns1:datafield[@tag='004A']/ns1:subfield[@code='0']", ns)) or ""
    status = text_of(record.find(".//ns1:datafield[@tag='002@']/ns1:subfield[@code='0']", ns))
    author = f"{author_last_name}, {author_first_name}"
    if subtitle:
        title_full = f"{title} : {subtitle}"
    else:
        title_full = title
    if title_full and author:
        records_by_author_title[(author, title_full)].append(record)

# 5. Drop duplicates entirely: any (author, title_full) group with more than
# one record is removed from the tree and never written to corpus.jsonl.
remove_records([record for recs in records_by_author_title.values() for record in recs if len(recs) > 1], root)




# 6. Transform remaining non-duplicate records
for record in root:
    title = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
    subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
    if subtitle:
        title_full = f"{title} : {subtitle}"
    else:
        title_full = title
    keywords = set(extract_gnd_keywords(record))
    keywords = change_ids_to_uris(keywords)
    subjects = [{"uri": uri} for uri in sorted(keywords)]
    output_record = {"text": title_full, "subjects": subjects}
    write_record_to_file(output_record)