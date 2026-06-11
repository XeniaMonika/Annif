
import json
import xml.etree.ElementTree as ET
from collections import Counter
import matplotlib.pyplot as plt

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
            # find subfield u
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

def map_keywords_to_id(record):
    """Return a list of unique keyword mappings as dicts: {'id': <id>, 'keyword': <text>}.

    Duplicates (same tag and keyword) are removed while preserving order.
    """
    
    mapped = []
    seen = set()
    for tag in ("044K", "041A"):
        for datafield in record.findall(f".//ns1:datafield[@tag='{tag}']", ns):
            subfield7 = datafield.find("ns1:subfield[@code='7']", ns)
            if subfield7 is None:
                continue

            id_text = (subfield7.text or "").strip()
            if not id_text:
                continue

            for subfield in datafield.findall("ns1:subfield", ns):
                code = subfield.attrib.get("code")
                if code not in ("a", "A"):
                    continue

                keyword_text = (subfield.text or "").strip()
                if not keyword_text:
                    continue

                key = (id_text, keyword_text)
                if key not in seen:
                    seen.add(key)
                    mapped.append({"id": id_text, "keyword": keyword_text})
               
   
    return mapped





tree = ET.parse(path_data_raw)
root = tree.getroot()
NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}
records = root.findall('.//record')
if not records:
    records = list(root)

mapped_keywords = []
for record in records:
    mapped_keywords.extend(map_keywords_to_id(record))



print(f"Found {len(mapped_keywords)} mapped keywords in XML records")


def keyword_distribution_from_jsonl(path_jsonl):
    keyword_counts = Counter()
    try:
        with open(path_jsonl, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                for key, value in record.items():
                    if "keyword" in key.lower() or "subject" in key.lower():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, str) and item.strip():
                                    keyword_counts[item.strip()] += 1
                        elif isinstance(value, str) and value.strip():
                            keyword_counts[value.strip()] += 1
    except FileNotFoundError:
        print(f"JSONL file not found: {path_jsonl}")
        return Counter()

    return keyword_counts


plot_path = "C:\\Users\\kudelamo\\Projects\\Annif\\keyword_frequency_plot.png"
keyword_counts = keyword_distribution_from_jsonl(path_data_ready)

if keyword_counts:
    counts = [count for _, count in keyword_counts.most_common()]
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(counts) + 1), counts, marker="o", linewidth=1)
    plt.title("Keyword Frequency Distribution")
    plt.xlabel("Keyword rank (descending frequency)")
    plt.ylabel("Frequency")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()

    print("Top 10 most frequent keywords:")
    for keyword, count in keyword_counts.most_common(10):

        
        print(f"{keyword}: {count}")
    print(f"Keyword frequency plot saved to: {plot_path}")
else:
    print(f"No keywords found in {path_data_ready}")
