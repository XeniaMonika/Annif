import json
import xml.etree.ElementTree as ET
from collections import defaultdict

INPUT_FILE = "./PicaXML/Data/Spanish/data_gnd.xml"
OUTPUT_FILE = "./PicaXML/Data/Spanish/duplicates_author_title_isbn.json"
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns= {"ns1": NS1}

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

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

records_by_author_title_isbn = defaultdict(list)

for record in root:
    title = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
    subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
    author_first_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='D']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='D']", ns))
    author_last_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='A']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='A']", ns))
    isbn = text_of(record.find(".//ns1:datafield[@tag='004A']/ns1:subfield[@code='0']", ns)) or ""
    author = f"{author_last_name}, {author_first_name}" 
    if title and author:
        records_by_author_title_isbn[(author, title, subtitle, isbn)].append(record)

# Keep only groups with duplicates
duplicates = {
    (author, title, subtitle, isbn): recs
    for (author, title, subtitle, isbn), recs in records_by_author_title_isbn.items()
    if len(recs) > 1
}

if not duplicates:
    print("No records found with the same author, title, and ISBN.")
else:
    total_duplicate_records = sum(len(recs) for recs in duplicates.values())
   
    for (author, title, subtitle, isbn), recs in sorted(duplicates.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"{len(recs)} records — author: {author!r}, title: {title!r}, subtitle: {subtitle!r}, isbn: {isbn!r}  ")
        for record in recs:
            rec_id = record.find(".//ns1:datafield[@tag='003@']/ns1:subfield[@code='0']", ns)
            rec_status = record.find(".//ns1:datafield[@tag='002@']/ns1:subfield[@code='0']", ns)       
            print("  id:", rec_id.text if rec_id is not None else "(no 003@)")
            print("  status:", rec_status.text if rec_status is not None else "(no 002@)")
        print()
    print(f"Found {len(duplicates)} duplicate groups with same author, title, and ISBN:")
    print(f"Total duplicate records: {total_duplicate_records}\n")

    output_data = []
    for (author, title, subtitle, isbn), recs in duplicates.items():
        output_data.append({
            "author": author,
            "title": title,
            "subtitle": subtitle,
            "isbn": isbn,
            "count": len(recs),
            "records": [
                {
                    "id": text_of(record.find(".//ns1:datafield[@tag='003@']/ns1:subfield[@code='0']", ns)),
                    "status": text_of(record.find(".//ns1:datafield[@tag='002@']/ns1:subfield[@code='0']", ns)),
                    "keywords": extract_gnd_keywords(record)
                }
                for record in recs
            ]
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(output_data, out, ensure_ascii=False, indent=2)

    print(f"Saved duplicate groups to {OUTPUT_FILE}")
