
import json
import xml.etree.ElementTree as ET
from collections import Counter

path_data_raw = "C:\\Users\\kudelamo\\Projects\\Annif\\PicaXML\\Data\\Spanish\\data_gnd.xml"
path_data_ready = "C:\\Users\\kudelamo\\Projects\\Annif\\PicaXML\\Data\\Spanish\\corpus.jsonl"
output_file = "C:\\Users\\kudelamo\\Projects\\Annif\\corpus_stats.md"

# Count records with abstracts in the data structure
def record_has_abstract(record):
    for field in record.iter():
        tag = field.tag
        field_id = field.attrib.get("id") or field.attrib.get("tag") or tag
        if field_id == "047I":
            # Check subfields for actual text content
            for subfield in field:
                if subfield.text and subfield.text.strip():
                    return True
            # Fallback: text directly in field element
            if field.text and field.text.strip():
                return True
    return False

# Count records with text-based catalog enrichment data available online
def record_has_text_in_html(record):
    # iterate over all datafields
    for datafield in record.findall(".//ns1:datafield", ns):
        tag = datafield.attrib.get("tag")
        if tag == "017G":
            # find subfield 7
            sub_u = datafield.find("ns1:subfield[@code='u']", ns)
            if sub_u is not None and sub_u.text and (sub_u.text.endswith("html") or sub_u.text.endswith("htm")):
                return True
    return False

# Determine subject count in a JSON record
def subject_count_from_json(record):
    if not isinstance(record, dict):
        return 0   

    for key, value in record.items():
        if "subject" in key.lower():
            if isinstance(value, list):
                return len(value)
            if isinstance(value, str) and value.strip():
                return 1
            return 0

    return 0



tree = ET.parse(path_data_raw)
root = tree.getroot()
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}
records = root.findall('.//record')
if not records:
    records = list(root)

raw_records_count = len(records)
abstracts_count = sum(1 for record in records if record_has_abstract(record))
text_in_html_count = sum(1 for record in records if record_has_text_in_html(record))
print(f"Records with 047I abstract: {abstracts_count} out of {len(records)}")
print(f"Records with 017G text in HTML: {text_in_html_count} out of {len(records)}")

subject_counts = Counter()
titles_long = 0
record_count = 0
try:
    with open(path_data_ready, "r", encoding="utf-8") as handle:
        for line in handle:#
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            subject_counts[subject_count_from_json(record)] += 1
            record_count += 1
            # Count titles with more than 25 characters
            if isinstance(record, dict):
                title = record.get("text", "")
                if isinstance(title, str) and len(title) > 25:
                    titles_long += 1
except FileNotFoundError:
    pass

if subject_counts:
    print("Subject counts per record:")
    for count in sorted(subject_counts):
        print(f"{count} subject(s): {subject_counts[count]}")
else:
    print(f"No subject counts available from {path_data_ready}")

print(f"Titles with more than 25 characters: {titles_long}")



with open(output_file, "w", encoding="utf-8") as f:
    f.write("# Corpus Statistics\n\n")
    f.write(f"**Raw records count:** {raw_records_count}\n\n")
    f.write(f"**Records count after merging duplicates:** {record_count}\n\n")
    f.write(f"**Records with 047I abstract:** {abstracts_count}\n\n")
    f.write(f"**Records with 017G text in HTML:** {text_in_html_count}\n\n")
    
    if subject_counts:
        f.write("## Subject counts per record:\n\n")
        for count in sorted(subject_counts):
            f.write(f"- {count} subject(s): {subject_counts[count]}\n")
    else:
        f.write(f"No subject counts available from {path_data_ready}\n\n")
    
    f.write(f"\n**Titles with more than 25 characters:** {titles_long}\n")

print(f"Results written to {output_file}")
print(f"Records with 047I abstract: {abstracts_count} out of {len(records)}")
print(f"Records with 017G text in HTML: {text_in_html_count} out of {len(records)}")
