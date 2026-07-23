import json

keywords_path = "./Data/Vocabs/keywords_mapped_both.json"
translated_path = "./Data/Vocabs/keywords_translated_deepl.json"

# Load keywords and labels
with open(keywords_path, 'r', encoding='utf-8') as f:
    keywords = json.load(f)

with open(translated_path, 'r', encoding='utf-8') as f:
    labels = json.load(f)

# Update keywords with spanish labels
keywords_without_spa_label = 0

for keyword in keywords:
    # Only update if spa_label is empty
    if not keyword.get("spa_label", "").strip():
        gnd_id = keyword.get("id")
        if gnd_id in labels:
            keyword["spa_label"] = labels[gnd_id]
        else:
            keywords_without_spa_label += 1
    else:
        # Keep existing spa_label as is
        pass

# Save updated keywords
with open(keywords_path, 'w', encoding='utf-8') as f:
    json.dump(keywords, f, ensure_ascii=False, indent=2)

print(f"Keywords without spanish labels after update: {keywords_without_spa_label}")

