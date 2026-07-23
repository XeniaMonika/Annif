from rdflib import Graph
from rdflib.namespace import OWL, Namespace
import json

data = "./Data/Vocabs/authorities-gnd-sachbegriff_lds_20260217.ttl"
output_file = "./Data/Vocabs/gnd_wikidata_links.json"

GNDO = Namespace("https://d-nb.info/standards/elementset/gnd#")

def extract_gnd_wikidata_links(ttl_path):
    g = Graph()
    g.parse(ttl_path, format="turtle")

    links = {}
    for s, o in g.subject_objects(OWL.sameAs):
        if str(o).startswith("http://www.wikidata.org/entity/"):
            if str(s).startswith("https://d-nb.info/gnd/"):
                gnd_id = str(s).rsplit("/", 1)[-1]
                qid = str(o).rsplit("/", 1)[-1]
                ger_label = g.value(s, GNDO.preferredNameForTheSubjectHeading)
                links[gnd_id] = {"qid": qid, "ger_label": str(ger_label) if ger_label else ""}
    return links

linkdata = extract_gnd_wikidata_links(data)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(linkdata, f, ensure_ascii=False, indent=2)
    
print(f"Extracted {len(linkdata)} GND-Wikidata links.")