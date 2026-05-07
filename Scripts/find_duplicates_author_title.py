import json
import xml.etree.ElementTree as ET
from collections import defaultdict

INPUT_FILE = "./Data/Spanish/data_689.xml"
OUTPUT_FILE = "./Data/Spanish/duplicates_author_title.json"
NS1 = "http://www.loc.gov/MARC21/slim"
ns= {"ns1": NS1}

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

def text_of(element):
    return element.text.strip() if element is not None and element.text else None

records_by_author_title = defaultdict(list)

for record in root:
    title = text_of(record.find(".//ns1:datafield[@tag='245']/ns1:subfield[@code='a']", ns))
    author = text_of(record.find(".//ns1:datafield[@tag='100']/ns1:subfield[@code='a']", ns))

    if title and author:
        records_by_author_title[(author, title)].append(record)

# Keep only groups with duplicates
duplicates = {
    (author, title): recs
    for (author, title), recs in records_by_author_title.items()
    if len(recs) > 1
}

if not duplicates:
    print("No records found with the same author and the same title.")
else:
    total_duplicate_records = sum(len(recs) for recs in duplicates.values())
   
    for (author, title), recs in sorted(duplicates.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"{len(recs)} records — author: {author!r}, title: {title!r}")
        for record in recs:
            rec_id = record.find(".//ns1:controlfield[@tag='001']", ns)
            rec_isbn = record.find(".//ns1:datafield[@tag='020']/ns1:subfield[@code='a']", ns)           
            print("  id:", rec_id.text if rec_id is not None else "(no 001)")
            print("  isbn:", rec_isbn.text if rec_isbn is not None else "(no 020a)")
        print()
    print(f"Found {len(duplicates)} duplicate groups with same author and title:")
    print(f"Total duplicate records: {total_duplicate_records}\n")

    output_data = []
    for (author, title), recs in duplicates.items():
        output_data.append({
            "author": author,
            "title": title,
            "count": len(recs),
            "records": [
                {
                    "id": text_of(record.find(".//ns1:controlfield[@tag='001']", ns)),
                    "isbn": text_of(record.find(".//ns1:datafield[@tag='020']/ns1:subfield[@code='a']", ns)),
                }
                for record in recs
            ]
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(output_data, out, ensure_ascii=False, indent=2)

    print(f"Saved duplicate groups to {OUTPUT_FILE}")
