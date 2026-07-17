# 1. Combine mapped keywords from both corpora - done
# 2. Map uris to mapping file 
    # 2.1. Iterate over the mapping list of lists 
    # 2.2. Iterate over the nested lists of dictionaries
    # 2.3. See if the key '@id starts with "https://d-nb.info/"
    # 2.4. If yes, save the id after the last slash as ger_id and take the value of the key "http://www.w3.org/2004/02/skos/core#closeMatch" which is a list of dicts
    # 2.5. Take the fist item, go to the key @id and take its value 
    # 2.6. As spa_id take the id present in the uri (from https://datos.bne.es/resource/XX465978 only XX465978)
    # 2.7. The results should be a list of dicts with ger_id as key and spa_id as value, e.g. {"4055964-6": "XX465978"}
# 3. See how many keywords are mapped in %
# 4. Get the spanish labels for the mapped keywords
# 5. The rest of the vocabs has to be mapped to wikidata or translated with an LLM


import json

path_keywords_small = "Docs/mapped_keywords_fid.json"
path_keywords_large = "Docs/mapped_keywords_all.json"
mapping_file = "Data/Vocabs/mapping-authorities-gnd-embne_lds_20250916.jsonld"

def combine_keyword_lists(path_a, path_b):
    """Load two mapped-keyword JSON files and combine them into one unique list.

    Each input file is a JSON array of dicts shaped like:
        {"id": "gnd/4055964-6", "keyword": "Spanien", "count": 16977}

    Each output dict has keys ger_id, ger_text, count, spa_id, spa_text.
    ger_id and ger_text are taken from "id" and "keyword".
    count is summed across both files when the same id+keyword appears in both.
    spa_id and spa_text are empty strings, to be filled in later.
    """
    with open(path_a, encoding="utf-8") as f:
        list_a = json.load(f)
    with open(path_b, encoding="utf-8") as f:
        list_b = json.load(f)

    combined = {}

    for item in list_a + list_b:
        if not isinstance(item, dict):
            continue

        ger_id = item.get("id", "")
        ger_text = item.get("keyword", "")

        if not ger_id:
            continue

        key = (ger_id, ger_text)
        combined[key] = {
                "ger_id": ger_id,
                "ger_text": ger_text,
                "spa_id": "",
                "spa_text": "",
            }

    return list(combined.values())




def load_mapping_file(path):
    """Load the mapping file and return its JSON content."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_gnd_to_bne_mappings(mapping_data):
    """Extract GND-to-BNE mappings from the nested mapping file structure.

    Iterate over the top-level list of lists and the nested lists of dicts.
    For each dict whose '@id' starts with 'https://d-nb.info/', extract the GND
    id after the last slash. Then take the first item from the
    'http://www.w3.org/2004/02/skos/core#closeMatch' list, extract its '@id'
    and use the id after the last slash as the BNE id.
    """
    mappings = []

    for nested_list in mapping_data:
        if not isinstance(nested_list, list):
            continue

        for item in nested_list:
            if not isinstance(item, dict):
                continue

            gnd_uri = item.get("@id", "")
            if not isinstance(gnd_uri, str) or not gnd_uri.startswith("https://d-nb.info/"):
                continue

            ger_id = gnd_uri.rsplit("/", 1)[-1]
            close_matches = item.get("http://www.w3.org/2004/02/skos/core#closeMatch", [])
            if not isinstance(close_matches, list) or not close_matches:
                continue

            first_match = close_matches[0]
            if not isinstance(first_match, dict):
                continue

            spa_uri = first_match.get("@id", "")
            if not isinstance(spa_uri, str) or "/" not in spa_uri:
                continue

            spa_id = spa_uri.rsplit("/", 1)[-1]
            if not ger_id or not spa_id:
                continue

            mappings.append({ger_id: spa_id})

    return mappings


def add_spa_id_to_combined(combined_keywords, mappings):
    """Add spa_id values to the combined keyword list using GND-to-BNE mappings."""
    mapping_lookup = {}
    for entry in mappings:
        if isinstance(entry, dict) and len(entry) == 1:
            ger_id, spa_id = next(iter(entry.items()))
            mapping_lookup[ger_id] = spa_id

    for item in combined_keywords:
        if not isinstance(item, dict):
            continue

        ger_id = item.get("ger_id", "")
        if not isinstance(ger_id, str) or not ger_id:
            continue

        ger_id_key = ger_id.rsplit("/", 1)[-1]
        spa_id = mapping_lookup.get(ger_id_key)
        if spa_id:
            item["spa_id"] = spa_id

    return combined_keywords


def get_unmapped_spa_id_stats(combined_keywords):
    """Calculate the percentage and count of keywords with no Spanish ID.
    
    Returns a dict with keys: count (unmapped), total, percentage.
    """
    if not combined_keywords:
        return {"count": 0, "total": 0, "percentage": 0.0}
    
    unmapped_count = 0
    for item in combined_keywords:
        if isinstance(item, dict):
            spa_id = item.get("spa_id", "")
            if not spa_id:
                unmapped_count += 1
    
    total = len(combined_keywords)
    percentage = (unmapped_count / total * 100) if total > 0 else 0.0
    
    return {
        "count": unmapped_count,
        "total": total,
        "percentage": round(percentage, 2)
    }


combined = combine_keyword_lists(path_keywords_small, path_keywords_large)
mapping_data = load_mapping_file(mapping_file)
mappings = extract_gnd_to_bne_mappings(mapping_data)
combined_mapped = add_spa_id_to_combined(combined, mappings)
stats = get_unmapped_spa_id_stats(combined_mapped)
#print(combined[0:10])
#print(f"Combined list has {len(combined)} unique keywords")
#print(f"Loaded mapping file with {len(mapping_data)} entries")

#print(mapping_data[7][0])  # Print the second entry's mapping for inspection
#print("---------------------------")
#print(mapping_data[7][200])  # Print the second entry's mapping for inspection
#print("---------------------------")
#print(mapping_data[7][-1])


print(stats)