import csv
import re
import sys

def clean_label(label):
    if not label:
        return ""
    # Entfernt administrative System-Meldungen
    label = re.sub(r'!!!GESPERRT!!!', '', label)
    label = re.sub(r'!!!BLOQUEADO!!!', '', label)
    return label.strip()

def escape_quotes(text):
    return text.replace('"', '\\"')

def extract_plain_and_qualifier(german_label):
    # Erkennt Begriffe mit Qualifikatoren wie "Dame <Schach>"
    match = re.match(r'^([^<]+)\s*<([^>]+)>$', german_label)
    if match:
        plain_term = match.group(1).strip()
        qualifier = match.group(2).strip()
        return plain_term, qualifier
    return german_label, None

def convert_csv_to_ttl(csv_path, ttl_path):
    print(f"Lese CSV-Datei: {csv_path}...")
    concepts = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Header überprüfen
        headers = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
        if 'uri' not in headers or 'label_de' not in headers or 'label_es' not in headers:
            print(f"Fehler: CSV-Header müssen 'uri', 'label_de' und 'label_es' enthalten. Gefunden: {reader.fieldnames}", file=sys.stderr)
            return False
            
        for row in reader:
            uri = row['uri'].strip()
            if not uri:
                continue
                
            label_de = clean_label(row['label_de'])
            label_es = clean_label(row['label_es'])
            
            # Extrahiere reinen deutschen Begriff als altLabel (Synonym)
            plain_de, qualifier_de = extract_plain_and_qualifier(label_de)
            
            concept = {
                'uri': uri,
                'pref_de': label_de,       # Behält das <Qualifikator>-Tag für die DNB-Anzeige
                'pref_es': label_es,       # Spanisches preferred Label
                'alt_de': plain_de if qualifier_de else None  # Plain Term als MLLM-Suchanker
            }
            concepts.append(concept)

    print(f"Schreibe Turtle-Datei (SKOS): {ttl_path}...")
    
    with open(ttl_path, 'w', encoding='utf-8') as out:
        # SKOS-Header schreiben
        out.write("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n")
        out.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n")
        
        for concept in concepts:
            uri = concept['uri']
            pref_de = escape_quotes(concept['pref_de'])
            pref_es = escape_quotes(concept['pref_es'])
            
            out.write(f"<{uri}> rdf:type skos:Concept ;\n")
            out.write(f'    skos:prefLabel "{pref_de}"@de ;\n')
            out.write(f'    skos:prefLabel "{pref_es}"@es')
            
            # Falls ein reines altLabel für das Deutsche existiert, anfügen
            if concept['alt_de']:
                alt_de = escape_quotes(concept['alt_de'])
                out.write(f" ;\n    skos:altLabel \"{alt_de}\"@de .\n\n")
            else:
                out.write(" .\n\n")
                
    print(f"Erfolgreich konvertiert! {len(concepts)} Konzepte importiert.")
    return True

if __name__ == "__main__":
    CSV_INPUT = ".\\Data\\Vocabs\\vocabs.csv"
    TTL_OUTPUT = ".\\Data\\Vocabs\\subjects.ttl"
    convert_csv_to_ttl(CSV_INPUT, TTL_OUTPUT)
