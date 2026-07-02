import json
import xml.etree.ElementTree as ET
from collections import Counter

input_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\data_gnd.xml"
output_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\mapped_keywords.json"

# Map GND keywords to their IDs and text to make the analysis of keyword distribution human-readable
def map_keywords_to_id(record):
    mapped = []
    for tag in ("044K", "041A", "044L"):
        for datafield in record.findall(f".//ns1:datafield[@tag='{tag}']", ns):
            subfield7 = datafield.find("ns1:subfield[@code='7']", ns)
            id_text = (subfield7.text or "").strip() if subfield7 is not None else ""

            # Only proceed if subfield 7 is present and non-empty
            if not id_text:
                continue

            for subfield in datafield.findall("ns1:subfield", ns):
                code = subfield.attrib.get("code")
                if code not in ("a", "A"):
                    continue

                keyword_text = (subfield.text or "").strip()
                if not keyword_text:
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