import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

# 1. Basic setup and parsing
INPUT_FILE = "./Data/Spanish_FID/data_gnd.xml"
OUTPUT_FILE = "./Data/Spanish_FID/corpus.jsonl"
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns= {"ns1": NS1}

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

# 2. Helper functions
def text_of(element):
    return element.text.strip() if element is not None and element.text else None
  
def extract_gnd_keywords(record):
    """Extract text from 044K and 041A fields subfield 7 only"""
    keywords = []
    for tag in ("044K", "041A"):
        for datafield in record.findall(f".//ns1:datafield[@tag='{tag}']", ns):
           for subfield in datafield.findall(f"ns1:subfield[@code='7']", ns):
                    text = text_of(subfield)
                    if text:
                        keywords.append(text)
    return keywords


def get_level(record):
    return text_of(record.find(".//ns1:datafield[@tag='002@']/ns1:subfield[@code='0']", ns))


def get_isbn(record):
    """Extract ISBN from record field 004A subfield 0"""
    return text_of(record.find(".//ns1:datafield[@tag='004A']/ns1:subfield[@code='0']", ns))


def change_ids_to_uris(keywords_set):
    """Convert GND IDs to URIs, e.g. gnd12345 -> https://d-nb.info/gnd/12345"""
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
   # rec_id = text_of(record.find(".//ns1:datafield[@tag='003@']/ns1:subfield[@code='0']", ns)) or ""
    status = text_of(record.find(".//ns1:datafield[@tag='002@']/ns1:subfield[@code='0']", ns))
   # text = text_of(record.find(".//ns1:datafield[@tag='047I']/ns1:subfield[@code='a']", ns)) or ""
   # keywords = extract_gnd_keywords(record)
    author = f"{author_last_name}, {author_first_name}"    
    if subtitle:
        title_full = f"{title} : {subtitle}"
    else:
        title_full = title    
   # if title_full and author and isbn:
    #    records_by_author_title_isbn[(author, title_full, isbn)].append(record)    
    if title_full and author:
        records_by_author_title[(author, title_full)].append(record)

remove_records([record for recs in records_by_author_title.values() for record in recs if len(recs) > 1], root)


# 5. Transform duplicates 
for (author, title_full), recs in list(records_by_author_title.items()):
    if len(recs) <= 1:
        continue
    #5.1. Transform duplicates with same author, title and ISBNs into records with subjects
    records_by_isbn = defaultdict(list)
    for record in recs:
        isbn = get_isbn(record)
        if isbn:
            records_by_isbn[isbn].append(record)
    for isbn, isbn_recs in records_by_isbn.items():
        if len(isbn_recs) <= 1:
            continue
        keywords = set()
        for record in isbn_recs:
            keywords.update(extract_gnd_keywords(record))
        keywords = change_ids_to_uris(keywords)
        subjects = [{"uri": uri} for uri in sorted(keywords)]
        output_record = {"text": title_full, "subjects": subjects}
        write_record_to_file(output_record)
        for record in isbn_recs:
            records_by_author_title[(author, title_full)].remove(record)
        if not records_by_author_title[(author, title_full)]:
            del records_by_author_title[(author, title_full)]
    #5.2. Transform duplicates with same author and title and bibliographical level into records with subjects
    records_by_level = defaultdict(list)
    for record in recs:
        level = get_level(record)
        if level:
            records_by_level[level].append(record)
    for level, level_recs in records_by_level.items():
        if len(level_recs) <= 1:
            continue
        keywords = set()
        for record in level_recs:
            keywords.update(extract_gnd_keywords(record))
        keywords = change_ids_to_uris(keywords)
        subjects = [{"uri": uri} for uri in sorted(keywords)]
        output_record = {"text": title_full, "subjects": subjects}
        write_record_to_file(output_record)
        for record in level_recs:
            records_by_author_title[(author, title_full)].remove(record)
        if not records_by_author_title[(author, title_full)]:
            del records_by_author_title[(author, title_full)]
    # 5.3. From the remaining duplicates with same author and title, keep only the record with the most GND keywords and transform it into a record with subjects, remove the rest
    best_record = None
    max_keywords = 0
    for record in recs:
        keywords = set(extract_gnd_keywords(record))
        if len(keywords) > max_keywords:
            max_keywords = len(keywords)
            best_record = record
    if best_record is not None and max_keywords > 0:
        keywords = set(extract_gnd_keywords(best_record))
        keywords = change_ids_to_uris(keywords)
        subjects = [{"uri": uri} for uri in sorted(keywords)]
        output_record = {"text": title_full, "subjects": subjects}
        write_record_to_file(output_record)


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
