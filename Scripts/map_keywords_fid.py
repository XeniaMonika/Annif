import json
import xml.etree.ElementTree as ET
from collections import Counter

input_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\data_gnd.xml"
output_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\mapped_keywords.json"
forms_to_exclude = [
    "Autobiografie",
    "Bibliografie",
    "Biografie",
    "Festschrift",
    "Schulbuch",
    "Adressbuch",
    "Anthologie",
    "Atlas",
    "Aufgabensammlung",
    "Aufsatzsammlung",
    "Ausstellungskatalog",
    "Autobiografie",
    "Beispielsammlung",
    "Bibliografie",
    "Bilderbuch",
    "Biografie",
    "Brief",
    "Datensammlung",
    "Diagramm",
    "Drehbuch",
    "Einblattdruck",
    "Einführung",
    "Enzyklopädie",
    "Fahrplan",
    "Faksimile",
    "Fallstudiensammlung",
    "Festschrift",
    "Fiktionale Darstellung",
    "Film",
    "Filmografie",
    "Flugblatt",
    "Flugschrift",
    "Formelsammlung",
    "Formularsammlung",
    "Forschungsbericht",
    "Forschungsdaten",
    "Fotografie",
    "Führer",
    "Fundstellenverzeichnis",
    "Genealogische Tafel",
    "Gespräch",
    "Globus",
    "Grafik",
    "Graphzine",
    "Handschrift",
    "Haushaltsplan",
    "Hochschulschrift",
    "Hörbuch",
    "Hörspiel",
    "Humoristische Darstellung",
    "Inkunabel",
    "Interview",
    "Inventar",
    "Jugendbuch",
    "Jugendsachbuch",
    "Kalender",
    "Karikatur",
    "Karte",
    "Katalog",
    "Kinderbuch",
    "Kindersachbuch",
    "Kochbuch",
    "Kolumnensammlung",
    "Kommentar",
    "Konferenzschrift",
    "Konkordanz",
    "Künstlerbuch",
    "Kunstführer",
    "Laudatio",
    "Lehrbuch",
    "Lehrerhandbuch",
    "Lehr- und Lernressource",
    "Lehrplan",
    "Lernsoftware",
    "Lesebuch",
    "Liederbuch",
    "Literaturbericht",
    "Loseblattsammlung",
    "Mehrsprachiges Wörterbuch",
    "Mitgliederverzeichnis",
    "Modell",
    "Monografische Reihe",
    "Musikhandschrift",
    "Nachruf",
    "Norm",
    "Ortsverzeichnis",
    "Papyrus",
    "Patentschrift",
    "Plakat",
    "Plan",
    "Podcast",
    "Postkarte",
    "Praktikum",
    "Predigthilfe",
    "Pressendruck",
    "Pressestimme",
    "Programmheft",
    "Puzzle",
    "Quelle",
    "Ratgeber",
    "Rede",
    "Referateorgan",
    "Regest",
    "Reisebericht",
    "Reportagensammlung",
    "Rezension",
    "Richtlinie",
    "Röntgenbild",
    "Rückläufiges Wörterbuch",
    "Sachbilderbuch",
    "Satzung",
    "Schematismus",
    "Schulbuch",
    "Schulprogramm",
    "Software",
    "Spiel",
    "Spielfilm",
    "Sprachatlas",
    "Sprachführer",
    "Sprachkurs (Lehr- und Lernressource)",
    "Stadtplan",
    "Statistik",
    "Tabelle",
    "Tafel",
    "Tagebuch",
    "Technische Zeichnung",
    "Telefonbuch",
    "Testmaterial",
    "Theaterstück",
    "Thesaurus",
    "Übungssammlung",
    "Umfrage",
    "Unterrichtseinheit",
    "Urkunde",
    "Verkaufskatalog",
    "Verzeichnis",
    "Vorlesungsverzeichnis",
    "Weblog",
    "Website",
    "Weltkarte",
    "Werkverzeichnis",
    "Werkzeitschrift",
    "Wörterbuch",
    "Zeichnung",
    "Zeitschrift",
    "Zeittafel",
    "Zeitung",
    "Zitatensammlung",
    "Amateurfilm",
    "Buchobjekt",
    "Bühnenmanuskript",
    "Digitale Edition",
    "Dokumentarfilm",
    "Edeldruck",
    "Fernsehsendung",
    "Fotobuch",
    "Gebetbuch",
    "Gelegenheitsschrift",
    "Gesangbuch",
    "Grünbuch",
    "Konzertzettel",
    "Kritische Ausgabe",
    "Kurzfilm",
    "Lehrfilm",
    "Leichenpredigt",
    "Missale",
    "Ortsansicht",
    "Persönliches Fotobuch",
    "Pop-up-Buch",
    "Stummfilm",
    "Theaterzettel",
    "Trailer (Film)",
    "Vedute",
    "Vogelschaukarte",
    "Wandkarte",
    "Werbefilm",
    "Wochenschau"
]

# Map GND keywords to their IDs and text to make the analysis of keyword distribution human-readable
def map_keywords_to_id(record):
    mapped = []
    for tag in ("044K", "041A", "044L"):
        for datafield in record.findall(f".//ns1:datafield[@tag='{tag}']", ns):
            subfield7 = datafield.find("ns1:subfield[@code='7']", ns)
            id_text = (subfield7.text or "").strip() if subfield7 is not None else ""
            ark_subfield = datafield.find("ns1:subfield[@code='A']", ns)
            ark_text = (ark_subfield.text or "").strip() if ark_subfield is not None else ""
            # Only proceed if subfield 7 is present and non-empty and subfield A is not exactly ARK
            if not id_text or ark_text.upper() == "ARK":
                continue

            for subfield in datafield.findall("ns1:subfield", ns):
                code = subfield.attrib.get("code")
                if code not in ("a", "A"):
                    continue

                keyword_text = (subfield.text or "").strip()
                if not keyword_text:
                    continue

                # omit any keyword forms that are in the exclusion list
                
                if keyword_text in forms_to_exclude:
                    continue
                

                # If subfield is A, check for subfield D and fuse them as "A, D"
                if code == "A":
                    subfield_d = datafield.find("ns1:subfield[@code='D']", ns)
                    if subfield_d is not None and subfield_d.text and subfield_d.text.strip():
                        keyword_text = f"{keyword_text}, {subfield_d.text.strip()}"

                mapped.append({"id": id_text, "keyword": keyword_text})
                break

    return mapped

tree = ET.parse(input_file)
root = tree.getroot()
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}
records = root.findall('.//record')
if not records:
    records = list(root)

mapped_keywords = []
for record in records:
    mapped_keywords.extend(map_keywords_to_id(record))

print(mapped_keywords[0:10])

print(f"Found {len(mapped_keywords)} mapped keywords in XML records")

# Aggregate counts per keyword (keep first seen id for each keyword)
keyword_counts = Counter()
keyword_first_id = {}
for item in mapped_keywords:
    kw = item.get("keyword")
    kid = item.get("id")
    if kw is None:
        continue
    keyword_counts[kw] += 1
    if kw not in keyword_first_id and kid:
        keyword_first_id[kw] = kid

# Build unique list with counts, ordered by decreasing count
unique_mapped = [
    {"id": keyword_first_id.get(kw, ""), "keyword": kw, "count": count}
    for kw, count in keyword_counts.items()
]
unique_mapped.sort(key=lambda x: x["count"], reverse=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(unique_mapped, f, ensure_ascii=False, indent=2)