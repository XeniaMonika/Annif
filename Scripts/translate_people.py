import json

input_file = "./Data/Vocabs/keywords_mapped_both.json"

# Load the JSON file
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Process each entry to identify people by comma pattern
people_count = 0
for entry in data:
    keyword = entry.get("keyword", "")
    
    # Check if keyword matches the pattern "Word, Word" (person name pattern)
    if "," in keyword: #nd entry.get("spa_label") == "":
        # Set the keyword as the spanish label for person names
        entry["spa_label"] = keyword
        people_count += 1

print(f"Total people entries processed: {people_count}")

# Save the modified file back to the same path
with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)