import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

# 1. Basic setup and parsing
INPUT_FOLDER = "./Data/Spanish_ALL/Split"
OUTPUT_FILE = "./Data/Spanish_ALL/corpus.jsonl"
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}

CLEAN_FILE_PATTERN = re.compile(r"_clean\.xml$", re.IGNORECASE)

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


# 3. Streaming helpers
#
# ET.parse() loads the whole file into memory as a DOM, which is what was
# blowing up memory on 2GB+ files. iterparse() + elem.clear() below
# processes one record at a time, so peak memory is roughly O(one record)
# instead of O(file size).


def _clean_files(folder_path):
    folder = Path(folder_path)
    return sorted(p for p in folder.iterdir() if p.is_file() and CLEAN_FILE_PATTERN.search(p.name))


def _iter_records(file_obj):
    depth = 0
    for event, elem in ET.iterparse(file_obj, events=("start", "end")):
        if event == "start":
            depth += 1
        else:
            depth -= 1
            if depth == 1:  # direct child of the root == one record
                yield elem
                elem.clear()


def process_file(xml_file, out_handle):
    """
    Single streaming pass: the *_clean.xml files are already deduplicated
    upstream, so every record is transformed as-is — no duplicate-group
    detection or cross-file title tracking needed anymore. Records with no
    GND subjects at all are dropped, since a title with an empty subjects
    list isn't useful training/indexing data.
    """
    kept = skipped_no_subjects = 0

    with open(xml_file, "rb") as f:
        for record in _iter_records(f):
            title = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
            subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
            title_full = f"{title} : {subtitle}" if subtitle else title

            if not title_full:
                continue

            keywords = set(extract_gnd_keywords(record))
            keywords = change_ids_to_uris(keywords)
            subjects = [{"uri": uri} for uri in sorted(keywords)]

            if not subjects:
                skipped_no_subjects += 1
                continue

            output_record = {"text": title_full, "subjects": subjects}

            out_handle.write(json.dumps(output_record, ensure_ascii=False) + "\n")
            kept += 1

    print(f"{xml_file.name}: wrote {kept} records, skipped {skipped_no_subjects} with no subjects")


if __name__ == "__main__":
    xml_files = _clean_files(INPUT_FOLDER)
    if not xml_files:
        print(f"No *_clean.xml files found in {INPUT_FOLDER}")
    else:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as out_handle:
            for xml_file in xml_files:
                process_file(xml_file, out_handle)