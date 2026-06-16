
import json
import xml.etree.ElementTree as ET
from collections import Counter
#import matplotlib.pyplot as plt

path_data_raw = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\data_gnd.xml"
path_data_ready = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\corpus.jsonl"
output_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Docs\\corpus_stats_all.md"

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
def record_has_text_online(record):
    htmls = []
    htms = []
    pdfs = []
    jpgs = []
    for datafield in record.findall(".//ns1:datafield", ns):
        tag = datafield.attrib.get("tag")
        if tag == "017G":
            sub_u = datafield.find("ns1:subfield[@code='u']", ns)
            if sub_u is not None and sub_u.text and sub_u.text.endswith("html"):
                sub_a = datafield.find("ns1:subfield[@code='A']", ns)
                sub_kind = sub_a.text.strip() if sub_a is not None and sub_a.text and sub_a.text.strip() else "unknown"
                htmls.append(sub_kind)
            if sub_u is not None and sub_u.text and sub_u.text.endswith("htm"):
                sub_3 = datafield.find("ns1:subfield[@code='3']", ns)
                sub_kind = sub_3.text.strip() if sub_3 is not None and sub_3.text and sub_3.text.strip() else "unknown"
                htms.append(sub_kind)
            if sub_u is not None and sub_u.text and sub_u.text.endswith("pdf"):
                sub_y_3 = datafield.find("ns1:subfield[@code='y']", ns)
                if sub_y_3 is None:
                    sub_y_3 = datafield.find("ns1:subfield[@code='3']", ns)
                sub_kind = sub_y_3.text.strip() if sub_y_3 is not None and sub_y_3.text and sub_y_3.text.strip() else "unknown"
                pdfs.append(sub_kind)
            if sub_u is not None and sub_u.text and sub_u.text.endswith("jpg"):
                sub_3 = datafield.find("ns1:subfield[@code='3']", ns)
                sub_kind = sub_3.text.strip() if sub_3 is not None and sub_3.text and sub_3.text.strip() else "unknown"
                jpgs.append(sub_kind)
    return htmls, htms, pdfs, jpgs

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



NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}
records = []
for event, elem in ET.iterparse(path_data_raw, events=("end",)):
    if elem.tag.endswith("}record") or elem.tag == "record":
        records.append(elem)
# basic counts
raw_records_count = len(records)

all_htmls = []
all_htms = []
all_pdfs = []
all_jpgs = []

for record in records:
    htmls, htms, pdfs, jpgs = record_has_text_online(record)
    all_htmls.extend(htmls)
    all_htms.extend(htms)
    all_pdfs.extend(pdfs)
    all_jpgs.extend(jpgs)

html_counts = Counter(all_htmls)
htm_counts = Counter(all_htms)
pdf_counts = Counter(all_pdfs)
jpg_counts = Counter(all_jpgs)

html_total = len(all_htmls)
htm_total = len(all_htms)
pdf_total = len(all_pdfs)
jpg_total = len(all_jpgs)
print(f"Total records with HTML online: {html_total}")
print(f"Total records with HTM online: {htm_total}")
print(f"Total records with PDF online: {pdf_total}")
print(f"Total records with JPG online: {jpg_total}")

print(f"\nHTML resource kind frequencies: {dict(html_counts)}")
print(f"HTM resource kind frequencies: {dict(htm_counts)}")
print(f"PDF resource kind frequencies: {dict(pdf_counts)}")
print(f"JPG resource kind frequencies: {dict(jpg_counts)}")

# Count abstracts in XML records
abstracts_count = 0
for record in records:
    if record_has_abstract(record):
        abstracts_count += 1

# Count merged records and subject distribution and long titles from JSONL
subject_counts = Counter()
titles_long = 0
merged_count = 0
try:
    with open(path_data_ready, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            merged_count += 1
            sc = subject_count_from_json(rec)
            subject_counts[sc] += 1
            # find title fields
            for k, v in rec.items():
                if 'text' in k.lower() and isinstance(v, str):
                    if len(v.strip()) > 25:
                        titles_long += 1
                    break
except FileNotFoundError:
    print(f"JSONL file not found: {path_data_ready}")

# write markdown output
with open(output_file, 'w', encoding='utf-8') as out:
    out.write('# Corpus Statistics\n\n')
    out.write(f'**Raw records count:** {raw_records_count}\n\n')
    out.write(f'**Records count after merging duplicates:** {merged_count}\n\n')
    out.write(f'**Records with 047I abstract:** {abstracts_count}\n\n')
    out.write('**Online text resources**\n\n')
    out.write(f'- Total records with HTML online: {html_total}\n')
    out.write(f'- Total records with HTM online: {htm_total}\n')
    out.write(f'- Total records with PDF online: {pdf_total}\n')
    out.write(f'- Total records with JPG online: {jpg_total}\n\n')
    out.write('**Resources in HTML format**\n\n')
    for kind, count in html_counts.most_common():
        out.write(f'- {kind}: {count}\n')
    out.write('\n')
    out.write('**Resources in HTM format**\n\n')
    for kind, count in htm_counts.most_common():
        out.write(f'- {kind}: {count}\n')
    out.write('\n')
    out.write('**Resources in PDF format**\n\n')
    for kind, count in pdf_counts.most_common():
        out.write(f'- {kind}: {count}\n')
    out.write('\n')
    out.write('**Resources in JPG format**\n\n')
    for kind, count in jpg_counts.most_common():
        out.write(f'- {kind}: {count}\n')
    out.write('\n')
    out.write('**Subject counts per record:**\n\n')
    for sc, cnt in sorted(subject_counts.items()):
        out.write(f'- {sc} subject(s): {cnt}\n')
    out.write('\n')
    out.write(f'**Titles with more than 25 characters:** {titles_long}\n')

print(f"Wrote stats to: {output_file}")

#WIP - analyze the distribution of keywords in the JSONL file and plot it, also print top 10 keywords with counts to a markdown file
'''
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
'''