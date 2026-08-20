import csv
import rdflib

INPUT_FILE = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Vocabs\\\\authorities-gnd-sachbegriff_lds_20260217.ttl"      
OUTPUT_FILE = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Vocabs\\Annif_ready\\sachbegriffe.csv" 
GND_NAMESPACE = "https://d-nb.info/standards/elementset/gnd#"
PREDICATE_PREF_LABEL = rdflib.URIRef(GND_NAMESPACE + "preferredNameForTheSubjectHeading")
 
 
def main():
    print(f"Reading {INPUT_FILE} ...")
    graph = rdflib.Graph()
    graph.parse(INPUT_FILE, format="turtle")
 
    results = []
    for concept_uri, label in graph.subject_objects(PREDICATE_PREF_LABEL):
        results.append((str(concept_uri), str(label)))
 
    results.sort(key=lambda row: row[1].lower())  # alphabetical by label
 
    print(f"Found {len(results)} subject headings. Writing {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["uri", "label_de", "label_es", "notation"])
        for uri, label_de in results:
            writer.writerow([uri, label_de, "", ""])
 
    print("Done.")
 
 
if __name__ == "__main__":
    main()
 