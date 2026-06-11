import json

INPUT_FILE = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\duplicates_author_title.json"
OUTPUT_FILE = "C:\\Users\\kudelamo\\Projects\\Annif\\Docs\\edge_cases_duplicates.md"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

same_status_diff_keywords = []
diff_status_diff_keywords = []

for entry in data:
    records = entry["records"]
    if len(records) < 2:
        continue

    # Deduplicate keywords per record
    keywords_per_record = [set(r["keywords"]) for r in records]
    statuses = [r["status"] for r in records]

    # Check if any pair has different keywords
    all_same_keywords = all(kw == keywords_per_record[0] for kw in keywords_per_record)
    all_same_status = len(set(statuses)) == 1

    if not all_same_keywords and all_same_status:
        same_status_diff_keywords.append(entry)
    elif not all_same_keywords and not all_same_status:
        diff_status_diff_keywords.append(entry)

output_lines = []
output_lines.append(f"Different keywords, same status: {len(same_status_diff_keywords)}")
for entry in same_status_diff_keywords:
    ppns = ", ".join(r["id"] for r in entry["records"])
    output_lines.append(f"  {entry['author']} — {entry['title']}")
    output_lines.append(f"  PPNs: {ppns}")
    output_lines.append(f"  -----------------------------------")

output_lines.append("\n")

output_lines.append(f"Different keywords, different status: {len(diff_status_diff_keywords)}")
for entry in diff_status_diff_keywords:
    ppns = ", ".join(r["id"] for r in entry["records"])
    output_lines.append(f"  {entry['author']} — {entry['title']}")
    output_lines.append(f"  PPNs: {ppns}")
    output_lines.append(f"  -----------------------------------")

output_text = "\n".join(output_lines)
print(output_text)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(output_text)
