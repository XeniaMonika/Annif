import json
from collections import Counter

input_corpus = "Data/Spanish_FID/corpus_validation.jsonl"
output_corpus = "Data/Spanish_FID/corpus_validation_no_longtail.jsonl"

# First pass: count all uri occurrences in subjects lists
uri_counts = Counter()
with open(input_corpus, encoding="utf-8") as infile:
    for line in infile:
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        subjects = record.get("subjects", [])
        for subj in subjects:
            uri = subj.get("uri")
            if uri is not None:
                uri_counts[uri] += 1
print(uri_counts)
# Determine uris to remove
threshold = 50
low_freq_uris = {uri for uri, count in uri_counts.items() if count < threshold}

deleted_keywords = 0
remaining_entries = 0
with open(input_corpus, encoding="utf-8") as infile, open(output_corpus, "w", encoding="utf-8") as outfile:
    for line in infile:
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        subjects = record.get("subjects", [])
        filtered_subjects = []
        for subj in subjects:
            uri = subj.get("uri")
            if uri is None or uri not in low_freq_uris:
                filtered_subjects.append(subj)
            else:
                deleted_keywords += 1
        if filtered_subjects:
            record["subjects"] = filtered_subjects
            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
            remaining_entries += 1

print(f"Deleted keywords: {deleted_keywords}")
print(f"Entries left in output corpus: {remaining_entries}")