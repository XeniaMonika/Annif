import json
from pathlib import Path

keywords_big = Path(r".\Data\Vocabs\keywords_mapped_big.json")
keywords_small = Path(r".\Data\Vocabs\keywords_mapped_small.json")
keywords_both = Path(r".\Data\Vocabs\keywords_mapped_both.json")
spa_labels = Path(r".\Data\Vocabs\wikidata_spanish_labels.json")


def load_json(path):
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def save_json(path, data):
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)


def build_lookup(labels_data):
    lookup = {}
    for wikidata_id, entry in labels_data.items():
        ger_id = entry.get("ger_id")
        if not ger_id:
            continue
        lookup[ger_id] = {
            "label": entry.get("label", ""),
            "wikidata_id": wikidata_id,
        }
    return lookup


def add_spanish_labels(items, lookup):
    before = 0
    added = 0
    for item in items:
        spa_label = item.get("spa_label", "") or ""
        if spa_label:
            before += 1
            continue
        item_id = item.get("id", "")
        if item_id.startswith("gnd/"):
            item_id = item_id.split("/", 1)[1]
        match = lookup.get(item_id)
        if match and match.get("label"):
            item["spa_id"] = match.get("wikidata_id", item.get("spa_id", ""))
            item["spa_label"] = match["label"]
            added += 1
    return before, added


def process_file(path, lookup):
    data = load_json(path)
    before, added = add_spanish_labels(data, lookup)
    after = before + added
    missing = len(data) - after
    save_json(path, data)
    print(f"{path}: {before} keywords before adding, {after} keywords after adding, {missing} still missing")
    return before, added, missing


if __name__ == "__main__":
    labels_data = load_json(spa_labels)
    lookup = build_lookup(labels_data)

    process_file(keywords_big, lookup)
    process_file(keywords_small, lookup)
    process_file(keywords_both, lookup)

