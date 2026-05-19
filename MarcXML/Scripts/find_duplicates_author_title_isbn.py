import json
import xml.etree.ElementTree as ET
from collections import defaultdict

INPUT_FILE = "./Data/Spanish/data_689.xml"
OUTPUT_FILE = "./Data/Spanish/duplicates_author_title_isbn.json"
NS1 = "http://www.loc.gov/MARC21/slim"
ns= {"ns1": NS1}

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

def text_of(element):
    return element.text.strip() if element is not None and element.text else None

def extract_689_keywords(record):
    """Extract text from 689 field subfield a only"""
    keywords = []
    for datafield in record.findall(".//ns1:datafield[@tag='689']", ns):
        for subfield in datafield.findall("ns1:subfield[@code='a']", ns):
            text = text_of(subfield)
            if text:
                keywords.append(text)
    return keywords

records_by_author_title_isbn = defaultdict(list)

for record in root:
    title = text_of(record.find(".//ns1:datafield[@tag='245']/ns1:subfield[@code='a']", ns))
    author = text_of(record.find(".//ns1:datafield[@tag='100']/ns1:subfield[@code='a']", ns))
    isbn = text_of(record.find(".//ns1:datafield[@tag='020']/ns1:subfield[@code='a']", ns))

    if title and author and isbn:
        records_by_author_title_isbn[(author, title, isbn)].append(record)

# Keep only groups with duplicates
duplicates = {
    (author, title, isbn): recs
    for (author, title, isbn), recs in records_by_author_title_isbn.items()
    if len(recs) > 1
}

if not duplicates:
    print("No records found with the same author, title, and isbn.")
else:
    total_duplicate_records = sum(len(recs) for recs in duplicates.values())
   
    for (author, title, isbn), recs in sorted(duplicates.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"{len(recs)} records — author: {author!r}, title: {title!r}, isbn: {isbn!r}")
        for record in recs:
            rec_id = record.find(".//ns1:controlfield[@tag='001']", ns)
            print("  id:", rec_id.text if rec_id is not None else "(no 001)")
        print()
    print(f"Found {len(duplicates)} duplicate groups with same author, title, and isbn:")
    print(f"Total duplicate records: {total_duplicate_records}\n")

    output_data = []
    for (author, title, isbn), recs in duplicates.items():
        output_data.append({
            "author": author,
            "title": title,
            "isbn": isbn,
            "count": len(recs),
            "records": [
                {
                    "id": text_of(record.find(".//ns1:controlfield[@tag='001']", ns)),
                    "keywords": extract_689_keywords(record)
                }
                for record in recs
            ]
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(output_data, out, ensure_ascii=False, indent=2)

    print(f"Saved duplicate groups to {OUTPUT_FILE}")
